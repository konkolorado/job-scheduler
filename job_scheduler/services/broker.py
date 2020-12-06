from typing import Sequence
from uuid import UUID

from job_scheduler.api.models import Schedule
from job_scheduler.broker import ScheduleBroker


async def enqueue_jobs(
    broker: ScheduleBroker, *schedules: Schedule
) -> Sequence[Schedule]:
    enqueued = await broker.publish(*[str(s.id) for s in schedules])
    return [s for s in schedules if str(s.id) in enqueued]


async def dequeue_jobs(broker: ScheduleBroker) -> Sequence[UUID]:
    schedule_ids = await broker.drain(limit=100)
    return [UUID(s_id) for s_id in schedule_ids]


async def ack_jobs(broker: ScheduleBroker, *schedules: Schedule):
    await broker.ack(*[str(s.id) for s in schedules])
