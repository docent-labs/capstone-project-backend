from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHAT_MODEL: str = "gpt-4o-mini"
    TOP_K_CHUNKS: int = 5
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    model_config = {"env_file": ".env"}


settings = Settings()
