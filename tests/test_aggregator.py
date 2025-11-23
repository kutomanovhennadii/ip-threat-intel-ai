import pytest
from src.services.aggregator import aggregate_ip_data

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.mark.anyio
async def test_aggregator_basic(monkeypatch):
    # Mock abuseipdb
    def mock_abuse(ip):
        return {"abuse_score": 10, "recent_reports": 2}

    # Mock IPQualityScore
    def mock_quality(ip):
        return {"fraud_score": 30, "vpn": False}

    # Mock ipapi (async)
    async def mock_ipapi(ip):
        return {"hostname": "host.example", "isp": "ExampleISP", "country": "US"}

    # Mock virustotal
    def mock_vt(ip):
        return {"vt_score": 99}

    monkeypatch.setattr("src.services.aggregator.fetch_abuse", mock_abuse)
    monkeypatch.setattr("src.services.aggregator.fetch_quality", mock_quality)
    monkeypatch.setattr("src.services.aggregator.fetch_ipapi", mock_ipapi)
    monkeypatch.setattr("src.services.aggregator.fetch_virustotal", mock_vt)

    result = await aggregate_ip_data("8.8.8.8")

    assert result["ip"] == "8.8.8.8"
    assert result["hostname"] == "host.example"
    assert result["isp"] == "ExampleISP"
    assert result["country"] == "US"
    assert result["abuse_score"] == 10
    assert result["recent_reports"] == 2
    assert result["fraud_score"] == 30
    assert result["vpn_proxy"] is False
    assert result["vt_score"] == 99
    assert result["risk_score"] == (10 + 30) / 2
