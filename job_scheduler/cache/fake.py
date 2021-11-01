from __future__ import annotations

import typing as t
from datetime import datetime, timedelta, timezone

from job_scheduler.cache.base import ScheduleCache


class FakeScheduleCache(ScheduleCache):
    def __init__(self):
        self.ttl_s = 10
        self.cache: t.Dict[str, datetime] = {}

    @classmethod
    async def get_cache(cls) -> FakeScheduleCache:
        return cls()

    async def get(self, *items: str) -> t.List[t.Union[str, None]]:
        # Filter out expired items
        now = datetime.now(timezone.utc)
        for i, exp_at in self.cache.items():
            if exp_at > now:
                self.cache.pop(i)

        results: t.List[t.Union[str, None]] = []
        for i in items:
            if i in self.cache:
                results.append(i)
            else:
                results.append(None)
        return results

    async def add(self, *items: str) -> None:
        exp_at = datetime.now(timezone.utc) + timedelta(seconds=self.ttl_s)
        for i in items:
            self.cache[i] = exp_at
