from typing import List, Mapping, Optional, Union
from uuid import UUID

from job_scheduler.api.models import Job, Schedule
from job_scheduler.db import JobRepository, ScheduleRepository
from job_scheduler.db.types import JobRepoItem, JsonMap, ScheduleRepoItem


async def store_schedule(
    repo: ScheduleRepository, schedule: Union[List[Schedule], Schedule]
) -> List[Schedule]:
    if isinstance(schedule, Schedule):
        data = [
            ScheduleRepoItem(
                id=str(schedule.id),
                schedule=schedule.json(),
                priority=schedule.priority,
            )
        ]
        schedule = [schedule]
    else:
        data = [
            ScheduleRepoItem(id=str(s.id), schedule=s.json(), priority=s.priority)
            for s in schedule
        ]
    await repo.add(*data)
    return schedule


async def get_schedule(
    repo: ScheduleRepository, schedule_id: Union[UUID, List[UUID]]
) -> List[Schedule]:
    if isinstance(schedule_id, UUID):
        schedule_id = [schedule_id]

    schedule_ids = [str(s) for s in schedule_id]
    data = await repo.get(*schedule_ids)
    return [Schedule.parse_raw(d) for d in data]


async def update_schedule(
    repo: ScheduleRepository,
    updates: Mapping[UUID, JsonMap],
) -> List[Schedule]:
    update_ids = [k for k in updates.keys()]
    schedules = await get_schedule(repo, update_ids)

    new_schedules = []
    for s in schedules:
        s_update = updates[s.id]
        updated_schedule = s.copy(update=s_update)
        new_schedules.append(updated_schedule)

    all_updates = [
        ScheduleRepoItem(id=str(ns.id), schedule=ns.json(), priority=ns.priority)
        for ns in new_schedules
    ]
    await repo.update(*all_updates)
    return new_schedules


async def delete_schedule(
    repo: ScheduleRepository, schedule_id: Union[UUID, List[UUID]]
) -> List[Schedule]:
    if isinstance(schedule_id, UUID):
        schedule_id = [schedule_id]

    schedule_ids = [str(s) for s in schedule_id]
    data = await repo.get(*schedule_ids)

    await repo.delete(*schedule_ids)
    return [Schedule.parse_raw(d) for d in data]


async def get_range(
    repo: ScheduleRepository,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
) -> List[Schedule]:
    if min_value is None:
        min_value = float("-inf")
    if max_value is None:
        max_value = float("inf")

    schedule_ids = await repo.get_range(min_value, max_value)
    data = await repo.get(*schedule_ids)
    return [Schedule.parse_raw(d) for d in data]


async def add_jobs(repo: JobRepository, jobs: Union[List[Job], Job]):
    if isinstance(jobs, Job):
        jobs = [jobs]

    items = []
    for j in jobs:
        item = JobRepoItem(id=str(j.id), schedule_id=str(j.schedule_id), job=j.json())
        items.append(item)
    await repo.add(*items)


async def get_jobs(repo: JobRepository, *job_ids: UUID):
    ids = [str(j) for j in job_ids]
    jobs = await repo.get(*ids)
    return [Job.parse_raw(j) for j in jobs]


async def get_schedule_jobs(repo: JobRepository, *schedule_ids: UUID):
    ids = [str(s_id) for s_id in schedule_ids]
    schedules_to_jobs = await repo.get_by_parent(*ids)

    result = {}
    for s_id, jobs in schedules_to_jobs.items():
        parsed_jobs = []
        for j in jobs:
            j = Job.parse_raw(j)
            parsed_jobs.append(j)
        result[UUID(s_id)] = parsed_jobs

    return result
