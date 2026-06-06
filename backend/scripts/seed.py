from backend.dependencies.db_deps import get_session


def insert_problem_statements(session):
    from backend.db.schemas.problem import Problem, Difficulty

    problems = [
        Problem(
            name="Two Sum",
            difficulty=Difficulty.EASE,
            slug="two_sum",
            description="Given two numbers, calculate and return their sum.",
            test_cases_count=2,
            solution="function summation(a, b) {\r\n    // Write your code here\r\n}\r\n"
        ),
        Problem(
            name="Three Sum",
            difficulty=Difficulty.MEDIUM,
            slug="three_sum",
            description="Given three numbers, calculate and return their sum.",
            test_cases_count=3,
            solution="function sum_three(a, b, c) {\r\n    // Write your code here\r\n    return a + b + c\r\n}\r\n"
        )
    ]
    session.add_all(problems)
    session.commit()


def insert_demo_user(session):
    from backend.db.schemas import User
    from pwdlib import PasswordHash
    import os 
    
    password_hash = PasswordHash.recommended()
    password = os.getenv("DEMO_USER_PASSWORD", "321321")
    hashed_password = password_hash.hash(password)
    already_exists = session.query(User).filter_by(username="Divv919").first()
    if already_exists:
        return
    demo_user = User(username="Divv919", email="demo@example.com",password=hashed_password, provider="local", provider_user_id="Divv919")
    session.add(demo_user)
    session.commit()


def insert_languages(session):
    from backend.db.schemas import Language

    languages = [
        Language(name="JavaScript", judge0id=63),
        Language(name="Python", judge0id=71),
        Language(name="CPP", judge0id=54)
    ]
    session.add_all(languages)
    session.commit()

def seed():
    session = next(get_session())
    try:
        insert_problem_statements(session)
        insert_demo_user(session)
        insert_languages(session)
    finally:
        session.close()

if __name__ == "__main__":
    print("Seeding initial data...")
    seed()
    print("Seeding completed successfully.")