import uuid

from job_scheduler.api.models import ScheduleRequest


def test_get_schedule(client, schedule_request: ScheduleRequest):
    resp = client.post("/schedule/", json=schedule_request.dict())
    resp = client.get(f"/schedule/{resp.json()['id']}")
    assert resp.status_code == 200


def test_get_nonexistant(client, schedule_request):
    resp = client.get(f"/schedule/{uuid.uuid4()}")
    assert resp.status_code == 404
