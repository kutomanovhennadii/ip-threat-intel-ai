import os
import pytest
from src.external.abuseipdb import fetch_abuse


@pytest.mark.live
@pytest.mark.anyio
async def test_abuseipdb_live_real_api():
    # Purpose: verify real AbuseIPDB API call works and returns valid fields.

    # Arrange
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    assert api_key, "ABUSEIPDB_API_KEY missing — FAIL"

    # Act
    result = await fetch_abuse("8.8.8.8")

    # Assert
    assert isinstance(result, dict)
    assert result["abuse_score"] is not None
