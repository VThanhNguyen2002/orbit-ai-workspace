import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

AuthMode = Literal["dev", "jwt"]
NotesRepositoryMode = Literal["memory", "supabase"]


@dataclass(frozen=True)
class Settings:
    service_name: str = "Synapse API"
    service_slug: str = "synapse-api"
    app_version: str = "0.0.0"
    api_version: str = "v1"
    api_prefix: str = "/v1"
    auth_mode: AuthMode = "dev"
    dev_user_id: str = "dev_user"
    notes_repository: NotesRepositoryMode = "memory"
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_jwt_secret: str | None = None
    supabase_service_role_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_version=os.getenv("SYNAPSE_API_VERSION", Settings.app_version),
        auth_mode=_auth_mode(os.getenv("SYNAPSE_AUTH_MODE", Settings.auth_mode)),
        dev_user_id=os.getenv("SYNAPSE_DEV_USER_ID", Settings.dev_user_id),
        notes_repository=_notes_repository_mode(
            os.getenv("SYNAPSE_NOTES_REPOSITORY", Settings.notes_repository)
        ),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY"),
        supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET"),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    )


def _auth_mode(value: str) -> AuthMode:
    if value == "jwt":
        return "jwt"

    return "dev"


def _notes_repository_mode(value: str) -> NotesRepositoryMode:
    if value == "supabase":
        return "supabase"

    return "memory"
