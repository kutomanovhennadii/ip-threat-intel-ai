import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import httpx
import importlib


class MockResponse:
    # Purpose: lightweight mock object for simulating httpx responses.
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._json = data

    def json(self):
        return self._json


def test_abuseipdb_handles_non_200(monkeypatch):
    # Purpose: ensure fallback is returned when API responds with non-200 code.

    # Arrange
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    import external.abuseipdb
    importlib.reload(external.abuseipdb)
    from external.abuseipdb import fetch_abuse

    def mock_get(*args, **kwargs):
        return MockResponse(500, {})

    monkeypatch.setattr("external.abuseipdb.httpx.get", mock_get)

    # Act
    res = fetch_abuse("8.8.8.8")

    # Assert
    assert res["abuse_score"] is None
    assert res["recent_reports"] is None


def test_abuseipdb_handles_valid_response(monkeypatch):
    # Purpose: ensure valid API payload is parsed correctly.

    # Arrange
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    import external.abuseipdb
    importlib.reload(external.abuseipdb)
    from external.abuseipdb import fetch_abuse

    def mock_get(*args, **kwargs):
        return MockResponse(200, {
            "data": {
                "abuseConfidenceScore": 42,
                "totalReports": 7
            }
        })

    monkeypatch.setattr("external.abuseipdb.httpx.get", mock_get)

    # Act
    res = fetch_abuse("8.8.8.8")

    # Assert
    assert res["abuse_score"] == 42
    assert res["recent_reports"] == 7


def test_abuseipdb_handles_exception(monkeypatch):
    # Purpose: ensure exceptions during HTTP call return fallback.

    # Arrange
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    import external.abuseipdb
    importlib.reload(external.abuseipdb)
    from external.abuseipdb import fetch_abuse

    def mock_get(*args, **kwargs):
        raise Exception("network error")

    monkeypatch.setattr("external.abuseipdb.httpx.get", mock_get)

    # Act
    res = fetch_abuse("8.8.8.8")

    # Assert
    assert res["abuse_score"] is None
    assert res["recent_reports"] is None
