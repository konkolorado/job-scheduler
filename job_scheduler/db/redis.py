from uuid import UUID

import aioredis
from rejson import Client, Path

from job_scheduler.db.base import ScheduleRepository
from job_scheduler.db.helpers import CustomEncoder, JsonMap

r = Client(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
    encoder=CustomEncoder(),
)


class RedisRepository(ScheduleRepository):
    def __init__(self, redis: Client):
        self.redis = redis

    def add(self, key: UUID, value: JsonMap) -> None:
        self.redis.jsonset(str(key), Path.rootPath(), value)

    def get(self, key: UUID) -> JsonMap:
        return self.redis.jsonget(str(key), no_escape=True)

    def update(self, key: UUID, value: JsonMap):
        self.redis.jsonset(str(key), Path.rootPath(), value)

    def delete(self, key: UUID):
        self.redis.jsondel(str(key))

    def list(self):
        pass

    @classmethod
    def get_repo(cls):
        return cls(redis=r)
