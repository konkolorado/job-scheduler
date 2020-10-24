from datetime import datetime
from uuid import UUID

import pytz

from job_scheduler.db.helpers import JsonMap


def test_valid_schedule(client, repo):
    data = {
        "name": "Test Name",
        "description": "Test Description",
        "schedule": "* * * * *",
    }
    resp = client.post("/schedule/", json=data)

    assert resp.status_code == 201
    # validate_data_in_repo(repo, data, resp.json())


def test_invalid_schedule(client):
    data = {
        "name": "Test Name",
        "description": "Test Description",
        "schedule": "BLAH * * * *",
    }
    resp = client.post("/schedule/", json=data)
    assert resp.status_code == 422


def test_valid_start_at(client):
    data = {
        "name": "Test Name",
        "description": "Test Description",
        "schedule": "* * * * *",
        "start_at": str(datetime.now(pytz.utc)),
    }
    resp = client.post("/schedule/", json=data)
    assert resp.status_code == 201
    assert datetime.fromisoformat(resp.json()["start_at"]) == datetime.fromisoformat(
        data["start_at"]
    )
    assert datetime.fromisoformat(resp.json()["next_run"]) > datetime.fromisoformat(
        data["start_at"]
    )


def test_missing_data(client, repo):
    data = {
        "name": "Test Name",
        "schedule": "Test Schedule",
    }
    resp = client.post("/schedule/", json=data)
    assert resp.status_code == 422

    # data.pop("silly_field")
    # validate_data_in_repo(repo, data, resp.json())


def validate_data_in_repo(repo, req_data: JsonMap, resp_data: JsonMap):
    assert resp_data["id"] in repo
    assert resp_data == repo.get(resp_data["id"])

    for k in req_data:
        assert k in resp_data
        assert req_data[k] == resp_data[k]
