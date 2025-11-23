# src/services/providers/ipapi_provider.py

import asyncio
import logging
from typing import Dict
from src.services.providers.base_provider import ThreatIntelProvider
from src.external.ipapi import fetch_ipapi

log = logging.getLogger("provider.ipapi")


class IPAPIProvider(ThreatIntelProvider):
    """
    Adapter provider for IPAPI.io data.
    Calls existing async fetch_ipapi(ip) without threads.
    Returns:
        hostname: str | None
        isp: str | None
        country: str | None
    """

    @property
    def name(self) -> str:
        return "IPAPI"

    @property
    def fields(self) -> tuple:
        return ("hostname", "isp", "country")

    async def fetch(self, ip: str) -> Dict:
        fallback = {"hostname": None, "isp": None, "country": None}

        try:
            # fetch_ipapi is already async — we call directly
            result = await fetch_ipapi(ip)
        except Exception as e:
            log.warning(f"[IPAPI] Exception: {repr(e)}")
            return fallback

        return {
            "hostname": result.get("hostname"),
            "isp": result.get("isp"),
            "country": result.get("country"),
        }
