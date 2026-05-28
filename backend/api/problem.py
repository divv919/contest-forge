from fastapi import APIRouter, HTTPException, status
from ..dependencies.db_deps import SessionDep
from sqlmodel import select
from ..dependencies.auth_deps import IsAuthenticatedDep
from ..db.schemas.problem import Problem, ProblemBase, ProblemInfo
from ..db.schemas.language import Language, LanguageCodes
from ..utils.general_utils import get_user_boilerplate_path, get_problem_dir
router = APIRouter(tags=["problem"],  prefix="/problems", dependencies=[IsAuthenticatedDep])

@router.get("/all", response_model=list[ProblemBase])
def all_problems (session : SessionDep):
    db_problems =  session.exec(select(Problem)).all()
    return db_problems

@router.get("/{slug}", response_model=ProblemInfo)
def problem_by_id(slug: str, session : SessionDep):
    problem = session.exec(select(Problem).where(Problem.slug == slug)).first()
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem information not found")
   

    boilerplate_codes: dict[int, str] = {}
    for language_code in LanguageCodes:
        language = session.exec(select(Language).where(Language.name == language_code.value)).first()
        if language is None or language.id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Language not found for {language_code.value}",
            )

        boilerplate_path = get_user_boilerplate_path(slug, language_code.name)
        if boilerplate_path is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Path not found for this problem",
            )
        with boilerplate_path.open("r", encoding="utf-8") as file_handle:
            boilerplate_codes[language.id] = file_handle.read()

    metadata_path = get_problem_dir(slug) / "metadata.md"
    with metadata_path.open("r", encoding="utf-8") as file_handle:
        metadata = file_handle.read()

    return ProblemInfo(**problem.model_dump(), problem_metadata=metadata, boilerplate_codes=boilerplate_codes)
    
    

    
# Todo
# 1. Add logic to send if a problem is attempted or not for better UX