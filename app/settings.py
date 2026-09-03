from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    google_books_api_key: Optional[str] = None
    google_books_api_url: str = ""
    supabase_api_key: Optional[str] = None
    supabase_url: Optional[str] = None
    user_agent: Optional[str] = None
    embedding_model: str = "all-MiniLM-L6-v2"
    top_k: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
