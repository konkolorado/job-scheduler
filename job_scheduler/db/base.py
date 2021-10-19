from abc import ABC, abstractclassmethod, abstractmethod

from job_scheduler.db.types import JobRepoItem, ScheduleRepoItem


class ScheduleRepository(ABC):
    @abstractmethod
    def add(self, *items: ScheduleRepoItem):
        pass

    @abstractmethod
    def get(self, *keys: str):
        pass

    @abstractmethod
    def update(self, *items: ScheduleRepoItem):
        pass

    @abstractmethod
    def delete(self, *keys: str):
        pass

    @abstractmethod
    def get_range(self, min: float, max: float):
        pass

    @property
    @abstractmethod
    async def size(self):
        pass

    @abstractclassmethod
    def get_repo(cls):
        pass


class JobRepository(ABC):
    @abstractmethod
    def add(self, *items: JobRepoItem):
        pass

    @abstractmethod
    def get(self, *keys: str):
        pass

    @abstractmethod
    def get_by_parent(self, *keys: str):
        pass

    @property
    @abstractmethod
    async def size(self) -> int:
        pass

    @abstractclassmethod
    def get_repo(cls):
        pass
