import asyncio
from datetime import datetime, timedelta, timezone
from typing import Sequence

import structlog

from job_scheduler.api.models import Schedule
from job_scheduler.broker import RabbitMQBroker, ScheduleBroker
from job_scheduler.cache import RedisScheduleCache, ScheduleCache
from job_scheduler.config import config
from job_scheduler.db import RedisScheduleRepository, ScheduleRepository
from job_scheduler.logging import setup_logging
from job_scheduler.services import (
    add_to_cache,
    diff_from_cache,
    enqueue_jobs,
    get_range,
)

logger = structlog.getLogger("job_scheduler.scheduler")


async def schedule_jobs(
    repo: ScheduleRepository, broker: ScheduleBroker, cache: ScheduleCache, interval=1
):
    now = get_now()
    schedule_candidates = await get_runnable_schedules(repo, now)
    runnable_schedules = await diff_from_cache(cache, *schedule_candidates)
    if len(runnable_schedules) < len(schedule_candidates):
        logger.warning(
            f"Ignoring {len(schedule_candidates)-len(runnable_schedules)} "
            "item(s) from cache"
        )

    await enqueue_jobs(broker, *runnable_schedules)
    await add_to_cache(cache, *runnable_schedules)

    total_delay = sum(s.current_delay.seconds for s in schedule_candidates)
    logger.info(f"Queued {len(runnable_schedules)} schedule(s) for execution at {now}.")
    logger.warning(
        f"Observed {total_delay} second(s) delay in {len(schedule_candidates)} schedule(s)."
    )
    logger.info(f"Sleeping for {interval} second(s).")
    await asyncio.sleep(interval)


async def get_runnable_schedules(
    repo: ScheduleRepository, now: datetime
) -> Sequence[Schedule]:
    return await get_range(repo, None, now.timestamp())


def get_now() -> datetime:
    now = datetime.now(timezone.utc)
    return now - timedelta(microseconds=now.microsecond)


async def schedule():
    cache = await RedisScheduleCache.get_cache()
    repo = await RedisScheduleRepository.get_repo()
    broker = await RabbitMQBroker.get_broker()
    while True:
        try:
            await schedule_jobs(repo, broker, cache)
        except KeyboardInterrupt:
            await broker.shutdown()


def main():
    setup_logging()
    try:
        asyncio.run(schedule())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    if config.dev_mode:
        from job_scheduler.services.reloading import with_reloading

        logger.info("Starting scheduler with reloading.")
        with_reloading(main)
    else:
        main()
