# src/services/providers/abuseipdb_provider.py

import asyncio
import logging
from typing import Dict
from src.services.providers.base_provider import ThreatIntelProvider
from src.external.abuseipdb import fetch_abuse

log = logging.getLogger("provider.abuseipdb")


class AbuseIPDBProvider(ThreatIntelProvider):
    """
    Adapter provider for AbuseIPDB.
    Uses existing sync function fetch_abuse(ip) and exposes a clean async interface.
    The provider guarantees stable output and handles all internal errors.
    """

    @property
    def name(self) -> str:
        return "AbuseIPDB"

    @property
    def fields(self) -> tuple:
        return ("abuse_score", "recent_reports")

    async def fetch(self, ip: str) -> Dict:
        fallback = {
            "abuse_score": None,
            "recent_reports": None,
        }

        try:
            result = await fetch_abuse(ip)   # direct await, NO threadpool
        except Exception as e:
            log.warning(f"[AbuseIPDB] Exception: {repr(e)}")
            return fallback

        return {
            "abuse_score": result.get("abuse_score"),
            "recent_reports": result.get("recent_reports"),
        }

