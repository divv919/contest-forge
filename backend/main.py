from fastapi import FastAPI, Body
import asyncio
import os
import httpx
from pydantic import BaseModel
from typing import Annotated
from .db.schemas import *
from .api.auth import router as auth_router
from .api.problem import router as problem_router
from .api.submission import router as submission_router
from .api.contests import router as contests_router
from .services.contest_finalizer import contest_finalizer_loop
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = asyncio.Event()
    scheduler_task = asyncio.create_task(contest_finalizer_loop(stop_event))
    yield
    stop_event.set()
    await scheduler_task

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(problem_router)
app.include_router(submission_router)
app.include_router(contests_router)

class SolutionRequest(BaseModel):
    source_code : str
    problem_slug: str
    language_id : int | None = 63

@app.post("/submit")
async def submit_solution(solution: Annotated[SolutionRequest, Body()]):
    problem_slug = solution.problem_slug
    source_code = solution.source_code

    input_dir = os.getcwd() + "/problem-statements/" + problem_slug + "/test.txt"
    output_dir = os.getcwd() + "/problem-statements/"+ problem_slug + "/output.txt"
    boilerplate_dir = os.getcwd() + "/problem-statements/"+ problem_slug + "/boilerplate/js/full-js-boilerplate.js"
    with open(boilerplate_dir, "r", encoding="utf-8") as f:
        full_source_code = f.read().replace("<USER_CODE>", source_code)
    with open(input_dir, "r", encoding="utf-8") as f:
        test_input_lines = f.read().splitlines()[1:]
    with open(output_dir, "r", encoding="utf-8") as f:
        output = f.read().splitlines()

    test_cases = [test_input_lines[index:index + 2] for index in range(0, len(test_input_lines), 2)]

    data_body = {
        "submissions": [{
            "source_code": full_source_code,
            "language_id": 52,
            "stdin": "\n".join(test_case),
            "expected_output": expected_output,
            "callback_url": "http://fastapi-starter:80/submission/submission_webhook"
        } for test_case, expected_output in zip(test_cases, output)]

    }

    async with httpx.AsyncClient() as client:
        res = await  client.post("http://server:2358/submissions/batch?base64_encoded=false",json=data_body )
    response = res.json()
    # response["status"] = SubmissionStatusId(response["status"]["id"])
    # submission = SubmissionInDB(**response,source_code=full_source_code)
    # with Session(engine) as session:
    #     session.add(submission)
    #     session.flush()
    #     print("submission.id is " ,submission.id)
    #     session.commit()

    return response

@app.get("/health")
async def health_check():
    print("ok health")
    return "OK 13"

