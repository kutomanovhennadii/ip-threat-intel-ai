from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import ipaddress

app = FastAPI()

# --- CORS (минимально, на будущее UI) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Валидация IP ---
def validate_ip(ip: str) -> str:
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address")


# --- Маршрут ---
@app.get("/api/analyze-ip")
def analyze_ip(ip: str):
    validate_ip(ip)

    # Заглушка — просто проверяем, что маршрут жив
    return {
        "ip": ip,
        "raw": {},
        "ai": {
            "risk_level": None,
            "analysis": None,
            "recommendations": None,
        }
    }
