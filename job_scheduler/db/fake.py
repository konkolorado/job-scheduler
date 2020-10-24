import json
from uuid import UUID

from job_scheduler.db.base import ScheduleRepository
from job_scheduler.db.helpers import CustomEncoder, JsonMap


class FakeRepository(ScheduleRepository):
    data: JsonMap = {}

    def add(self, key: UUID, value: JsonMap):
        self.data[str(key)] = json.dumps(value, cls=CustomEncoder)

    def get(self, key: UUID) -> JsonMap:
        return json.loads(self.data[str(key)])

    def update(self, key: UUID, value: JsonMap):
        self.data[str(key)] = json.dumps(value, cls=CustomEncoder)

    def delete(self, key: UUID):
        self.data.pop(str(key))

    def __contains__(self, item):
        return str(item) in self.data

    def list(self):
        pass

    @classmethod
    def get_repo(cls):
        return cls()
