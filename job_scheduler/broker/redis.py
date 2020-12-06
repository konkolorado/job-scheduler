import logging
from typing import Sequence

import aioredis
from aioredis.commands import MultiExec

from job_scheduler.broker.base import ScheduleBroker


class RedisBroker(ScheduleBroker):
    redis: aioredis.Redis
    brokers: int = 0

    job_queue = "job_queue"
    jobs_in_broker = "enqueued"
    running_jobs = "running_jobs"

    def __init__(self):
        RedisBroker.brokers += 1

    async def publish(self, *messages: str) -> Sequence[str]:
        """
        Publishes a list of messages to a broker. Returns a list containing the
        deduplicated messages that were successfully added onto the queue for
        execution.
        """
        deduplicated = [
            m
            for m in messages
            if not await self.redis.sismember(self.jobs_in_broker, m)
        ]

        if len(deduplicated) > 0:
            await self.redis.rpush(self.job_queue, *deduplicated)
            await self.redis.sadd(self.jobs_in_broker, *deduplicated)

        logging.debug(f"Published {len(deduplicated)} schedules for execution.")
        return deduplicated

    async def get(self) -> str:
        _, message = await self.redis.blpop(self.job_queue)
        await self.redis.sadd(self.running_jobs, message)
        logging.debug(f"Got {message}")
        return message

    async def drain(self, limit=100) -> Sequence[str]:
        messages = [await self.get()]
        while await self.redis.llen(self.job_queue) > 0 and len(messages) < limit:
            m = await self.get()
            messages.append(m)
        return messages

    async def ack(self, *messages: str):
        tr: MultiExec = self.redis.multi_exec()
        tr.srem(self.jobs_in_broker, *messages)
        tr.srem(self.running_jobs, *messages)
        await tr.execute()

    @property
    async def size(self):
        return await self.redis.scard(self.jobs_in_broker)

    @classmethod
    async def requeue_unacked(cls):
        messages = await cls.redis.smembers(cls.running_jobs)
        if len(messages) > 0:
            await cls.redis.rpush(cls.job_queue, *messages)
        await cls.redis.delete(cls.running_jobs)
        logging.info(f"Moved {len(messages)} items from processing into job queue")

    @classmethod
    async def get_broker(cls, *, address: str = "redis://localhost"):
        if not hasattr(cls, "redis"):
            logging.info(f"Instantiating broker using redis at {address}.")
            rp = await aioredis.create_redis_pool(address, encoding="utf-8")
            cls.redis = rp

        return cls()

    @classmethod
    async def shutdown(cls):
        if cls.brokers == 1:
            await cls.requeue_unacked()

        cls.redis.close()
        await cls.redis.wait_closed()
        cls.brokers -= 1
        logging.info(f"Closed redis broker connection to {cls.redis.address}")
