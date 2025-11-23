from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import ipaddress
import asyncio

from src.services.aggregator import aggregate_ip_data
from src.ai.llm_client import analyze_with_llm
from src.validators.ip_validator import IPValidator

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API ENDPOINT
@app.get("/api/analyze-ip")
async def analyze_ip(ip: str):
    # 1) Validate IP
    IPValidator.validate(ip)

    # 2) Fetch threat intel
    raw = await aggregate_ip_data(ip)

    # 3) AI analysis
    ai_result = await asyncio.to_thread(analyze_with_llm, raw)

    # 4) Final object
    return {
        **raw,
        "risk_level": ai_result.get("risk_level"),
        "risk_analysis": ai_result.get("analysis"),
        "recommendations": ai_result.get("recommendations"),
    }

# STATIC FILES — ОЧЕНЬ ВАЖНО: В САМОМ КОНЦЕ!
app.mount("/", StaticFiles(directory="src/static", html=True), name="static")
