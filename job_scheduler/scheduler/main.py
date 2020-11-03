import asyncio
from datetime import datetime, timedelta, timezone

from job_scheduler.api.models import Schedule
from job_scheduler.db import RedisRepository, ScheduleRepository
from job_scheduler.services import get_range, update_schedule


async def schedule_jobs(repo: ScheduleRepository, interval=1):
    while True:
        now = datetime.now(timezone.utc)
        future = now + timedelta(seconds=interval)
        schedules_to_run = await get_range(repo, now.timestamp(), future.timestamp())
        for s in schedules_to_run:
            s.confirm_execution()
            await update_schedule(repo, {s.id: s.dict()})
            # Log something here
        await asyncio.sleep(interval)


async def main():
    repo = await RedisRepository.get_repo()
    await schedule_jobs(repo)


if __name__ == "__main__":
    asyncio.run(main())
