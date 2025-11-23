# src/services/base_provider.py

import abc
from typing import Dict


class ThreatIntelProvider(abc.ABC):
    """
    Base interface for all threat-intelligence data providers.
    Every provider must implement a fully asynchronous fetch() method.
    Providers hide internal API logic and expose only normalized fields.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Human-readable provider identifier.
        Used for logging, debugging, and registry inspection.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def fields(self) -> tuple:
        """
        Tuple of field names returned by this provider.
        Example: ("abuse_score", "recent_reports")
        The aggregator uses this to merge provider results safely.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def fetch(self, ip: str) -> Dict:
        """
        Asynchronous method that returns a dictionary containing only
        keys declared in self.fields. Each key must always exist.

        On success:
            return {"abuse_score": 42, "recent_reports": 3}

        On failure:
            return {"abuse_score": None, "recent_reports": None}

        No exceptions must ever propagate out of fetch();
        providers must handle their own errors gracefully and
        always return a well-formed result dictionary.
        """
        raise NotImplementedError
