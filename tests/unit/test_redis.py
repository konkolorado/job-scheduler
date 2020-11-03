import asyncio
import uuid
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
    await repo.add([(str(schedule.id), schedule.json(), schedule.priority)])
    size_after = await repo.size
    assert size_after == size_before + 1

    data = await RedisRepository.redis.get(str(schedule.id))
    assert schedule == Schedule.parse_raw(data)


@pytest.mark.asyncio
async def test_add_multiple(repo: RedisRepository, schedule: Schedule):
    size_before = await repo.size

    to_add = [
        (str(schedule.id), schedule.json(), schedule.priority),
        (str(uuid.uuid4()), schedule.json(), schedule.priority),
    ]

    await repo.add(to_add)
    size_after = await repo.size

    assert size_after == size_before + len(to_add)

    for added in to_add:
        s, *_ = await repo.get([added[0]])
        assert s == added[1]


@pytest.mark.asyncio
async def test_get(repo: RedisRepository, schedule: Schedule):
    await RedisRepository.redis.set(str(schedule.id), schedule.json())
    data, *_ = await repo.get([str(schedule.id)])
    assert schedule == Schedule.parse_raw(data)


@pytest.mark.asyncio
async def test_get_nonexistant(repo: RedisRepository, schedule: Schedule):
    data = await repo.get([str(schedule.id)])
    assert len(data) == 0


@pytest.mark.asyncio
async def test_update(repo: RedisRepository, schedule: Schedule):
    await repo.add([(str(schedule.id), schedule.json(), schedule.priority)])

    modified_schedule = schedule.copy()
    modified_schedule.schedule = "5 5 5 5 5"
    modified_schedule.description = f"Updated in test at {datetime.now()}"
    modified_schedule.active = False

    size_before = await repo.size
    await repo.update(
        [
            (
                str(modified_schedule.id),
                modified_schedule.json(),
                modified_schedule.priority,
            )
        ]
    )
    assert await repo.size == size_before

    data, *_ = await repo.get([str(schedule.id)])
    updated_schedule = Schedule.parse_raw(data)
    assert schedule != updated_schedule
    assert updated_schedule.schedule == modified_schedule.schedule
    assert updated_schedule.description == modified_schedule.description
    assert updated_schedule.active == modified_schedule.active


@pytest.mark.asyncio
async def test_update_nonexistant(repo: RedisRepository, schedule: Schedule):
    size_before = await repo.size
    s = await repo.update([(str(schedule.id), schedule.json(), schedule.priority)])
    size_after = await repo.size
    assert size_after == size_before


@pytest.mark.asyncio
async def test_delete(repo: RedisRepository, schedule: Schedule):
    await repo.add([(str(schedule.id), schedule.json(), schedule.priority)])

    size_before = await repo.size
    await repo.delete([str(schedule.id)])
    size_after = await repo.size
    assert size_after == size_before - 1

    data = await RedisRepository.redis.get(str(schedule.id))
    assert data is None


@pytest.mark.asyncio
async def test_delete_nonexistant(repo: RedisRepository, schedule: Schedule):
    size_before = await repo.size
    s = await repo.delete(str(schedule.id))

    assert s is None
    assert await repo.size == size_before
