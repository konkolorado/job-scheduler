from __future__ import annotations

import logging
import typing as t

import aioredis

from job_scheduler.cache.base import ScheduleCache
from job_scheduler.config import config

logger = logging.getLogger(__name__)


class RedisScheduleCache(ScheduleCache):
    redis: aioredis.Redis

    async def add(self, *items: str) -> None:
        for i in items:
            await self.redis.set(i, i, ex=config.cache.ttl_s, nx=True)

    async def get(self, *items: str) -> t.List[t.Union[str, None]]:
        return await self.redis.mget(items)

    @classmethod
    async def get_cache(cls) -> RedisScheduleCache:
        logger.info(f"Instantiating redis pool for caching at {config.cache.url}.")
        cls.redis = aioredis.from_url(
            config.cache.url, encoding="utf-8", decode_responses=True
        )
        logger.info(f"Redis pool for caching sucessfully instantiated.")
        return cls()
