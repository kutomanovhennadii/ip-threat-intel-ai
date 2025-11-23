import json
import importlib
import pytest
import src.ai.llm_client as llm


# ------------------------------------------------------------
# 1. generate_prompt
# ------------------------------------------------------------
def test_generate_prompt_format():
    prompt = llm.generate_prompt({"ip": "8.8.8.8"})
    assert "You MUST return ONLY a valid JSON object" in prompt
    assert '{"ip": "8.8.8.8"}' in prompt


# ------------------------------------------------------------
# 2. extract_json_block
# ------------------------------------------------------------
def test_extract_json_block_clean():
    text = '{"risk_level": "Low", "analysis": "X", "recommendations": "Y"}'
    parsed = llm.extract_json_block(text)
    assert parsed["risk_level"] == "Low"


def test_extract_json_block_dirty():
    text = "blah blah {\"risk\": 1, \"x\":2} trailing"
    parsed = llm.extract_json_block(text)
    assert parsed == {"risk": 1, "x": 2}


def test_extract_json_block_fail():
    text = "no json here"
    parsed = llm.extract_json_block(text)
    assert parsed is None


# ------------------------------------------------------------
# 3. call_llm (мокаем client.chat.completions.create)
# ------------------------------------------------------------
def test_call_llm_success(monkeypatch):
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
        def create(self, *args, **kwargs):
            return MockResponse("OK")

    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()

    class MockClient:
        def __init__(self):
            self.chat = MockChat()

    monkeypatch.setattr(llm, "client", MockClient())

    result = llm.call_llm("prompt")
    assert result == "OK"


def test_call_llm_error(monkeypatch):
    class BadComp:
        def create(self, *a, **k):
            raise RuntimeError("fail")

    class BadChat:
        def __init__(self):
            self.completions = BadComp()

    class BadClient:
        def __init__(self):
            self.chat = BadChat()

    monkeypatch.setattr(llm, "client", BadClient())
    assert llm.call_llm("prompt") is None


# ------------------------------------------------------------
# 4. repair_json
# ------------------------------------------------------------
def test_repair_json_success(monkeypatch):
    # Мокаем LLM чтобы вернуть валидный JSON
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
        def create(self, *args, **kwargs):
            return MockResponse('{"a": 1}')

    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()

    class MockClient:
        def __init__(self):
            self.chat = MockChat()

    monkeypatch.setattr(llm, "client", MockClient())

    result = llm.repair_json("broken")
    assert result == {"a": 1}


def test_repair_json_fail(monkeypatch):
    class BadComp:
        def create(self, *a, **k):
            raise RuntimeError()

    class BadChat:
        def __init__(self):
            self.completions = BadComp()

    class BadClient:
        def __init__(self):
            self.chat = BadChat()

    monkeypatch.setattr(llm, "client", BadClient())
    assert llm.repair_json("broken") is None


# ------------------------------------------------------------
# 5. analyze_with_llм (интеграция)
# ------------------------------------------------------------
def test_analyze_with_llm_success(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "TESTKEY")
    importlib.reload(llm)

    payload = {
        "risk_level": "High",
        "analysis": "OK",
        "recommendations": "Do",
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
        def create(self, *a, **k):
            return MockResponse(json.dumps(payload))

    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()

    class MockClient:
        def __init__(self):
            self.chat = MockChat()

    monkeypatch.setattr(llm, "client", MockClient())

    result = llm.analyze_with_llm({"ip": "8.8.8.8"})

    assert result["risk_level"] == "High"
    assert result["analysis"] == "OK"
    assert result["recommendations"] == "Do"


def test_analyze_with_llm_fallback_no_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    importlib.reload(llm)

    result = llm.analyze_with_llm({"ip": "1.1.1.1"})
    assert result["risk_level"] == "Unknown"
