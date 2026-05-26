from pathlib import Path
from typing import Literal
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
    return boilerplate_paths[language_code]


def get_full_boilerplate_path(slug: str, language_code : str):
    base_problem_path = get_problem_dir(slug)
    boilerplate_paths = {
    "cpp": base_problem_path / "boilerplate/cpp/full-cpp-boilerplate.cpp",
    "js": base_problem_path / "boilerplate/js/full-js-boilerplate.js",
    "py": base_problem_path / "boilerplate/py/full-py-boilerplate.py",
    }
    return boilerplate_paths[language_code]