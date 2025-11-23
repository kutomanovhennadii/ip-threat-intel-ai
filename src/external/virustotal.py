import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

VT_KEY = os.getenv("VIRUSTOTAL_API_KEY")

# Proper VirusTotal v3 endpoint (required by assignment)
VT_URL = "https://www.virustotal.com/api/v3/ip_addresses/"


async def fetch_virustotal(ip: str) -> dict:
    """
    Asynchronously fetches VirusTotal v3 IP report.

    IMPORTANT:
    The API key provided in the assignment does NOT work with
    ANY VirusTotal API family (v3, v2, legacy, or UI API).
    VirusTotal consistently returns:

        {"error": {"code": "WrongCredentialsError", "message": "Wrong API key"}}

    or HTTP 403 Forbidden on legacy/v2 endpoints.

    Because of this, vt_score will always be None when using the assignment key.
    """

    fallback = {"vt_score": None}

    if not VT_KEY:
        print(f"[VT] No VIRUSTOTAL_API_KEY provided. Using fallback for {ip}")
        return fallback

    url = f"{VT_URL}{ip}"

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, headers={"x-apikey": VT_KEY})
    except Exception as e:
        print(f"[VT] Network error for {ip}: {e!r}")
        return fallback

    # Handle non-200 responses
    if resp.status_code != 200:
        print(
            f"[VT] Bad status {resp.status_code} for {ip}. "
            f"Body preview: {resp.text[:200]!r}"
        )
        return fallback

    try:
        data = resp.json()
    except Exception as e:
        print(
            f"[VT] JSON parse error for {ip}: {e!r}. "
            f"Raw response: {resp.text[:200]!r}"
        )
        return fallback

    # Detect WrongCredentialsError explicitly
    if "error" in data:
        err = data["error"]
        code = err.get("code")
        msg = err.get("message")

        print(f"[VT] API error for {ip}: code={code!r}, message={msg!r}")

        if code == "WrongCredentialsError":
            print("[VT] Provided key is invalid or not recognized by VirusTotal.")

        return fallback

    # v3 schema: malicious count resides in attributes.last_analysis_stats
    stats = (
        data.get("data", {})
        .get("attributes", {})
        .get("last_analysis_stats", {})
    )

    # Combine malicious + suspicious as heuristic
    vt_score = (
        stats.get("malicious", 0) +
        stats.get("suspicious", 0)
    )

    return {"vt_score": vt_score}
