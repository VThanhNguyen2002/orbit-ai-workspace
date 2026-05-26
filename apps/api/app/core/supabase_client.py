from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import SecretStr

from app.core.auth import AuthContext
from app.core.config import Settings

PublicApiKeySource = Literal["publishable", "anon"]


class SupabaseUserClientConfigurationError(Exception):
    """Raised when a request-scoped Supabase client cannot be safely created."""


@runtime_checkable
class UserScopedSupabaseQuery(Protocol):
    """Minimal query-builder operations required by the Notes repository."""

    def select(self, fields: str, *, count: str | None = None) -> "UserScopedSupabaseQuery": ...

    def insert(self, payload: dict[str, Any]) -> "UserScopedSupabaseQuery": ...

    def update(self, payload: dict[str, Any]) -> "UserScopedSupabaseQuery": ...

    def eq(self, field: str, value: object) -> "UserScopedSupabaseQuery": ...

    def order(self, field: str, *, desc: bool) -> "UserScopedSupabaseQuery": ...

    def range(self, start: int, end: int) -> "UserScopedSupabaseQuery": ...

    def limit(self, value: int) -> "UserScopedSupabaseQuery": ...

    def execute(self) -> Any: ...


@runtime_checkable
class UserScopedSupabaseClient(Protocol):
    """Request-local Data API client surface consumed by repositories."""

    def table(self, table_name: str) -> UserScopedSupabaseQuery: ...


@dataclass(frozen=True)
class UserScopedSupabaseClientDescriptor:
    """Inert inputs for a future request-scoped Supabase SDK adapter."""

    project_url: str
    user_id: str
    key_source: PublicApiKeySource
    public_api_key: SecretStr = field(repr=False)
    access_token: SecretStr = field(repr=False)

    def __repr__(self) -> str:
        return (
            "UserScopedSupabaseClientDescriptor("
            f"project_url={self.project_url!r}, "
            f"user_id={self.user_id!r}, "
            f"key_source={self.key_source!r}, "
            "public_api_key=<redacted>, access_token=<redacted>)"
        )

    __str__ = __repr__


@runtime_checkable
class UserScopedSupabaseClientAdapter(Protocol):
    """Implementation-neutral factory for a future request-local SDK client."""

    def build(
        self,
        descriptor: UserScopedSupabaseClientDescriptor,
    ) -> UserScopedSupabaseClient: ...


def get_supabase_user_client(
    *,
    auth_context: AuthContext,
    settings: Settings,
) -> UserScopedSupabaseClientDescriptor:
    """Build request-scoped client inputs without creating an SDK client or network request."""
    if auth_context.auth_mode != "jwt":
        raise SupabaseUserClientConfigurationError(
            "User-scoped Supabase clients require JWT authentication"
        )

    if not auth_context.access_token:
        raise SupabaseUserClientConfigurationError(
            "User-scoped Supabase clients require a verified access token"
        )

    public_api_key, key_source = _public_api_key(settings)
    if not settings.supabase_url or not public_api_key or not key_source:
        raise SupabaseUserClientConfigurationError("User-scoped Supabase client is not configured")

    return UserScopedSupabaseClientDescriptor(
        project_url=settings.supabase_url,
        user_id=auth_context.user_id,
        key_source=key_source,
        public_api_key=SecretStr(public_api_key),
        access_token=auth_context.access_token,
    )


def _public_api_key(settings: Settings) -> tuple[str | None, PublicApiKeySource | None]:
    if settings.supabase_publishable_key:
        return settings.supabase_publishable_key, "publishable"

    if settings.supabase_anon_key:
        return settings.supabase_anon_key, "anon"

    return None, None
