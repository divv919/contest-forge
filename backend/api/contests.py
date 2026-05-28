from fastapi import APIRouter, Body, HTTPException, status
from ..dependencies.db_deps import SessionDep
from ..dependencies.auth_deps import UserDep ,IsAuthenticatedDep
from ..db.schemas.contests import ContestCreateRequest, Contest, ContestProblems, ContestInfoResponse, ContestPoints
from ..db.schemas.submission import ContestSubmissionsResponse
from ..db.schemas.problem import Problem, ContestInfoProblems
from ..utils.general_utils import sluggify, PAGE
from typing import Annotated
from datetime import datetime, timezone , timedelta
from sqlmodel import select, col, and_


router = APIRouter(prefix="/contests", tags=["contests"])


@router.post("/create")
def create_contest(body: Annotated[ContestCreateRequest, Body()], session: SessionDep, user: UserDep):
    if body.problem_ids is None or len(body.problem_ids) <=0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Problem ids array cannot be empty")
    now = datetime.now(tz=timezone.utc)
    if body.startTime <= now or body.endTime <= now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please make sure start time and end time of contest both lie in future")
    if body.endTime <= (body.startTime + timedelta(minutes=30)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please make sure the duration of the contest is atleast 30 minutes")
    if body.endTime <= body.startTime:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End time should be greater than start time")
    already_exists = session.exec(select(Contest).where(Contest.name == body.name)).first()
    if already_exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This contest name is already taken")
    problems = session.exec(select(Problem).where(col(Problem.id).in_(body.problem_ids))).all()
    if len(problems) < len(body.problem_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Problems does not exist for provided ids")
    slug = sluggify(body.name)
    if slug == "":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="This slug generated for this name is invalid")
        
    contest_to_create = Contest(created_by=user.id,name=body.name, startTime=body.startTime, endTime=body.endTime ,slug=slug)

    session.add(contest_to_create)
    session.commit()
    session.refresh(contest_to_create)
    if contest_to_create is None or contest_to_create.id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The contest cannot be created")
    
    contest_problems_add = [ContestProblems(contest_id=contest_to_create.id,problem_id=problem.id) for problem in problems if problem is not None and problem.id is not None] 

    session.add_all(contest_problems_add)
    session.commit()
    
    return {"message" : f"Contest created successfully with name {contest_to_create.name}"}

@router.get("/all_upcoming_contests", dependencies=[IsAuthenticatedDep], response_model=list[Contest])
def get_all_upcoming_contests(session: SessionDep):
    contests = session.exec(select(Contest).where(Contest.startTime >= datetime.now())).all()
    return contests

@router.get("/ongoing_contests", dependencies=[IsAuthenticatedDep], response_model=list[Contest])
def  get_ongoing_contests(session: SessionDep):
    contests = session.exec(select(Contest).where(and_(Contest.endTime >= datetime.now(), Contest.startTime <= datetime.now()))).all()
    return contests

@router.get("/past_contests", dependencies=[IsAuthenticatedDep], response_model=list[Contest])
def get_past_contests(session: SessionDep):
    contests = session.exec(select(Contest).where(Contest.endTime < datetime.now())).all()
    return contests

@router.post("/contest_info", dependencies=[IsAuthenticatedDep], response_model=ContestInfoResponse)
def get_contest_info_by_id(session: SessionDep,  contest_slug : Annotated[str, Body(embed=True)]):
    contest = session.exec(select(Contest).where(Contest.slug == contest_slug)).first()
    if contest is None or contest.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contest found for this id")
    contest_problems = session.exec(select(ContestProblems).where(ContestProblems.contest_id == contest.id)).all()
    if len(contest_problems) <= 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No problems found for this contest")
    return ContestInfoResponse(**contest.model_dump(),problems=[ContestInfoProblems(**contest_problem.model_dump(), **contest_problem.problem.model_dump()) for contest_problem in contest_problems ])
        

@router.post("/contest_submissions", response_model=list[ContestSubmissionsResponse])
def get_contest_submissions(user: UserDep, slug: Annotated[str, Body(embed=True)], session: SessionDep):
    # Do not use ContestSubmissions as a source of truth as it only contains values that are accepted
    # Currently ongoing contest is showign all data , only show truncated data 
    contest = session.exec(select(Contest).where(Contest.slug == slug)).first()
    if contest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contest found for this slug")
    is_contest_ended = False
    if contest.endTime <= datetime.now(tz=timezone.utc):
        is_contest_ended = True
    if is_contest_ended:
        user_submissions = [submission for submission in contest.contests_submissions_link if submission.submission.user_id == user.id]
        submissions_info = [ContestSubmissionsResponse(id=submission.submission.id, points=submission.points, status=submission.submission.status, created_at=submission.submission.created_at) for submission in user_submissions if submission is not None and submission.submission is not None and submission.submission.id is not None]
        return submissions_info
    else:
        user_submissions = [submission for submission in contest.contests_submissions_link if submission.submission.user_id == user.id]

        return [ContestSubmissionsResponse(**submission.submission.model_dump(), points=submission.points) for submission in user_submissions if submission is not None and submission.submission is not None and submission.submission.id is not None] 


@router.get("/contest_ranking/{slug}", response_model=list[ContestPoints])
def get_contest_ranking(slug: str, session: SessionDep, page: int = 1):
    contest = session.exec(select(Contest).where(Contest.slug == slug)).first()
    if contest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contest found for this slug")
    if contest.endTime > datetime.now(tz=timezone.utc):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contest ranking will be available once the contest is ended")
    if contest.is_finalized == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contest ranking is being finalized and will be available soon")
        
    ranking = session.exec(select(ContestPoints).where(ContestPoints.contest_id == contest.id).order_by(col(ContestPoints.rank)).offset((page - 1) * PAGE["MEDIUM"]).limit(PAGE["MEDIUM"])).all()
    if ranking is None or len(ranking) <= 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ranking information found for this contest")
    return ranking



# Todos
# Add a message or status with every successful API
# Add an api to check the name of the contest in the frontend if it exists or not 
# Add a redis cache layer to store the contest rankings 
# rate limit all the APIs especially ones that create something in db
# Add a queue worker system to find the final contest ranking after it is ended for now it is being handled by scheduling
# Add active contest slug during submission