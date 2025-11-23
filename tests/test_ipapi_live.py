import os
import importlib
import pytest

from src.external import ipapi


# Purpose: small helper to execute async functions inside normal pytest tests.
def run_async(coro):
    import asyncio
    return asyncio.run(coro)


pytest.run = run_async


@pytest.mark.live
def test_ipapi_live_real_api():
    # Purpose: verify real IPAPI.io endpoint returns valid structure and field types.

    # Arrange
    api_key = os.getenv("IPAPI_KEY")
    assert api_key, "IPAPI_KEY is missing - FAIL, not SKIP"

    importlib.reload(ipapi)
    from src.external.ipapi import fetch_ipapi

    # Act
    result = pytest.run(fetch_ipapi("8.8.8.8"))

    # Assert
    assert isinstance(result, dict)
    assert "hostname" in result
    assert "country" in result
    assert "isp" in result

    assert isinstance(result["hostname"], (str, type(None)))
    assert isinstance(result["country"], (str, type(None)))
    assert isinstance(result["isp"], (str, type(None)))
