import asyncio
import logging
import time
from datetime import datetime, timezone

from aiohttp import ClientConnectorError, ClientSession, ClientTimeout

from job_scheduler.api.models import HttpMethod, Job, Schedule
from job_scheduler.broker import RedisBroker, ScheduleBroker
from job_scheduler.config import config
from job_scheduler.db import (
    JobRepository,
    RedisJobRepository,
    RedisScheduleRepository,
    ScheduleRepository,
)
from job_scheduler.logging import setup_logging
from job_scheduler.services import (
    ack_jobs,
    add_jobs,
    dequeue_jobs,
    get_schedule,
    update_schedule,
)

logger = logging.getLogger("job_runner")


async def run_jobs(
    s_repo: ScheduleRepository,
    j_repo: JobRepository,
    broker: ScheduleBroker,
    session: ClientSession,
):
    schedule_ids = await dequeue_jobs(broker)
    schedules = await get_schedule(s_repo, *schedule_ids)

    start = time.perf_counter()
    results = await asyncio.gather(*[execute(session, s) for s in schedules])
    elapsed = time.perf_counter() - start

    await add_jobs(j_repo, *results)
    for s in schedules:
        s.confirm_execution()
    await update_schedule(s_repo, {s.id: s.dict() for s in schedules})
    await ack_jobs(broker, *schedules)
    logger.info(f"Ran {len(schedule_ids)} schedules in {elapsed:0.4f} second(s).")


async def execute(session: ClientSession, s: Schedule) -> Job:
    http_operations = {HttpMethod.post: session.post}
    http_op = http_operations[s.job.http_method]

    try:
        async with http_op(s.job.callback_url, json=s.job.payload) as response:
            response_code = response.status
            response_result = await response.json()
    except (ClientConnectorError, asyncio.exceptions.TimeoutError) as e:
        response_code = 400
        response_result = {"error": str(e)}

    return Job(
        schedule_id=s.id,
        callback_url=s.job.callback_url,
        http_method=s.job.http_method,
        status_code=response_code,
        result=response_result,
        ran_at=datetime.now(timezone.utc),
    )


async def main():
    setup_logging()
    schedule_repo = await RedisScheduleRepository.get_repo(config.database_url)
    job_repo = await RedisJobRepository.get_repo(config.database_url)
    broker = await RedisBroker.get_broker(config.broker_url)
    session = ClientSession(timeout=ClientTimeout(total=1))

    while True:
        try:
            await run_jobs(schedule_repo, job_repo, broker, session)
        except KeyboardInterrupt:
            await schedule_repo.shutdown()
            await job_repo.shutdown()
            await broker.shutdown()
            await session.close()


if __name__ == "__main__":
    asyncio.run(main())