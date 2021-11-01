from __future__ import annotations

import typing as t
from abc import ABC, abstractclassmethod, abstractmethod


class ScheduleCache(ABC):
    @abstractmethod
    async def add(self, *items: str) -> None:
        ...

    @abstractmethod
    async def get(self, *items: str) -> t.List[t.Union[str, None]]:
        ...

    @abstractclassmethod
    async def get_cache(cls) -> ScheduleCache:
        ...
