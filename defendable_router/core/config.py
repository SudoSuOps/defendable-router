from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DEFENDABLE_ROUTER_", env_file=".env", extra="ignore")

    env: str = "local"
    database_url: str = "sqlite:///./data/defendable_router.db"
    receipts_dir: Path = Path("./data/receipts")


@lru_cache
def get_settings() -> Settings:
    return Settings()
