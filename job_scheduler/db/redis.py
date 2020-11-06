import itertools
import logging
from typing import Sequence

import aioredis
from aioredis import Redis

from job_scheduler.db.base import ScheduleRepository
from job_scheduler.db.types import RepoItem


class RedisRepository(ScheduleRepository):
    redis: Redis

    def __init__(self):
        self.table = "schedules"

    async def add(self, items: Sequence[RepoItem]) -> None:
        keys_and_vals = {i[0]: i[1] for i in items}
        scores_and_keys = [(i[2], i[0]) for i in items]

        await self.redis.mset(keys_and_vals)
        await self.redis.zadd(
            self.table,
            *itertools.chain.from_iterable(scores_and_keys),
        )

    async def get(self, keys: Sequence[str]) -> Sequence[str]:
        if len(keys) == 0:
            return []

        result = await self.redis.mget(*keys)
        if len(result) == 1 and result[0] == None:
            return []
        return result

    async def update(self, items: Sequence[RepoItem]):
        keys_and_vals = ((i[0], i[1]) for i in items)
        scores_and_keys = ((i[2], i[0]) for i in items)

        await self.redis.mset(*itertools.chain.from_iterable(keys_and_vals))
        await self.redis.zadd(
            self.table,
            *itertools.chain.from_iterable(scores_and_keys),
            exist=self.redis.ZSET_IF_EXIST,
        )

    async def delete(self, keys: Sequence[str]) -> None:
        delete = await self.redis.delete(*keys)
        zrem = await self.redis.zrem(self.table, *keys)

    async def get_range(self, min_value: float, max_value: float) -> Sequence[str]:
        return await self.redis.zrangebyscore(self.table, min=min_value, max=max_value)

    def __contains__(self, item) -> bool:
        # Test this
        return False

    @property
    async def size(self) -> int:
        return await self.redis.zcount(self.table)

    @classmethod
    async def get_repo(cls, address: str = "redis://localhost"):
        if not hasattr(cls, "redis"):
            logging.info(f"Instantiating repository using redis client at {address}.")
            rp = await aioredis.create_redis_pool(address, encoding="utf-8")
            cls.redis = rp
        return cls()

    @classmethod
    async def shutdown(cls):
        cls.redis.close()
        await cls.redis.wait_closed()
        logging.info(f"Closed redis client.")
