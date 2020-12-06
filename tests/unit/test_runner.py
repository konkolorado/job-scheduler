import pytest
from aiohttp import web

from job_scheduler.api.models import Schedule
from job_scheduler.broker import FakeBroker, ScheduleBroker
from job_scheduler.db import (
    FakeJobRepository,
    FakeScheduleRepository,
    JobRepository,
    ScheduleRepository,
)
from job_scheduler.runner.main import run_jobs
from job_scheduler.services import get_schedule, get_schedule_jobs, store_schedule


@pytest.fixture(scope="session")
def s_repo():
    return FakeScheduleRepository.get_repo()


@pytest.fixture(scope="session")
def j_repo():
    return FakeJobRepository.get_repo()


@pytest.fixture(scope="session")
def broker():
    return FakeBroker.get_broker()


async def test_jobs_get_run(
    schedule: Schedule,
    s_repo: ScheduleRepository,
    j_repo: JobRepository,
    broker: ScheduleBroker,
    aiohttp_client,
):
    await broker.publish(str(schedule.id))
    await store_schedule(s_repo, schedule)

    tc = await aiohttp_client(web.Application())
    await run_jobs(s_repo, j_repo, broker, tc.session)

    # assert schedule was run
    s, *_ = await get_schedule(s_repo, schedule.id)
    assert s.last_run is not None

    # assert job was created
    jobs = await get_schedule_jobs(j_repo, schedule.id)
    assert len(jobs[schedule.id]) == 1
