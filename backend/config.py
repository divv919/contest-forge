from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str | None = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    demo_user_password: str = "321321"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
