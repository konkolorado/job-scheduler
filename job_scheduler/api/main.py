from uuid import UUID

import uvicorn
from fastapi import Depends, FastAPI, Response

from job_scheduler.api.models import Schedule, ScheduleRequest
from job_scheduler.db.base import ScheduleRepository
from job_scheduler.db.redis import RedisRepository

app = FastAPI()


# TODO test the rest of these methods
# TODO investigate async redis
def get_repo() -> ScheduleRepository:
    return RedisRepository.get_repo()


@app.post("/schedule/", response_model=Schedule, status_code=201)
async def create_schedule(
    req: ScheduleRequest, repo: ScheduleRepository = Depends(get_repo)
):
    s = Schedule(**req.dict())
    repo.add(s.id, s.dict())
    return s


@app.get("/schedule/{s_id}", response_model=Schedule)
async def get_schedule(s_id: UUID, repo: ScheduleRepository = Depends(get_repo)):
    s = repo.get(s_id)
    return Schedule(**s)


@app.put("/schedule/{s_id}", response_model=Schedule)
async def update_schedule(
    s_id: UUID,
    req: ScheduleRequest,
    repo: ScheduleRepository = Depends(get_repo),
):
    s = Schedule(**req.dict(), id=s_id)
    repo.update(s_id, s.dict())
    return repo.get(s_id)


@app.delete("/schedule/{s_id}", response_model=Schedule)
async def delete_schedule(s_id: UUID, repo: ScheduleRepository = Depends(get_repo)):
    s = repo.get(s_id)
    repo.delete(s_id)
    return s


if __name__ == "__main__":
    uvicorn.run(
        "job_scheduler.api.main:app",
        host="127.0.0.1",
        log_level="debug",
        reload=True,
    )
