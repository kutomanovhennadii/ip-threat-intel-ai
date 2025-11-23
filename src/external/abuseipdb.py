import os
import httpx
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/check"


def fetch_abuse(ip: str) -> dict:
    # Fetches AbuseIPDB threat intelligence for a given IP.
    # Returns a dict with abuse score and recent report count.
    """
    Return dictionary:
    {
        "abuse_score": int | None,
        "recent_reports": int | None
    }
    """

    api_key = os.getenv("ABUSEIPDB_API_KEY")  # Read API key from environment

    # If key missing, return neutral values
    if not api_key:
        return {"abuse_score": None, "recent_reports": None}

    try:
        # Perform GET request to AbuseIPDB API
        resp = httpx.get(
            ABUSEIPDB_URL,
            params={"ipAddress": ip, "maxAgeInDays": 90},
            headers={"Key": api_key, "Accept": "application/json"},
            timeout=5.0,
        )
    except Exception:
        # Any network failure returns fallback
        return {"abuse_score": None, "recent_reports": None}

    # If HTTP status unexpected — fallback
    if resp.status_code != 200:
        return {"abuse_score": None, "recent_reports": None}

    try:
        # Parse JSON and extract "data" block
        data = resp.json().get("data", {})
    except Exception:
        return {"abuse_score": None, "recent_reports": None}

    # Return normalized fields
    return {
        "abuse_score": data.get("abuseConfidenceScore"),
        "recent_reports": data.get("totalReports"),
    }
