from abc import ABC, abstractclassmethod, abstractmethod


class ScheduleRepository(ABC):
    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractclassmethod
    def get_repo(cls):
        pass
