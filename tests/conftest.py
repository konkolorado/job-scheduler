import asyncio

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from job_scheduler.api.main import app, get_schedule_repo
from job_scheduler.api.models import Schedule, ScheduleRequest
from job_scheduler.db import FakeRepository


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_schedule_repo] = FakeRepository.get_repo
    yield TestClient(app)


@pytest.fixture(scope="session")
async def async_client():
    app.dependency_overrides[get_schedule_repo] = FakeRepository.get_repo
    return AsyncClient(app=app, base_url="http://localhost")


@pytest.fixture(scope="session")
def repo():
    return FakeRepository.get_repo()


@pytest.fixture
def schedule_request():
    return ScheduleRequest(
        name="Test Schedule Name",
        description="Test Schedule Description",
        schedule="* * * * *",
        job={
            "callback_url": "http://127.0.0.1:8080",
            "http_method": "post",
            "payload": {},
        },
    )


@pytest.fixture
def n_schedules(schedule_request: ScheduleRequest):
    def _make_n_schedules(n: int):
        schedules = []
        for _ in range(n):
            s = Schedule(**schedule_request.dict())
            schedules.append(s)
        return schedules

    return _make_n_schedules


@pytest.fixture
def schedule(schedule_request: ScheduleRequest):
    return Schedule(**schedule_request.dict())


@pytest.yield_fixture(scope="session")
def event_loop(request):
    """
    We need to override the event_loop fixture such that it is of the
    correct scope.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
