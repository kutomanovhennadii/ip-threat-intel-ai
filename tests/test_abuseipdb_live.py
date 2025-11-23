import os
import pytest
from src.external.abuseipdb import fetch_abuse



@pytest.mark.skipif(
    not os.getenv("ABUSEIPDB_API_KEY"),
    reason="ABUSEIPDB_API_KEY not set — skipping live API test",
)
def test_abuseipdb_live_real_api():
    """
    Этот тест вызывает реальный API AbuseIPDB.
    Работает только если установлен env-переменная ABUSEIPDB_API_KEY.
    """

    result = fetch_abuse("8.8.8.8")

    # В реальном API допускаем вариации, но важно что результат не пустой
    assert isinstance(result, dict)
    assert "abuse_score" in result
    assert "recent_reports" in result
