from datetime import datetime

import pytest
from croniter import croniter

from job_scheduler.api.models import Schedule, ScheduleRequest


@pytest.fixture
def schedule_req():
    return ScheduleRequest(
        name="Test Schedule Name",
        description="Test Schedule Description",
        schedule="* * * * *",
    )


def test_schedule_request_to_schedule(schedule_req):
    s = Schedule(**schedule_req.dict())

    assert s.name == schedule_req.name
    assert s.description == schedule_req.description
    assert s.schedule == schedule_req.schedule
    assert s.active == schedule_req.active
    assert s.start_at == schedule_req.start_at
    assert not s.last_run
    assert s.next_run == s.calc_next_run(s.start_at)
