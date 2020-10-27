import json
from typing import Optional
from uuid import UUID

from job_scheduler.api.models import Schedule, ScheduleRequest
from job_scheduler.db import ScheduleRepository


async def store_schedule(repo: ScheduleRepository, schedule: Schedule) -> Schedule:
    await repo.add(str(schedule.id), schedule.priority, schedule.json())
    return schedule


async def get_schedule(
    repo: ScheduleRepository, schedule_id: UUID
) -> Optional[Schedule]:
    data = await repo.get(str(schedule_id))
    if data is None:
        return None

    return Schedule.parse_raw(data)


async def update_schedule(
    repo: ScheduleRepository,
    schedule_id: UUID,
    req: ScheduleRequest,
) -> Optional[Schedule]:
    data = await repo.get(str(schedule_id))
    if data is None:
        return None

    s = Schedule.parse_raw(data)
    update_data = req.dict(exclude_unset=True)
    updated_schedule = s.copy(update=update_data)
    await repo.update(
        str(schedule_id), updated_schedule.priority, updated_schedule.json()
    )
    return updated_schedule


async def delete_schedule(
    repo: ScheduleRepository, schedule_id: UUID
) -> Optional[Schedule]:
    data = await repo.get(str(schedule_id))
    if data is None:
        return None

    await repo.delete(str(schedule_id))
    return Schedule.parse_raw(data)
