from __future__ import annotations

import asyncio
import json

import structlog
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from job_scheduler.config import config
from job_scheduler.db.base import JobRepository, ScheduleRepository
from job_scheduler.db.pg_models import Base
from job_scheduler.db.types import JobRepoItem, ScheduleRepoItem

from .pg_models import Schedule

logger = structlog.get_logger(__name__)


async def create_engine() -> AsyncEngine:
    conn_string = f"postgresql+asyncpg://{config.db.username}:{config.db.password}@{config.db.host}:{config.db.port}"
    safe_string = f"postgresql+asyncpg://{config.db.username}:***{config.db.password[-5:]}@{config.db.host}:{config.db.port}"
    engine = create_async_engine(conn_string, echo=True, pool_pre_ping=True)
    while True:
        try:
            logger.info(f"Instantiating Postgres engine at {safe_string}.")
            async with engine.connect():
                ...
        except OSError:
            logger.warning(
                f"Unable to Postgres engine at {safe_string}. "
                f"Retrying in {config.db.connect_retry_sleep} seconds.",
                exc_info=True,
            )
            await asyncio.sleep(config.db.connect_retry_sleep)
        else:
            logger.info(f"Postgres engine sucessfully instantiated.")
            return engine


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_session(engine: AsyncEngine) -> AsyncSession:
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class PostgresScheduleRepository(ScheduleRepository):
    session: AsyncSession

    @classmethod
    async def get_repo(cls) -> PostgresScheduleRepository:
        engine = await create_engine()
        await create_tables(engine)
        cls.session = await create_session(engine)
        return cls()

    def add(self, *items: ScheduleRepoItem):
        for i in items:
            shim_schedule  = json.loads(i.schedule)
            Schedule(
                id=i.id,
                i.schedule.name,
            )
            i.id
            i.priority
            i.schedule
        pass

    def get(self, *keys: str):
        pass

    def update(self, *items: ScheduleRepoItem):
        pass

    def delete(self, *keys: str):
        pass

    def get_range(self, min: float, max: float):
        pass

    @property
    async def size(self):
        pass


class PostgresJobRepository(JobRepository):
    session: AsyncSession

    @classmethod
    async def get_repo(cls) -> PostgresJobRepository:
        engine = await create_engine()
        await create_tables(engine)
        cls.session = await create_session(engine)
        return cls()


if __name__ == "__main__":
    import asyncio

    asyncio.run(PostgresScheduleRepository.get_repo())
