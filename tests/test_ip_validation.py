import pytest
from fastapi.testclient import TestClient
import sys, os

# add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from main import app

client = TestClient(app)


def test_valid_ip():
    r = client.get("/api/analyze-ip?ip=8.8.8.8")
    assert r.status_code == 200


def test_invalid_ip():
    r = client.get("/api/analyze-ip?ip=999.999.999.999")
    assert r.status_code == 400
