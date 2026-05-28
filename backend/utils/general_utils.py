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
    base_points = {
        Difficulty.EASE: 100,
        Difficulty.MEDIUM: 150,
        Difficulty.HARD: 200,
    }

    points = base_points.get(difficulty, 100)
    solved_at = solved_at or datetime.now(timezone.utc)

    contest_duration = max(0.0, (endTime - startTime).total_seconds())
    if contest_duration == 0:
        return points

    elapsed_time = max(0.0, (solved_at - startTime).total_seconds())
    normalized_time = min(1.0, elapsed_time / contest_duration)

    time_bonus_cap = max(1, round(points * 0.2))
    step_seconds = contest_duration / time_bonus_cap
    step_seconds = min(180.0, max(120.0, step_seconds))

    remaining_time = max(0.0, contest_duration * (1.0 - normalized_time))
    time_bonus = min(time_bonus_cap, int(remaining_time // step_seconds))

    return points + time_bonus


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