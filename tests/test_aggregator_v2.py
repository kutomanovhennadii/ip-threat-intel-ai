# tests/test_aggregator_v2.py

import pytest
import asyncio

from src.services.aggregator_v2 import aggregate_ip_data_v2
from src.services.providers_registry import PROVIDERS


class DummyProviderOK:
    """
    Provider that always succeeds and returns fixed values.
    Used to test normal operation of the aggregator.
    """
    @property
    def name(self):
        return "DummyOK"

    @property
    def fields(self):
        return ("dummy_value",)

    async def fetch(self, ip: str):
        return {"dummy_value": 123}


class DummyProviderFail:
    """
    Provider that always fails.
    Used to test graceful fallback behavior.
    """
    @property
    def name(self):
        return "DummyFail"

    @property
    def fields(self):
        return ("fail_value",)

    async def fetch(self, ip: str):
        raise RuntimeError("boom")


@pytest.mark.anyio
async def test_aggregator_v2_success(monkeypatch):
    """
    aggregator_v2 should correctly merge data from providers
    and return fixed shape + dynamic fields.
    """

    # Patch registry to use only dummy providers
    monkeypatch.setattr(
        "src.services.aggregator_v2.PROVIDERS",
        [DummyProviderOK()]
    )

    result = await aggregate_ip_data_v2("1.2.3.4")

    # IP must be preserved
    assert result["ip"] == "1.2.3.4"

    # Dummy provider should add its field
    assert result["dummy_value"] == 123

    # Default shape must still exist
    assert "hostname" in result
    assert "fraud_score" in result
    assert "vpn_proxy" in result
    assert "vt_score" in result


@pytest.mark.anyio
async def test_aggregator_v2_provider_error(monkeypatch):
    """
    aggregator_v2 must not crash when a provider fails.
    Failed provider fields must remain None (fallback value).
    """

    monkeypatch.setattr(
        "src.services.aggregator_v2.PROVIDERS",
        [DummyProviderFail()]
    )

    result = await aggregate_ip_data_v2("8.8.8.8")

    # Provider's declared field must exist but be None
    assert "fail_value" in result
    assert result["fail_value"] is None



