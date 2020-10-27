import uuid
from datetime import datetime

from job_scheduler.api.models import Schedule, ScheduleRequest


def test_update_schedule(client, repo, schedule_request: ScheduleRequest):
    resp = client.post("/schedule/", json=schedule_request.dict())
    id = resp.json()["id"]

    schedule_request.description = f"Updated in tests at {datetime.now()}"
    size_before = len(repo)
    resp = client.put(f"/schedule/{id}", json=schedule_request.dict())

    assert resp.status_code == 200
    assert len(repo) == size_before
    assert Schedule(**resp.json()) in repo


def test_bad_update(client, repo, schedule_request: ScheduleRequest):
    resp = client.post("/schedule/", json=schedule_request.dict())
    id = resp.json()["id"]

    schedule_request.schedule = "Not_A_SCHEDULE"
    size_before = len(repo)
    resp = client.put(f"/schedule/{id}", json=schedule_request.dict())

    assert resp.status_code == 422
    assert len(repo) == size_before


def test_update_nonexistant(client, repo, schedule_request: ScheduleRequest):
    resp = client.put(f"/schedule/{uuid.uuid4()}", json=schedule_request.dict())
    assert resp.status_code == 404
