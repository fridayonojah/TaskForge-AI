from __future__ import annotations
import os
import redis.asyncio as aioredis


def create_redis_client() -> aioredis.Redis:
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return aioredis.from_url(redis_url, decode_responses=False)
