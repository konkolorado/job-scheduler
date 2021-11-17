import enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm.decl_api import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


class HttpMethod(str, enum.Enum):
    post = "post"


class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(50))
    schedule = Column(String(50))
    description = Column(String(150))
    active = Column(Boolean)
    created_at = Column(DateTime(timezone=True))
    start_at = Column(DateTime(timezone=True))
    next_run = Column(DateTime(timezone=True), index=True)
    last_run = Column(DateTime(timezone=True))
    jobs = relationship("Job")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True)
    schedule_id = Column(ForeignKey("schedules.id"))
    ran_at = Column(DateTime(timezone=True))
    callback_url = Column(String(150))
    http_method = Column(Enum(HttpMethod))
    status_code = Column(Integer)
    result = Column(JSON)
