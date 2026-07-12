"""
Feature engineering helpers for predictive analytics.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.case import CaseMaster
from app.models.crime_type import CrimeHead, CrimeSubHead
from app.models.people import Accused


VIOLENT_CRIME_KEYWORDS = {
    "murder",
    "homicide",
    "attempt to murder",
    "assault",
    "rape",
    "kidnapping",
    "robbery",
    "dacoity",
    "attack",
    "grievous",
    "violent",
}


@dataclass(frozen=True)
class StationProfile:
    district: str
    police_station: str
    series: List[Dict[str, Any]]
    crime_mix: List[Dict[str, Any]]
    recent_7d: int
    previous_7d: int
    growth_pct: float
    average_daily_count: float
    violent_cases: int
    violent_share: float
    repeat_offender_ratio: float
    total_records: int
    start_date: Optional[str]
    end_date: Optional[str]


class PredictionFeatureEngineer:
    """Builds compact, explainable feature sets from the FIR database."""

    def build_daily_series(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        police_station: Optional[str] = None,
        crime_head_id: Optional[int] = None,
        crime_subhead_id: Optional[int] = None,
        lookback_days: int = 180,
    ) -> List[Dict[str, Any]]:
        start_date = self._lookback_start(lookback_days)
        query = (
            db.query(
                func.date(CaseMaster.registered_date).label("day"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .filter(CaseMaster.registered_date >= start_date)
            .group_by("day")
            .order_by("day")
        )
        query = self._apply_case_filters(query, district, police_station, crime_head_id, crime_subhead_id)
        rows = query.all()
        return [{"date": str(row.day), "count": int(row.case_count)} for row in rows]

    def build_grouped_daily_series(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        police_station: Optional[str] = None,
        crime_head_id: Optional[int] = None,
        crime_subhead_id: Optional[int] = None,
        lookback_days: int = 180,
    ) -> List[StationProfile]:
        start_date = self._lookback_start(lookback_days)
        query = (
            db.query(
                CaseMaster.district.label("district"),
                CaseMaster.unit_name.label("police_station"),
                func.date(CaseMaster.registered_date).label("day"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .filter(CaseMaster.registered_date >= start_date)
            .group_by(CaseMaster.district, CaseMaster.unit_name, "day")
            .order_by(CaseMaster.district, CaseMaster.unit_name, "day")
        )
        query = self._apply_case_filters(query, district, police_station, crime_head_id, crime_subhead_id)
        rows = query.all()

        crime_mix_map = self._load_crime_mix(
            db,
            district=district,
            police_station=police_station,
            crime_head_id=crime_head_id,
            crime_subhead_id=crime_subhead_id,
            lookback_days=lookback_days,
        )
        accused_repeat_map = self._load_repeat_offender_ratio(
            db,
            district=district,
            police_station=police_station,
            lookback_days=lookback_days,
        )

        grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[(row.district, row.police_station)].append({"date": str(row.day), "count": int(row.case_count)})

        profiles: List[StationProfile] = []
        for (row_district, row_station), series in grouped.items():
            summary = self.summarize_series(series)
            crime_mix = crime_mix_map.get((row_district, row_station), [])
            violent_cases = sum(item["case_count"] for item in crime_mix if self._is_violent_label(item["crime_label"]))
            total_records = summary["total_records"]
            violent_share = round((violent_cases / total_records) if total_records else 0.0, 4)
            profiles.append(
                StationProfile(
                    district=row_district,
                    police_station=row_station,
                    series=series,
                    crime_mix=crime_mix,
                    recent_7d=summary["recent_7d"],
                    previous_7d=summary["previous_7d"],
                    growth_pct=summary["growth_pct"],
                    average_daily_count=summary["average_daily_count"],
                    violent_cases=violent_cases,
                    violent_share=violent_share,
                    repeat_offender_ratio=accused_repeat_map.get((row_district, row_station), 0.0),
                    total_records=total_records,
                    start_date=summary["start_date"],
                    end_date=summary["end_date"],
                )
            )

        return profiles

    def summarize_series(self, series: List[Dict[str, Any]]) -> Dict[str, Any]:
        ordered = sorted(series, key=lambda item: item["date"])
        counts = [int(item["count"]) for item in ordered]
        total_records = sum(counts)
        recent_7d = sum(counts[-7:]) if counts else 0
        previous_7d = sum(counts[-14:-7]) if len(counts) > 7 else 0
        growth_pct = self._growth_pct(recent_7d, previous_7d)
        average_daily_count = round(total_records / max(len(counts), 1), 4)
        return {
            "total_records": total_records,
            "start_date": ordered[0]["date"] if ordered else None,
            "end_date": ordered[-1]["date"] if ordered else None,
            "recent_7d": recent_7d,
            "previous_7d": previous_7d,
            "growth_pct": growth_pct,
            "average_daily_count": average_daily_count,
        }

    def build_warning_features(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        police_station: Optional[str] = None,
        lookback_days: int = 14,
    ) -> List[StationProfile]:
        return self.build_grouped_daily_series(
            db,
            district=district,
            police_station=police_station,
            lookback_days=lookback_days,
        )

    def _apply_case_filters(self, query, district, police_station, crime_head_id, crime_subhead_id):
        if district:
            query = query.filter(CaseMaster.district.ilike(f"%{district}%"))
        if police_station:
            query = query.filter(CaseMaster.unit_name.ilike(f"%{police_station}%"))
        if crime_head_id:
            query = query.filter(CaseMaster.crime_head_id == crime_head_id)
        if crime_subhead_id:
            query = query.filter(CaseMaster.crime_subhead_id == crime_subhead_id)
        return query

    def _load_crime_mix(
        self,
        db: Session,
        *,
        district: Optional[str],
        police_station: Optional[str],
        crime_head_id: Optional[int],
        crime_subhead_id: Optional[int],
        lookback_days: int,
    ) -> Dict[Tuple[str, str], List[Dict[str, Any]]]:
        start_date = self._lookback_start(lookback_days)
        query = (
            db.query(
                CaseMaster.district.label("district"),
                CaseMaster.unit_name.label("police_station"),
                func.coalesce(CrimeHead.name, "Unknown").label("crime_head"),
                func.coalesce(CrimeSubHead.name, "Unknown").label("crime_subhead"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .join(CrimeHead, CaseMaster.crime_head_id == CrimeHead.id)
            .join(CrimeSubHead, CaseMaster.crime_subhead_id == CrimeSubHead.id)
            .filter(CaseMaster.registered_date >= start_date)
            .group_by(CaseMaster.district, CaseMaster.unit_name, CrimeHead.name, CrimeSubHead.name)
            .order_by(CaseMaster.district, CaseMaster.unit_name, func.count(CaseMaster.id).desc())
        )
        query = self._apply_case_filters(query, district, police_station, crime_head_id, crime_subhead_id)
        rows = query.all()

        grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[(row.district, row.police_station)].append(
                {
                    "crime_label": f"{row.crime_head} / {row.crime_subhead}",
                    "case_count": int(row.case_count),
                }
            )
        return grouped

    def _load_repeat_offender_ratio(
        self,
        db: Session,
        *,
        district: Optional[str],
        police_station: Optional[str],
        lookback_days: int,
    ) -> Dict[Tuple[str, str], float]:
        start_date = self._lookback_start(lookback_days)
        query = (
            db.query(
                CaseMaster.district.label("district"),
                CaseMaster.unit_name.label("police_station"),
                Accused.name.label("accused_name"),
                func.count(Accused.id).label("occurrences"),
            )
            .join(Accused, Accused.case_id == CaseMaster.id)
            .filter(CaseMaster.registered_date >= start_date)
            .group_by(CaseMaster.district, CaseMaster.unit_name, Accused.name)
        )
        query = self._apply_case_filters(query, district, police_station, None, None)
        rows = query.all()

        totals: Dict[Tuple[str, str], int] = defaultdict(int)
        repeated: Dict[Tuple[str, str], int] = defaultdict(int)
        for row in rows:
            key = (row.district, row.police_station)
            totals[key] += int(row.occurrences)
            if int(row.occurrences) > 1:
                repeated[key] += int(row.occurrences) - 1
        return {key: round(repeated[key] / totals[key], 4) if totals[key] else 0.0 for key in totals}

    def _lookback_start(self, lookback_days: int) -> datetime:
        return datetime.utcnow() - timedelta(days=max(lookback_days, 1))

    def _growth_pct(self, recent: int, previous: int) -> float:
        if previous <= 0:
            return 100.0 if recent > 0 else 0.0
        return round(((recent - previous) / previous) * 100.0, 2)

    def _is_violent_label(self, label: str) -> bool:
        lower = label.lower()
        return any(keyword in lower for keyword in VIOLENT_CRIME_KEYWORDS)


feature_engineer = PredictionFeatureEngineer()
