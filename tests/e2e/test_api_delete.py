import uuid

from job_scheduler.api.models import Schedule, ScheduleRequest


def test_delete(client, repo, schedule_request: ScheduleRequest):
    resp = client.post("/schedule/", json=schedule_request.dict())
    s = Schedule(**resp.json())
    size_before = len(repo)

    resp = client.delete(f"/schedule/{s.id}")

    assert resp.status_code == 200
    assert s not in repo
    assert len(repo) == size_before - 1


def test_delete_nonexistant_schedule(client, repo, schedule_request: ScheduleRequest):
    size_before = len(repo)
    resp = client.delete(f"/schedule/{uuid.uuid4()}")

    assert resp.status_code == 404
    assert len(repo) == size_before
