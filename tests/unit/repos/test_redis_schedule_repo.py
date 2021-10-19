import uuid
from datetime import datetime, timedelta, timezone
from typing import Sequence

import pytest

from job_scheduler.api.models import Schedule
from job_scheduler.db import RedisScheduleRepository
from job_scheduler.db.types import ScheduleRepoItem


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def repo():
    return await RedisScheduleRepository.get_repo()


def schedule_to_schedulerepoitem(*schedules: Schedule) -> Sequence[ScheduleRepoItem]:
    items = []
    for s in schedules:
        sri = ScheduleRepoItem(
            id=str(s.id),
            schedule=s.json(),
            priority=s.priority,
        )
        items.append(sri)
    return items


@pytest.mark.asyncio
async def test_add(n_schedules, repo: RedisScheduleRepository, schedule: Schedule):
    schedules = n_schedules(2)
    sris = schedule_to_schedulerepoitem(*schedules)

    size_before = await repo.size
    await repo.add(*sris)
    size_after = await repo.size

    assert size_after == size_before + len(schedules)
    for sri in sris:
        s, *_ = await repo.get(sri.id)
        assert s == sri.schedule


@pytest.mark.asyncio
async def test_get(repo: RedisScheduleRepository, n_schedules):
    schedule, *_ = n_schedules(1)
    sris = schedule_to_schedulerepoitem(schedule)
    await repo.add(*sris)

    data, *_ = await repo.get(str(schedule.id))
    assert schedule == Schedule.parse_raw(data)


@pytest.mark.asyncio
async def test_get_nothing(repo: RedisScheduleRepository):
    assert await repo.get() == []


@pytest.mark.asyncio
async def test_get_nonexistant(repo: RedisScheduleRepository):
    assert await repo.get(str(uuid.uuid4())) == []


@pytest.mark.asyncio
async def test_update(repo: RedisScheduleRepository, schedule: Schedule):
    await repo.add(*schedule_to_schedulerepoitem(schedule))

    schedule.schedule = "5 5 5 5 5"
    schedule.description = f"Updated in test at {datetime.now()}"
    schedule.active = False

    size_before = await repo.size
    await repo.update(*schedule_to_schedulerepoitem(schedule))
    assert await repo.size == size_before

    data, *_ = await repo.get(str(schedule.id))
    updated_schedule = Schedule.parse_raw(data)
    assert updated_schedule.schedule == schedule.schedule
    assert updated_schedule.description == schedule.description
    assert updated_schedule.active == schedule.active


@pytest.mark.asyncio
async def test_update_nonexistant(repo: RedisScheduleRepository, schedule: Schedule):
    size_before = await repo.size
    await repo.update(*schedule_to_schedulerepoitem(schedule))
    assert await repo.size == size_before


@pytest.mark.asyncio
async def test_delete(repo: RedisScheduleRepository, schedule: Schedule):
    await repo.add(*schedule_to_schedulerepoitem(schedule))

    size_before = await repo.size
    await repo.delete(str(schedule.id))
    assert await repo.size == size_before - 1

    assert await repo.get(str(schedule.id)) == []


@pytest.mark.asyncio
async def test_delete_nonexistant(repo: RedisScheduleRepository, schedule: Schedule):
    size_before = await repo.size
    await repo.delete(str(schedule.id))
    assert await repo.size == size_before


@pytest.mark.asyncio
async def test_get_range(repo: RedisScheduleRepository, n_schedules):
    schedules = n_schedules(3)
    for i, s in enumerate(schedules):
        s.schedule = f"*/{i+1} * * * *"
        s.description = f"Every {i} mins"
        s.next_run = s.calc_next_run()

    await repo.add(*schedule_to_schedulerepoitem(*schedules))

    now = datetime.now(timezone.utc)
    future = now + timedelta(minutes=1)
    results = await repo.get_range(now.timestamp(), future.timestamp())

    for s in schedules:
        if now.timestamp() <= s.priority <= future.timestamp():
            assert str(s.id) in results
        else:
            assert str(s.id) not in results


# @pytest.mark.asyncio
# async def test_redis_shutdown(repo: RedisScheduleRepository):
#    await repo.shutdown()
#    assert repo.redis.closed


def test_namespaced_key(repo: RedisScheduleRepository):
    key = "some_key"

    result = repo.namespaced_key(key)
    assert result.startswith(repo.namespace)
    assert repo.namespaced_key(result) == result
