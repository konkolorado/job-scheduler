from queue import Empty, LifoQueue
from typing import MutableSet, Sequence

from job_scheduler.broker.base import ScheduleBroker


class FakeBroker(ScheduleBroker):
    job_queue: LifoQueue = LifoQueue()
    jobs_in_broker: MutableSet[str] = set()
    running_jobs: MutableSet[str] = set()

    def __init__(self, *messages: str):
        for m in messages:
            self.job_queue.put(m)
            self.jobs_in_broker.add(m)

    def publish(self, *messages: str) -> Sequence[str]:
        deduplicated = []
        for m in messages:
            if m not in self.jobs_in_broker:
                self.job_queue.put(m)
                self.jobs_in_broker.add(m)
                deduplicated.append(m)
        return m

    def get(self, block=True) -> str:
        m = self.job_queue.get(block)
        self.running_jobs.add(m)
        return m

    def drain(self, limit=100) -> Sequence[str]:
        messages = [self.get()]
        while True:
            try:
                m = self.get(block=False)
                messages.append(m)
            except Empty:
                return messages

    def ack(self, *messages: str):
        for m in messages:
            self.running_jobs.remove(m)
            self.jobs_in_broker.remove(m)
            self.job_queue.task_done()

    @classmethod
    def requeue_unacked(cls):
        for m in cls.running_jobs:
            cls.job_queue.put(m)
        cls.running_jobs = set()

    @classmethod
    def get_broker(cls):
        return cls()

    @classmethod
    def shutdown(cls):
        cls.requeue_unacked()
