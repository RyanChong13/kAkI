from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/redeploy_db"
    ANTHROPIC_API_KEY: str = "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"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    MAX_BATCH_SIZE: int = 20  # max applications per batch

    class Config:
        env_file = ".env"


settings = Settings()
