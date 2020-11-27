import logging
from typing import Sequence
from uuid import UUID

import uvicorn
from fastapi import Depends, FastAPI, HTTPException

from job_scheduler.api.models import Job, Schedule, ScheduleRequest
from job_scheduler.db import (
    JobRepository,
    RedisJobRepository,
    RedisScheduleRepository,
    ScheduleRepository,
)
from job_scheduler.logging import setup_logging
from job_scheduler.services import (
    delete_schedule,
    get_jobs,
    get_schedule,
    get_schedule_jobs,
    store_schedule,
    update_schedule,
)

logger = logging.getLogger("api")
app = FastAPI()


async def get_schedule_repo() -> ScheduleRepository:
    return await RedisScheduleRepository.get_repo()


async def get_job_repo() -> JobRepository:
    return await RedisJobRepository.get_repo()


@app.on_event("startup")
async def startup_event():
    logging.getLogger("uvicorn").propagate = False
    setup_logging()


@app.on_event("shutdown")
async def shutdown_event():
    await RedisScheduleRepository.shutdown()
    logger.info("Repository shut down.")


@app.post("/schedule/", response_model=Schedule, status_code=201)
async def create(
    req: ScheduleRequest, repo: ScheduleRepository = Depends(get_schedule_repo)
):
    s = Schedule.parse_obj(req.dict())
    result, *_ = await store_schedule(repo, s)
    return result


@app.get("/schedule/{s_id}", response_model=Schedule)
async def get(s_id: UUID, repo: ScheduleRepository = Depends(get_schedule_repo)):
    s = await get_schedule(repo, s_id)
    if len(s) == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return s[0]


@app.put("/schedule/{s_id}", response_model=Schedule)
async def update(
    s_id: UUID,
    req: ScheduleRequest,
    repo: ScheduleRepository = Depends(get_schedule_repo),
):
    s = await update_schedule(repo, {s_id: req.dict(exclude_unset=True)})
    if len(s) == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return s[0]


@app.delete("/schedule/{s_id}", response_model=Schedule)
async def delete(s_id: UUID, repo: ScheduleRepository = Depends(get_schedule_repo)):
    s = await delete_schedule(repo, s_id)
    if len(s) == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return s[0]


@app.get("/schedule/{s_id}/jobs", response_model=Sequence[Job])
async def get_jobs_by_schedule(
    s_id: UUID, j_repo: JobRepository = Depends(get_job_repo)
):
    jobs = await get_schedule_jobs(j_repo, s_id)
    if len(jobs) == 0:
        raise HTTPException(status_code=404, detail="Jobs not found")
    return jobs[s_id]


@app.get("/schedule/{s_id}/jobs/{j_id}", response_model=Job)
async def get_schedule_job(
    s_id: UUID, j_id: UUID, j_repo: JobRepository = Depends(get_job_repo)
):
    jobs = await get_jobs(j_repo, j_id)
    if len(jobs) == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[0]


if __name__ == "__main__":
    uvicorn.run(
        "job_scheduler.api.main:app",
        host="127.0.0.1",
        log_level="debug",
        reload=True,
    )
