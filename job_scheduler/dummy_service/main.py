import asyncio

import structlog
import uvicorn
from fastapi import FastAPI, Request

from job_scheduler.config import config
from job_scheduler.logging import setup_logging

logger = structlog.get_logger("job_scheduler.dummy_endpoint")

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    setup_logging()


@app.post("/")
async def post(request: Request):
    data = await request.json()
    logger.info(f"Received POST with data {data}")
    await asyncio.sleep(config.dummy.sleep)
    return data


@app.get("/")
async def get(request: Request):
    body = await request.body()
    logger.info(f"Received GET with data {str(body)}")
    return body


if __name__ == "__main__":
    from job_scheduler.logging import logging_config

    uvicorn.run(
        "job_scheduler.dummy_service.main:app",
        host=config.dummy.host,
        port=config.dummy.port,
        log_level=config.logging.level,
        log_config=logging_config,
        reload=config.dev_mode,
    )
