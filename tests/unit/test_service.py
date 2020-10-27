import uuid
from datetime import datetime

import pytest

from job_scheduler.api.models import Schedule, ScheduleRequest
from job_scheduler.db import ScheduleRepository
from job_scheduler.services import (
    delete_schedule,
    get_schedule,
    store_schedule,
    update_schedule,
)


@pytest.mark.asyncio
async def test_store_schedule(repo: ScheduleRepository, schedule: Schedule):
    s = await store_schedule(repo, schedule)

    assert s is not None
    assert s in repo


@pytest.mark.asyncio
async def test_get_schedule(repo: ScheduleRepository, schedule: Schedule):
    await store_schedule(repo, schedule)
    retrieved = await get_schedule(repo, schedule.id)
    assert retrieved == schedule


@pytest.mark.asyncio
async def test_get_nonexistant_schedule(repo: ScheduleRepository, schedule: Schedule):
    retrieved = await get_schedule(repo, schedule.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_delete_schedule(repo: ScheduleRepository, schedule: Schedule):
    await store_schedule(repo, schedule)

    size_before = await repo.size
    s = await delete_schedule(repo, schedule.id)
    size_after = await repo.size

    assert s is not None
    assert schedule not in repo
    assert size_after == size_before - 1


@pytest.mark.asyncio
async def test_delete_nonexistant_schedule(
    repo: ScheduleRepository, schedule: Schedule
):
    size_before = await repo.size
    s = await delete_schedule(repo, schedule.id)
    size_after = await repo.size

    assert s is None
    assert schedule not in repo
    assert size_after == size_before


@pytest.mark.asyncio
async def test_update_schedule(
    repo: ScheduleRepository, schedule: Schedule, schedule_request: ScheduleRequest
):
    await store_schedule(repo, schedule)

    size_before = await repo.size
    schedule_request.name = f"Updated in test at {datetime.now()}"
    updated_schedule = await update_schedule(repo, schedule.id, schedule_request)
    size_after = await repo.size

    assert updated_schedule is not None
    assert updated_schedule.name == schedule_request.name
    assert size_after == size_before


@pytest.mark.asyncio
async def test_update_nonexistant_schedule(
    repo: ScheduleRepository, schedule_request: ScheduleRequest
):
    size_before = await repo.size
    s = await update_schedule(repo, uuid.uuid4(), schedule_request)
    size_after = await repo.size

    assert s is None
    assert size_after == size_before
