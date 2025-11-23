class RiskScorer:
    """
    Composite risk scorer using equal weights for all configured signals.
    Each available signal contributes equally to the final score.
    Missing signals simply do not participate.
    """

    def __init__(self, max_values: dict):
        """
        max_values: {
            "abuse_score": 100,
            "fraud_score": 100,
            "vt_score": 20,
        }

        Key = field name in aggregated data
        Value = normalization denominator (max possible value)
        """
        self.max_values = max_values

    def _normalize(self, value, max_value):
        """
        Normalize value into [0, 1].
        Returns None for missing or invalid values.
        """
        if value is None:
            return None

        try:
            v = float(value)
        except Exception:
            return None

        if max_value <= 0:
            return None

        return max(0.0, min(v / max_value, 1.0))

    def compute(self, data: dict):
        """
        Compute the composite score using equal weights.
        Only available signals participate.
        """
        normalized = []

        for field, max_value in self.max_values.items():
            raw_val = data.get(field)
            norm = self._normalize(raw_val, max_value)
            if norm is not None:
                normalized.append(norm)

        if not normalized:
            return None

        # Each available signal contributes equally
        score = sum(normalized) / len(normalized)

        return round(score, 4)
