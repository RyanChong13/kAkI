from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    jwt_secret_key: str = "change-me-to-a-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    database_url: str = "sqlite:///./skillsg.db"
    course_refresh_interval_hours: int = 6
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # SkillsFuture live crawl (courses.myskillsfuture.gov.sg search results)
    skillsfuture_live_crawl: bool = True
    # Comma-separated seed search terms the crawler paginates through.
    skillsfuture_crawl_queries: str = (
        "data,python,cloud,cybersecurity,software,marketing,design,finance,"
        "leadership,project management,artificial intelligence,communication,"
        "healthcare,logistics,human resources,accounting"
    )
    skillsfuture_crawl_max_pages: int = 4  # pages per query term
    skillsfuture_crawl_concurrency: int = 6  # concurrent page fetches

    # LLM — required for role redesign feature.
    # Set OPENAI_API_KEY or ANTHROPIC_API_KEY (OpenAI takes priority if both set).
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    @property
    def skillsfuture_crawl_query_list(self) -> list[str]:
        return [q.strip() for q in self.skillsfuture_crawl_queries.split(",") if q.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
