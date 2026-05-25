from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.core.auth import AuthContext, get_auth_context
from app.core.config import Settings, get_settings
from app.core.jwt_verifier import PyJwtRsaVerifier
from app.main import create_app

ISSUER = "https://issuer.example.invalid/auth/v1"
AUDIENCE = "authenticated"
SUBJECT = "11111111-1111-4111-8111-111111111111"
TEST_UTC = timezone.utc  # noqa: UP017 - local verification also runs with Python 3.10.


@dataclass(frozen=True)
class RsaKeys:
    private_key: str
    public_key: str


@pytest.fixture
def rsa_keys() -> RsaKeys:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return RsaKeys(
        private_key=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode(),
        public_key=private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode(),
    )


def test_jwt_mode_maps_verified_subject_to_auth_context(rsa_keys: RsaKeys) -> None:
    token = _token(rsa_keys)

    auth_context = get_auth_context(
        request=_request(token),
        settings=Settings(auth_mode="jwt"),
        jwt_verifier=_verifier(rsa_keys),
    )

    assert auth_context == AuthContext(user_id=SUBJECT, auth_mode="jwt", access_token=token)
    assert auth_context.access_token is not None
    assert auth_context.access_token.get_secret_value() == token
    assert token not in repr(auth_context)
    assert token not in str(auth_context)


def test_notes_route_works_with_valid_jwt_auth_context(
    monkeypatch: pytest.MonkeyPatch,
    rsa_keys: RsaKeys,
) -> None:
    _configure_jwt_mode(monkeypatch, rsa_keys)
    token = _token(rsa_keys)

    with TestClient(create_app()) as client:
        response = client.post(
            "/v1/notes",
            headers={"authorization": f"Bearer {token}"},
            json={"title": "JWT note", "content": "Authenticated", "content_type": "plain"},
        )

    assert response.status_code == 201
    assert response.json()["data"]["user_id"] == SUBJECT


@pytest.mark.parametrize(
    "authorization",
    [
        None,
        "",
        "Token malformed",
        "Bearer",
        "Bearer malformed extra",
    ],
)
def test_jwt_mode_rejects_missing_or_malformed_bearer_header(
    authorization: str | None,
    monkeypatch: pytest.MonkeyPatch,
    rsa_keys: RsaKeys,
) -> None:
    _configure_jwt_mode(monkeypatch, rsa_keys)
    headers = {} if authorization is None else {"authorization": authorization}

    with TestClient(create_app()) as client:
        response = client.get("/v1/notes", headers=headers)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.parametrize(
    "invalid_case",
    [
        "malformed_token",
        "expired",
        "invalid_signature",
        "wrong_issuer",
        "wrong_audience",
        "missing_sub",
        "malformed_sub",
        "unsupported_role",
        "unsigned",
    ],
)
def test_jwt_mode_rejects_invalid_token_claims_and_signature(
    invalid_case: str,
    monkeypatch: pytest.MonkeyPatch,
    rsa_keys: RsaKeys,
) -> None:
    _configure_jwt_mode(monkeypatch, rsa_keys)
    token = _invalid_token(invalid_case, rsa_keys)

    with TestClient(create_app()) as client:
        response = client.get("/v1/notes", headers={"authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
    assert response.json()["error"]["message"] == "Invalid bearer token"
    assert token not in response.text


def test_jwt_mode_with_invalid_public_key_configuration_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    rsa_keys: RsaKeys,
) -> None:
    _configure_jwt_mode(monkeypatch, rsa_keys, public_key="not-a-public-key")

    with TestClient(create_app()) as client:
        response = client.get(
            "/v1/notes",
            headers={"authorization": f"Bearer {_token(rsa_keys)}"},
        )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def _verifier(rsa_keys: RsaKeys) -> PyJwtRsaVerifier:
    return PyJwtRsaVerifier(public_key=rsa_keys.public_key, issuer=ISSUER, audience=AUDIENCE)


def _claims(**overrides: Any) -> dict[str, Any]:
    claims: dict[str, Any] = {
        "sub": SUBJECT,
        "role": "authenticated",
        "iss": ISSUER,
        "aud": AUDIENCE,
        "exp": datetime.now(TEST_UTC) + timedelta(minutes=5),
    }
    claims.update(overrides)
    return claims


def _token(rsa_keys: RsaKeys, **overrides: Any) -> str:
    return jwt.encode(_claims(**overrides), rsa_keys.private_key, algorithm="RS256")


def _invalid_token(invalid_case: str, rsa_keys: RsaKeys) -> str:
    if invalid_case == "malformed_token":
        return "not-a-jwt"
    if invalid_case == "expired":
        return _token(rsa_keys, exp=datetime.now(TEST_UTC) - timedelta(minutes=1))
    if invalid_case == "invalid_signature":
        return _token(_new_rsa_keys())
    if invalid_case == "wrong_issuer":
        return _token(rsa_keys, iss="https://wrong.example.invalid/auth/v1")
    if invalid_case == "wrong_audience":
        return _token(rsa_keys, aud="wrong-audience")
    if invalid_case == "missing_sub":
        claims = _claims()
        claims.pop("sub")
        return jwt.encode(claims, rsa_keys.private_key, algorithm="RS256")
    if invalid_case == "malformed_sub":
        return _token(rsa_keys, sub="not-a-user-uuid")
    if invalid_case == "unsupported_role":
        return _token(rsa_keys, role="service_role")
    if invalid_case == "unsigned":
        return jwt.encode(_claims(), key=None, algorithm="none")
    raise AssertionError(f"Unsupported test case: {invalid_case}")


def _new_rsa_keys() -> RsaKeys:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return RsaKeys(
        private_key=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode(),
        public_key=private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode(),
    )


def _configure_jwt_mode(
    monkeypatch: pytest.MonkeyPatch,
    rsa_keys: RsaKeys,
    *,
    public_key: str | None = None,
) -> None:
    monkeypatch.setenv("SYNAPSE_AUTH_MODE", "jwt")
    monkeypatch.setenv("SYNAPSE_JWT_ISSUER", ISSUER)
    monkeypatch.setenv("SYNAPSE_JWT_AUDIENCE", AUDIENCE)
    monkeypatch.setenv("SYNAPSE_JWT_PUBLIC_KEY", public_key or rsa_keys.public_key)
    get_settings.cache_clear()


def _request(token: str) -> Request:
    return Request(
        {"type": "http", "headers": [(b"authorization", f"Bearer {token}".encode())]}
    )
