import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .consumer import consume_forever
from .routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = asyncio.Event()
    task = asyncio.create_task(consume_forever(stop))
    try:
        yield
    finally:
        stop.set()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="LabLumen notification-service", version="0.1.0", lifespan=lifespan)
app.include_router(health.router)
