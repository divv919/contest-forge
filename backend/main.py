from fastapi import FastAPI, Body
import os
import httpx
from pydantic import BaseModel
from typing import Annotated
from db.schemas import *
from db.schemas.submission import SubmissionAPI, SubmissionInDB, SubmissionStatusId
from sqlmodel import SQLModel , Session

from db.engine import engine
 
app = FastAPI()

SQLModel.metadata.create_all(engine)



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
            "callback_url": "http://backend-fastapi-starter-1/submission_webhook"
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

@app.put("/submission_webhook")
async def submission_webhook(body: SubmissionAPI):
    # Will add logic to add this in db tomorrow
    print("body from webhook", body)
    return "OK"
