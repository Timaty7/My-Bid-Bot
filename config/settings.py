"""
Централизованная конфигурация проекта на pydantic-settings.
Все переменные окружения валидируются здесь и нигде больше не читаются напрямую из os.environ.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Единая точка конфигурации приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---- Telegram ----
    TELEGRAM_TOKEN: str
    TELEGRAM_CHAT_ID: int
    CREATOR_ID: int = Field(..., description="Telegram ID создателя бота — эксклюзивный доступ к handlers/creator.py")

    # ---- Режим запуска бота ----
    USE_WEBHOOK: bool = False
    WEBHOOK_HOST: str = "https://example.com"
    WEBHOOK_PATH: str = "/webhook"
    WEBAPP_HOST: str = "0.0.0.0"
    WEBAPP_PORT: int = 8080
    WEBHOOK_SECRET: str = Field(..., min_length=16)

    # ---- Gemini ----
    GEMINI_API_KEYS: str
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # ---- Freelancer.com API ----
    FREELANCER_API_URL: str = "https://www.freelancer.com/api/"
    FREELANCER_ACCESS_TOKEN: str

    # ---- Фильтрация заказов ----
    INCLUDE_WORDS: str = "python,bot,scrape,api,automation"
    EXCLUDE_WORDS: str = "wordpress,php,java,c++,laravel,seo"

    # ---- Параметры автобиддера ----
    CHECK_INTERVAL: int = 60
    MAX_DAILY_BIDS: int = 20

    # ---- База данных ----
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # ---- Redis ----
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # ---- Логирование ----
    LOG_LEVEL: str = "INFO"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def gemini_keys_list(self) -> List[str]:
        return [k.strip() for k in self.GEMINI_API_KEYS.split(",") if k.strip()]

    @property
    def include_words_list(self) -> List[str]:
        return [w.strip().lower() for w in self.INCLUDE_WORDS.split(",") if w.strip()]

    @property
    def exclude_words_list(self) -> List[str]:
        return [w.strip().lower() for w in self.EXCLUDE_WORDS.split(",") if w.strip()]

    @field_validator("GEMINI_API_KEYS")
    @classmethod
    def validate_gemini_keys(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("GEMINI_API_KEYS не может быть пустым — нужен минимум один ключ")
        return v


@lru_cache
def get_settings() -> Settings:
    """Возвращает синглтон настроек приложения (кэшируется на весь процесс)."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
