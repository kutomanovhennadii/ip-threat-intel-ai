import os
import importlib
import pytest
import httpx

from src.external import virustotal


@pytest.mark.live
def test_virustotal_live_real_api():
    # Purpose: verify real VirusTotal API connectivity and wrapper correctness.

    # Arrange
    api_key = os.getenv("VIRUSTOTAL_API_KEY")
    assert api_key, "VIRUSTOTAL_API_KEY is missing - FAIL"

    importlib.reload(virustotal)
    from src.external.virustotal import VT_URL, fetch_virustotal

    # Build correct v3 URL
    url = f"{VT_URL}8.8.8.8"

    # Act — RAW CHECK (VirusTotal v3)
    resp = httpx.get(
        url,
        headers={"x-apikey": api_key},
        timeout=8.0
    )

    # If the key is invalid → skip test, because wrapper must handle this
    if resp.status_code in (401, 403):
        pytest.skip("VirusTotal key does not have access to v3 IP-address endpoint")

    # Assert good HTTP response
    assert resp.status_code == 200, (
        f"VirusTotal v3 rejected key: {resp.status_code}, body={resp.text}"
    )

    data = resp.json()
    assert "data" in data, f"Unexpected structure: {data}"

    # Act — FUNCTION CHECK
    # fetch_virustotal is async — call through event loop
    import asyncio
    result = asyncio.get_event_loop().run_until_complete(
        fetch_virustotal("8.8.8.8")
    )

    # Assert — wrapper result
    assert "vt_score" in result
    assert isinstance(result["vt_score"], (int, type(None)))

    print("\nRAW DATA:", data)
    print("FUNC RESULT:", result)
