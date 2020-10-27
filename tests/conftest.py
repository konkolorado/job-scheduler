import pytest
from fastapi.testclient import TestClient

from job_scheduler.api.main import app, get_repo
from job_scheduler.api.models import Schedule, ScheduleRequest
from job_scheduler.db.fake import FakeRepository


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_repo] = FakeRepository.get_repo
    yield TestClient(app)


@pytest.fixture(scope="session")
def repo():
    return FakeRepository.get_repo()


@pytest.fixture
def schedule_request():
    return ScheduleRequest(
        name="Test Schedule Name",
        description="Test Schedule Description",
        schedule="* * * * *",
    )


@pytest.fixture
def schedule(schedule_request: ScheduleRequest):
    return Schedule(**schedule_request.dict())
