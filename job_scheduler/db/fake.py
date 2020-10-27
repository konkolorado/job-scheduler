import json
from uuid import UUID

from job_scheduler.api.models import Schedule
from job_scheduler.db.base import ScheduleRepository
from job_scheduler.db.helpers import JsonMap


class FakeRepository(ScheduleRepository):
    scored_data: JsonMap = {}
    data: JsonMap = {}

    async def add(self, key: str, score: float, value: str):
        self.data[key] = value
        self.scored_data[key] = score

    async def get(self, key: str):
        return self.data.get(key, None)

    async def update(self, key: str, score: float, value: str):
        self.data[key] = value
        self.scored_data[key] = score

    async def delete(self, key: str):
        self.data.pop(key)

    def __contains__(self, item: Schedule):
        return str(item.id) in self.data

    @property
    async def size(self):
        return len(self.data)

    @classmethod
    def get_repo(cls):
        return cls()

    @classmethod
    def shutdown(cls):
        pass
