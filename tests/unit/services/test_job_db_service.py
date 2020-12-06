import pytest

from job_scheduler.db import FakeJobRepository, JobRepository
from job_scheduler.services.db import add_jobs, get_jobs, get_schedule_jobs


@pytest.fixture(scope="session")
def repo():
    return FakeJobRepository.get_repo()


@pytest.mark.asyncio
async def test_adding_and_getting_jobs(repo: JobRepository, n_jobs):
    jobs = n_jobs(3)
    stored = await add_jobs(repo, *jobs)

    assert len(stored) == len(jobs)
    for j in jobs:
        retrieved, *_ = await get_jobs(repo, j.id)
        assert j == retrieved


@pytest.mark.asyncio
async def test_get_by_parent(repo: JobRepository, n_jobs):
    jobs = n_jobs(3)
    await add_jobs(repo, *jobs)

    schedule_jobs = await get_schedule_jobs(repo, jobs[0].schedule_id)
    for j in jobs:
        assert j in schedule_jobs[jobs[0].schedule_id]
