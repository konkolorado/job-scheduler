import json
from uuid import UUID

from job_scheduler.api.models import Schedule, ScheduleRequest
from job_scheduler.db import ScheduleRepository


async def store_schedule(repo: ScheduleRepository, schedule: Schedule):
    await repo.add(str(schedule.id), schedule.priority, schedule.json())
    return schedule


async def get_schedule(repo: ScheduleRepository, schedule_id: UUID):
    data = await repo.get(str(schedule_id))
    if data is None:
        return None
    data = json.loads(data)
    return Schedule(**data)


async def update_schedule(
    repo: ScheduleRepository,
    schedule_id: UUID,
    req: ScheduleRequest,
):
    data = await repo.get(str(schedule_id))
    if data is None:
        return None
    data = json.loads(data)
    s = Schedule(**data)
    update_data = req.dict(exclude_unset=True)
    updated_schedule = s.copy(update=update_data)
    await repo.update(
        str(schedule_id), updated_schedule.priority, updated_schedule.json()
    )
    return updated_schedule


async def delete_schedule(repo: ScheduleRepository, schedule_id: UUID):
    data = await repo.get(str(schedule_id))
    if data is None:
        return None
    await repo.delete(str(schedule_id))
    return Schedule(**json.loads(data))
