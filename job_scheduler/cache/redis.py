from __future__ import annotations

import logging
import typing as t

import aioredis

from job_scheduler.cache.base import ScheduleCache
from job_scheduler.config import config

logger = logging.getLogger(__name__)

logger.info(f"Instantiating redis pool for caching at {config.cache_url}.")
redis = aioredis.from_url(config.cache_url, encoding="utf-8", decode_responses=True)
logger.info(f"Redis pool for caching sucessfully instantiated.")


class RedisScheduleCache(ScheduleCache):
    def __init__(self) -> None:
        self.ttl_s = 10

    async def add(self, *items: str) -> None:
        for i in items:
            await redis.set(i, i, ex=self.ttl_s, nx=True)

    async def get(self, *items: str) -> t.List[t.Union[str, None]]:
        return await redis.mget(items)

    @classmethod
    async def get_cache(cls) -> RedisScheduleCache:
        return cls()
