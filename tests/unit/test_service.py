import uuid
from datetime import datetime

import pytest

from job_scheduler.api.models import Schedule, ScheduleRequest
from job_scheduler.api.service import (
    delete_schedule,
    get_schedule,
    store_schedule,
    update_schedule,
)
from job_scheduler.db import ScheduleRepository


@pytest.mark.asyncio
async def test_store_schedule(repo: ScheduleRepository, schedule: Schedule):
    s = await store_schedule(repo, schedule)

    assert s
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
    await delete_schedule(repo, schedule.id)

    assert schedule not in repo


@pytest.mark.asyncio
async def test_delete_nonexistant_schedule(
    repo: ScheduleRepository, schedule: Schedule
):
    s = await delete_schedule(repo, schedule.id)

    assert s is None
    assert schedule not in repo


@pytest.mark.asyncio
async def test_update_schedule(
    repo: ScheduleRepository, schedule: Schedule, schedule_request: ScheduleRequest
):
    await store_schedule(repo, schedule)

    schedule_request.name = f"Updated in test at {datetime.now()}"
    await update_schedule(repo, schedule.id, schedule_request)

    updated_schedule = await get_schedule(repo, schedule.id)
    assert updated_schedule.name == schedule_request.name


@pytest.mark.asyncio
async def test_update_nonexistant_schedule(
    repo: ScheduleRepository, schedule_request: ScheduleRequest
):
    size_before = len(repo)
    s = await update_schedule(repo, uuid.uuid4(), schedule_request)

    assert s is None
    assert len(repo) == size_before
