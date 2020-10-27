from abc import ABC, abstractclassmethod, abstractmethod

from job_scheduler.api.models import Schedule


class ScheduleRepository(ABC):
    @abstractmethod
    async def add(self, key: str, score: float, value: str) -> None:
        pass

    @abstractmethod
    async def get(self, key: str) -> str:
        pass

    @abstractmethod
    async def update(self, key: str, score: float, value: str) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractclassmethod
    def get_repo(cls):
        pass

    @abstractclassmethod
    def shutdown(cls):
        pass

    @abstractmethod
    def __contains__(self, s: Schedule) -> bool:
        ...

    @property
    @abstractmethod
    async def size(self) -> int:
        ...
