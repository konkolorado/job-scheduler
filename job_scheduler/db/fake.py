from __future__ import annotations

from collections import defaultdict
from typing import MutableMapping, Sequence

from job_scheduler.db.base import JobRepository, ScheduleRepository
from job_scheduler.db.types import JobRepoItem, JsonMap, ScheduleRepoItem


class FakeScheduleRepository(ScheduleRepository):
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
    def get_repo(cls) -> FakeScheduleRepository:
        return cls()


class FakeJobRepository(JobRepository):
    def __init__(self):
        self.by_parent: MutableMapping[str, set] = defaultdict(set)
        self.jobs: MutableMapping[str, str] = dict()

    async def add(self, *items: JobRepoItem):
        for i in items:
            self.by_parent[i.schedule_id].add(i.job)
            self.jobs[i.id] = i.job

    async def get(self, *keys: str):
        results = []
        for k in keys:
            job = self.jobs[k]
            results.append(job)
        return results

    async def get_by_parent(self, *keys: str):
        results = {}
        for k in keys:
            results[k] = list(self.by_parent[k])
        return results

    @property
    def size(self):
        pass

    @classmethod
    def get_repo(cls) -> FakeJobRepository:
        return cls()
