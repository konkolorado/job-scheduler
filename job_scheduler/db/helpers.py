import datetime
from json import JSONEncoder
from typing import Any, Mapping
from uuid import UUID

JsonMap = Mapping[str, Any]


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime.date):
            return str(obj)
        return JSONEncoder.default(self, obj)
