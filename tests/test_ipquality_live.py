import os
import importlib
import pytest
from dotenv import load_dotenv

# Ensure env variables are loaded BEFORE reloading module
load_dotenv()

# Correct import path
from src.external import ipquality


@pytest.mark.live
def test_ipquality_live_real_api():
    """
    REAL LIVE TEST.
    Verifies that the real IPQualityScore API works with a real API key.
    """

    api_key = os.getenv("IPQUALITYSCORE_API_KEY")
    if not api_key:
        pytest.skip("No IPQUALITYSCORE_API_KEY in environment – skipping live test")

    # reload to ensure the module reads the key
    importlib.reload(ipquality)
    from src.external.ipquality import fetch_quality

    result = fetch_quality("8.8.8.8")

    # API always returns numeric/boolean fields
    assert "fraud_score" in result
    assert "vpn" in result

    print("\nREAL API RESPONSE:", result)

    # Fraud score must be an integer
    assert isinstance(result["fraud_score"], int)

    # VPN must be bool
    assert isinstance(result["vpn"], bool)

