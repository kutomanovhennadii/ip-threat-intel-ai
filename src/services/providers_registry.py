# src/services/providers_registry.py

from src.services.providers.abuseipdb_provider import AbuseIPDBProvider
from src.services.providers.ipquality_provider import IPQualityScoreProvider
from src.services.providers.ipapi_provider import IPAPIProvider
from src.services.providers.virustotal_provider import VirusTotalProvider

"""
Central registry of all threat-intel providers.
Aggregator imports this list and runs all providers uniformly.

Adding new data sources does not require modifying the aggregator:
just append another provider class to PROVIDERS.
"""

PROVIDERS = [
    AbuseIPDBProvider(),
    IPQualityScoreProvider(),
    IPAPIProvider(),
    VirusTotalProvider(),
]
