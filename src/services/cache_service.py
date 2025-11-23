import time

class CacheService:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self.store = {}      # { ip: { "ts": float, "data": dict } }

    def get(self, ip: str):
        entry = self.store.get(ip)
        if not entry:
            return None

        if time.time() - entry["ts"] > self.ttl:
            # expired → deletion + miss
            del self.store[ip]
            return None

        return entry["data"]

    def set(self, ip: str, data: dict):
        self.store[ip] = {
            "ts": time.time(),
            "data": data
        }
