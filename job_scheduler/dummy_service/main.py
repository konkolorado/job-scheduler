import asyncio
import logging

import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/")
async def post(request: Request):
    data = await request.json()
    await asyncio.sleep(1)
    return data


@app.get("/")
async def get(request: Request):
    return await request.body()


if __name__ == "__main__":
    uvicorn.run(
        "job_scheduler.dummy_service.main:app",
        host="127.0.0.1",
        port=8080,
        log_level="debug",
        reload=False,
    )
