import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List

from job_scheduler.api.models import Schedule
from job_scheduler.db import RedisRepository, ScheduleRepository
from job_scheduler.logging import setup_logging
from job_scheduler.services import get_range, update_schedule

logger = logging.getLogger("job_scheduler")


async def schedule_jobs(repo: ScheduleRepository, interval=1):
    missed_schedules = await get_missed_schedules(repo)
    for m in missed_schedules:
        m.confirm_execution()
        await update_schedule(repo, {m.id: m.dict()})
    logger.warning(f"Corrected for {len(missed_schedules)} missed job(s).")

    while True:
        now = datetime.now(timezone.utc)
        past = now - timedelta(seconds=interval / 2)
        future = now + timedelta(seconds=interval)

        schedules_to_run = await get_range(repo, past.timestamp(), future.timestamp())
        for s in schedules_to_run:
            print(s.job.callback_url)
            s.confirm_execution()
            await update_schedule(repo, {s.id: s.dict()})

        logger.info(
            f"Ran {len(schedules_to_run)} jobs between {past.replace(tzinfo=None)} "
            f"and {future.replace(tzinfo=None)}. Sleeping for {interval} second(s)."
        )
        await asyncio.sleep(interval)


async def get_missed_schedules(repo: ScheduleRepository) -> List[Schedule]:
    now = datetime.now(timezone.utc)
    last_yr = now - timedelta(weeks=52)
    return await get_range(repo, last_yr.timestamp(), now.timestamp())


async def main():
    setup_logging()
    repo = await RedisRepository.get_repo()
    await schedule_jobs(repo)


if __name__ == "__main__":
    asyncio.run(main())
