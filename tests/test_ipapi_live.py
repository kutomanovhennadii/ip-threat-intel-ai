import os
import importlib
import pytest

from src.external import ipapi


# Helper to run async code inside sync pytest test
# Helper to run async code inside sync pytest test
def run_async(coro):
    import asyncio
    return asyncio.run(coro)


pytest.run = run_async


@pytest.mark.live
def test_ipapi_live_real_api():
    """
    LIVE test for the REAL IPAPI API.
    Requires IPAPI_KEY in environment.
    """

    api_key = os.getenv("IPAPI_KEY")
    if not api_key:
        pytest.skip("IPAPI_KEY missing - skipping live test")

    # Reload module so it re-reads env
    importlib.reload(ipapi)
    from src.external.ipapi import fetch_ipapi

    # Make actual API call
    result = pytest.run(fetch_ipapi("8.8.8.8"))

    print("\nREAL IPAPI RESPONSE:", result)

    # Validate structure
    assert "hostname" in result
    assert "isp" in result
    assert "country" in result

    # Values must be str or None
    assert isinstance(result["hostname"], (str, type(None)))
    assert isinstance(result["isp"], (str, type(None)))
    assert isinstance(result["country"], (str, type(None)))
