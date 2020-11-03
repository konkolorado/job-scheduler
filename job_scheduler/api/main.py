from uuid import UUID

import uvicorn
from fastapi import Depends, FastAPI, HTTPException

from job_scheduler.api.models import Schedule, ScheduleRequest
from job_scheduler.db import RedisRepository, ScheduleRepository
from job_scheduler.services import (
    delete_schedule,
    get_schedule,
    store_schedule,
    update_schedule,
)

app = FastAPI()


async def get_repo() -> ScheduleRepository:
    return await RedisRepository.get_repo()


@app.on_event("shutdown")
async def shutdown_event():
    await RedisRepository.shutdown()


@app.post("/schedule/", response_model=Schedule, status_code=201)
async def create(req: ScheduleRequest, repo: ScheduleRepository = Depends(get_repo)):
    s = Schedule.parse_obj(req.dict())
    result, *_ = await store_schedule(repo, s)
    return result


@app.get("/schedule/{s_id}", response_model=Schedule)
async def get(s_id: UUID, repo: ScheduleRepository = Depends(get_repo)):
    s = await get_schedule(repo, s_id)
    if len(s) == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return s[0]


@app.put("/schedule/{s_id}", response_model=Schedule)
async def update(
    s_id: UUID, req: ScheduleRequest, repo: ScheduleRepository = Depends(get_repo)
):
    s = await update_schedule(repo, {s_id: req.dict(exclude_unset=True)})
    if len(s) == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return s[0]


@app.delete("/schedule/{s_id}", response_model=Schedule)
async def delete(s_id: UUID, repo: ScheduleRepository = Depends(get_repo)):
    s = await delete_schedule(repo, s_id)
    if len(s) == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return s[0]


if __name__ == "__main__":
    uvicorn.run(
        "job_scheduler.api.main:app",
        host="127.0.0.1",
        log_level="debug",
        reload=True,
    )
