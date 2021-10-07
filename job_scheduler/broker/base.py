from __future__ import annotations

import typing as t
from abc import ABC, abstractclassmethod, abstractmethod

from .messages import DequeuedMessage, EnqueuedMessage


class ScheduleBroker(ABC):
    @abstractmethod
    async def publish(self, *messages: str) -> t.Sequence[EnqueuedMessage]:
        pass

    @abstractmethod
    async def get(self) -> DequeuedMessage:
        """
        This implementation should block until a message is ready for processing
        """
        pass

    @abstractmethod
    async def drain(self, limit: int = 100) -> t.Sequence[DequeuedMessage]:
        """
        This implementation should block until at least one message is ready for
        processing
        """
        pass

    @abstractmethod
    def ack(self, *messages: DequeuedMessage):
        pass

    @abstractclassmethod
    async def get_broker(cls) -> ScheduleBroker:
        pass

    @abstractmethod
    def shutdown(self):
        pass
