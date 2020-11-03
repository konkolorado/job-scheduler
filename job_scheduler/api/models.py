from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

import pytz
from croniter import croniter
from pydantic import BaseModel, Field, validator


class ScheduleRequest(BaseModel):
    name: str
    schedule: str
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    active: bool = True

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
        self.last_run = datetime.now(timezone.utc)
        self.next_run = self.calc_next_run(self.next_run)

    @property
    def priority(self) -> float:
        assert self.next_run
        return self.next_run.timestamp()
