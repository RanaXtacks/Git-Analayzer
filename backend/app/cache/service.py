import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("git_analyzer.cache")


class CacheService(ABC):
    """Abstract Cache Interface."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Dict[str, Any], ttl_seconds: int = 3600) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass


class InMemoryCacheService(CacheService):
    """Fallback in-memory cache with TTL support for minimal dev mode without Redis."""

    def __init__(self):
        self._store: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self._store:
            expiry, data = self._store[key]
            if time.time() < expiry:
                return data
            else:
                del self._store[key]
        return None

    async def set(self, key: str, value: Dict[str, Any], ttl_seconds: int = 3600) -> None:
        self._store[key] = (time.time() + ttl_seconds, value)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)


class RedisCacheService(CacheService):
    """Production Redis cache implementation."""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client = None

    async def _get_client(self):
        if self._client is None:
            import redis.asyncio as aioredis
            self._client = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._client

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            client = await self._get_client()
            raw = await client.get(key)
            if raw:
                return json.loads(raw)
        except Exception as e:
            logger.warning(f"Redis get failed for key {key}: {e}")
        return None

    async def set(self, key: str, value: Dict[str, Any], ttl_seconds: int = 3600) -> None:
        try:
            client = await self._get_client()
            await client.set(key, json.dumps(value), ex=ttl_seconds)
        except Exception as e:
            logger.warning(f"Redis set failed for key {key}: {e}")

    async def delete(self, key: str) -> None:
        try:
            client = await self._get_client()
            await client.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete failed for key {key}: {e}")


def build_cache_key(owner: str, repo: str, commit_sha: Optional[str], model: str) -> str:
    """
    Constructs a cache key bound to the repository commit SHA and model version.
    Ensures outdated guides are invalidated when new commits land.
    """
    sha_part = commit_sha or "latest"
    return f"guide:{owner.lower()}/{repo.lower()}:{sha_part}:{model}"
