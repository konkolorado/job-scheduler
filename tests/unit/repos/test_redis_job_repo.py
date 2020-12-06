import uuid
from typing import Sequence

import pytest

from job_scheduler.api.models import Job
from job_scheduler.db.redis import JobRepoItem, JobRepository, RedisJobRepository


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def repo():
    return await RedisJobRepository.get_repo()


def job_to_jobrepoitem(*jobs: Job) -> Sequence[JobRepoItem]:
    items = []
    for j in jobs:
        jri = JobRepoItem(id=str(j.id), schedule_id=str(j.schedule_id), job=j.json())
        items.append(jri)
    return items


@pytest.mark.asyncio
async def test_add(n_jobs, repo: RedisJobRepository):
    jobs = n_jobs(2)
    jris = job_to_jobrepoitem(*jobs)

    await repo.add(*jris)
    for jri in jris:
        j, *_ = await repo.get(jri.id)
        assert j == jri.job


@pytest.mark.asyncio
async def test_get(repo: RedisJobRepository, n_jobs):
    job, *_ = n_jobs(1)
    jris = job_to_jobrepoitem(job)
    await repo.add(*jris)

    data, *_ = await repo.get(str(job.id))
    assert job == Job.parse_raw(data)


@pytest.mark.asyncio
async def test_get_nothing(repo: RedisJobRepository):
    assert await repo.get() == []


@pytest.mark.asyncio
async def test_get_nonexistant(repo: RedisJobRepository):
    assert await repo.get(str(uuid.uuid4())) == []


@pytest.mark.asyncio
async def test_get_by_parent(n_jobs, repo: RedisJobRepository):
    jobs = n_jobs(5)
    jris = job_to_jobrepoitem(*jobs)

    await repo.add(*jris)

    s_id = str(jobs[0].schedule_id)
    results = await repo.get_by_parent(s_id)

    assert len(results[s_id]) == len(jobs)


@pytest.mark.asyncio
async def test_redis_shutdown(repo: RedisJobRepository):
    await repo.shutdown()
    assert repo.redis.closed


def test_namespaced_key(repo: RedisJobRepository):
    key = "some_key"

    result = repo.namespaced_key(key)
    assert result.startswith(repo.namespace)
    assert repo.namespaced_key(result) == result
