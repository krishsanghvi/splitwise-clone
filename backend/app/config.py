from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    database_url: str  # Fill in in .env

    api_prefix: str = "/api/v1"
    project_name: str = "SplitFlow API"

    class Config:
        env_file = ".env"


settings = Settings()
