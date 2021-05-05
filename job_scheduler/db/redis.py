import itertools
import logging
from typing import MutableMapping, Sequence

import aioredis

from job_scheduler.db.base import JobRepository, ScheduleRepository
from job_scheduler.db.types import JobRepoItem, ScheduleRepoItem


class RedisScheduleRepository(ScheduleRepository):
    redis: aioredis.Redis

    def __init__(self):
        self.table = "schedules"
        self.namespace = "schedules"

    def namespaced_key(self, key) -> str:
        if key.startswith(f"{self.namespace}:"):
            return key
        return f"{self.namespace}:{key}"

    async def add(self, *items: ScheduleRepoItem) -> None:
        keys_and_vals = {self.namespaced_key(i.id): i.schedule for i in items}
        scores_and_keys = [(i.priority, i.id) for i in items]

        await self.redis.mset(keys_and_vals)
        await self.redis.zadd(
            self.table,
            *itertools.chain.from_iterable(scores_and_keys),
        )

    async def get(self, *keys: str) -> Sequence[str]:
        if len(keys) == 0:
            return []

        namespaced = [self.namespaced_key(k) for k in keys]
        result = await self.redis.mget(*namespaced)
        if len(result) == 1 and result[0] == None:
            return []
        return result

    async def update(self, *items: ScheduleRepoItem) -> None:
        keys_and_vals = {self.namespaced_key(i.id): i.schedule for i in items}
        scores_and_keys = [(i.priority, i.id) for i in items]

        await self.redis.mset(keys_and_vals)
        await self.redis.zadd(
            self.table,
            *itertools.chain.from_iterable(scores_and_keys),
            exist=self.redis.ZSET_IF_EXIST,
        )

    async def delete(self, *keys: str) -> None:
        namespaced = [self.namespaced_key(k) for k in keys]
        delete = await self.redis.delete(*namespaced)
        zrem = await self.redis.zrem(self.table, *keys)

    async def get_range(self, min_value: float, max_value: float) -> Sequence[str]:
        return await self.redis.zrangebyscore(self.table, min=min_value, max=max_value)

    @property
    async def size(self) -> int:
        return await self.redis.zcount(self.table)

    @classmethod
    async def get_repo(
        cls, address: str = "redis://localhost"
    ) -> "RedisScheduleRepository":
        if not hasattr(cls, "redis"):
            logging.info(f"Instantiating schedule repository using redis at {address}.")
            rp = await aioredis.create_redis_pool(address, encoding="utf-8")
            logging.info("Schedule repository successfully instantiated.")
            cls.redis = rp
        return cls()

    @classmethod
    async def shutdown(cls) -> None:
        cls.redis.close()
        await cls.redis.wait_closed()
        logging.info(
            f"Schedule repository closed redis connection to {cls.redis.address}"
        )


class RedisJobRepository(JobRepository):
    redis: aioredis.Redis

    def __init__(self):
        self.namespace = "jobs"

    def namespaced_key(self, key: str) -> str:
        if key.startswith(f"{self.namespace}:"):
            return key
        return f"{self.namespace}:{key}"

    async def add(self, *items: JobRepoItem):
        keys_and_vals = {self.namespaced_key(i.id): i.job for i in items}
        await self.redis.mset(keys_and_vals)

        for i in items:
            await self.redis.sadd(self.namespaced_key(i.schedule_id), i.id)

    async def get(self, *keys: str) -> Sequence[str]:
        if len(keys) == 0:
            return []

        namespaced = [self.namespaced_key(k) for k in keys]
        result = await self.redis.mget(*namespaced)
        if len(result) == 1 and result[0] == None:
            return []
        return result

    async def get_by_parent(self, *keys: str) -> MutableMapping[str, Sequence[str]]:
        result = {}
        for k in keys:
            namespaced_k = self.namespaced_key(k)
            job_ids = await self.redis.smembers(namespaced_k)
            jobs = await self.get(*job_ids)
            result[k] = jobs
        return result

    @property
    async def size(self) -> int:
        return 0
        # return await self.redis.dbsize()

    @classmethod
    async def get_repo(cls, address: str = "redis://localhost") -> "RedisJobRepository":
        if not hasattr(cls, "redis"):
            logging.info(f"Instantiating job repository using redis at {address}.")
            rp = await aioredis.create_redis_pool(address, encoding="utf-8")
            logging.info(f"Job repository sucessfully instantiated.")
            cls.redis = rp
        return cls()

    @classmethod
    async def shutdown(cls) -> None:
        cls.redis.close()
        await cls.redis.wait_closed()
        logging.info(f"Job repository closed redis connection to {cls.redis.address}")
