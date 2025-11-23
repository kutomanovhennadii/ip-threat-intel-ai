import os
import httpx
from dotenv import load_dotenv

# Load variables
load_dotenv()

IPQUALITY_API_KEY = os.getenv("IPQUALITYSCORE_API_KEY")
BASE_URL = "https://ipqualityscore.com/api/json/ip"


async def fetch_quality(ip: str) -> dict:
    """
    Correct async version for IPQualityScore.
    Works stably even when the server breaks TLS handshake
    or responds with a non-standard chain.
    """

    # Missing key → fallback
    if not IPQUALITY_API_KEY:
        print(f"[IPQS] No IPQUALITYSCORE_API_KEY provided. Using fallback for {ip}")
        return {
            "fraud_score": None,
            "vpn": None,
        }

    url = f"{BASE_URL}/{IPQUALITY_API_KEY}/{ip}"

    try:
        # The ONLY reliable way to call IPQS async:
        # - disable strict certificate verification
        # - use explicit AsyncHTTPTransport
        # - allow retries (server often drops first connection)
        transport = httpx.AsyncHTTPTransport(retries=2)

        async with httpx.AsyncClient(
            transport=transport,
            verify=False,     # IPQS free-tier often has broken cert chain
            timeout=8.0
        ) as client:
            resp = await client.get(url)

    except Exception as e:
        print(f"[IPQS] Network/TLS error for {ip}: {e!r}")
        return {
            "fraud_score": None,
            "vpn": None,
        }

    # Wrong HTTP status → fallback (but first print diagnostic)
    if resp.status_code != 200:
        print(
            f"[IPQS] Bad status {resp.status_code} for {ip}. "
            f"Body preview: {resp.text[:200]!r}"
        )
        return {
            "fraud_score": None,
            "vpn": None,
        }

    try:
        data = resp.json()
    except Exception as e:
        print(
            f"[IPQS] JSON parse error for {ip}: {e!r}. "
            f"Raw response: {resp.text[:200]!r}"
        )
        return {
            "fraud_score": None,
            "vpn": None,
        }

    # Special case: IPQS returns success=False with quota or key errors
    if not data.get("success", True):
        message = data.get("message", "")
        print(f"[IPQS] API error for {ip}: success=False, message={message!r}")

        # Specific detection: DAILY QUOTA EXHAUSTED
        if "exceeded your request quota" in message:
            print(f"[IPQS] DAILY QUOTA EXHAUSTED for key. Raw={data!r}")

        return {
            "fraud_score": None,
            "vpn": None,
        }

    # Normal behavior
    return {
        "fraud_score": data.get("fraud_score"),
        "vpn": data.get("vpn"),
    }
