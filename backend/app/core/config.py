import os
from dataclasses import dataclass, field


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    github_base_url: str = os.getenv("GITHUB_BASE_URL", "https://api.github.com")
    github_token: str | None = os.getenv("GITHUB_TOKEN") or None
    github_timeout_seconds: float = float(os.getenv("GITHUB_TIMEOUT_SECONDS", "8"))
    github_retry_attempts: int = int(os.getenv("GITHUB_RETRY_ATTEMPTS", "2"))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    stale_cache_ttl_seconds: int = int(os.getenv("STALE_CACHE_TTL_SECONDS", "1800"))
    default_repositories: list[str] = field(
        default_factory=lambda: _split_csv(
            os.getenv(
                "DASHBOARD_REPOSITORIES",
                "fastapi/fastapi,encode/httpx,pydantic/pydantic,vitejs/vite",
            )
        )
    )
    cors_origins: list[str] = field(
        default_factory=lambda: _split_csv(
            os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            )
        )
    )


settings = Settings()
