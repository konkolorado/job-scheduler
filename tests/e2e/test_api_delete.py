import uuid

import pytest

from job_scheduler.api.models import Schedule, ScheduleRequest


@pytest.mark.asyncio
async def test_delete(async_client, repo, schedule_request: ScheduleRequest):
    async with async_client:
        resp = await async_client.post("/schedule/", json=schedule_request.dict())
    s = Schedule.parse_obj(resp.json())

    size_before = await repo.size
    async with async_client:
        resp = await async_client.delete(f"/schedule/{s.id}")
    size_after = await repo.size

    assert resp.status_code == 200
    assert str(s.id) not in repo
    assert size_after == size_before - 1


@pytest.mark.asyncio
async def test_delete_nonexistant_schedule(async_client, repo):
    size_before = await repo.size
    async with async_client:
        resp = await async_client.delete(f"/schedule/{uuid.uuid4()}")
    size_after = await repo.size

    assert resp.status_code == 404
    assert size_after == size_before
