"""Backend configuration - all env vars in one place."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings from environment variables."""

    # Server
    PORT: int = int(os.getenv("PORT", 8001))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # DeepSeek LLM
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # Kalodata TikTok Shop API
    KALODATA_API_KEY: str = os.getenv("KALODATA_API_KEY", "")
    KALODATA_REGION: str = os.getenv("KALODATA_REGION", "US")
    KALODATA_PRICE_MIN: float = float(os.getenv("KALODATA_PRICE_MIN", "0"))
    KALODATA_PRICE_MAX: float = float(os.getenv("KALODATA_PRICE_MAX", "0"))

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")
    LLM_TIMEOUT_S: int = int(os.getenv("LLM_TIMEOUT_S", "45"))
    LLM_MAX_CONCURRENCY: int = int(os.getenv("LLM_MAX_CONCURRENCY", "8"))
    LLM_CACHE_TTL_S: int = int(os.getenv("LLM_CACHE_TTL_S", "3600"))

    # Crawl Settings
    CRAWL_SOURCES: str = os.getenv(
        "CRAWL_SOURCES",
        "tiktok,amazon,ebay,shopee,lazada,etsy",
    )
    CRAWL_WATCHLIST: str = os.getenv(
        "CRAWL_WATCHLIST",
        "personalized tumbler,halloween decor,christmas ornament,mug"
    )
    CRAWL_INTERVAL_MIN: int = int(os.getenv("CRAWL_INTERVAL_MIN", "60"))
    CRAWL_MAX_ITEMS: int = int(os.getenv("CRAWL_MAX_ITEMS", "30"))
    CRAWL_AUTO_START: bool = os.getenv("CRAWL_AUTO_START", "false").lower() in ("true", "1", "yes")
    CRAWL_DEMO_FALLBACK: bool = os.getenv("CRAWL_DEMO_FALLBACK", "false").lower() in ("true", "1", "yes")

    # Paths
    DATA_DIR: Path = Path(__file__).resolve().parent.parent.parent / "data"

    @property
    def crawl_sources(self) -> list:
        return [s.strip() for s in self.CRAWL_SOURCES.split(",") if s.strip()]

    @property
    def crawl_watchlist(self) -> list:
        return [s.strip() for s in self.CRAWL_WATCHLIST.split(",") if s.strip()]

    @property
    def signals_dir(self) -> Path:
        d = self.DATA_DIR / "signals"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def has_kalodata_key(self) -> bool:
        return bool(self.KALODATA_API_KEY and len(self.KALODATA_API_KEY) > 10)

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


settings = Settings()
