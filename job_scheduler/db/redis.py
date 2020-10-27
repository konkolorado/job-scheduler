from uuid import UUID

import aioredis
from aioredis import Redis

from job_scheduler.api.models import Schedule
from job_scheduler.db.base import ScheduleRepository
from job_scheduler.db.helpers import JsonMap


class RedisRepository(ScheduleRepository):
    redis: Redis

    def __init__(self):
        self.table = "schedules"

    async def add(self, key: str, score: float, value: str) -> None:
        await self.redis.set(key, value)
        await self.redis.zadd(self.table, score, key)

    async def get(self, key: str) -> str:
        return await self.redis.get(key)

    async def update(self, key: str, score: float, value: str) -> None:
        await self.redis.set(key, value)
        await self.redis.zadd(self.table, score, key)

    async def delete(self, key: str) -> None:
        delete = await self.redis.delete(key)
        zrem = await self.redis.zrem(self.table, key)

    async def get_range(self, min_value: float, max_value: float):
        return await self.redis.zrangebyscore(self.table, min=min_value)

    def __contains__(self, item) -> bool:
        return False

    @property
    async def size(self) -> int:
        return await self.redis.dbsize()

    @classmethod
    async def get_repo(cls, address: str = "redis://localhost"):
        if not hasattr(cls, "redis"):
            rp = await aioredis.create_redis_pool(address, encoding="utf-8")
            cls.redis = rp
        return cls()

    @classmethod
    async def shutdown(cls):
        cls.redis.close()
        await cls.redis.wait_closed()
