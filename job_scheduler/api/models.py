from datetime import datetime
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
            return datetime.now()
        return v

    @validator("next_run", always=True)
    def init_next_run(cls, _, values) -> datetime:
        schedule, start_at = values["schedule"], values["start_at"]
        try:
            start_at = pytz.utc.localize(start_at)
        except ValueError:
            pass
        return croniter(schedule, start_at).get_next(datetime)

    def calc_next_run(self, start: Optional[datetime] = None) -> datetime:
        if start is None:
            start = datetime.now()
        uct_start = pytz.utc.localize(start)
        return croniter(self.schedule, uct_start).get_next(datetime)

    def confirm_execution(self):
        self.last_run = pytz.utc.localize(datetime.now())
        self.next_run = self.calc_next_run()

    @property
    def priority(self) -> float:
        if self.next_run is None:
            raise ValueError("next_run not set")
        return self.next_run.timestamp()
