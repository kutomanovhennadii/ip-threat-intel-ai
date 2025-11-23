# src/validators/ip_validator.py

import ipaddress
from fastapi import HTTPException


class IPValidator:
    """
    Responsible for validating IPv4/IPv6 addresses.
    This allows future extension (CIDR, private ranges, blacklists, etc.)
    """

    @staticmethod
    def validate(ip: str) -> str:
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid IP address format")

        return ip
