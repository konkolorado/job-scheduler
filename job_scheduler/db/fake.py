import json
from typing import Sequence, Tuple, Union
from uuid import UUID

from job_scheduler.api.models import Schedule
from job_scheduler.db.base import ScheduleRepository
from job_scheduler.db.types import JsonMap, RepoItem


class FakeRepository(ScheduleRepository):
    scored_data: JsonMap = {}
    data: JsonMap = {}

    async def add(self, items: Sequence[RepoItem]) -> None:
        for key, value, score in items:
            self.data[key] = value
            self.scored_data[key] = score

    async def get(self, keys: Sequence[str]) -> Sequence[str]:
        return [self.data.get(k, "") for k in keys if self.data.get(k)]

    async def update(self, items: Sequence[RepoItem]) -> Sequence[str]:
        ret_val = []
        for key, value, score in items:
            self.data[key] = value
            self.scored_data[key] = score
            ret_val.append(value)
        return ret_val

    async def delete(self, keys: Sequence[str]) -> None:
        for k in keys:
            self.data.pop(k, None)

    async def get_range(self, min_val: float, max_val: float) -> Sequence[str]:
        sorted_data = sorted(self.scored_data.items(), key=lambda x: x[1])

        results = []
        for data in sorted_data:
            if min_val <= data[1] <= max_val:
                results.append(data[0])
        return results

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
