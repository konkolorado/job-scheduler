from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

import pytz
from croniter import croniter
from pydantic import BaseModel, Field, HttpUrl, validator

from job_scheduler.db.types import JsonMap


class HttpMethod(str, Enum):
    post = "post"
    get = "get"


class JobRequest(BaseModel):
    callback_url: HttpUrl
    http_method: HttpMethod = HttpMethod.post


class Job(BaseModel):
    schedule_id: UUID
    job_id: UUID = Field(default_factory=uuid4)
    callback_url: HttpUrl
    http_method: HttpMethod
    status_code: int
    result: JsonMap


class ScheduleRequest(BaseModel):
    name: str
    schedule: str
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    active: bool = True
    job: JobRequest

    @validator("schedule")
    def validate_schedule(cls, v):
        if croniter.is_valid(v):
            return v
        raise ValueError("Use a valid cron format")

    @validator("start_at")
    def validate_start_at(cls, v):
        if v is None:
            return v

        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("Datetime must be UTC-localized")
        return v


class Schedule(BaseModel):
    name: str
    schedule: str
    description: Optional[str] = None
    start_at: Optional[datetime]
    active: bool
    job: JobRequest
    id: UUID = Field(default_factory=uuid4)
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None

    @validator("start_at", always=True)
    def validate_start_at(cls, v) -> datetime:
        if v is None:
            return datetime.now(timezone.utc)
        return v

    @validator("next_run", always=True)
    def init_next_run(cls, next_run, values) -> datetime:
        if next_run is not None:
            return next_run

        schedule, start_at = values["schedule"], values["start_at"]
        return croniter(schedule, start_at).get_next(datetime)

    def calc_next_run(self, start: Optional[datetime] = None) -> datetime:
        if start is None:
            start = datetime.now(timezone.utc)

        try:
            utc_start = pytz.utc.localize(start)
        except ValueError:
            utc_start = start

        return croniter(self.schedule, utc_start).get_next(datetime)

    def confirm_execution(self):
        utc_now = datetime.now(timezone.utc)
        self.last_run = utc_now

        if self.next_run < utc_now:
            # Calc next run relative to current time
            self.next_run = self.calc_next_run()
        else:
            # Calc next run relative to when the job is going to
            # run next
            self.next_run = self.calc_next_run(self.next_run)

    @property
    def priority(self) -> float:
        assert self.next_run
        return self.next_run.timestamp()
