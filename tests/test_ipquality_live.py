import os
import importlib
import pytest
from dotenv import load_dotenv

# Purpose: ensure environment variables are loaded before module reload.
load_dotenv()

from src.external import ipquality


def test_ipquality_live_real_api():
    # Purpose: verify real IPQualityScore API responds with valid fields.

    # Arrange
    api_key = os.getenv("IPQUALITYSCORE_API_KEY")
    assert api_key, "IPQUALITYSCORE_API_KEY is missing — FAIL"

    importlib.reload(ipquality)
    from src.external.ipquality import fetch_quality

    # Act
    result = fetch_quality("8.8.8.8")

    # Assert
    assert result["fraud_score"] is not None
    assert result["vpn"] in (True, False)
