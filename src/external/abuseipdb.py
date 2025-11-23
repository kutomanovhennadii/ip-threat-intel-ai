import os
import httpx
from dotenv import load_dotenv

load_dotenv()  

ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/check"


def fetch_abuse(ip: str) -> dict:
    """
    Return dictionary:
    {
        "abuse_score": int | None,
        "recent_reports": int | None
    }
    """

    api_key = os.getenv("ABUSEIPDB_API_KEY")

    if not api_key:
        return {"abuse_score": None, "recent_reports": None}

    try:
        resp = httpx.get(
            ABUSEIPDB_URL,
            params={"ipAddress": ip, "maxAgeInDays": 90},
            headers={"Key": api_key, "Accept": "application/json"},
            timeout=5.0,
        )
    except Exception:
        return {"abuse_score": None, "recent_reports": None}

    if resp.status_code != 200:
        return {"abuse_score": None, "recent_reports": None}

    try:
        data = resp.json().get("data", {})
    except Exception:
        return {"abuse_score": None, "recent_reports": None}

    return {
        "abuse_score": data.get("abuseConfidenceScore"),
        "recent_reports": data.get("totalReports"),
    }
