from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str | None = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    demo_user_password: str = "321321"
    database_url: str = "postgresql+pg8000://judge0:judge0postgres@db:5432/judge0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings():
    return Settings()
