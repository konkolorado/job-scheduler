from datetime import datetime, timezone

import pytest

from job_scheduler.api.models import Schedule


@pytest.mark.asyncio
async def test_valid_schedule(async_client, repo):
    data = {
        "name": "Test Name",
        "description": "Test Description",
        "schedule": "* * * * *",
        "job": {
            "callback_url": "http://127.0.0.1:8080",
            "http_method": "post",
            "payload": {},
        },
    }
    size_before = await repo.size
    async with async_client:
        resp = await async_client.post("/schedule/", json=data)
    size_after = await repo.size
    new_s = Schedule.parse_obj(resp.json())

    assert resp.status_code == 201
    assert str(new_s.id) in repo
    assert size_after == size_before + 1


@pytest.mark.asyncio
async def test_invalid_schedule(async_client, repo):
    data = {
        "name": "Test Name",
        "description": "Test Description",
        "schedule": "BLAH * * * *",
        "job": {
            "callback_url": "http://127.0.0.1:8080",
            "http_method": "post",
        },
    }
    size_before = await repo.size
    async with async_client:
        resp = await async_client.post("/schedule/", json=data)
    size_after = await repo.size

    assert resp.status_code == 422
    assert size_after == size_before


@pytest.mark.asyncio
async def test_valid_start_at(async_client, repo):
    data = {
        "name": "Test Name",
        "description": "Test Description",
        "schedule": "* * * * *",
        "start_at": str(datetime.now(timezone.utc)),
        "job": {
            "callback_url": "http://127.0.0.1:8080",
            "http_method": "post",
            "payload": {},
        },
    }
    size_before = await repo.size
    async with async_client:
        resp = await async_client.post("/schedule/", json=data)
    size_after = await repo.size

    assert resp.status_code == 201
    assert datetime.fromisoformat(resp.json()["start_at"]) == datetime.fromisoformat(
        data["start_at"]
    )
    assert datetime.fromisoformat(resp.json()["next_run"]) > datetime.fromisoformat(
        data["start_at"]
    )
    assert size_after == size_before + 1


@pytest.mark.asyncio
async def test_missing_data(async_client, repo):
    data = {
        "name": "Test Name",
        "schedule": "Test Schedule",
    }
    size_before = await repo.size
    async with async_client:
        resp = await async_client.post("/schedule/", json=data)
    size_after = await repo.size

    assert resp.status_code == 422
    assert size_after == size_before
