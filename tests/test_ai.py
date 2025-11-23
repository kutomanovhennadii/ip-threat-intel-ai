import json
import importlib
import src.ai.llm_client as llm


def test_ai_success(monkeypatch):
    # Set the API key BEFORE importing the module fully
    monkeypatch.setenv("GROQ_API_KEY", "TESTKEY")
    importlib.reload(llm)

    # Ensure the module-level variable reflects the env
    llm.GROQ_API_KEY = "TESTKEY"

    #
    # Correct mock structure that 1:1 matches what llm_client expects:
    # response.choices[0].message["content"]
    #

    class MockChoice:
        def __init__(self, content: str):
            self.message = {"content": content}

    class MockResponse:
        def __init__(self):
            payload = {
                "risk_level": "High",
                "analysis": "OK",
                "recommendations": "Do something",
            }
            self.choices = [MockChoice(json.dumps(payload))]

    class MockCompletions:
        def create(self, *args, **kwargs):
            return MockResponse()

    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()

    class MockClient:
        def __init__(self):
            self.chat = MockChat()

    # Patch the real Groq client
    monkeypatch.setattr(llm, "client", MockClient())

    result = llm.analyze_with_llm({"ip": "8.8.8.8"})

    assert result["risk_level"] == "High"
    assert result["analysis"] == "OK"
    assert result["recommendations"] == "Do something"


def test_ai_fallback(monkeypatch):
    # No API key -> should return fallback
    monkeypatch.setenv("GROQ_API_KEY", "")
    importlib.reload(llm)
    llm.GROQ_API_KEY = ""

    result = llm.analyze_with_llm({"ip": "1.1.1.1"})
    assert result["risk_level"] == "Unknown"
