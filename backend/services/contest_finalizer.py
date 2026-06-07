import asyncio
from contextlib import suppress
from datetime import datetime, timezone

from sqlmodel import Session, select, text

from ..db.engine import engine
from ..db.schemas.contests import Contest
from ..utils.general_utils import FINALIZE_AND_INSERTION_QUERY

FINALIZER_INTERVAL_SECONDS = 86400


def finalize_contest_results(session: Session, contest: Contest) -> None:
    session.connection().execute(text(FINALIZE_AND_INSERTION_QUERY), {"contest_id": contest.id})
    contest.is_finalized = True
    session.add(contest)
    session.commit()


def finalize_due_contests_once() -> None:
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        contests = session.exec(
            select(Contest).where(
                Contest.endTime <= now,
                not Contest.is_finalized,
            )
        ).all()

        for contest in contests:
            try:
                if contest.id is None:
                    raise Exception("Contest ID is None for contest %s", contest.name)

                finalize_contest_results(session, contest)
            except Exception:
                print(
                    "Failed to finalize contest %s",
                    contest.id or contest.name,
                )


async def contest_finalizer_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        await asyncio.to_thread(finalize_due_contests_once)

        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(
                stop_event.wait(),
                timeout=FINALIZER_INTERVAL_SECONDS,
            )
