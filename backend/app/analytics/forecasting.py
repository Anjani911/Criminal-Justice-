"""
Forecasting helpers for crime prediction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from sklearn.linear_model import LinearRegression


@dataclass(frozen=True)
class ForecastOutput:
    model_name: str
    predicted_values: List[float]
    total_predicted: int
    confidence: float
    trend_direction: str
    explanation: str


class CrimeForecaster:
    """Simple, explainable forecasting using linear regression with fallback."""

    def forecast_series(self, series: List[Dict[str, Any]], horizon_days: int) -> ForecastOutput:
        ordered = sorted(series, key=lambda item: item["date"])
        counts = [float(item["count"]) for item in ordered]

        if not counts:
            return ForecastOutput(
                model_name="NoData",
                predicted_values=[],
                total_predicted=0,
                confidence=0.0,
                trend_direction="stable",
                explanation="No historical incidents were available for forecasting.",
            )

        if len(counts) < 4:
            predicted_values = self._moving_average_forecast(counts, horizon_days)
            confidence = round(min(0.65, 0.25 + 0.1 * len(counts)), 2)
            model_name = "MovingAverageFallback"
        else:
            model = LinearRegression()
            x_values = [[index] for index in range(len(counts))]
            model.fit(x_values, counts)
            future_x = [[index] for index in range(len(counts), len(counts) + horizon_days)]
            predicted_values = [max(0.0, float(value)) for value in model.predict(future_x)]
            score = model.score(x_values, counts) if len(set(counts)) > 1 else 0.0
            confidence = round(min(0.95, max(0.35, 0.35 + (score * 0.5) + min(len(counts), 30) / 100.0)), 2)
            model_name = "LinearRegression"

        total_predicted = int(round(sum(predicted_values)))
        trend_direction = self._trend_direction(counts, predicted_values)
        explanation = self._build_explanation(counts, predicted_values, trend_direction, model_name)
        return ForecastOutput(
            model_name=model_name,
            predicted_values=predicted_values,
            total_predicted=total_predicted,
            confidence=confidence,
            trend_direction=trend_direction,
            explanation=explanation,
        )

    def score_station_risk(self, features: Dict[str, Any]) -> Dict[str, Any]:
        recent_7d = float(features.get("recent_7d", 0))
        previous_7d = float(features.get("previous_7d", 0))
        average_daily_count = float(features.get("average_daily_count", 0))
        violent_share = float(features.get("violent_share", 0))
        repeat_offender_ratio = float(features.get("repeat_offender_ratio", 0))
        growth_pct = float(features.get("growth_pct", 0))
        total_records = float(features.get("total_records", 0))

        recent_pressure = min(1.0, recent_7d / max((average_daily_count * 7.0), 1.0))
        growth_pressure = min(1.0, max(growth_pct, 0.0) / 100.0)
        repeat_pressure = min(1.0, repeat_offender_ratio)
        volume_pressure = min(1.0, total_records / 50.0)

        raw_score = (
            (recent_pressure * 35.0)
            + (growth_pressure * 25.0)
            + (violent_share * 20.0)
            + (repeat_pressure * 15.0)
            + (volume_pressure * 5.0)
        )
        risk_score = round(min(100.0, max(0.0, raw_score)), 2)
        confidence = round(min(0.95, max(0.35, 0.4 + min(total_records, 60.0) / 100.0)), 2)
        risk_level = self._risk_level(risk_score)

        explanation = (
            f"Risk was assigned using recent crime volume ({int(recent_7d)} incidents in 7 days), "
            f"growth rate ({growth_pct:.1f}%), violent crime share ({violent_share:.1%}), "
            f"and repeat offender ratio ({repeat_offender_ratio:.1%})."
        )

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence": confidence,
            "model_name": "WeightedRiskHeuristic",
            "explanation": explanation,
            "features_used": {
                "recent_7d": int(recent_7d),
                "previous_7d": int(previous_7d),
                "growth_pct": round(growth_pct, 2),
                "average_daily_count": round(average_daily_count, 4),
                "violent_share": round(violent_share, 4),
                "repeat_offender_ratio": round(repeat_offender_ratio, 4),
                "total_records": int(total_records),
            },
        }

    def _moving_average_forecast(self, counts: List[float], horizon_days: int) -> List[float]:
        window = counts[-7:] if len(counts) >= 7 else counts
        average = sum(window) / max(len(window), 1)
        return [max(0.0, average) for _ in range(horizon_days)]

    def _trend_direction(self, counts: List[float], predicted_values: List[float]) -> str:
        recent_average = sum(counts[-3:]) / max(len(counts[-3:]), 1)
        forecast_average = sum(predicted_values[:3]) / max(len(predicted_values[:3]), 1)
        if forecast_average > recent_average * 1.05:
            return "upward"
        if forecast_average < recent_average * 0.95:
            return "downward"
        return "stable"

    def _build_explanation(self, counts: List[float], predicted_values: List[float], trend_direction: str, model_name: str) -> str:
        recent_average = sum(counts[-7:]) / max(len(counts[-7:]), 1)
        forecast_average = sum(predicted_values) / max(len(predicted_values), 1)
        return (
            f"{model_name} forecast compared the recent average of {recent_average:.1f} incidents "
            f"with the projected average of {forecast_average:.1f} incidents, indicating a {trend_direction} trend."
        )

    def _risk_level(self, score: float) -> str:
        if score >= 75:
            return "CRITICAL"
        if score >= 50:
            return "HIGH"
        if score >= 25:
            return "MEDIUM"
        return "LOW"


forecaster = CrimeForecaster()
