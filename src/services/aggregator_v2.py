import asyncio
from typing import Dict, List

from src.services.providers_registry import PROVIDERS
from src.services.risk_scorer import RiskScorer


# Fixed output shape to ensure consistent API response.
DEFAULT_SHAPE = {
    "hostname": None,
    "isp": None,
    "country": None,
    "abuse_score": None,
    "recent_reports": None,
    "fraud_score": None,
    "vpn_proxy": None,
    "vt_score": None,
}


SCORER = RiskScorer(
    max_values={
        "abuse_score": 100,
        "fraud_score": 100,
        "vt_score": 20,
    }
)



async def aggregate_ip_data_v2(ip: str) -> Dict:
    """
    Aggregates threat-intel data from all registered providers.
    Uses async fetch, unified schema, graceful fallback on errors,
    and applies composite risk scoring at the end.
    """

    # Pre-fill output with default structure
    merged: Dict = {"ip": ip, **DEFAULT_SHAPE}

    # Launch all providers concurrently
    tasks = [provider.fetch(ip) for provider in PROVIDERS]

    # Gather results without propagating exceptions
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    normalized_results: List[Dict] = []

    # Convert exceptions into fallback dicts
    for provider, result in zip(PROVIDERS, raw_results):
        if isinstance(result, Exception):
            fallback = {field: None for field in provider.fields}
            normalized_results.append(fallback)
        else:
            normalized_results.append(result)

    # Merge provider results
    for result in normalized_results:
        merged.update(result)

    # Compute composite risk score using external RiskScorer
    merged["risk_score"] = SCORER.compute(merged)

    return merged
