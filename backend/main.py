from fastapi import FastAPI, Request
from enum import Enum
from pydantic import BaseModel 

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



@app.get("/health")
async def health_check():
    print("ok health")
    return "OK 13"

@app.put("/submission_webhook")
async def submission_webhook(body: SubmissionResponse):
    try:
        print("body from webhook" ,body )

    except Exception as e:
        print("error during req", e)
    return "OK"
