from fastapi import FastAPI, Body
import os
import httpx
from enum import Enum
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()


class SubmissionStatusId(int, Enum):
    IN_QUEUE = 1
    PROCESSING = 2
    AC = 3
    WA = 4
    TLE = 5
    CE = 6
    RTE_SIGSEGV = 7
    RTE_SIGXFSZ = 8
    RTE_SIGFPE = 9
    RTE_SIGABRT = 10
    NZEC = 11
    RTE_OTHER = 12
    INTERNAL_ERROR = 13
    EXEC_FORMAT_ERROR = 14


class SubmissionStatus(BaseModel):
    id : SubmissionStatusId
    description: str | None = None

class SubmissionResponse(BaseModel):
    stdout : str | None = None
    time: str 
    memory : int
    stderr: str | None = None
    token: str
    compile_output: str | None = None
    message : str
    status : SubmissionStatus


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
            "language_id": 63,
            "stdin": "\n".join(test_case),
            "expected_output": expected_output,
            "callback_url": "http://fastapi-start:80/submission_webhook"
        } for test_case, expected_output in zip(test_cases, output)]

    }

    async with httpx.AsyncClient() as client:
        res = await  client.post("http://server:2358/submissions/batch",json=data_body )
    response = res.json()
    return response

@app.get("/health")
async def health_check():
    print("ok health")
    return "OK 13"

@app.put("/submission_webhook")
async def submission_webhook(body: SubmissionResponse):
    print("body from webhook", body)
    return "OK"
