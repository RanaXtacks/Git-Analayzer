import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.responses import StreamingResponse

from app.config import get_settings, Settings
from app.github.repository import parse_and_validate_github_url
from app.github.client import (
    GitHubClient,
    GitHubNotFoundError,
    GitHubRateLimitError,
    GitHubAuthError,
    GitHubAPIError,
)
from app.context.builder import ContextBuilder
from app.guide.generator import GuideGenerator
from app.models.repository import (
    AnalyzeRequest,
    AnalysisResponse,
    AnalysisMetadata,
    RepositoryMetadata,
)
from app.models.guide import OnboardingGuide
from app.cache.service import CacheService, build_cache_key
from app.api.dependencies import (
    get_github_client,
    get_analyzer,
    get_llm_provider,
    get_cache,
    get_active_analyses_map,
)

logger = logging.getLogger("git_analyzer.api.routes")
router = APIRouter(prefix="/api")


@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    """Health check endpoint exposing system status and inference provider connectivity."""
    llm = get_llm_provider()
    llm_healthy = await llm.health_check()
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_healthy": llm_healthy,
        "database_enabled": settings.DATABASE_ENABLED,
        "redis_enabled": settings.REDIS_ENABLED,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/repositories/{owner}/{repo}/status")
async def get_repository_status(
    owner: str,
    repo: str,
    cache: CacheService = Depends(get_cache),
    settings: Settings = Depends(get_settings),
):
    """Check if an analyzed guide currently exists in cache for the repository."""
    model_name = settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else settings.VLLM_MODEL
    key = build_cache_key(owner, repo, "HEAD", model_name)
    cached = await cache.get(key)
    if cached:
        return {"status": "analyzed", "cached": True, "generated_at": cached.get("metadata", {}).get("generated_at")}
    return {"status": "not_analyzed", "cached": False}


@router.post("/analyze/sync", response_model=AnalysisResponse)
async def analyze_repository_sync(
    body: AnalyzeRequest,
    settings: Settings = Depends(get_settings),
    cache: CacheService = Depends(get_cache),
):
    """
    Synchronous analysis endpoint returning full AnalysisResponse directly.
    Ideal for direct API consumption and automated test verification.
    """
    start_time = time.time()
    try:
        owner, repo = parse_and_validate_github_url(body.url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    model_name = settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else settings.VLLM_MODEL
    active_map = get_active_analyses_map()
    dedup_key = f"{owner.lower()}/{repo.lower()}"

    # Check deduplication: wait if an analysis is already in-progress
    if dedup_key in active_map:
        await active_map[dedup_key].wait()
        # After waiting, check cache
        cached = await cache.get(build_cache_key(owner, repo, None, model_name))
        if cached:
            return AnalysisResponse.model_validate(cached)

    github_client = get_github_client()
    try:
        # Pre-check repo and HEAD SHA for cache
        meta = await github_client.get_repository(owner, repo)
        cache_key = build_cache_key(owner, repo, meta.head_sha, model_name)

        cached_data = await cache.get(cache_key)
        if cached_data:
            cached_data["metadata"]["cached"] = True
            return AnalysisResponse.model_validate(cached_data)

        # Mark in-progress for deduplication
        event = asyncio.Event()
        active_map[dedup_key] = event

        try:
            analyzer = get_analyzer()
            context_builder = ContextBuilder(
                github_client=github_client,
                analyzer=analyzer,
                max_readme_size=settings.MAX_README_SIZE,
                max_file_size=settings.MAX_FILE_SIZE,
                max_issues=settings.MAX_ISSUES,
            )
            context = await context_builder.build(owner, repo)

            llm = get_llm_provider()
            generator = GuideGenerator(llm)
            guide = await generator.generate_guide(context)

            duration = round(time.time() - start_time, 2)
            response = AnalysisResponse(
                repository=context.metadata,
                guide=guide,
                metadata=AnalysisMetadata(
                    commit_sha=context.metadata.head_sha,
                    model=model_name,
                    provider=settings.LLM_PROVIDER,
                    generated_at=datetime.now(timezone.utc).isoformat(),
                    cached=False,
                    duration_seconds=duration,
                ),
            )

            # Save in cache
            await cache.set(cache_key, response.model_dump(), ttl_seconds=settings.CACHE_TTL)
            return response
        finally:
            event.set()
            active_map.pop(dedup_key, None)

    except GitHubNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except GitHubRateLimitError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except (GitHubAuthError, GitHubAPIError) as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Analysis failed: {str(e)}")
    finally:
        await github_client.close()


@router.post("/analyze")
async def analyze_repository_stream(
    request: Request,
    body: AnalyzeRequest,
    settings: Settings = Depends(get_settings),
    cache: CacheService = Depends(get_cache),
):
    """
    Server-Sent Events (SSE) streaming endpoint:
    Streams granular progress stages ("metadata", "readme", "structure", "generating", etc.)
    followed by the final "complete" event containing the full AnalysisResponse.
    """
    try:
        owner, repo = parse_and_validate_github_url(body.url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def event_generator() -> AsyncGenerator[Dict[str, str], None]:
        start_time = time.time()
        model_name = settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else settings.VLLM_MODEL
        github_client = get_github_client()
        active_map = get_active_analyses_map()
        dedup_key = f"{owner.lower()}/{repo.lower()}"

        try:
            # Yield initial connection event
            yield {
                "event": "progress",
                "data": json.dumps({"stage": "init", "status": "running", "detail": f"Initializing analysis for {owner}/{repo}..."}),
            }

            # Check deduplication
            if dedup_key in active_map:
                yield {
                    "event": "progress",
                    "data": json.dumps({"stage": "dedup", "status": "running", "detail": "Analysis in progress by another client. Awaiting result..."}),
                }
                await active_map[dedup_key].wait()
                cached = await cache.get(build_cache_key(owner, repo, None, model_name))
                if cached:
                    cached["metadata"]["cached"] = True
                    yield {
                        "event": "complete",
                        "data": json.dumps(cached),
                    }
                    return

            # Check cache with HEAD commit
            meta = await github_client.get_repository(owner, repo)
            cache_key = build_cache_key(owner, repo, meta.head_sha, model_name)
            cached_data = await cache.get(cache_key)

            if cached_data:
                cached_data["metadata"]["cached"] = True
                yield {
                    "event": "progress",
                    "data": json.dumps({"stage": "cache", "status": "complete", "detail": "Loaded fresh guide from cache."}),
                }
                yield {
                    "event": "complete",
                    "data": json.dumps(cached_data),
                }
                return

            # Set in-flight event
            event = asyncio.Event()
            active_map[dedup_key] = event

            # Progress callback for ContextBuilder
            queue: asyncio.Queue = asyncio.Queue()

            async def progress_callback(stage: str, status_val: str, payload: Dict):
                await queue.put({
                    "stage": stage,
                    "status": status_val,
                    "detail": payload.get("detail", ""),
                })

            async def run_context_and_generation():
                analyzer = get_analyzer()
                builder = ContextBuilder(
                    github_client=github_client,
                    analyzer=analyzer,
                    max_readme_size=settings.MAX_README_SIZE,
                    max_file_size=settings.MAX_FILE_SIZE,
                    max_issues=settings.MAX_ISSUES,
                )
                context = await builder.build(owner, repo, progress_cb=progress_callback)

                await queue.put({
                    "stage": "generating",
                    "status": "running",
                    "detail": f"Reasoning over repository evidence using open-weight {model_name}...",
                })

                llm = get_llm_provider()
                generator = GuideGenerator(llm)
                guide = await generator.generate_guide(context)

                await queue.put({
                    "stage": "validating",
                    "status": "running",
                    "detail": "Verifying claims against repository tree and open issues...",
                })

                duration = round(time.time() - start_time, 2)
                response = AnalysisResponse(
                    repository=context.metadata,
                    guide=guide,
                    metadata=AnalysisMetadata(
                        commit_sha=context.metadata.head_sha,
                        model=model_name,
                        provider=settings.LLM_PROVIDER,
                        generated_at=datetime.now(timezone.utc).isoformat(),
                        cached=False,
                        duration_seconds=duration,
                    ),
                )

                # Save in cache
                await cache.set(cache_key, response.model_dump(), ttl_seconds=settings.CACHE_TTL)
                await queue.put({"complete_result": response.model_dump()})

            task = asyncio.create_task(run_context_and_generation())

            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info("Client disconnected from SSE stream.")
                    task.cancel()
                    break

                try:
                    item = await asyncio.wait_for(queue.get(), timeout=1.0)
                    if "complete_result" in item:
                        yield {
                            "event": "complete",
                            "data": json.dumps(item["complete_result"]),
                        }
                        break
                    else:
                        yield {
                            "event": "progress",
                            "data": json.dumps(item),
                        }
                except asyncio.TimeoutError:
                    if task.done():
                        # If task finished with exception, propagate it
                        exc = task.exception()
                        if exc:
                            raise exc
                        break

            await task

        except GitHubNotFoundError as e:
            yield {"event": "error", "data": json.dumps({"error": str(e), "type": "not_found"})}
        except GitHubRateLimitError as e:
            yield {"event": "error", "data": json.dumps({"error": str(e), "type": "rate_limit"})}
        except Exception as e:
            logger.exception("Analysis pipeline exception in SSE generator")
            yield {"event": "error", "data": json.dumps({"error": f"Analysis failed: {str(e)}", "type": "server_error"})}
        finally:
            if dedup_key in active_map:
                active_map[dedup_key].set()
                active_map.pop(dedup_key, None)
            await github_client.close()

    async def sse_stream() -> AsyncGenerator[str, None]:
        async for item in event_generator():
            yield f"event: {item['event']}\ndata: {item['data']}\n\n"

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(sse_stream(), headers=headers, media_type="text/event-stream")
