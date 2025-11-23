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
        print(f"[IPAPI] No IPAPI_KEY provided. Using fallback for {ip}")
        return fallback

    # Build request URL
    url = f"https://ipapi.co/{ip}/json/?api_key={IPAPI_KEY}"

    try:
        # Perform real async HTTP GET request
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
    except Exception as e:
        # Network or request failure
        print(f"[IPAPI] Network error for {ip}: {e!r}")
        return fallback

    # If non-200 response — fallback
    if resp.status_code != 200:
        print(
            f"[IPAPI] Bad status {resp.status_code} for {ip}. "
            f"Body preview: {resp.text[:200]!r}"
        )
        return fallback

    try:
        # Parse response as JSON
        data = resp.json()
    except Exception as e:
        print(
            f"[IPAPI] JSON parse error for {ip}: {e!r}. "
            f"Raw response: {resp.text[:200]!r}"
        )
        return fallback

    # Return parsed fields
    return {
        "hostname": data.get("hostname"),
        "isp": data.get("org") or data.get("asn"),  # Prefer org, fallback to ASN
        "country": data.get("country_name"),
    }
