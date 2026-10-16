from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Git-Analyzer"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Server Network Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # GitHub API Settings
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_API_BASE: str = "https://api.github.com"

    # LLM Settings
    LLM_PROVIDER: str = "ollama"  # "ollama", "vllm", or "deterministic"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    OLLAMA_NUM_GPU: Optional[int] = None
    VLLM_BASE_URL: str = "http://localhost:8000"
    VLLM_MODEL: str = "qwen3:8b"
    VLLM_API_KEY: Optional[str] = None
    AUTO_FALLBACK_TO_DETERMINISTIC: bool = True
    LLM_TIMEOUT: int = 65
    LLM_MAX_RETRIES: int = 1

    # Database Settings
    DATABASE_ENABLED: bool = False
    DATABASE_URL: str = "sqlite+aiosqlite:///./git_analyzer.db"

    # Redis Cache Settings
    REDIS_ENABLED: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hour

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 5

    # Context & Truncation Limits
    MAX_TREE_ENTRIES: int = 5000
    MAX_FILE_SIZE: int = 200000
    MAX_README_SIZE: int = 100000
    MAX_ISSUES: int = 30
    MAX_CONTEXT_SIZE: int = 50000

    # Concurrency & Safeguards
    MAX_ANALYSIS_DURATION: int = 75
    MAX_CONCURRENT_ANALYSES: int = 5


    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


def get_settings() -> Settings:
    return Settings()
