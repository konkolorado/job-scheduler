import pydantic
import pytest

from job_scheduler.api.models import Schedule, ScheduleRequest


def test_schedule_request_to_schedule(
    schedule: Schedule, schedule_request: ScheduleRequest
):

    assert schedule.name == schedule_request.name
    assert schedule.description == schedule_request.description
    assert schedule.schedule == schedule_request.schedule
    assert schedule.active == schedule_request.active
    assert schedule.start_at is not None
    assert schedule.last_run is None
    assert schedule.next_run == schedule.calc_next_run(schedule.start_at)


def test_schedule_req_invalid_schedule():
    with pytest.raises(pydantic.ValidationError):
        schedule_req = ScheduleRequest(
            name="Test Schedule Name",
            description="Test Schedule Description",
            schedule="invalid_schedule",
        )


def test_schedule_req_non_active():
    schedule_req = ScheduleRequest(
        name="Test Schedule Name",
        description="Test Schedule Description",
        schedule="* * * * *",
        active=False,
    )

    assert not schedule_req.active
