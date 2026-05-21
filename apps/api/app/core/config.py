import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    service_name: str = "Synapse API"
    service_slug: str = "synapse-api"
    app_version: str = "0.0.0"
    api_version: str = "v1"
    api_prefix: str = "/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_version=os.getenv("SYNAPSE_API_VERSION", Settings.app_version),
    )
