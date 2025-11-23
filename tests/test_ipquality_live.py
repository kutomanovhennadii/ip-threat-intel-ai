import os
import importlib
import pytest
from dotenv import load_dotenv

load_dotenv()

from src.external import ipquality


@pytest.mark.live
@pytest.mark.anyio
async def test_ipquality_live_real_api():
    # Purpose: verify real IPQualityScore API responds and returns expected shape.

    api_key = os.getenv("IPQUALITYSCORE_API_KEY")
    assert api_key, "IPQUALITYSCORE_API_KEY is missing - FAIL"

    importlib.reload(ipquality)
    from src.external.ipquality import fetch_quality

    result = await fetch_quality("8.8.8.8")

    # Validate returned structure
    assert "fraud_score" in result
    assert "vpn" in result

    # fraud_score may legitimately be None OR int
    assert result["fraud_score"] is None or isinstance(result["fraud_score"], int)

    # vpn may be True / False / None depending on what IPQS returns
    assert result["vpn"] in (True, False, None)
