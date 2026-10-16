import asyncio
from typing import Dict
from app.config import get_settings, Settings
from app.github.client import GitHubClient
from app.analyzer.repository import RepositoryAnalyzer
from app.llm.base import LLMProvider
from app.llm.ollama import OllamaProvider
from app.llm.vllm import VLLMProvider
from app.llm.deterministic import DeterministicProvider
from app.cache.service import CacheService, InMemoryCacheService, RedisCacheService

# Singleton instances
_cache_service: CacheService | None = None
_active_analyses: Dict[str, asyncio.Event] = {}


def get_cache() -> CacheService:
    global _cache_service
    if _cache_service is None:
        settings = get_settings()
        if settings.REDIS_ENABLED:
            _cache_service = RedisCacheService(settings.REDIS_URL)
        else:
            _cache_service = InMemoryCacheService()
    return _cache_service


def get_github_client() -> GitHubClient:
    settings = get_settings()
    return GitHubClient(
        token=settings.GITHUB_TOKEN,
        base_url=settings.GITHUB_API_BASE,
    )


def get_analyzer() -> RepositoryAnalyzer:
    settings = get_settings()
    return RepositoryAnalyzer(max_tree_entries=settings.MAX_TREE_ENTRIES)


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    provider_name = settings.LLM_PROVIDER.lower().strip()
    if provider_name == "vllm":
        return VLLMProvider(
            base_url=settings.VLLM_BASE_URL,
            model=settings.VLLM_MODEL,
            api_key=settings.VLLM_API_KEY,
            timeout=float(settings.LLM_TIMEOUT),
        )
    elif provider_name == "deterministic":
        return DeterministicProvider()
    else:
        return OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            timeout=float(settings.LLM_TIMEOUT),
            num_gpu=settings.OLLAMA_NUM_GPU,
        )


def get_active_analyses_map() -> Dict[str, asyncio.Event]:
    return _active_analyses
