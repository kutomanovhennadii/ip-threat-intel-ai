import os
import json
import logging
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
log = logging.getLogger("llm_client")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

FALLBACK = {
    "risk_level": "Unknown",
    "analysis": "LLM analysis unavailable.",
    "recommendations": "Fallback: manual review recommended.",
}


# ------------------------------------------------------------
# 1. PROMPT BUILDER
# ------------------------------------------------------------
def generate_prompt(threat_data: dict) -> str:
    return (
        "You MUST return ONLY a valid JSON object.\n"
        "No text before it. No text after it. No code fences.\n"
        "Schema:\n"
        "{\n"
        '  "risk_level": "Low" | "Medium" | "High",\n'
        '  "analysis": "string",\n'
        '  "recommendations": "string"\n'
        "}\n\n"
        "Input data:\n"
        f"{json.dumps(threat_data, ensure_ascii=False)}"
    )


# ------------------------------------------------------------
# 2. RAW CALL TO LLM (NO PARSING)
# ------------------------------------------------------------
def call_llm(prompt: str) -> str | None:
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Return ONLY JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        log.debug(f"[LLM ERROR] {e}")
        return None


# ------------------------------------------------------------
# 3. JSON EXTRACTOR / SELF-REPAIR
# ------------------------------------------------------------
def try_parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def extract_json_block(text: str):
    """
    Пробуем найти JSON в тексте:
    — чистый json
    — json внутри мусора
    """
    # 1. Прямая попытка
    data = try_parse_json(text)
    if data is not None:
        return data

    # 2. Отрезаем текст по первой { и последней }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        fragment = text[start : end + 1]
        data = try_parse_json(fragment)
        if data is not None:
            return data

    return None


def repair_json(text: str) -> dict | None:
    """
    Просим LLM исправить JSON. Второй шанс.
    """
    fix_prompt = (
        "Fix the following text into a VALID JSON object. "
        "Return ONLY the valid JSON.\n\n"
        f"{text}"
    )

    fixed = call_llm(fix_prompt)
    if not fixed:
        return None

    return extract_json_block(fixed)


# ------------------------------------------------------------
# 4. MAIN ENTRY POINT
# ------------------------------------------------------------
def analyze_with_llm(threat_data: dict) -> dict:
    if not GROQ_API_KEY:
        return FALLBACK

    # 1) Собираем промпт
    prompt = generate_prompt(threat_data)

    # 2) Получаем сырой ответ
    raw = call_llm(prompt)
    if raw is None:
        return FALLBACK

    # 3) Парсим JSON из ответа
    parsed = extract_json_block(raw)
    if parsed is not None:
        return parsed

    # 4) Попытка self-repair
    repaired = repair_json(raw)
    if repaired is not None:
        return repaired

    # 5) Fallback
    return FALLBACK
