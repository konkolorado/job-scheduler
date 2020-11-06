from datetime import datetime, timedelta, timezone

import pydantic
import pytest
from croniter import croniter

from job_scheduler.api.models import Schedule, ScheduleRequest


def test_schedule_req_to_schedule(schedule_request: ScheduleRequest):
    schedule = Schedule(**schedule_request.dict())
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


def test_schedule_req_defaults():
    schedule_req = ScheduleRequest(
        name="Test Schedule Name",
        description="Test Schedule Description",
        schedule="* * * * *",
    )

    assert schedule_req.active is True
    assert schedule_req.start_at is None


def test_schedule_req_invalid_start():
    with pytest.raises(pydantic.ValidationError):
        schedule_req = ScheduleRequest(
            name="Test Schedule Name",
            description="Test Schedule Description",
            schedule="* * * * *",
            active=False,
            start_at="WHENEVER YOU FEEL LIKE IT",
        )


def test_schedule_req_nonlocalized_start():
    with pytest.raises(pydantic.ValidationError):
        schedule_req = ScheduleRequest(
            name="Test Schedule Name",
            description="Test Schedule Description",
            schedule="* * * * *",
            active=False,
            start_at=datetime.now(),
        )


def test_schedule_defaults():
    s = Schedule(
        name="Test Schedule Name",
        description="Test Schedule Description",
        schedule="* * * * *",
        active=True,
    )

    assert s.start_at is not None
    assert s.next_run is not None
    assert croniter(s.schedule, s.start_at).get_next(datetime) == s.next_run


def test_schedule_with_start_at():
    start_at = datetime.now() + timedelta(1)
    s = Schedule(
        name="Test Schedule Name",
        description="Test Schedule Description",
        schedule="* * * * *",
        active=True,
        start_at=start_at,
    )

    assert croniter(s.schedule, start_at).get_next(datetime) == s.next_run


def test_schedule_calc_next_run():
    s = Schedule(
        name="Test Schedule Name",
        description="Test Schedule Description",
        schedule="* * * * *",
        active=True,
    )

    now = datetime.now(timezone.utc)
    assert croniter(s.schedule, now).get_next(datetime) == s.calc_next_run()


def test_schedule_confirm_execution():
    s = Schedule(
        name="Test Schedule Name",
        description="Test Schedule Description",
        schedule="* * * * *",
        active=True,
    )

    first_run = croniter(s.schedule, s.start_at).get_next(datetime)
    second_run = croniter(s.schedule, first_run).get_next(datetime)

    s.confirm_execution()
    assert s.last_run is not None
    assert second_run == s.next_run
