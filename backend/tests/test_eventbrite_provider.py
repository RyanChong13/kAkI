import types

import pytest

from app.providers.eventbrite_provider import EventbriteProvider


class DummyResponse:
    def __init__(self, status_code: int = 200, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class DummyAsyncClient:
    def __init__(self, *args, **kwargs):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params=None, headers=None):
        self.calls.append((url, params, headers))
        return DummyResponse(status_code=404, payload={})


@pytest.mark.asyncio
async def test_fetch_uses_eventbrite_search_endpoint(monkeypatch):
    monkeypatch.setattr(
        "app.providers.eventbrite_provider.get_settings",
        lambda: types.SimpleNamespace(eventbrite_private_token="fake-token", eventbrite_configured=True),
    )

    client_instance = DummyAsyncClient()
    monkeypatch.setattr("app.providers.eventbrite_provider.httpx.AsyncClient", lambda *args, **kwargs: client_instance)

    result = await EventbriteProvider().fetch()

    assert client_instance.calls[0][0] == "https://www.eventbriteapi.com/v3/events/search/"
    assert result.available is False
    assert "doesn't have access" in result.notice
