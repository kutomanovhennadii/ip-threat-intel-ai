import asyncio

from src.external.abuseipdb import fetch_abuse
from src.external.ipquality import fetch_quality
from src.external.virustotal import fetch_virustotal
from src.external.ipapi import fetch_ipapi


def compute_risk_score(data):
    # Computes an average of available numeric risk indicators.
    # If no indicators exist, returns None.
    values = []

    if data.get("abuse_score") is not None:
        values.append(data["abuse_score"])

    if data.get("fraud_score") is not None:
        values.append(data["fraud_score"])

    # If no numeric values, return None
    if not values:
        return None

    # Return arithmetic mean of collected values
    return sum(values) / len(values)


async def aggregate_ip_data(ip: str) -> dict:
    # Aggregates all external threat-intel sources for a given IP.
    # Mixes sync (thread-pooled) and async calls, then merges results.
    # Produces a unified dictionary including computed risk_score.

    # Launch sync functions in thread pool
    abuse_t = asyncio.to_thread(fetch_abuse, ip)
    quality_t = asyncio.to_thread(fetch_quality, ip)
    vt_t = asyncio.to_thread(fetch_virustotal, ip)

    # Launch async function normally
    ipapi_t = fetch_ipapi(ip)   # DO NOT wrap in to_thread

    # Await all tasks concurrently
    abuse, quality, ipapi, vt = await asyncio.gather(
        abuse_t, quality_t, ipapi_t, vt_t
    )

    # Assemble unified result object
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

    # Compute normalized risk score
    result["risk_score"] = compute_risk_score(result)

    return result
