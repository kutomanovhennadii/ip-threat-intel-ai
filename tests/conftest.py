import sys
import os
import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
