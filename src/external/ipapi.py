import os
import httpx
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

IPAPI_KEY = os.getenv("IPAPI_KEY")  # Read IPAPI key from environment


async def fetch_ipapi(ip: str) -> dict:
    # Asynchronously fetches hostname, ISP, and country info for a given IP address.
    # Uses the IPAPI.io service and returns a safe fallback on any error.
    """
    Fetches hostname, ISP, and country information for the given IP using IPAPI.io.
    Returns a safe fallback object on any failure.
    """

    # Default safe return object
    fallback = {
        "hostname": None,
        "isp": None,
        "country": None,
    }

    # If no API key — return fallback
    if not IPAPI_KEY:
        return fallback

    # Build request URL
    url = f"https://ipapi.co/{ip}/json/?api_key={IPAPI_KEY}"

    try:
        # Perform HTTP GET request
        resp = httpx.get(url, timeout=5.0)
    except Exception:
        # Network or request failure
        return fallback

    # If non-200 response — fallback
    if resp.status_code != 200:
        return fallback

    try:
        # Parse response as JSON
        data = resp.json()
    except Exception:
        return fallback

    # Return parsed fields
    return {
        "hostname": data.get("hostname"),
        "isp": data.get("org") or data.get("asn"),  # Prefer org, fallback to ASN
        "country": data.get("country_name"),
    }
