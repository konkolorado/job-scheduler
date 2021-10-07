from typing import Sequence
from uuid import UUID

from job_scheduler.api.models import Schedule
from job_scheduler.broker import ScheduleBroker
from job_scheduler.broker.messages import DequeuedMessage, EnqueuedMessage


async def enqueue_jobs(
    broker: ScheduleBroker, *schedules: Schedule
) -> Sequence[EnqueuedMessage]:
    return await broker.publish(*[str(s.id) for s in schedules])


def queue_jobs_to_schedule_ids(*queue_jobs: DequeuedMessage) -> Sequence[UUID]:
    return [UUID(qj.payload) for qj in queue_jobs]


async def dequeue_jobs(broker: ScheduleBroker) -> Sequence[DequeuedMessage]:
    queue_messages = await broker.drain(limit=100)
    return queue_messages


async def ack_jobs(broker: ScheduleBroker, *queue_jobs: DequeuedMessage):
    await broker.ack(*queue_jobs)
