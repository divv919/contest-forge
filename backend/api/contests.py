from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status
from sqlmodel import and_, col, select

from ..db.schemas.contests import (
    AllContestsResponse,
    Contest,
    ContestCreateRequest,
    ContestCreateResponse,
    ContestInfoResponse,
    ContestPoints,
    ContestProblems,
    ContestRankingsResponse,
)
from ..db.schemas.problem import ContestInfoProblems, Problem
from ..db.schemas.submission import ContestSubmissionsResponse, SubmissionStatusId
from ..db.schemas.user import User
from ..dependencies.auth_deps import UserDep
from ..dependencies.db_deps import SessionDep
from ..utils.general_utils import PAGE, sluggify

router = APIRouter(prefix="/contests", tags=["contests"])


def get_users_map(session: SessionDep, user_ids: set[int]) -> dict[int, str]:
    users = session.exec(select(User).where(col(User.id).in_(user_ids))).all()
    users_map = {user.id: user.username for user in users if user.id is not None}
    return users_map


@router.post("/create", response_model=ContestCreateResponse)
def create_contest(
    body: Annotated[ContestCreateRequest, Body()], session: SessionDep, user: UserDep
):
    if body.problem_ids is None or len(body.problem_ids) <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Problem ids array cannot be empty"
        )
    now = datetime.now(tz=timezone.utc)
    if body.startTime <= now or body.endTime <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please make sure start time and end time of contest both lie in future",
        )
    if body.endTime <= (body.startTime + timedelta(minutes=30)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please make sure the duration of the contest is atleast 30 minutes",
        )
    if body.endTime <= body.startTime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time should be greater than start time",
        )
    already_exists = session.exec(select(Contest).where(Contest.name == body.name)).first()
    if already_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This contest name is already taken"
        )
    problems = session.exec(select(Problem).where(col(Problem.id).in_(body.problem_ids))).all()
    if len(problems) < len(body.problem_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Problems does not exist for provided ids",
        )
    slug = sluggify(body.name)
    if slug == "":
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="This slug generated for this name is invalid",
        )

    contest_to_create = Contest(
        created_by=user.id,
        name=body.name,
        startTime=body.startTime,
        endTime=body.endTime,
        slug=slug,
    )

    session.add(contest_to_create)
    session.commit()
    session.refresh(contest_to_create)
    if contest_to_create is None or contest_to_create.id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The contest cannot be created"
        )

    contest_problems_add = [
        ContestProblems(contest_id=contest_to_create.id, problem_id=problem.id)
        for problem in problems
        if problem is not None and problem.id is not None
    ]

    session.add_all(contest_problems_add)
    session.commit()

    return ContestCreateResponse(
        id=contest_to_create.id,
        name=contest_to_create.name,
        slug=contest_to_create.slug,
        message=f"Contest created successfully with name {contest_to_create.name}",
    )


@router.get("/all_upcoming_contests", response_model=list[AllContestsResponse])
def get_all_upcoming_contests(session: SessionDep):
    contests = session.exec(select(Contest).where(Contest.startTime >= datetime.now())).all()
    contest_created_by_ids = {
        contest.created_by for contest in contests if contest.created_by is not None
    }
    users_map = get_users_map(session, contest_created_by_ids)
    return [
        AllContestsResponse(
            **{**contest.model_dump(), "created_by": users_map.get(contest.created_by)}
        )
        for contest in contests
    ]


@router.get("/ongoing_contests", response_model=list[AllContestsResponse])
def get_ongoing_contests(session: SessionDep):
    contests = session.exec(
        select(Contest).where(
            and_(Contest.endTime >= datetime.now(), Contest.startTime <= datetime.now())
        )
    ).all()
    contest_created_by_ids = {
        contest.created_by for contest in contests if contest.created_by is not None
    }
    users_map = get_users_map(session, contest_created_by_ids)
    return [
        AllContestsResponse(
            **{**contest.model_dump(), "created_by": users_map.get(contest.created_by)}
        )
        for contest in contests
    ]


@router.get("/past_contests", response_model=list[AllContestsResponse])
def get_past_contests(session: SessionDep):
    contests = session.exec(select(Contest).where(Contest.endTime < datetime.now())).all()
    contest_created_by_ids = {
        contest.created_by for contest in contests if contest.created_by is not None
    }
    users_map = get_users_map(session, contest_created_by_ids)
    return [
        AllContestsResponse(
            **{**contest.model_dump(), "created_by": users_map.get(contest.created_by)}
        )
        for contest in contests
    ]


@router.post("/contest_info", response_model=ContestInfoResponse)
def get_contest_info_by_id(
    user: UserDep, session: SessionDep, contest_slug: Annotated[str, Body(embed=True)]
):
    contest = session.exec(select(Contest).where(Contest.slug == contest_slug)).first()
    if contest is None or contest.id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No contest found for this id"
        )
    contest_problems = session.exec(
        select(ContestProblems).where(ContestProblems.contest_id == contest.id)
    ).all()
    if len(contest_problems) <= 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No problems found for this contest"
        )
    problem_to_status_map = {}
    for contest_problem in contest_problems:
        user_submissions = [
            submission
            for submission in contest_problem.problem.submissions
            if submission.user_id == user.id and submission.active_contest_id == contest.id
        ]
        if len(user_submissions) <= 0:
            problem_to_status_map[contest_problem.problem.id] = "NOT_ATTEMPTED"
        elif any(submission.status == SubmissionStatusId.AC for submission in user_submissions):
            problem_to_status_map[contest_problem.problem.id] = "ACCEPTED"
        else:
            problem_to_status_map[contest_problem.problem.id] = "REJECTED"

    return ContestInfoResponse(
        **contest.model_dump(),
        problems=[
            ContestInfoProblems(
                **contest_problem.model_dump(),
                **contest_problem.problem.model_dump(),
                attempted=problem_to_status_map.get(contest_problem.problem.id, "NOT_ATTEMPTED"),
            )
            for contest_problem in contest_problems
        ],
    )


@router.post("/contest_submissions", response_model=list[ContestSubmissionsResponse])
def get_contest_submissions(
    user: UserDep, slug: Annotated[str, Body(embed=True)], session: SessionDep
):

    contest = session.exec(select(Contest).where(Contest.slug == slug)).first()
    if contest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No contest found for this slug"
        )
    is_contest_ended = False
    if contest.endTime <= datetime.now(tz=timezone.utc):
        is_contest_ended = True

    user_submissions = [
        submission
        for submission in contest.contests_submissions_link
        if submission.submission.user_id == user.id
    ]

    if not is_contest_ended:
        return [
            ContestSubmissionsResponse(
                id=submission.submission.id,
                points=submission.points,
                status=submission.submission.status,
                created_at=submission.submission.created_at,
                problem_id=submission.submission.problem_id,
                active_contest_id=submission.submission.active_contest_id,
                language_id=submission.submission.language_id,
            )
            for submission in user_submissions
            if submission is not None
            and submission.submission.id is not None
            and submission.submission.active_contest_id is not None
        ]

    else:
        return [
            ContestSubmissionsResponse(
                **submission.submission.model_dump(), points=submission.points
            )
            for submission in user_submissions
            if submission is not None
            and submission.submission is not None
            and submission.submission.id is not None
        ]


@router.get("/contest_ranking/{slug}", response_model=list[ContestRankingsResponse])
def get_contest_ranking(slug: str, session: SessionDep, page: int = 1):
    contest = session.exec(select(Contest).where(Contest.slug == slug)).first()
    if contest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No contest found for this slug"
        )
    if contest.endTime > datetime.now(tz=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contest ranking will be available once the contest is ended",
        )
    if not contest.is_finalized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contest ranking is being finalized and will be available soon",
        )

    ranking = session.exec(
        select(ContestPoints)
        .where(ContestPoints.contest_id == contest.id)
        .order_by(col(ContestPoints.rank))
        .offset((page - 1) * PAGE["MEDIUM"])
        .limit(PAGE["MEDIUM"])
    ).all()
    if ranking is None or len(ranking) <= 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No ranking information found for this contest",
        )
    return [
        ContestRankingsResponse(
            user_id=rank.user_id,
            username=rank.user.username,
            total_points=rank.total_points,
            rank=rank.rank,
            contest_id=rank.contest_id,
        )
        for rank in ranking
    ]


# Todos
# Add a message or status with every successful API
# Add an api to check the name of the contest in the frontend if it exists or not
# Add a redis cache layer to store the contest rankings
# rate limit all the APIs especially ones that create something in db
# Add a queue worker system to find the final contest ranking after it is ended for now it is being
# handled by scheduling
# Only allow fixed contest durations of start and end time
# Add max and min problem number for a contest
# Make sure the get user map can be handled by a redis cache layer or some other in memory so that
# we dont have to touch db everytime we need users
# Pagination on past contests
