from datetime import datetime, timedelta

def contains_any_keyword(text: str, keywords: set[str]) -> bool:
    t = (text or "").lower()
    return any(k.lower() in t for k in keywords)

def clamp01(x: float) -> float:
        return 0.0 if x < 0 else 1.0 if x > 1 else x
    
def recency_score(received_at: datetime, now: datetime) -> float:
        age = now - received_at
        if age <= timedelta(hours=6): return 1.0
        if age <= timedelta(days=1): return 0.8
        if age <= timedelta(days=3): return 0.6
        if age <= timedelta(days=7): return 0.4
        return 0.2