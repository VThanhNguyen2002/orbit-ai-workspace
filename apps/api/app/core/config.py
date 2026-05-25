import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal, cast

AuthMode = Literal["dev", "jwt"]
ConfiguredAuthMode = AuthMode | str
NotesRepositoryMode = Literal["memory", "supabase"]
SUPPORTED_AUTH_MODES: tuple[AuthMode, ...] = ("dev", "jwt")


@dataclass(frozen=True)
class Settings:
    service_name: str = "Synapse API"
    service_slug: str = "synapse-api"
    app_version: str = "0.0.0"
    api_version: str = "v1"
    api_prefix: str = "/v1"
    auth_mode: ConfiguredAuthMode = "dev"
    dev_user_id: str = "dev_user"
    jwt_issuer: str | None = None
    jwt_audience: str | None = None
    jwt_public_key: str | None = None
    notes_repository: NotesRepositoryMode = "memory"
    supabase_url: str | None = None
    supabase_publishable_key: str | None = None
    supabase_anon_key: str | None = None
    supabase_jwt_secret: str | None = None
    supabase_service_role_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_version=os.getenv("SYNAPSE_API_VERSION", Settings.app_version),
        auth_mode=_auth_mode(os.getenv("SYNAPSE_AUTH_MODE", Settings.auth_mode)),
        dev_user_id=os.getenv("SYNAPSE_DEV_USER_ID", Settings.dev_user_id),
        jwt_issuer=os.getenv("SYNAPSE_JWT_ISSUER"),
        jwt_audience=os.getenv("SYNAPSE_JWT_AUDIENCE"),
        jwt_public_key=os.getenv("SYNAPSE_JWT_PUBLIC_KEY"),
        notes_repository=_notes_repository_mode(
            os.getenv("SYNAPSE_NOTES_REPOSITORY", Settings.notes_repository)
        ),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_publishable_key=os.getenv("SUPABASE_PUBLISHABLE_KEY"),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY"),
        supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET"),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    )


def _auth_mode(value: str) -> ConfiguredAuthMode:
    if value in SUPPORTED_AUTH_MODES:
        return cast(AuthMode, value)

    return value


def _notes_repository_mode(value: str) -> NotesRepositoryMode:
    if value == "supabase":
        return "supabase"

    return "memory"
