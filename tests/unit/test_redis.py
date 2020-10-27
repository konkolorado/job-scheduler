import asyncio
import json
from datetime import datetime

import pytest

from job_scheduler.api.models import Schedule
from job_scheduler.db import RedisRepository


@pytest.yield_fixture(scope="session")
def event_loop(request):
    """
    We need to override the event_loop fixture such that it is of the
    correct scope.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def repo():
    return await RedisRepository.get_repo()


@pytest.mark.asyncio
async def test_add(repo: RedisRepository, schedule: Schedule):
    size_before = len(repo)
    await repo.add(str(schedule.id), schedule.priority, schedule.json())

    assert len(repo) == size_before + 1
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

    size_before = len(repo)
    await repo.update(str(schedule.id), schedule.priority, schedule.json())
    assert len(repo) == size_before

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
    size_before = len(repo)
    s = await repo.update(str(schedule.id), schedule.priority, schedule.json())
    assert s is None
    assert len(repo) == size_before


@pytest.mark.asyncio
async def test_delete(repo: RedisRepository, schedule: Schedule):
    await repo.add(str(schedule.id), schedule.priority, schedule.json())
    size_before = len(repo)
    await repo.delete(str(schedule.id))
    assert len(repo) == size_before - 1

    data = await RedisRepository.redis.get(str(schedule.id))
    assert data is None


@pytest.mark.asyncio
async def test_delete_nonexistant(repo: RedisRepository, schedule: Schedule):
    size_before = len(repo)
    s = await repo.delete(str(schedule.id))

    assert s is None
    assert len(repo) == size_before
