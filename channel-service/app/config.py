from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., description="PostgreSQL async URL: postgresql+asyncpg://...")
    MAIN_BACKEND_URL: str = Field(default="http://localhost:8000", description="Main backend URL for callbacks")
    ENVIRONMENT: str = Field(default="development", description="dev/prod")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
