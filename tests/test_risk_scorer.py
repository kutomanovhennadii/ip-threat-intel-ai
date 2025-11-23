import pytest
from src.services.risk_scorer import RiskScorer


# ------------------------------------------------------------
# Basic configuration
# ------------------------------------------------------------

@pytest.fixture
def scorer():
    return RiskScorer(
        max_values={
            "abuse_score": 100,
            "fraud_score": 100,
            "vt_score": 20,
        }
    )


# ------------------------------------------------------------
# Normalization tests
# ------------------------------------------------------------

def test_normalization_valid(scorer):
    assert scorer._normalize(50, 100) == 0.5
    assert scorer._normalize(10, 20) == 0.5


def test_normalization_clipping(scorer):
    # Above max → clipped to 1.0
    assert scorer._normalize(999, 100) == 1.0
    assert scorer._normalize(30, 20) == 1.0

    # Below 0 → clipped to 0
    assert scorer._normalize(-5, 100) == 0.0


def test_normalization_invalid(scorer):
    assert scorer._normalize(None, 100) is None
    assert scorer._normalize("abc", 100) is None
    assert scorer._normalize(50, 0) is None
    assert scorer._normalize(50, -10) is None


# ------------------------------------------------------------
# Composite score tests
# ------------------------------------------------------------

def test_score_all_signals_present(scorer):
    data = {
        "abuse_score": 50,   # 0.5
        "fraud_score": 100,  # 1.0
        "vt_score": 10,      # 0.5
    }
    result = scorer.compute(data)
    assert result == pytest.approx((0.5 + 1.0 + 0.5) / 3, rel=1e-4)


def test_score_partial_missing(scorer):
    data = {
        "abuse_score": 80,  # 0.8
        "fraud_score": None,
        "vt_score": None,
    }
    result = scorer.compute(data)
    assert result == pytest.approx(0.8, rel=1e-4)


def test_score_two_missing(scorer):
    data = {
        "abuse_score": None,
        "fraud_score": 100,  # 1.0
        "vt_score": None,
    }
    result = scorer.compute(data)
    assert result == pytest.approx(1.0, rel=1e-4)


def test_score_all_missing(scorer):
    data = {
        "abuse_score": None,
        "fraud_score": None,
        "vt_score": None,
    }
    assert scorer.compute(data) is None


def test_score_invalid_values(scorer):
    data = {
        "abuse_score": "abc",   # invalid
        "fraud_score": 50,      # 0.5
        "vt_score": "??",       # invalid
    }
    result = scorer.compute(data)
    assert result == pytest.approx(0.5, rel=1e-4)


def test_score_rounding(scorer):
    data = {
        "abuse_score": 33,  # 0.33
        "fraud_score": 66,  # 0.66
        "vt_score": 5,      # 0.25
    }
    result = scorer.compute(data)
    assert isinstance(result, float)
    assert round(result, 4) == result
