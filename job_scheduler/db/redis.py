from uuid import UUID

import aioredis
from aioredis import Redis

from job_scheduler.api.models import Schedule
from job_scheduler.db.base import ScheduleRepository
from job_scheduler.db.helpers import JsonMap


class RedisRepository(ScheduleRepository):
    redis: Redis
    size: int = 0

    def __init__(self):
        self.table = "schedules"

    async def add(self, key: str, score: float, value: str) -> None:
        await self.redis.set(key, value)
        await self.redis.zadd(self.table, score, key)
        self.size += 1

    async def get(self, key: str) -> str:
        return await self.redis.get(key)

    async def update(self, key: str, score: float, value: str) -> None:
        await self.redis.set(key, value)
        await self.redis.zadd(self.table, score, key)

    async def delete(self, key: str) -> None:
        delete = await self.redis.delete(key)
        zrem = await self.redis.zrem(self.table, key)
        if delete != 0 and zrem != 0:
            self.size -= 1

    def __contains__(self, item) -> bool:
        return False

    def __len__(self) -> int:
        return self.size

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
