import time
from datetime import datetime, timezone

import pytest

from job_scheduler.api.models import Schedule
from job_scheduler.broker import FakeBroker, ScheduleBroker
from job_scheduler.cache import FakeScheduleCache, ScheduleCache
from job_scheduler.db import FakeScheduleRepository, ScheduleRepository
from job_scheduler.scheduler.main import schedule_jobs
from job_scheduler.services import store_schedule


@pytest.fixture(scope="session")
def repo():
    return FakeScheduleRepository.get_repo()


@pytest.fixture(scope="session")
async def broker():
    return await FakeBroker.get_broker()


@pytest.fixture(scope="session")
async def cache():
    return await FakeScheduleCache.get_cache()


@pytest.mark.asyncio
async def test_jobs_get_scheduled(
    schedule: Schedule,
    repo: ScheduleRepository,
    broker: ScheduleBroker,
    cache: ScheduleCache,
):
    # Add schedule to repo
    schedule.next_run = datetime.now(timezone.utc)
    await store_schedule(repo, schedule)

    # Run schedule_jobs to queue the job
    time.sleep(1)
    await schedule_jobs(repo, broker, cache)

    # Assert schedule is added to broker
    s = await broker.get()
    assert s.payload == str(schedule.id)
