from datetime import datetime, timedelta, timezone

import pytest

from job_scheduler.api.models import Schedule
from job_scheduler.broker import FakeBroker, ScheduleBroker
from job_scheduler.db import FakeScheduleRepository, ScheduleRepository
from job_scheduler.scheduler.main import schedule_jobs
from job_scheduler.services import store_schedule


@pytest.fixture(scope="session")
def repo():
    return FakeScheduleRepository.get_repo()


@pytest.fixture(scope="session")
def broker():
    return FakeBroker.get_broker()


@pytest.mark.asyncio
async def test_jobs_get_scheduled(
    schedule: Schedule, repo: ScheduleRepository, broker: ScheduleBroker
):
    # Add schedule to repo
    schedule.next_run = datetime.now(timezone.utc)
    await store_schedule(repo, schedule)

    # Run schedule_jobs twice to ensure the job is queued
    for _ in range(2):
        await schedule_jobs(repo, broker)

    # Assert schedule is added to broker
    s = await broker.get()
    assert s == str(schedule.id)
