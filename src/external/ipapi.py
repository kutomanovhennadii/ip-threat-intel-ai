import os
import httpx
from dotenv import load_dotenv

load_dotenv()

IPAPI_KEY = os.getenv("IPAPI_KEY")


async def fetch_ipapi(ip: str) -> dict:
    """
    Fetches hostname, ISP, and country information for the given IP using IPAPI.io.
    Returns a safe fallback object on any failure.
    """

    fallback = {
        "hostname": None,
        "isp": None,
        "country": None,
    }

    if not IPAPI_KEY:
        return fallback

    url = f"https://ipapi.co/{ip}/json/?api_key={IPAPI_KEY}"

    try:
        resp = httpx.get(url, timeout=5.0)
    except Exception:
        return fallback

    if resp.status_code != 200:
        return fallback

    try:
        data = resp.json()
    except Exception:
        return fallback

    return {
        "hostname": data.get("hostname"),
        "isp": data.get("org") or data.get("asn"),
        "country": data.get("country_name"),
    }
