import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import httpx
import importlib


class MockResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._json = data

    def json(self):
        return self._json


def test_abuseipdb_handles_non_200(monkeypatch):
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")

    import external.abuseipdb
    importlib.reload(external.abuseipdb)
    from external.abuseipdb import fetch_abuse

    def mock_get(*args, **kwargs):
        return MockResponse(500, {})

    monkeypatch.setattr("external.abuseipdb.httpx.get", mock_get)

    res = fetch_abuse("8.8.8.8")
    assert res["abuse_score"] is None
    assert res["recent_reports"] is None


def test_abuseipdb_handles_valid_response(monkeypatch):
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

    res = fetch_abuse("8.8.8.8")
    assert res["abuse_score"] == 42
    assert res["recent_reports"] == 7


def test_abuseipdb_handles_exception(monkeypatch):
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")

    import external.abuseipdb
    importlib.reload(external.abuseipdb)
    from external.abuseipdb import fetch_abuse

    def mock_get(*args, **kwargs):
        raise Exception("network error")

    monkeypatch.setattr("external.abuseipdb.httpx.get", mock_get)

    res = fetch_abuse("8.8.8.8")
    assert res["abuse_score"] is None
    assert res["recent_reports"] is None
