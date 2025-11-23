import os
import json
import re
import logging
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
log = logging.getLogger("llm_client")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


JSON_BLOCK_RE = re.compile(r"```json(.*?)```", re.DOTALL)


def extract_json_block(text: str):
    """Извлекает JSON внутри ```json ... ``` или возвращает None."""
    m = JSON_BLOCK_RE.search(text)
    if m:
        return m.group(1).strip()
    return text  # fallback — вдруг это чистый JSON


def analyze_with_llm(threat_data: dict) -> dict:
    fallback = {
        "risk_level": "Unknown",
        "analysis": "LLM analysis unavailable.",
        "recommendations": "Fallback: manual review recommended.",
    }

    if not GROQ_API_KEY:
        log.debug("[FALLBACK] No API key")
        return fallback

    prompt = f"""
        Analyze the following IP threat intelligence and return STRICT JSON only.

        Required JSON schema:
        {{
          "risk_level": "Low" | "Medium" | "High",
          "analysis": "string",
          "recommendations": "string"
        }}

        Data:
        {json.dumps(threat_data, ensure_ascii=False)}
        """

    try:
        log.debug("[LLM] calling Groq...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Return ONLY JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        raw_message = response.choices[0].message
        content = raw_message.content  # Главное исправление!
        log.debug(f"[LLM] Raw content: {content}")

        json_text = extract_json_block(content)
        data = json.loads(json_text)

        if (
            "risk_level" in data
            and "analysis" in data
            and "recommendations" in data
        ):
            return data

        return fallback

    except Exception as e:
        log.debug(f"[ERROR] {e!r}")
        return fallback
