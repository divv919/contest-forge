from fastapi import APIRouter, HTTPException, status, Depends, Body
from typing import Annotated
from ..dependencies.auth_deps import IsAuthenticatedDep, UserDep
from ..dependencies.db_deps import SessionDep
from ..db.schemas.submission import SubmissionRequest, SubmissionsPaginatedResponse, Judge0RequestObject, Judge0SubmitResponseObject, SubmissionStatusResponse, SubmissionStatusBase, Submission, SubmissionStatusId, TestCase, SubmissionResponse, SubmissionsPaginatedRequest
from ..db.schemas.language import Language , LanguageCodes
from ..db.schemas.problem import Problem
from ..db.schemas.contests import ContestSubmission
from ..db.schemas import Contest
from sqlmodel import select
from ..utils.general_utils import get_problem_dir ,get_full_boilerplate_path ,PAGE, get_points_from_submission_info
import httpx
from ..utils.exceptions import invalid_creds_exc
from ..db.schemas.submission import SubmissionAPI
from datetime import datetime, timezone


router = APIRouter(prefix="/submission", tags=["submissions"])

@router.post("/submit", response_model=SubmissionResponse, dependencies=[IsAuthenticatedDep])
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
    
    if submission.active_contest_id is not None:
        contest = session.exec(select(Contest).where(Contest.id == submission.active_contest_id)).first()
        if contest is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contest is not found")
        now = datetime.now(tz=timezone.utc)
        is_contest_valid = contest.startTime <= now <= contest.endTime
        if not is_contest_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contest is not active")            
        contest_problem_link = next(
            (link for link in contest.contests_problems_link if link.problem_id == problem.id),
            None,
        )
        if contest_problem_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The problem is not part of this contest")
        contest_problem_link.solve_count += 1
        session.add(contest_problem_link)
        
    problem_path = get_problem_dir(problem.slug)
    output_path = problem_path / "output.txt"
    test_cases_path = problem_path / "test.txt"
    boilerplate_path = get_full_boilerplate_path(problem.slug,LanguageCodes(language.name).name)
    if boilerplate_path is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Path not found for this submission problem",
            )
    with boilerplate_path.open() as f:
        full_code =  f.read().replace("<USER_CODE>", submission.source_code)

    with output_path.open() as f:
        expected_output = f.read().rstrip().splitlines()
    
    with test_cases_path.open() as f:
        test_cases = f.read().rstrip().splitlines()

    total_test_cases = int(test_cases[0])
    only_test_cases = test_cases[1:]
    if total_test_cases <= 0 or len(only_test_cases) % total_test_cases != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid test case file format")

    num_cases_per_submission = len(only_test_cases) // total_test_cases

    submission_add_in_db = Submission(source_code=submission.source_code, problem_id=problem.id,language_id=language.id,user_id=user_id, status=SubmissionStatusId.IN_QUEUE, total_testcases=total_test_cases, total_passed_cases=0, active_contest_id=submission.active_contest_id)

    session.add(submission_add_in_db)
    session.commit()
    session.refresh(submission_add_in_db)

    if submission_add_in_db is None or submission_add_in_db.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Submission is invalid because of internal server error")

    submissions = [Judge0RequestObject(callback_url="http://fastapi-starter:80/submission/submission_webhook",expected_output=expected_output[idx], language_id=language.judge0id, source_code=full_code, stdin="\n".join(only_test_cases[idx * num_cases_per_submission : (idx + 1) * num_cases_per_submission])).model_dump()
                for idx in range(total_test_cases)]
    
    with httpx.Client() as client:
        res = client.post("http://server:2358/submissions/batch?base64_encoded=false", json={"submissions": submissions})
    raw = res.json()
    response = [Judge0SubmitResponseObject.model_validate(item) for item in raw]
    test_cases_add_in_db = [TestCase(token=obj.token,status=SubmissionStatusId.IN_QUEUE,submission_id=submission_add_in_db.id, expected_output=expected_output[idx], stdin="\n".join(only_test_cases[idx * num_cases_per_submission : (idx + 1) * num_cases_per_submission])) for idx, obj in enumerate(response)]

    session.add_all(test_cases_add_in_db)
    session.commit()
    return SubmissionResponse(message="Your code has been submitted successfully", submission_id=submission_add_in_db.id, total_test_cases=total_test_cases if submission.active_contest_id is None else 0)
            


@router.put("/submission_webhook")
def submission_webhook(body: SubmissionAPI, session: SessionDep):
    testcase_to_change = session.exec(select(TestCase).where(TestCase.token == body.token)).first()
    if testcase_to_change is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    
    testcase_to_change.sqlmodel_update(
        body.model_dump(exclude_unset=True)
    )
    testcase_to_change.status = SubmissionStatusId(body.status.id if body.status.id is not None else 1)

    session.add(testcase_to_change)
    session.commit()
    yield "OK"
    submission = session.exec(select(Submission).where(Submission.id == testcase_to_change.submission_id)).first()
    if submission is None or submission.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    error_free_statuses = [SubmissionStatusId.AC, SubmissionStatusId.IN_QUEUE, SubmissionStatusId.PROCESSING] 
    if submission.status not in error_free_statuses:
        return
    
    if testcase_to_change.status == SubmissionStatusId.WA:
        submission.status = SubmissionStatusId.WA
        submission.total_time = str(float(submission.total_time or 0) + float(body.time or "0"))
        submission.max_memory = max(submission.max_memory or 0, body.memory or 0)
        if submission.active_contest_id is not None and submission.contests_submissions_link is not None:
                contest_submission = ContestSubmission(submission_id=submission.id,contest_id=submission.active_contest_id,problem_id=submission.problem_id, points=0,  user_id=submission.user_id)
                session.add(contest_submission)
                session.commit()

    elif testcase_to_change.status == SubmissionStatusId.CE:
        if submission.status != SubmissionStatusId.WA:
            submission.status = SubmissionStatusId.CE
        
        submission.total_time = str(float(submission.total_time or 0) + float(body.time or "0"))
        submission.max_memory = max(submission.max_memory or 0, body.memory or 0)
        if submission.active_contest_id is not None and submission.contests_submissions_link is not None:
                contest_submission = ContestSubmission(submission_id=submission.id,contest_id=submission.active_contest_id,problem_id=submission.problem_id, points=0,  user_id=submission.user_id)
                session.add(contest_submission)
                session.commit()

    elif testcase_to_change.status == SubmissionStatusId.AC:
        submission.total_passed_cases += 1
        submission.total_time = str(float(submission.total_time or 0) + float(body.time or "0"))
        submission.max_memory = max(submission.max_memory or 0, body.memory or 0)
        if submission.total_passed_cases == submission.total_testcases:
            submission.status = SubmissionStatusId.AC
            if submission.active_contest_id is not None and submission.contests_submissions_link is not None:
                points_awarded = get_points_from_submission_info(submission.active_contest.startTime, submission.active_contest.endTime, submission.problem.difficulty,submission.created_at)
                contest_submission = ContestSubmission(submission_id=submission.id,contest_id=submission.active_contest_id,problem_id=submission.problem_id, points=points_awarded, user_id=submission.user_id)
                session.add(contest_submission)
                session.commit()

    else:
        if submission.status not in (SubmissionStatusId.WA, SubmissionStatusId.CE):
            submission.status = testcase_to_change.status
        
        submission.total_time = str(float(submission.total_time or 0) + float(body.time or "0"))
        submission.max_memory = max(submission.max_memory or 0, body.memory or 0)
        if submission.active_contest_id is not None and submission.contests_submissions_link is not None:
                contest_submission = ContestSubmission(submission_id=submission.id,contest_id=submission.active_contest_id,problem_id=submission.problem_id, points=0, user_id=submission.user_id)
                session.add(contest_submission)
                session.commit()
    session.add(submission)
    session.commit()



@router.post("/submission_status")
def get_submission_status(user: UserDep, session: SessionDep, submission_id: Annotated[int, Body(embed=True)]):
    submission_test_cases = session.exec(select(TestCase).where(TestCase.submission_id == submission_id)).all()
    submission = session.exec(select(Submission).where(Submission.id == submission_id).where(Submission.user_id == user.id)).first()

    if submission_test_cases is None or len(submission_test_cases) <= 0 or submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The submission cannot be found")
    if any(
        test_case.status in (SubmissionStatusId.IN_QUEUE, SubmissionStatusId.PROCESSING)
        for test_case in submission_test_cases
    ):
        return SubmissionStatusResponse(state="PENDING")

    is_wa = False
    is_ce = False
    is_other_error = False

    max_memory = 0
    total_time = 0

    passed_count = 0

    for test_case in submission_test_cases:
        if not is_wa and test_case.status == SubmissionStatusId.WA:
            is_wa = test_case
        elif not is_ce and test_case.status == SubmissionStatusId.CE:
            is_ce = test_case
        elif test_case.status == SubmissionStatusId.AC:
            passed_count += 1
            max_memory = max(max_memory, test_case.memory or 0)
            total_time += float(test_case.time or "0")
        elif not is_other_error:  
            is_other_error = test_case
        
    if is_wa:
        if submission.active_contest_id is not None:
            return SubmissionStatusResponse(state="FINISH", status=SubmissionStatusId.WA, message="Only truncated info will be shown for active contest",is_truncated_for_contest=True)
        return SubmissionStatusResponse(state="FINISH",status=SubmissionStatusId.WA,max_memory=is_wa.memory, compile_output=is_wa.compile_output,total_time=str(float(is_wa.time or "0")) ,stderr=is_wa.stderr,stdout=is_wa.stdout,total_passed_cases=passed_count,total_testcases=len(submission_test_cases))
    if is_ce:
        if submission.active_contest_id is not None:
            return SubmissionStatusResponse(state="FINISH", status=SubmissionStatusId.CE, message="Only truncated info will be shown for active contest",is_truncated_for_contest=True)
        return SubmissionStatusResponse(state="FINISH",status=SubmissionStatusId.CE,compile_output=is_ce.compile_output, total_passed_cases=passed_count,total_testcases=len(submission_test_cases))
    if is_other_error:
        if submission.active_contest_id is not None:
            return SubmissionStatusResponse(state="FINISH", status=is_other_error.status, message="Only truncated info will be shown for active contest",is_truncated_for_contest=True)
        return SubmissionStatusResponse(state="FINISH",status=is_other_error.status,stderr=is_other_error.stderr,stdout=is_other_error.stdout, total_passed_cases=passed_count,total_testcases=len(submission_test_cases))
    if submission.active_contest_id is not None:
        return SubmissionStatusResponse(state="FINISH", status=SubmissionStatusId.AC, message="Only truncated info will be shown for active contest", is_truncated_for_contest=True)
        
    return SubmissionStatusResponse(state="FINISH",status=SubmissionStatusId.AC,total_passed_cases=passed_count,total_testcases=len(submission_test_cases), max_memory=max_memory, total_time=str(total_time))

@router.post("/problem_submissions", response_model=list[SubmissionsPaginatedResponse])
def get_problem_submissions(session: SessionDep, user: UserDep, body: Annotated[SubmissionsPaginatedRequest,Body()]):
    submissions = session.exec(select(Submission).where(Submission.problem_id == body.problem_id).where(Submission.user_id == user.id).offset(PAGE["MEDIUM"] * (body.current_page -1)).limit(PAGE["MEDIUM"])).all()
    if submissions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No submission found for this problem")
    return [SubmissionsPaginatedResponse(**submission.model_dump(), language=submission.language.name) for submission in submissions if submission.active_contest_id is None or submission.active_contest.endTime < datetime.now(tz=timezone.utc)]

@router.post("/submission_info")
def get_submission_info(user: UserDep, session : SessionDep, submission_id : Annotated[int, Body(embed=True)]):
    submission = session.exec(select(Submission).where(Submission.user_id == user.id).where(Submission.id == submission_id)).first()
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No info found for submission")

    if submission.active_contest_id is not None:
        now = datetime.now(tz=timezone.utc)
        if submission.active_contest.startTime < now < submission.active_contest.endTime:
            return SubmissionStatusBase(status=submission.status, message="Only truncated info will be shown for active contest", is_truncated_for_contest=True) 
         
    if submission.status == SubmissionStatusId.WA:
        test_case = session.exec(
            select(TestCase).where(TestCase.submission_id == submission_id).where(TestCase.status == SubmissionStatusId.WA)
        ).first()
        if test_case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No test cases found for submission")
        return SubmissionStatusBase(
            total_testcases=submission.total_testcases,
            total_passed_cases=submission.total_passed_cases,
            max_memory=test_case.memory,
            total_time=str(float(test_case.time or "0")),
            stderr=test_case.stderr,
            stdout=test_case.stdout,
            compile_output=test_case.compile_output,
            status=SubmissionStatusId.WA,
        )

    if submission.status == SubmissionStatusId.CE:
        test_case = session.exec(
            select(TestCase).where(TestCase.submission_id == submission_id).where(TestCase.status == SubmissionStatusId.CE)
        ).first()
        if test_case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No test cases found for submission")
        return SubmissionStatusBase(
            compile_output=test_case.compile_output,
            total_passed_cases=submission.total_passed_cases,
            total_testcases=submission.total_testcases,
            status=SubmissionStatusId.CE,
        )

    if submission.status == SubmissionStatusId.TLE:
        test_case = session.exec(
            select(TestCase).where(TestCase.submission_id == submission_id).where(TestCase.status == SubmissionStatusId.TLE)
        ).first()
        if test_case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No test cases found for submission")
        return SubmissionStatusBase(
            stderr=test_case.stderr,
            stdout=test_case.stdout,
            total_passed_cases=submission.total_passed_cases,
            total_testcases=submission.total_testcases,
            status=SubmissionStatusId.TLE,
        )

    if submission.status == SubmissionStatusId.AC:
        return SubmissionStatusBase(
            status=SubmissionStatusId.AC,
            total_passed_cases=submission.total_passed_cases,
            total_testcases=submission.total_testcases,
            max_memory=submission.max_memory,
            total_time=str(submission.total_time) if submission.total_time is not None else None,
        )

    test_case = session.exec(
        select(TestCase).where(TestCase.submission_id == submission_id).where(TestCase.status == submission.status)
    ).first()
    if test_case:
        return SubmissionStatusBase(
            stderr=test_case.stderr,
            stdout=test_case.stdout,
            total_passed_cases=submission.total_passed_cases,
            total_testcases=submission.total_testcases,
            status=submission.status,
        )

    return SubmissionStatusBase(
        status=submission.status,
        total_passed_cases=submission.total_passed_cases,
        total_testcases=submission.total_testcases,
        max_memory=submission.max_memory,
        total_time=str(submission.total_time) if submission.total_time is not None else None,
    )


# Todo 
# Add a transaction in the API so that even if error occurs it is rolledback
# Learn how u can make the webhook authenticable
# Define max memory and time limit and only accept if they lie in the same bracket
# add a header type auth for polling api to make sure user cant misuse the status API
# in case of retries of webhook the total count can give wrong value 
# Use relationships to get data instead of quering using foreign key
# Add lock on submission webhook so that every test case for a submission is processed one at a time