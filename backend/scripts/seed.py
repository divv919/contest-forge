from sqlmodel import select

from ..config import settings
from ..dependencies.db_deps import get_session


def insert_problem_statements(session):
    from ..db.schemas.problem import Difficulty, Problem

    existing_slugs = set(session.exec(select(Problem.slug)).all())

    problems = [
        Problem(
            name="Two Sum",
            difficulty=Difficulty.EASE,
            slug="two_sum",
            description="Given two numbers, calculate and return their sum.",
            test_cases_count=2,
            solution="function summation(a, b) {\r\n    // Write your code here\r\n}\r\n",
        ),
        Problem(
            name="Three Sum",
            difficulty=Difficulty.MEDIUM,
            slug="three_sum",
            description="Given three numbers, calculate and return their sum.",
            test_cases_count=3,
            solution="function sum_three(a, b, c) {\r\n    // Write your code here\r\n"
            "    return a + b + c\r\n}\r\n",
        ),
    ]

    session.add_all([problem for problem in problems if problem.slug not in existing_slugs])


def insert_demo_user(session):

    from pwdlib import PasswordHash

    from ..db.schemas import User

    existing_user = session.exec(select(User).where(User.username == "Divv919")).first()

    if existing_user:
        return

    password_hash = PasswordHash.recommended()

    session.add(
        User(
            username="Divv919",
            email="demo@example.com",
            password=password_hash.hash(settings.demo_user_password),
            provider="local",
            provider_user_id="Divv919",
        )
    )


def insert_languages(session):
    from ..db.schemas import Language

    existing_names = set(session.exec(select(Language.name)).all())

    languages = [
        Language(name="JavaScript", judge0id=63),
        Language(name="Python", judge0id=71),
        Language(name="CPP", judge0id=54),
    ]

    session.add_all([language for language in languages if language.name not in existing_names])


def seed():
    session = next(get_session())
    try:
        insert_problem_statements(session)
        insert_demo_user(session)
        insert_languages(session)

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    print("Seeding initial data...")
    seed()
    print("Seeding completed successfully.")
