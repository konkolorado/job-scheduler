from typing import List, Mapping, Union
from uuid import UUID

from job_scheduler.api.models import Schedule
from job_scheduler.db import ScheduleRepository
from job_scheduler.db.types import JsonMap


async def store_schedule(
    repo: ScheduleRepository, schedule: Union[List[Schedule], Schedule]
) -> List[Schedule]:
    if isinstance(schedule, Schedule):
        data = [(str(schedule.id), schedule.json(), schedule.priority)]
        ret_val = [schedule]
    else:
        data = [(str(s.id), s.json(), s.priority) for s in schedule]
        ret_val = schedule

    await repo.add(data)
    return ret_val


async def get_schedule(
    repo: ScheduleRepository, schedule_id: Union[UUID, List[UUID]]
) -> List[Schedule]:
    if isinstance(schedule_id, UUID):
        schedule_id = [schedule_id]

    schedule_ids = [str(s) for s in schedule_id]
    data = await repo.get(schedule_ids)
    return [Schedule.parse_raw(d) for d in data]


async def update_schedule(
    repo: ScheduleRepository,
    schedule_updates: Mapping[UUID, JsonMap],
) -> List[Schedule]:
    update_ids = [str(k) for k in schedule_updates.keys()]
    data = await repo.get(update_ids)
    schedules = [Schedule.parse_raw(d) for d in data]

    new_schedules = []
    for s in schedules:
        s_updates = schedule_updates[s.id]
        updated_schedule = s.copy(update=s_updates)
        new_schedules.append(updated_schedule)

    updates = [(str(ns.id), ns.json(), ns.priority) for ns in new_schedules]
    await repo.update(updates)
    return new_schedules


async def delete_schedule(
    repo: ScheduleRepository, schedule_id: Union[UUID, List[UUID]]
) -> List[Schedule]:
    if isinstance(schedule_id, UUID):
        schedule_id = [schedule_id]

    schedule_ids = [str(s) for s in schedule_id]
    data = await repo.get(schedule_ids)

    await repo.delete(schedule_ids)
    return [Schedule.parse_raw(d) for d in data]


async def get_range(
    repo: ScheduleRepository, min_value: float, max_value: float
) -> List[Schedule]:
    schedule_ids = await repo.get_range(min_value, max_value)
    data = await repo.get(schedule_ids)

    return [Schedule.parse_raw(d) for d in data]
