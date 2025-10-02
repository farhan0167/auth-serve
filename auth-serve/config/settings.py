import os

from pydantic_settings import BaseSettings, SettingsConfigDict

MIN = 60  # seconds
HOUR = MIN * 60
DAY = HOUR * 24


class Settings(BaseSettings):
    # Database settings
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "secret123")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "postgres")

    # JWT Settings
    JWT_TOKEN_EXPIRATION_TIME: int = 2 * HOUR

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_KEY_EXPIRATION_TIME: int = 5 * DAY

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
