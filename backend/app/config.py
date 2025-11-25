from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/buzzer"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 24 * 60  # 24 hours

    # CORS
    CORS_ORIGINS: list = ["*"]

    # App
    APP_NAME: str = "Buzzer"
    DEBUG: bool = False

    class Config:
        env_file = "../.env"
        case_sensitive = True


settings = Settings()
