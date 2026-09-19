import redis.asyncio as aioredis
from ports.cache.cache_store import CacheStore
from adapters.exceptions import CacheError


class RedisCacheStore(CacheStore):
    def __init__(self, client: aioredis.Redis) -> None:
        self._client = client

    async def get(self, key: str) -> str | None:
        try:
            value = await self._client.get(key)
            return value.decode() if value else None
        except Exception as exc:
            raise CacheError(str(exc)) from exc

    async def set(self, key: str, value: str, ttl_seconds: int = 300) -> None:
        try:
            await self._client.set(key, value, ex=ttl_seconds)
        except Exception as exc:
            raise CacheError(str(exc)) from exc

    async def delete(self, key: str) -> None:
        try:
            await self._client.delete(key)
        except Exception as exc:
            raise CacheError(str(exc)) from exc
