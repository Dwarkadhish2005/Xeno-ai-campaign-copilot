from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., description="PostgreSQL URL (will auto-convert to asyncpg)")
    GROQ_API_KEY: str = Field(default="", description="Groq API key")
    CHANNEL_SERVICE_URL: str = Field(default="http://localhost:8001", description="Channel service URL")
    ENVIRONMENT: str = Field(default="development", description="dev/prod")

    # ── Demo / Presentation Mode ──────────────────────────────────────────────
    DEMO_MODE: bool = Field(
        default=False,
        description="When True, only DEMO_LIMIT messages are actually dispatched per campaign launch."
    )
    DEMO_LIMIT: int = Field(
        default=10,
        description="Max customers to process when DEMO_MODE is enabled."
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        """Ensure async-compatible URL for asyncpg driver."""
        if v.startswith("postgresql://") or v.startswith("postgres://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
