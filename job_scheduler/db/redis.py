from __future__ import annotations

import logging
from typing import MutableMapping, Sequence

import aioredis

from job_scheduler.config import config
from job_scheduler.db.base import JobRepository, ScheduleRepository
from job_scheduler.db.types import JobRepoItem, ScheduleRepoItem

logger = logging.getLogger(__name__)

logger.info(f"Instantiating redis pool as DB at {config.database_url}.")
redis = aioredis.from_url(config.database_url, encoding="utf-8", decode_responses=True)
logger.info(f"Redis pool for DB sucessfully instantiated.")


class RedisScheduleRepository(ScheduleRepository):
    def __init__(self):
        self.table = "schedules"
        self.namespace = "schedules"

    def namespaced_key(self, key) -> str:
        if key.startswith(f"{self.namespace}:"):
            return key
        return f"{self.namespace}:{key}"

    async def add(self, *items: ScheduleRepoItem) -> None:
        keys_and_vals = {self.namespaced_key(i.id): i.schedule for i in items}
        keys_to_scores = {i.id: i.priority for i in items}

        await redis.mset(keys_and_vals)
        await redis.zadd(self.table, mapping=keys_to_scores, nx=True)

    async def get(self, *keys: str) -> Sequence[str]:
        if len(keys) == 0:
            return []

        namespaced = [self.namespaced_key(k) for k in keys]
        result = await redis.mget(*namespaced)
        if len(result) == 1 and result[0] == None:
            return []
        return result

    async def update(self, *items: ScheduleRepoItem) -> None:
        keys_and_vals = {self.namespaced_key(i.id): i.schedule for i in items}
        keys_to_scores = {i.id: i.priority for i in items}

        await redis.mset(keys_and_vals)
        await redis.zadd(self.table, mapping=keys_to_scores, xx=True)

    async def delete(self, *keys: str) -> None:
        namespaced = [self.namespaced_key(k) for k in keys]
        delete = await redis.delete(*namespaced)
        zrem = await redis.zrem(self.table, *keys)

    async def get_range(self, min_value: float, max_value: float) -> Sequence[str]:
        return await redis.zrangebyscore(self.table, min=min_value, max=max_value)

    @property
    async def size(self) -> int:
        return await redis.zcount(self.table, "-inf", "+inf")

    @classmethod
    async def get_repo(cls) -> RedisScheduleRepository:
        return cls()


class RedisJobRepository(JobRepository):
    def __init__(self):
        self.namespace = "jobs"

    def namespaced_key(self, key: str) -> str:
        if key.startswith(f"{self.namespace}:"):
            return key
        return f"{self.namespace}:{key}"

    async def add(self, *items: JobRepoItem):
        keys_and_vals = {self.namespaced_key(i.id): i.job for i in items}
        await redis.mset(keys_and_vals)

        for i in items:
            await redis.sadd(self.namespaced_key(i.schedule_id), i.id)

    async def get(self, *keys: str) -> Sequence[str]:
        if len(keys) == 0:
            return []

        namespaced = [self.namespaced_key(k) for k in keys]
        result = await redis.mget(*namespaced)
        if len(result) == 1 and result[0] == None:
            return []
        return result

    async def get_by_parent(self, *keys: str) -> MutableMapping[str, Sequence[str]]:
        result = {}
        for k in keys:
            namespaced_k = self.namespaced_key(k)
            job_ids = await redis.smembers(namespaced_k)
            jobs = await self.get(*job_ids)
            result[k] = jobs
        return result

    @property
    async def size(self) -> int:
        return 0
        # return await self.redis.dbsize()

    @classmethod
    async def get_repo(cls) -> RedisJobRepository:
        return cls()
