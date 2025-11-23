from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio

from src.services.aggregator import aggregate_ip_data
from src.services.aggregator_v2 import aggregate_ip_data_v2
from src.ai.llm_client import analyze_with_llm
from src.validators.ip_validator import IPValidator
from src.services.cache_service import CacheService


# Toggle which aggregator is used globally
USE_V2 = True
cache = CacheService(ttl_seconds=300)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/analyze-ip")
async def analyze_ip(ip: str):
    # 1. Validate IP address
    IPValidator.validate(ip)

    # 2. Try cache first
    cached = cache.get(ip)
    if cached:
        print(f"[CACHE] HIT for {ip}")
        return cached

    # 3. Select correct aggregator via toggle
    if USE_V2:
        raw = await aggregate_ip_data_v2(ip)
    else:
        raw = await aggregate_ip_data(ip)

    # 4. Run LLM in thread
    ai_result = await asyncio.to_thread(analyze_with_llm, raw)

    # 5. Unified response object
    response = {
        **raw,
        "risk_level": ai_result.get("risk_level"),
        "risk_analysis": ai_result.get("analysis"),
        "recommendations": ai_result.get("recommendations"),
    }

    # 6. Save to cache
    cache.set(ip, response)
    print(f"[CACHE] STORE for {ip}")

    return response


# Serve static frontend
app.mount("/", StaticFiles(directory="src/static", html=True), name="static")
