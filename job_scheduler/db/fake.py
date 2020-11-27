import json
from typing import Sequence, Tuple, Union
from uuid import UUID

from job_scheduler.db.base import ScheduleRepository
from job_scheduler.db.types import JsonMap, ScheduleRepoItem


class FakeRepository(ScheduleRepository):
    scored_data: JsonMap = {}
    data: JsonMap = {}

    async def add(self, *items: ScheduleRepoItem) -> None:
        for i in items:
            self.data[i.id] = i.schedule
            self.scored_data[i.id] = i.priority

    async def get(self, *keys: str) -> Sequence[str]:
        return [self.data.get(k, "") for k in keys if self.data.get(k)]

    async def update(self, *items: ScheduleRepoItem) -> Sequence[str]:
        ret_val = []
        for i in items:
            self.data[i.id] = i.schedule
            self.scored_data[i.id] = i.priority
            ret_val.append(i.schedule)
        return ret_val

    async def delete(self, *keys: str) -> None:
        for k in keys:
            self.data.pop(k, None)

    async def get_range(self, min_val: float, max_val: float) -> Sequence[str]:
        sorted_data = sorted(self.scored_data.items(), key=lambda x: x[1])

        results = []
        for data in sorted_data:
            if min_val <= data[1] <= max_val:
                results.append(data[0])
        return results

    def __contains__(self, key: str):
        return key in self.data

    @property
    async def size(self):
        return len(self.data)

    @classmethod
    def get_repo(cls):
        return cls()

    @classmethod
    def shutdown(cls):
        pass
