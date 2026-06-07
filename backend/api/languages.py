from fastapi import APIRouter
from sqlmodel import select

from ..db.schemas.language import Language
from ..dependencies.db_deps import SessionDep

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("/", response_model=list[Language])
def list_languages(session: SessionDep):
    languages = session.exec(select(Language)).all()
    return languages
