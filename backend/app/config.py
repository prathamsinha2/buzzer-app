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

    # VAPID Keys (Loaded from environment variables - preferred for production)
    VAPID_PRIVATE_KEY: str = ""
    VAPID_PUBLIC_KEY: str = ""
    VAPID_CLAIMS_EMAIL: str = ""

    class Config:
        env_file = "../.env"
        case_sensitive = True

# Load VAPID keys from JSON file if environment variables not set (for local development)
import json
import os
if not os.environ.get("VAPID_PUBLIC_KEY"):
    try:
        with open(os.path.join(os.path.dirname(__file__), "..", "vapid.json"), "r") as f:
            vapid_data = json.load(f)
            os.environ.setdefault("VAPID_PRIVATE_KEY", vapid_data.get("private_key", ""))
            os.environ.setdefault("VAPID_PUBLIC_KEY", vapid_data.get("public_key", ""))
            os.environ.setdefault("VAPID_CLAIMS_EMAIL", vapid_data.get("email", ""))
    except Exception as e:
        print(f"Warning: Could not load vapid.json: {e}")


settings = Settings()
