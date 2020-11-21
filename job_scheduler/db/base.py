from abc import ABC, abstractclassmethod, abstractmethod
from typing import Sequence

from job_scheduler.db.types import RepoItem


class ScheduleRepository(ABC):
    @abstractmethod
    async def add(self, items: Sequence[RepoItem]) -> None:
        pass

    @abstractmethod
    async def get(self, keys: Sequence[str]) -> Sequence[str]:
        pass

    @abstractmethod
    async def update(self, items: Sequence[RepoItem]) -> Sequence[str]:
        pass

    @abstractmethod
    async def delete(self, keys: Sequence[str]) -> None:
        pass

    @abstractmethod
    async def get_range(self, min: float, max: float) -> Sequence[str]:
        pass

    @abstractclassmethod
    def get_repo(cls):
        pass

    @abstractclassmethod
    def shutdown(cls):
        pass

    @abstractmethod
    def __contains__(self, s: str) -> bool:
        ...

    @property
    @abstractmethod
    async def size(self) -> int:
        ...
