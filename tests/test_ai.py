import json
import importlib
import pytest
import src.ai.llm_client as llm


def test_ai_success(monkeypatch):
    # Purpose: verify successful LLM parsing returns correct values.

    # Arrange
    monkeypatch.setenv("GROQ_API_KEY", "TESTKEY")
    importlib.reload(llm)

    payload = {
        "risk_level": "High",
        "analysis": "OK",
        "recommendations": "Do something",
    }

    class MockMessage:
        def __init__(self, c):
            self.content = c

    class MockChoice:
        def __init__(self, c):
            self.message = MockMessage(c)

    class MockResponse:
        def __init__(self, c):
            self.choices = [MockChoice(c)]

    class MockCompletions:
        def create(self, *a, **kw):
            return MockResponse(json.dumps(payload))

    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()

    class MockClient:
        def __init__(self):
            self.chat = MockChat()

    monkeypatch.setattr(llm, "client", MockClient())

    # Act
    result = llm.analyze_with_llm({"ip": "8.8.8.8"})

    # Assert
    assert result["risk_level"] == "High"
    assert result["analysis"] == "OK"
    assert result["recommendations"] == "Do something"


def test_ai_fallback(monkeypatch):
    # Purpose: ensure fallback is returned when API key missing.

    # Arrange
    monkeypatch.setenv("GROQ_API_KEY", "")
    importlib.reload(llm)

    # Act
    result = llm.analyze_with_llm({"ip": "1.1.1.1"})

    # Assert
    assert result["risk_level"] == "Unknown"
