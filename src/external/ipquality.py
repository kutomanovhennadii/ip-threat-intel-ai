import os
import httpx
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

IPQUALITY_API_KEY = os.getenv("IPQUALITYSCORE_API_KEY")  # Read IPQualityScore API key
IPQUALITY_URL = "https://ipqualityscore.com/api/json/ip"  # Base URL for IPQS API


def fetch_quality(ip: str) -> dict:
    # Fetches fraud score and VPN status for a given IP using IPQualityScore API.
    # Returns safe None-based fallback on any error or missing API key.
    """
    Возвращает:
      {
        "fraud_score": int | None,
        "vpn": bool | None
      }
    """

    # Early fallback if API key is missing
    if not IPQUALITY_API_KEY:
        return {"fraud_score": None, "vpn": None}

    # Build full request URL
    url = f"{IPQUALITY_URL}/{IPQUALITY_API_KEY}/{ip}"

    try:
        # Perform GET request to IPQS API
        resp = httpx.get(url, timeout=5.0)
    except Exception:
        # Network failure or timeout
        return {"fraud_score": None, "vpn": None}

    # If status code is not OK — fallback
    if resp.status_code != 200:
        return {"fraud_score": None, "vpn": None}

    # Parse JSON response (assumes valid JSON from API)
    data = resp.json()

    # Return normalized data fields
    return {
        "fraud_score": data.get("fraud_score"),
        "vpn": data.get("vpn"),
    }
