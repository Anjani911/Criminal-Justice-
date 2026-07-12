"""
Early warning generation rules.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.analytics.feature_engineering import StationProfile, feature_engineer


class WarningEngine:
    """Generates explainable operational warnings from recent incidents."""

    def generate_warnings(
        self,
        db,
        *,
        district: Optional[str] = None,
        police_station: Optional[str] = None,
    ) -> Dict[str, Any]:
        profiles = feature_engineer.build_warning_features(
            db,
            district=district,
            police_station=police_station,
            lookback_days=14,
        )

        warnings: List[Dict[str, Any]] = []
        for profile in profiles:
            warnings.extend(self._profile_warnings(profile))

        warnings = sorted(warnings, key=lambda item: (item["severity_rank"], item["supporting_statistics"].get("growth_pct", 0)), reverse=True)
        formatted = [self._strip_internal_fields(item) for item in warnings]

        if not formatted:
            return {
                "status": "insufficient_data" if not profiles else "success",
                "generated_at": self._now_iso(),
                "warnings": [],
                "explanation": "No warning thresholds were crossed with the currently available historical data.",
            }

        return {
            "status": "success",
            "generated_at": self._now_iso(),
            "warnings": formatted,
            "explanation": "Warnings were generated using spike detection, repeat-offender signals, and hotspot emergence rules.",
        }

    def _profile_warnings(self, profile: StationProfile) -> List[Dict[str, Any]]:
        warnings: List[Dict[str, Any]] = []
        if self._is_growth_spike(profile.growth_pct, profile.recent_7d, profile.previous_7d):
            category, title = self._dominant_category(profile)
            severity = self._severity_from_growth(profile.growth_pct)
            warnings.append(
                self._warning_payload(
                    severity=severity,
                    title=title,
                    category=category,
                    profile=profile,
                    reason=(
                        f"Crime volume increased by {profile.growth_pct:.1f}% in the last 7 days compared with the previous 7 days."
                    ),
                    supporting_statistics={
                        "recent_7d": profile.recent_7d,
                        "previous_7d": profile.previous_7d,
                        "growth_pct": profile.growth_pct,
                        "violent_share": profile.violent_share,
                    },
                    confidence=min(0.95, 0.5 + min(abs(profile.growth_pct), 100.0) / 200.0),
                )
            )

        if profile.repeat_offender_ratio >= 0.2 and profile.total_records >= 5:
            warnings.append(
                self._warning_payload(
                    severity="HIGH" if profile.repeat_offender_ratio < 0.35 else "CRITICAL",
                    title="Repeat Offender Activity Detected",
                    category="repeat_offender_activity",
                    profile=profile,
                    reason=(
                        f"Repeat offender ratio is {profile.repeat_offender_ratio:.1%}, indicating repeated activity by the same accused names."
                    ),
                    supporting_statistics={
                        "repeat_offender_ratio": profile.repeat_offender_ratio,
                        "total_records": profile.total_records,
                    },
                    confidence=min(0.92, 0.45 + profile.repeat_offender_ratio),
                )
            )

        if profile.violent_share >= 0.35 and profile.recent_7d >= 3:
            warnings.append(
                self._warning_payload(
                    severity="HIGH",
                    title="Violent Crime Increase",
                    category="assault_increase",
                    profile=profile,
                    reason="Violent crimes form a significant share of recent incidents.",
                    supporting_statistics={
                        "violent_share": profile.violent_share,
                        "recent_7d": profile.recent_7d,
                        "total_records": profile.total_records,
                    },
                    confidence=0.74,
                )
            )

        if profile.recent_7d >= 5 and profile.growth_pct >= 30:
            warnings.append(
                self._warning_payload(
                    severity="HIGH" if profile.growth_pct < 60 else "CRITICAL",
                    title="Emerging Hotspot",
                    category="emerging_hotspot",
                    profile=profile,
                    reason="Recent crime volume is rising quickly enough to indicate an emerging hotspot.",
                    supporting_statistics={
                        "recent_7d": profile.recent_7d,
                        "growth_pct": profile.growth_pct,
                        "average_daily_count": profile.average_daily_count,
                    },
                    confidence=min(0.9, 0.55 + min(profile.growth_pct, 100.0) / 200.0),
                )
            )

        return warnings

    def _warning_payload(
        self,
        *,
        severity: str,
        title: str,
        category: str,
        profile: StationProfile,
        reason: str,
        supporting_statistics: Dict[str, Any],
        confidence: float,
    ) -> Dict[str, Any]:
        return {
            "severity": severity,
            "severity_rank": self._severity_rank(severity),
            "title": title,
            "category": category,
            "district": profile.district,
            "police_station": profile.police_station,
            "reason": reason,
            "supporting_statistics": supporting_statistics,
            "timestamp": self._now_iso(),
            "confidence": round(confidence, 2),
        }

    def _strip_internal_fields(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(payload)
        payload.pop("severity_rank", None)
        return payload

    def _is_growth_spike(self, growth_pct: float, recent_7d: int, previous_7d: int) -> bool:
        return recent_7d >= 3 and growth_pct >= 30.0 and recent_7d >= previous_7d

    def _dominant_category(self, profile: StationProfile) -> tuple[str, str]:
        if not profile.crime_mix:
            return "emerging_hotspot", "Emerging Hotspot"
        top_label = profile.crime_mix[0]["crime_label"].lower()
        if "theft" in top_label or "burglary" in top_label:
            return "theft_spike", "Theft Spike"
        if any(word in top_label for word in ("assault", "attack", "homicide", "murder", "rape")):
            return "assault_increase", "Assault Increase"
        if "burglary" in top_label:
            return "burglary_spike", "Burglary Spike"
        return "emerging_hotspot", "Emerging Hotspot"

    def _severity_from_growth(self, growth_pct: float) -> str:
        if growth_pct >= 80:
            return "CRITICAL"
        if growth_pct >= 50:
            return "HIGH"
        if growth_pct >= 30:
            return "MEDIUM"
        return "LOW"

    def _severity_rank(self, severity: str) -> int:
        return {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}.get(severity, 1)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()


warning_engine = WarningEngine()
