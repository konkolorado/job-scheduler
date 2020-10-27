import asyncio
import json
from datetime import datetime

import pytest

from job_scheduler.api.models import Schedule
from job_scheduler.db import RedisRepository

# TODO Determine what behavior we need and fix tests


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def repo():
    return await RedisRepository.get_repo()


@pytest.mark.asyncio
async def test_add(repo: RedisRepository, schedule: Schedule):
    size_before = await repo.size
    await repo.add(str(schedule.id), schedule.priority, schedule.json())
    size_after = await repo.size
    assert size_after == size_before + 1

    data = await RedisRepository.redis.get(str(schedule.id))
    assert data

    data = json.loads(data)
    assert schedule == Schedule(**data)


@pytest.mark.asyncio
async def test_get(repo: RedisRepository, schedule: Schedule):
    await RedisRepository.redis.set(str(schedule.id), schedule.json())
    data = await repo.get(str(schedule.id))
    assert data

    data = json.loads(data)
    assert schedule == Schedule(**data)


@pytest.mark.asyncio
async def test_get_nonexistant(repo: RedisRepository, schedule: Schedule):
    data = await repo.get(str(schedule.id))
    assert data is None


@pytest.mark.asyncio
async def test_update(repo: RedisRepository, schedule: Schedule):
    await repo.add(str(schedule.id), schedule.priority, schedule.json())

    schedule.schedule = "5 5 5 5 5"
    schedule.description = f"Updated in test at {datetime.now()}"
    schedule.active = False

    size_before = await repo.size
    await repo.update(str(schedule.id), schedule.priority, schedule.json())
    assert await repo.size == size_before

    data = await repo.get(str(schedule.id))
    assert data
    data = json.loads(data)
    updated_schedule = Schedule(**data)
    assert schedule != updated_schedule
    assert schedule.schedule == updated_schedule.schedule
    assert schedule.description == updated_schedule.description
    assert schedule.active == updated_schedule.active


@pytest.mark.asyncio
async def test_update_nonexistant(repo: RedisRepository, schedule: Schedule):
    size_before = await repo.size
    s = await repo.update(str(schedule.id), schedule.priority, schedule.json())
    assert s is None
    assert await repo.size == size_before + 1


@pytest.mark.asyncio
async def test_delete(repo: RedisRepository, schedule: Schedule):
    await repo.add(str(schedule.id), schedule.priority, schedule.json())
    size_before = await repo.size
    await repo.delete(str(schedule.id))
    assert await repo.size == size_before - 1

    data = await RedisRepository.redis.get(str(schedule.id))
    assert data is None


@pytest.mark.asyncio
async def test_delete_nonexistant(repo: RedisRepository, schedule: Schedule):
    size_before = await repo.size
    s = await repo.delete(str(schedule.id))

    assert s is None
    assert await repo.size == size_before
