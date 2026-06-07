import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .api.auth import router as auth_router
from .api.contests import router as contests_router
from .api.languages import router as languages_router
from .api.problem import router as problem_router
from .api.submission import router as submission_router
from .db import schemas  # noqa: F401
from .services.contest_finalizer import contest_finalizer_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = asyncio.Event()
    scheduler_task = asyncio.create_task(contest_finalizer_loop(stop_event))
    yield
    stop_event.set()
    await scheduler_task


origins = [
    "http://localhost:3000",
    "http://frontend:3000",
]

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(problem_router)
app.include_router(submission_router)
app.include_router(contests_router)
app.include_router(languages_router)


class SolutionRequest(BaseModel):
    source_code: str
    problem_slug: str
    language_id: int | None = 63


@app.get("/health")
async def health_check():
    print("ok health")
    return "OK 13"
