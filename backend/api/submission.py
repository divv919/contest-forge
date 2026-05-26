from fastapi import APIRouter, HTTPException, status
from ..dependencies.auth_deps import IsAuthenticatedDep, UserDep
from ..dependencies.db_deps import SessionDep
from ..db.schemas.submission import SubmissionRequest, Judge0RequestObject, Judge0SubmitResponseObject, Submission, SubmissionStatusId, TestCase, SubmissionResponse
from ..db.schemas.language import Language
from ..db.schemas.problem import Problem
from sqlmodel import select
from ..utils.constants import ROOT
import httpx
from ..utils.exceptions import invalid_creds_exc


router = APIRouter(prefix="/submission", tags=["submissions"], dependencies=[IsAuthenticatedDep])

@router.post("/submit", response_model=SubmissionResponse)
def add_submission(user: UserDep, session: SessionDep, submission: SubmissionRequest):
    
    user_id = user.id
    if user_id is None:
        raise invalid_creds_exc
    language = session.exec(select(Language).where(Language.id == submission.language_id)).first()
    if language is None or language.judge0id is None or language.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The language id provided does not belong to any language")
    problem = session.exec(select(Problem).where(Problem.id == submission.problem_id)).first()
    if problem is None or problem.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The problem id provided does not belong to any problem")

    if submission.source_code.strip() == "":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Submission source code should contain more characters")
    

    problem_path = ROOT / "problem-statements" / problem.slug
    output_path = problem_path / "output.txt"
    test_cases_path = problem_path / "test.txt"

    with output_path.open() as f:
        expected_output = f.read().rstrip().splitlines()
    
    with test_cases_path.open() as f:
        test_cases = f.read().rstrip().splitlines()

    total_test_cases = int(test_cases[0])
    only_test_cases = test_cases[1:]
    if total_test_cases <= 0 or len(only_test_cases) % total_test_cases != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid test case file format")

    num_cases_per_submission = len(only_test_cases) // total_test_cases

    submission_add_in_db = Submission(source_code=submission.source_code, problem_id=problem.id,language_id=language.id,user_id=user_id, status=SubmissionStatusId.IN_QUEUE, total_testcases=total_test_cases, total_passed_cases=0)
    session.add(submission_add_in_db)
    session.commit()
    session.refresh(submission_add_in_db)

    if submission_add_in_db is None or submission_add_in_db.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Submission is invalid because of internal server error")

    submissions = [Judge0RequestObject(callback_url="http://fastapi-start:80/submission_webhook",expected_output=expected_output[idx], language_id=language.judge0id, source_code=submission.source_code, stdin="\n".join(only_test_cases[idx * num_cases_per_submission : (idx + 1) * num_cases_per_submission])).model_dump()
                for idx in range(total_test_cases)]
    
    with httpx.Client() as client:
        res = client.post("http://server:2358/submissions/batch?base64_encoded=false", json={"submissions": submissions})
    raw = res.json()
    response = [Judge0SubmitResponseObject.model_validate(item) for item in raw]
    test_cases_add_in_db = [TestCase(token=obj.token,status=SubmissionStatusId.IN_QUEUE,submission_id=submission_add_in_db.id ) for obj in response]

    session.add_all(test_cases_add_in_db)
    session.commit()
    return SubmissionResponse(message="Your code has been submitted successfully", submission_id=submission_add_in_db.id)
            

# Todo 
# Add a transaction in the API so that even if error occurs it is rolledback