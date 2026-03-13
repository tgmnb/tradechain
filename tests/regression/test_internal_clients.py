from apps.api_service.app.core.config import Settings, get_settings
from apps.api_service.app.services.internal_clients import InternalClients


def test_internal_clients_uses_configured_timeout(monkeypatch) -> None:
    monkeypatch.setenv("INTERNAL_REQUEST_TIMEOUT_SECONDS", "45")
    get_settings.cache_clear()
    settings = Settings()

    clients = InternalClients()

    assert settings.internal_request_timeout_seconds == 45.0
    assert clients.timeout.read == 45.0
