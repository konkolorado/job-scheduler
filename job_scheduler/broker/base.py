from abc import ABC, abstractclassmethod, abstractmethod


class ScheduleBroker(ABC):
    @abstractmethod
    def publish(self, *messages: str):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def drain(self, limit: int = 100):
        pass

    @abstractmethod
    def ack(self, *messages: str):
        pass

    @property
    @abstractmethod
    def size(self):
        pass

    @abstractclassmethod
    def get_broker(cls):
        pass

    @abstractclassmethod
    def shutdown(cls):
        pass

    @abstractclassmethod
    def requeue_unacked(cls):
        pass
