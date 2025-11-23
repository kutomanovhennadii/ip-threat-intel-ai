import os
import httpx
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

VT_KEY = os.getenv("VIRUSTOTAL_API_KEY")  # Read VirusTotal API key
VT_URL = "https://www.virustotal.com/vtapi/v2/ip-address/report"  # VT v2 API endpoint


def fetch_virustotal(ip: str) -> dict:
    # Fetches basic VirusTotal v2 IP report.
    # Extracts detection count as a simplified "vt_score".
    # Returns safe fallback if any error occurs.
    """
    VirusTotal API v2.
    Возвращает:
    {
        "vt_score": int | None
    }
    """

    # If no API key — return fallback immediately
    if not VT_KEY:
        return {"vt_score": None}

    try:
        # Send HTTP GET request to VirusTotal API v2
        resp = httpx.get(
            VT_URL,
            params={"apikey": VT_KEY, "ip": ip},
            timeout=8.0
        )
    except Exception:
        # Any network or request failure → fallback
        return {"vt_score": None}

    # Non-200 status means error
    if resp.status_code != 200:
        return {"vt_score": None}

    try:
        # Parse JSON response body
        data = resp.json()
    except Exception:
        return {"vt_score": None}

    # VirusTotal API v2 does not provide "malicious" field.
    # Use number of detected URLs as a basic indicator.
    vt_score = len(data.get("detected_urls", []))

    # Return normalized result
    return {"vt_score": vt_score}
