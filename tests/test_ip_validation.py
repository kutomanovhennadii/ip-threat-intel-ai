import pytest
from fastapi.testclient import TestClient
import sys, os

# Purpose: include project src/ folder in Python path for imports.
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from main import app

client = TestClient(app)


def test_valid_ip():
    # Purpose: valid IPv4 address should be accepted and return 200.

    # Arrange / Act
    r = client.get("/api/analyze-ip?ip=8.8.8.8")

    # Assert
    assert r.status_code == 200


def test_invalid_ip():
    # Purpose: invalid IP must trigger validator and return 400.

    # Arrange / Act
    r = client.get("/api/analyze-ip?ip=999.999.999.999")

    # Assert
    assert r.status_code == 400
