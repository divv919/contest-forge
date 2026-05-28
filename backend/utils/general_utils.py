from pathlib import Path
from ..db.schemas.problem import Difficulty
from datetime import datetime, timezone
import re
from secrets import token_urlsafe
import unicodedata

ROOT = Path(__file__).resolve().parents[1]


PAGE = {
    "MEDIUM" : 20
}


def get_problem_dir(slug: str):
    return ROOT / "problem-statements" / slug
    

def get_user_boilerplate_path(slug: str, language_code : str):
    base_problem_path = get_problem_dir(slug)
    boilerplate_paths = {
    "cpp": base_problem_path / "boilerplate/cpp/user-cpp-boilerplate.cpp",
    "js": base_problem_path / "boilerplate/js/user-js-boilerplate.js",
    "py": base_problem_path / "boilerplate/py/user-py-boilerplate.py",
    }
    path = boilerplate_paths.get(language_code)
    return path


def get_full_boilerplate_path(slug: str, language_code : str):
    base_problem_path = get_problem_dir(slug)
    boilerplate_paths = {
    "cpp": base_problem_path / "boilerplate/cpp/full-cpp-boilerplate.cpp",
    "js": base_problem_path / "boilerplate/js/full-js-boilerplate.js",
    "py": base_problem_path / "boilerplate/py/full-py-boilerplate.py",
    }
    path = boilerplate_paths.get(language_code)
    return  path


def get_points_from_submission_info(startTime : datetime, endTime: datetime, difficulty: Difficulty, solved_at: datetime | None = None) -> int:
    # Fix the logic to get correct points
    if difficulty == Difficulty.EASE:
        points = 1
    elif difficulty == Difficulty.MEDIUM:
        points = 2
    else:
        points = 3

    solved_at = solved_at or datetime.now(timezone.utc)
    contest_duration = (endTime - startTime).total_seconds()
    if contest_duration <= 0:
        return points

    elapsed_time = (solved_at - startTime).total_seconds()
    normalized_time = max(0.0, min(1.0, elapsed_time / contest_duration))

    if normalized_time < 0.5:
        points += 1

    return points


def sluggify(to_slug_from : str):
    if not to_slug_from:
        return ""

    # Normalize unicode characters to ASCII, lowercase and trim
    s = to_slug_from.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")

    # Remove any characters that are not word chars, spaces or hyphens
    s = re.sub(r"[^\w\s-]", "", s)

    # Replace whitespace and underscores with single hyphen
    s = re.sub(r"[\s_]+", "-", s)

    # Collapse multiple hyphens and strip leading/trailing hyphens
    s = re.sub(r"-{2,}", "-", s).strip("-")

    return f"{s}-{token_urlsafe(6)}"