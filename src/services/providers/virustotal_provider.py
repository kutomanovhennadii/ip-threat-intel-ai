# src/services/providers/virustotal_provider.py

import asyncio
import logging
from typing import Dict
from src.services.providers.base_provider import ThreatIntelProvider
from src.external.virustotal import fetch_virustotal

log = logging.getLogger("provider.virustotal")


class VirusTotalProvider(ThreatIntelProvider):
    """
    Adapter provider for VirusTotal data.
    Uses sync fetch_virustotal(ip) wrapped in a thread.
    Returns:
        vt_score: int | None
    """

    @property
    def name(self) -> str:
        return "VirusTotal"

    @property
    def fields(self) -> tuple:
        return ("vt_score",)

    async def fetch(self, ip: str) -> Dict:
        fallback = {"vt_score": None}

        try:
            # Native async call — no threadpool, no blocking IO
            result = await fetch_virustotal(ip)
        except Exception as e:
            log.warning(f"[VirusTotal] Exception: {repr(e)}")
            return fallback

        return {
            "vt_score": result.get("vt_score"),
        }

