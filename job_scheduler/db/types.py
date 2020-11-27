from dataclasses import dataclass
from typing import Any, MutableMapping

JsonMap = MutableMapping[str, Any]


@dataclass
class ScheduleRepoItem:
    id: str
    schedule: str
    priority: float


@dataclass
class JobRepoItem:
    id: str
    schedule_id: str
    job: str
