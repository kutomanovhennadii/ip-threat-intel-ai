import os
import httpx
from dotenv import load_dotenv

load_dotenv()  

IPQUALITY_API_KEY = os.getenv("IPQUALITYSCORE_API_KEY")
IPQUALITY_URL = "https://ipqualityscore.com/api/json/ip"


def fetch_quality(ip: str) -> dict:
    """
    Возвращает:
      {
        "fraud_score": int | None,
        "vpn": bool | None
      }
    """

    if not IPQUALITY_API_KEY:
        return {"fraud_score": None, "vpn": None}

    url = f"{IPQUALITY_URL}/{IPQUALITY_API_KEY}/{ip}"

    try:
        resp = httpx.get(url, timeout=5.0)
    except Exception:
        return {"fraud_score": None, "vpn": None}

    if resp.status_code != 200:
        return {"fraud_score": None, "vpn": None}

    data = resp.json()

    return {
        "fraud_score": data.get("fraud_score"),
        "vpn": data.get("vpn"),
    }
