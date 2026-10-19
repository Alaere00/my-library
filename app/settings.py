from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    supabase_api_key: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    user_agent: Optional[str] = None
    hardcover_api_url: Optional[str] = ""
    hardcover_api_key: Optional[str] = None
    openlibrary_url: str = ""
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
