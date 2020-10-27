import uuid
from datetime import datetime

import pytest

from job_scheduler.api.models import Schedule, ScheduleRequest


@pytest.mark.asyncio
async def test_update_schedule(async_client, repo, schedule_request: ScheduleRequest):
    async with async_client:
        resp = await async_client.post("/schedule/", json=schedule_request.dict())
    s_id = resp.json()["id"]

    size_before = await repo.size
    schedule_request.description = f"Updated in tests at {datetime.now()}"

    async with async_client:
        resp = await async_client.put(f"/schedule/{s_id}", json=schedule_request.dict())
    size_after = await repo.size

    assert resp.status_code == 200
    assert size_after == size_before
    assert Schedule.parse_obj(resp.json()) in repo


@pytest.mark.asyncio
async def test_bad_update(async_client, repo, schedule_request: ScheduleRequest):
    async with async_client:
        resp = await async_client.post("/schedule/", json=schedule_request.dict())
    s_id = resp.json()["id"]

    size_before = await repo.size
    schedule_request.schedule = "Not_A_SCHEDULE"

    async with async_client:
        resp = await async_client.put(f"/schedule/{s_id}", json=schedule_request.dict())
    size_after = await repo.size

    assert resp.status_code == 422
    assert size_after == size_before


@pytest.mark.asyncio
async def test_update_nonexistant(
    async_client, repo, schedule_request: ScheduleRequest
):
    size_before = await repo.size
    async with async_client:
        resp = await async_client.put(
            f"/schedule/{uuid.uuid4()}", json=schedule_request.dict()
        )
    size_after = await repo.size

    assert resp.status_code == 404
    assert size_after == size_before
