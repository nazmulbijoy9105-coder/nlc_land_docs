from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "NLC Land Evidence API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    FRONTEND_URL: str = "https://nlc-land-docs.vercel.app"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str

    # Database
    DATABASE_URL: str  # postgresql+asyncpg://...

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24hr

    # Gemini
    GEMINI_API_KEY: str

    # Redis / Upstash
    REDIS_URL: str

    # Resend
    RESEND_API_KEY: str
    FROM_EMAIL: str = "noreply@neumlexcounsel.com"

    # Sentry
    SENTRY_DSN: Optional[str] = None

    # bKash
    BKASH_APP_KEY: str = ""
    BKASH_APP_SECRET: str = ""
    BKASH_USERNAME: str = ""
    BKASH_PASSWORD: str = ""
    BKASH_BASE_URL: str = "https://tokenized.sandbox.bka.sh/v1.2.0-beta"

    # Nagad
    NAGAD_MERCHANT_ID: str = ""
    NAGAD_MERCHANT_KEY: str = ""
    NAGAD_BASE_URL: str = "https://api.mynagad.com"

    # Storage
    SUPABASE_BUCKET: str = "land-evidence"

    # Admin
    ADMIN_SECRET_KEY: str = "nlc-admin-2024"

    class Config:
        env_file = ".env"

settings = Settings()
