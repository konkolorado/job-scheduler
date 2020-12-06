import uuid
from datetime import datetime, timedelta, timezone

import pytest

from job_scheduler.api.models import Schedule, ScheduleRequest
from job_scheduler.db import ScheduleRepository
from job_scheduler.services import (
    delete_schedule,
    get_range,
    get_schedule,
    store_schedule,
    update_schedule,
)


@pytest.mark.asyncio
async def test_storing_schedules(repo: ScheduleRepository, n_schedules):
    schedules = n_schedules(3)
    stored = await store_schedule(repo, *schedules)

    assert len(stored) == len(schedules)
    for s in schedules:
        retrieved, *_ = await get_schedule(repo, s.id)
        assert s == retrieved


@pytest.mark.asyncio
async def test_get_schedule(repo: ScheduleRepository, schedule: Schedule):
    await store_schedule(repo, schedule)
    retrieved = await get_schedule(repo, schedule.id)
    assert retrieved[0] == schedule


@pytest.mark.asyncio
async def test_get_nonexistant_schedule(repo: ScheduleRepository, schedule: Schedule):
    retrieved = await get_schedule(repo, schedule.id)
    assert len(retrieved) == 0


@pytest.mark.asyncio
async def test_delete_schedule(repo: ScheduleRepository, schedule: Schedule):
    await store_schedule(repo, schedule)

    size_before = await repo.size
    s = await delete_schedule(repo, schedule.id)

    assert s is not None
    assert await get_schedule(repo, schedule.id) == []
    assert await repo.size == size_before - 1


@pytest.mark.asyncio
async def test_delete_nonexistant_schedule(
    repo: ScheduleRepository, schedule: Schedule
):
    size_before = await repo.size
    s = await delete_schedule(repo, schedule.id)

    assert len(s) == 0
    assert await get_schedule(repo, schedule.id) == []
    assert await repo.size == size_before


@pytest.mark.asyncio
async def test_update_schedule(
    repo: ScheduleRepository, schedule: Schedule, schedule_request: ScheduleRequest
):
    await store_schedule(repo, schedule)

    size_before = await repo.size
    schedule_request.name = f"Updated in test at {datetime.now()}"
    updated_schedules = await update_schedule(
        repo, {schedule.id: schedule_request.dict(exclude_unset=True)}
    )

    assert len(updated_schedules) == 1
    retrieved, *_ = await get_schedule(repo, schedule.id)
    assert updated_schedules[0] == retrieved
    assert await repo.size == size_before


@pytest.mark.asyncio
async def test_update_nonexistant_schedule(
    repo: ScheduleRepository, schedule_request: ScheduleRequest
):
    size_before = await repo.size
    update_schedules = await update_schedule(repo, {uuid.uuid4(): schedule_request})

    assert len(update_schedules) == 0
    assert await repo.size == size_before


@pytest.mark.asyncio
async def test_get_range(repo: ScheduleRepository, n_schedules):
    schedules = n_schedules(3)
    for i, s in enumerate(schedules):
        s.schedule = f"*/{i+1} * * * *"
        s.description = f"Every {i} mins"
        s.next_run = s.calc_next_run()

    await store_schedule(repo, *schedules)

    now = datetime.now(timezone.utc)
    future = now + timedelta(minutes=1)
    results = await get_range(repo, now.timestamp(), future.timestamp())

    for s in schedules:
        if now.timestamp() <= s.priority <= future.timestamp():
            assert s in results
        else:
            assert s not in results


@pytest.mark.asyncio
async def test_get_range_no_min(repo: ScheduleRepository, n_schedules):
    schedules = n_schedules(3)
    for i, s in enumerate(schedules):
        s.schedule = f"*/{i+1} * * * *"
        s.description = f"Every {i} mins"
        s.next_run = s.calc_next_run()

    await store_schedule(repo, *schedules)

    future = datetime.now(timezone.utc) + timedelta(minutes=1)
    results = await get_range(repo, None, future.timestamp())

    for s in schedules:
        if s.priority <= future.timestamp():
            assert s in results
        else:
            assert s not in results


@pytest.mark.asyncio
async def test_get_range_no_max(repo: ScheduleRepository, n_schedules):
    schedules = n_schedules(3)
    for i, s in enumerate(schedules):
        s.schedule = f"*/{i+1} * * * *"
        s.description = f"Every {i} mins"
        s.next_run = s.calc_next_run()

    await store_schedule(repo, *schedules)

    now = datetime.now(timezone.utc)
    results = await get_range(repo, now.timestamp(), None)

    for s in schedules:
        if s.priority >= now.timestamp():
            assert s in results
        else:
            assert s not in results
