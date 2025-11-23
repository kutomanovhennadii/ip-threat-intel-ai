import pytest
from fastapi import HTTPException
from src.validators.ip_validator import IPValidator

def test_valid_ip():
    assert IPValidator.validate("8.8.8.8") == "8.8.8.8"

def test_invalid_ip():
    with pytest.raises(HTTPException):
        IPValidator.validate("999.999.999.999")
