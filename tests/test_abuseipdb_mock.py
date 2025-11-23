import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
import importlib
from types import SimpleNamespace


class MockAsyncClient:
    """
    Minimal async mock that simulates httpx.AsyncClient.
    It returns a preconfigured response object via `get`.
    """
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def get(self, *args, **kwargs):
        return self._response


class MockResponse:
    """
    Lightweight mock for httpx.Response-like object with .status_code, .json(), and .text.
    """
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._json = data
        self.text = str(data)  # <<< ВОТ ЭТО — ЕДИНСТВЕННОЕ, ЧТО НУЖНО ДОБАВИТЬ

    def json(self):
        return self._json


@pytest.mark.anyio
async def test_abuseipdb_handles_non_200(monkeypatch):
    # Arrange
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")

    import external.abuseipdb
    importlib.reload(external.abuseipdb)
    from external.abuseipdb import fetch_abuse

    response = MockResponse(500, {})

    # Patch AsyncClient to return our mock response
    monkeypatch.setattr(
        "external.abuseipdb.httpx.AsyncClient",
        lambda *args, **kwargs: MockAsyncClient(response)
    )

    # Act
    res = await fetch_abuse("8.8.8.8")

    # Assert
    assert res["abuse_score"] is None
    assert res["recent_reports"] is None


@pytest.mark.anyio
async def test_abuseipdb_handles_valid_response(monkeypatch):
    # Arrange
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")

    import external.abuseipdb
    importlib.reload(external.abuseipdb)
    from external.abuseipdb import fetch_abuse

    response = MockResponse(200, {
        "data": {
            "abuseConfidenceScore": 42,
            "totalReports": 7
        }
    })

    monkeypatch.setattr(
        "external.abuseipdb.httpx.AsyncClient",
        lambda *args, **kwargs: MockAsyncClient(response)
    )

    # Act
    res = await fetch_abuse("8.8.8.8")

    # Assert
    assert res["abuse_score"] == 42
    assert res["recent_reports"] == 7


@pytest.mark.anyio
async def test_abuseipdb_handles_exception(monkeypatch):
    # Arrange
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")

    import external.abuseipdb
    importlib.reload(external.abuseipdb)
    from external.abuseipdb import fetch_abuse

    class ErrorAsyncClient:
        async def __aenter__(self):
            raise Exception("network error")

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(
        "external.abuseipdb.httpx.AsyncClient",
        lambda *args, **kwargs: ErrorAsyncClient()
    )

    # Act
    res = await fetch_abuse("8.8.8.8")

    # Assert
    assert res["abuse_score"] is None
    assert res["recent_reports"] is None
