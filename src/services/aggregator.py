import asyncio

from src.external.abuseipdb import fetch_abuse
from src.external.ipquality import fetch_quality
# Эти источники пока не реализованы, но структура должна быть полной:
try:
    from src.external.ipapi import fetch_ipapi
except Exception:
    fetch_ipapi = lambda ip: {"hostname": None, "isp": None, "country": None}

try:
    from src.external.virustotal import fetch_virustotal
except Exception:
    fetch_virustotal = lambda ip: {"vt_score": None}


def compute_risk_score(data):
    values = []

    if data.get("abuse_score") is not None:
        values.append(data["abuse_score"])

    if data.get("fraud_score") is not None:
        values.append(data["fraud_score"])

    if not values:
        return None

    return sum(values) / len(values)


async def aggregate_ip_data(ip: str) -> dict:
    # sync-functions executed in thread pool
    abuse_t = asyncio.to_thread(fetch_abuse, ip)
    quality_t = asyncio.to_thread(fetch_quality, ip)
    vt_t = asyncio.to_thread(fetch_virustotal, ip)

    # async function executed normally
    ipapi_t = fetch_ipapi(ip)   # DO NOT wrap in to_thread

    # await everything
    abuse, quality, ipapi, vt = await asyncio.gather(
        abuse_t, quality_t, ipapi_t, vt_t
    )

    # Assemble result
    result = {
        "ip": ip,
        "hostname": ipapi.get("hostname"),
        "isp": ipapi.get("isp"),
        "country": ipapi.get("country"),

        "abuse_score": abuse.get("abuse_score"),
        "recent_reports": abuse.get("recent_reports"),

        "fraud_score": quality.get("fraud_score"),
        "vpn_proxy": quality.get("vpn"),

        "vt_score": vt.get("vt_score"),
    }

    result["risk_score"] = compute_risk_score(result)

    return result
