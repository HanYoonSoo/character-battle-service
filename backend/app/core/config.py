from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Character Battle"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    database_url: str = "postgresql+psycopg://app:app@postgres:5432/character_battle"
    database_auto_create: bool = True
    database_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle_seconds: int = 1_800
    redis_url: str = "redis://redis:6379/0"
    session_cookie_name: str = "anon_session"
    session_ttl_seconds: int = 2_592_000
    session_cookie_secure: bool = False
    max_characters_per_user: int = 5
    max_character_name_length: int = 20
    max_character_description_length: int = 255
    leaderboard_zset_key: str = "leaderboard:characters"
    leaderboard_last_win_key: str = "leaderboard:characters:last_win"
    leaderboard_win_points: int = 1
    vector_search_enabled: bool = False
    openai_model: str = "gpt-4o"
    openai_api_key: str = "replace_me"
    llm_max_attempts: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()
