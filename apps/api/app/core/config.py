import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal, cast

AuthMode = Literal["dev", "jwt"]
ConfiguredAuthMode = AuthMode | str
NotesRepositoryMode = Literal["memory", "supabase"]
AiProvider = Literal["fake", "openai"]
OpenAIAuthMode = Literal["fake", "api_key", "workload_identity"]
SUPPORTED_AUTH_MODES: tuple[AuthMode, ...] = ("dev", "jwt")
SUPPORTED_AI_PROVIDERS: tuple[AiProvider, ...] = ("fake", "openai")
SUPPORTED_OPENAI_AUTH_MODES: tuple[OpenAIAuthMode, ...] = (
    "fake",
    "api_key",
    "workload_identity",
)


class AiConfigError(ValueError):
    """Raised for fail-closed AI provider configuration errors."""


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
    # AI summarization settings (no provider secrets — fake only)
    ai_summarization_enabled: bool = False
    ai_provider: AiProvider = "fake"
    ai_max_input_chars: int = 50_000
    openai_model: str = "openai-summary-placeholder"
    openai_timeout_seconds: int = 30
    openai_max_retries: int = 0
    openai_request_budget: int = 0
    openai_auth_mode: OpenAIAuthMode = "fake"


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
        ai_summarization_enabled=os.getenv(
            "SYNAPSE_AI_SUMMARIZATION_ENABLED", ""
        ).lower() in ("1", "true", "yes"),
        ai_provider=_ai_provider_mode(
            os.getenv("SYNAPSE_AI_PROVIDER", Settings.ai_provider)
        ),
        openai_model=_openai_model(
            os.getenv("SYNAPSE_OPENAI_MODEL", Settings.openai_model)
        ),
        openai_timeout_seconds=_positive_int_env(
            "SYNAPSE_OPENAI_TIMEOUT_SECONDS",
            Settings.openai_timeout_seconds,
        ),
        openai_max_retries=_non_negative_int_env(
            "SYNAPSE_OPENAI_MAX_RETRIES",
            Settings.openai_max_retries,
        ),
        openai_request_budget=_non_negative_int_env(
            "SYNAPSE_OPENAI_REQUEST_BUDGET",
            Settings.openai_request_budget,
        ),
        openai_auth_mode=_openai_auth_mode(
            os.getenv("SYNAPSE_OPENAI_AUTH_MODE", Settings.openai_auth_mode)
        ),
    )


def _auth_mode(value: str) -> ConfiguredAuthMode:
    if value in SUPPORTED_AUTH_MODES:
        return cast(AuthMode, value)

    return value


def _notes_repository_mode(value: str) -> NotesRepositoryMode:
    if value == "supabase":
        return "supabase"

    return "memory"


def _ai_provider_mode(value: str) -> AiProvider:
    if value == "fake":
        return "fake"
    if value == "openai":
        return "openai"

    msg = "Unsupported AI provider"
    raise AiConfigError(msg)


def _openai_auth_mode(value: str) -> OpenAIAuthMode:
    if value == "fake":
        return "fake"
    if value == "api_key":
        return "api_key"
    if value == "workload_identity":
        return "workload_identity"

    msg = "Unsupported OpenAI auth mode"
    raise AiConfigError(msg)


def _openai_model(value: str) -> str:
    if value.strip():
        return value

    msg = "OpenAI model must be configured"
    raise AiConfigError(msg)


def _positive_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError as exc:
        msg = f"{name} must be a positive integer"
        raise AiConfigError(msg) from exc

    if value < 1:
        msg = f"{name} must be a positive integer"
        raise AiConfigError(msg)

    return value


def _non_negative_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError as exc:
        msg = f"{name} must be a non-negative integer"
        raise AiConfigError(msg) from exc

    if value < 0:
        msg = f"{name} must be a non-negative integer"
        raise AiConfigError(msg)

    return value


def validate_ai_provider_runtime(settings: Settings) -> None:
    """Fail closed for provider modes that are not runtime-enabled yet."""
    if settings.ai_provider == "fake":
        if settings.openai_auth_mode != "fake":
            msg = "OpenAI auth mode requires a future OpenAI runtime slice"
            raise AiConfigError(msg)
        return

    if settings.openai_auth_mode == "fake":
        msg = "OpenAI provider requires an explicit future credential mode"
        raise AiConfigError(msg)
    if settings.openai_auth_mode == "api_key":
        msg = "OpenAI API-key runtime is not implemented"
        raise AiConfigError(msg)
    if settings.openai_auth_mode == "workload_identity":
        msg = "OpenAI workload identity runtime is not implemented"
        raise AiConfigError(msg)
