import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Sequence

from job_scheduler.api.models import Schedule
from job_scheduler.broker import RedisBroker, ScheduleBroker
from job_scheduler.db import RedisScheduleRepository, ScheduleRepository
from job_scheduler.logging import setup_logging
from job_scheduler.services import enqueue_jobs, get_range

logger = logging.getLogger("job_scheduler")


async def schedule_jobs(repo: ScheduleRepository, broker: ScheduleBroker, interval=1):
    now = get_now()
    schedules_to_run = await get_runnable_schedules(repo, now)
    enqueued = await enqueue_jobs(broker, *schedules_to_run)

    n_late = len(schedules_to_run) - len(enqueued)
    total_delay = 0.0
    for s in schedules_to_run:
        if s not in enqueued:
            total_delay += s.current_delay.seconds

    logger.info(f"Queued {len(enqueued)} schedule(s) for execution at {now}.")
    if n_late > 0:
        logger.warning(f"Observed {total_delay} seconds delay in {n_late} schedule(s).")
    logger.info(f"Sleeping for {interval} second(s).")
    await asyncio.sleep(interval)


async def get_runnable_schedules(
    repo: ScheduleRepository, now: datetime
) -> Sequence[Schedule]:
    return await get_range(repo, None, now.timestamp())


def get_now() -> datetime:
    now = datetime.now(timezone.utc)
    return now - timedelta(microseconds=now.microsecond)


async def main():
    setup_logging()
    repo = await RedisScheduleRepository.get_repo()
    broker = await RedisBroker.get_broker()

    while True:
        try:
            await schedule_jobs(repo, broker)
        except KeyboardInterrupt:
            await repo.shutdown()
            await broker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
