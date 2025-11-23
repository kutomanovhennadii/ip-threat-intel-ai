from external.abuseipdb import fetch_abuse
from external.ipquality import fetch_quality


def compute_risk_score(abuse: dict, quality: dict) -> float | None:
    """
    Примитивный risk_score:
    - берём поля: abuse_score, fraud_score
    - если отсутствуют → игнорируем
    - итог: среднее двух
    """

    values = []

    if abuse.get("abuse_score") is not None:
        values.append(abuse["abuse_score"])

    if quality.get("fraud_score") is not None:
        values.append(quality["fraud_score"])

    if not values:
        return None

    return sum(values) / len(values)


def aggregate_ip_data(ip: str) -> dict:
    """
    Возвращает единый словарь данных обо всех источниках.
    """

    abuse = fetch_abuse(ip)
    quality = fetch_quality(ip)

    risk_score = compute_risk_score(abuse, quality)

    return {
        "ip": ip,
        "abuse": abuse,
        "quality": quality,
        "risk_score": risk_score,
    }
