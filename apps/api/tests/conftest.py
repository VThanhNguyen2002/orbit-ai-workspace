from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture(autouse=True)
def use_deterministic_api_settings(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    monkeypatch.setenv("SYNAPSE_AUTH_MODE", "dev")
    monkeypatch.setenv("SYNAPSE_NOTES_REPOSITORY", "memory")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(create_app()) as test_client:
        yield test_client
