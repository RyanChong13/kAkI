from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./redeploy.db"
    ANTHROPIC_API_KEY: str = ""
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    MAX_BATCH_SIZE: int = 20  # max applications per batch

    class Config:
        env_file = ".env"


settings = Settings()
