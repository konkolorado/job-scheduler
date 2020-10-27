from datetime import datetime

import pytz

from job_scheduler.api.models import Schedule


def test_valid_schedule(client, repo):
    data = {
        "name": "Test Name",
        "description": "Test Description",
        "schedule": "* * * * *",
    }
    size_before = len(repo)
    resp = client.post("/schedule/", json=data)

    assert resp.status_code == 201
    assert Schedule(**resp.json()) in repo
    assert len(repo) == size_before + 1


def test_invalid_schedule(client, repo):
    data = {
        "name": "Test Name",
        "description": "Test Description",
        "schedule": "BLAH * * * *",
    }
    size_before = len(repo)
    resp = client.post("/schedule/", json=data)
    assert resp.status_code == 422
    assert len(repo) == size_before


def test_valid_start_at(client, repo):
    data = {
        "name": "Test Name",
        "description": "Test Description",
        "schedule": "* * * * *",
        "start_at": str(datetime.now(pytz.utc)),
    }
    size_before = len(repo)
    resp = client.post("/schedule/", json=data)
    assert resp.status_code == 201
    assert datetime.fromisoformat(resp.json()["start_at"]) == datetime.fromisoformat(
        data["start_at"]
    )
    assert datetime.fromisoformat(resp.json()["next_run"]) > datetime.fromisoformat(
        data["start_at"]
    )
    assert len(repo) == size_before + 1


def test_missing_data(client, repo):
    data = {
        "name": "Test Name",
        "schedule": "Test Schedule",
    }
    size_before = len(repo)

    resp = client.post("/schedule/", json=data)
    assert resp.status_code == 422
    assert len(repo) == size_before
