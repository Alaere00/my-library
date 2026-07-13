from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_books_api_key: str = ""
    embedding_model: str = "all-MiniLM-L6-v2"
    top_k: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
