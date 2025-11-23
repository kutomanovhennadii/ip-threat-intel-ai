# src/services/providers/ipquality_provider.py

import logging
from typing import Dict

from src.services.providers.base_provider import ThreatIntelProvider
from src.external.ipquality import fetch_quality

log = logging.getLogger("provider.ipquality")


class IPQualityScoreProvider(ThreatIntelProvider):
    """
    Async provider adapter for IPQualityScore.

    This class adapts the async fetch_quality(ip) function to the unified
    ThreatIntelProvider interface.

    Expected normalized output fields:
        fraud_score: int | None
        vpn_proxy: bool | None

    Any failure (network error, invalid key, unexpected response structure)
    results in a safe fallback object containing None values.
    """

    @property
    def name(self) -> str:
        return "IPQualityScore"

    @property
    def fields(self) -> tuple:
        """
        Declares the exact output fields produced by this provider.
        The aggregator relies on this list when merging results.
        """
        return ("fraud_score", "vpn_proxy")

    async def fetch(self, ip: str) -> Dict:
        """
        Fetches fraud_score and VPN/proxy indicators for the specified IP.

        Returns:
            {
                "fraud_score": int | None,
                "vpn_proxy": bool | None
            }

        The provider guarantees that all keys specified in self.fields
        are always present in the returned dict.
        """

        fallback = {
            "fraud_score": None,
            "vpn_proxy": None,
        }

        try:
            # Call the async external API wrapper
            result = await fetch_quality(ip)
        except Exception as e:
            log.warning(f"[IPQualityScore] Exception during fetch: {repr(e)}")
            return fallback

        # Map external result keys → unified provider fields
        return {
            "fraud_score": result.get("fraud_score"),
            "vpn_proxy": result.get("vpn"),   # Correct alignment of field name
        }
