import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API endpoint for AbuseIPDB IP check
ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/check"


async def fetch_abuse(ip: str) -> dict:
    """
    Asynchronously fetches threat intelligence data from the AbuseIPDB API.
    Returns a normalized dictionary with two fields:
        {
            "abuse_score": int | None,
            "recent_reports": int | None
        }

    The function is fully async and performs real non-blocking network I/O
    via httpx.AsyncClient. All errors (network, HTTP status, JSON parse)
    are handled internally and produce a neutral fallback object.

    Expected schema from AbuseIPDB:
        {
            "data": {
                "ipAddress": "...",
                "abuseConfidenceScore": 42,
                "totalReports": 3,
                ...
            }
        }

    The external API may return partial fields, missing keys, or unusual
    status codes, so all extraction is defensive.
    """

    # Retrieve API key from environment variables.
    # Missing key must not cause exceptions; fallback is returned.
    api_key = os.getenv("ABUSEIPDB_API_KEY")

    if not api_key:
        print(f"[AbuseIPDB] No API key provided. Using fallback for {ip}")
        return {
            "abuse_score": None,
            "recent_reports": None,
        }

    try:
        # Use AsyncClient for non-blocking HTTP I/O.
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                ABUSEIPDB_URL,
                params={"ipAddress": ip, "maxAgeInDays": 90},
                headers={"Key": api_key, "Accept": "application/json"},
            )
    except Exception as e:
        # Network errors: DNS issues, timeouts, connection refused, SSL errors.
        print(f"[AbuseIPDB] Network error for {ip}: {e!r}")
        return {
            "abuse_score": None,
            "recent_reports": None,
        }

    # Non-200 status codes: AbuseIPDB returns meaningful errors,
    # but the service contract for this function requires that we never
    # propagate error states beyond this boundary.
    if resp.status_code != 200:
        print(
            f"[AbuseIPDB] Bad status {resp.status_code} for {ip}. "
            f"Body preview: {resp.text[:200]!r}"
        )
        return {
            "abuse_score": None,
            "recent_reports": None,
        }

    try:
        # Extract the root "data" payload.
        data = resp.json().get("data", {})
    except Exception as e:
        # JSON parsing can fail if a partial or malformed response is returned.
        print(
            f"[AbuseIPDB] JSON parse error for {ip}: {e!r}. "
            f"Raw response: {resp.text[:200]!r}"
        )
        return {
            "abuse_score": None,
            "recent_reports": None,
        }

    # Normalize the fields we expose to the aggregator layer.
    # Missing or invalid fields should not crash the call; they degrade to None.
    return {
        "abuse_score": data.get("abuseConfidenceScore"),
        "recent_reports": data.get("totalReports"),
    }
