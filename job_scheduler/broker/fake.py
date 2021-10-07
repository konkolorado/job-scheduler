from __future__ import annotations

import typing as t
from queue import Empty, LifoQueue

from job_scheduler.broker.base import ScheduleBroker

from .messages import DequeuedMessage, EnqueuedMessage


class FakeBroker(ScheduleBroker):
    def __init__(self):
        self.job_queue = LifoQueue()

    async def publish(self, *messages: str) -> t.Sequence[EnqueuedMessage]:
        published: t.List[EnqueuedMessage] = []
        for m in messages:
            em = EnqueuedMessage.from_string(m)
            self.job_queue.put(em)
            published.append(em)
        return published

    async def get(self) -> DequeuedMessage:
        return self.job_queue.get(block=True)

    async def drain(self, limit=100) -> t.Sequence[DequeuedMessage]:
        messages = [await self.get()]
        while True:
            try:
                m = self.job_queue.get(block=False)
                messages.append(m)
            except Empty:
                return messages

    async def ack(self, *messages: DequeuedMessage):
        for m in messages:
            self.job_queue.task_done()

    @classmethod
    async def get_broker(cls) -> FakeBroker:
        return cls()

    @classmethod
    def shutdown(cls):
        return
