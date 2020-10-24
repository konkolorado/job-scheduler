import pytest
from fastapi.testclient import TestClient

from job_scheduler.api.main import app, get_repo
from job_scheduler.db.fake import FakeRepository


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_repo] = override_get_repo
    yield TestClient(app)


@pytest.fixture(scope="session")
def repo():
    return FakeRepository.get_repo()


def override_get_repo():
    return FakeRepository.get_repo()
