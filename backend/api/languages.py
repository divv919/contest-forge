from fastapi import APIRouter
from ..dependencies.db_deps import SessionDep
from sqlmodel import select
from ..db.schemas.language import Language

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("/", response_model=list[Language])
def list_languages(session: SessionDep):
    languages = session.exec(select(Language)).all()
    return languages
