import os
import importlib
import pytest
import httpx

from src.external import virustotal


@pytest.mark.live
def test_virustotal_live_real_api():
    # Purpose: verify real VirusTotal v2 API connectivity and wrapper correctness.

    # Arrange
    api_key = os.getenv("VIRUSTOTAL_API_KEY")
    assert api_key, "VIRUSTOTAL_API_KEY is missing - FAIL"

    importlib.reload(virustotal)
    from src.external.virustotal import VT_URL, fetch_virustotal

    # Act — RAW CHECK
    resp = httpx.get(
        VT_URL,
        params={"apikey": api_key, "ip": "8.8.8.8"},
        timeout=8.0
    )

    # Если ключ не имеет доступа к v2 endpoint → тест не должен падать
    if resp.status_code == 403:
        pytest.skip("VirusTotal key does not have access to v2 IP-report endpoint")

    # Assert — raw VT response
    assert resp.status_code == 200, (
        f"VirusTotal V2 API rejected key: {resp.status_code}, body={resp.text}"
    )

    data = resp.json()
    assert "response_code" in data, f"Unexpected structure: {data}"

    # Act — FUNCTION CHECK
    result = fetch_virustotal("8.8.8.8")

    # Assert — wrapper result
    assert "vt_score" in result
    assert isinstance(result["vt_score"], (int, type(None)))

    print("\nRAW DATA:", data)
    print("FUNC RESULT:", result)
