"""
AI orchestration engine.

Workflow:
User Question -> Intent Detection -> Validated Query Plan ->
Database Query / Analytics Layer -> Gemini Summarisation -> JSON Response

The module never accepts raw SQL from the user. It maps the request to a
whitelisted query plan and only executes approved database or service calls.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.schemas.ai import AIChatResponse
from app.schemas.case import CaseDetailOut
from app.services.prediction_service import prediction_service
from app.services.analytics_service import analytics_service
from app.services.crime_service import crime_service
from app.services.network_service import network_service
from app.utils.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QueryPlan:
    """Approved query action derived from intent detection."""

    intent: str
    query_kind: str
    params: Dict[str, Any]


class CrimeAIService:
    """
    Controls the AI question-answer workflow.

    The service only executes approved query kinds and returns structured
    JSON that is safe to expose to the frontend.
    """

    def answer(self, db: Session, question: str, context: Optional[Dict[str, Any]] = None) -> AIChatResponse:
        context = context or {}
        
        detected_language = self._detect_language(question)
        target_language = detected_language
        
        english_question = question
        if detected_language == "Kannada":
            translated = self._translate_to_english(question)
            if translated:
                english_question = translated
                
        intent, confidence = self.detect_intent(english_question, context)
        plan = self.build_query_plan(intent, english_question, context)

        try:
            data = self.execute_plan(db, plan)
            answer = self.summarize(english_question, plan, data, target_language)
            return AIChatResponse(
                status="success",
                intent=plan.intent,
                confidence=confidence,
                query_kind=plan.query_kind,
                detected_language=detected_language,
                response_language=target_language,
                answer=answer,
                data=data,
                suggestions=self.suggestions_for_intent(plan.intent),
            )
        except LookupError as exc:
            return AIChatResponse(
                status="partial",
                intent=plan.intent,
                confidence=confidence,
                query_kind=plan.query_kind,
                detected_language=detected_language,
                response_language=target_language,
                answer=str(exc),
                data={"error": str(exc)},
                suggestions=self.suggestions_for_intent(plan.intent),
            )
        except Exception as exc:  # pragma: no cover - defensive safety net
            logger.exception("AI chat workflow failed")
            return AIChatResponse(
                status="error",
                intent=plan.intent,
                confidence=confidence,
                query_kind=plan.query_kind,
                detected_language=detected_language,
                response_language="English",
                answer="The request could not be processed safely.",
                data={"error": str(exc)},
                suggestions=["Try asking for crime trends, hotspots, crime categories, or case details."],
            )

    def detect_intent(self, question: str, context: Optional[Dict[str, Any]] = None) -> Tuple[str, float]:
        text = question.lower().strip()
        context = context or {}

        if any(keyword in text for keyword in ("dashboard", "overview", "kpi", "summary")):
            return "dashboard", 0.93
        if any(keyword in text for keyword in ("monthly statistics", "monthly stats", "clearance by month")):
            return "monthly_statistics", 0.92
        if any(keyword in text for keyword in ("crime trend", "crime trends", "trend", "monthly crime")):
            return "crime_trends", 0.91
        if any(keyword in text for keyword in ("crime type", "crime categories", "category distribution", "subhead")):
            return "crime_categories", 0.9
        if any(keyword in text for keyword in ("hotspot", "hotspots", "police station", "district heatmap")):
            return "hotspots", 0.9
        if any(keyword in text for keyword in ("station statistics", "station stats", "police station statistics")):
            return "police_station_statistics", 0.9
        if any(keyword in text for keyword in ("network metrics", "criminal network", "graph metrics", "centrality")):
            return "network_metrics", 0.9
        if any(keyword in text for keyword in ("predict", "predicted", "forecast", "forecasting", "likely to become", "risk score", "warning", "early warning", "hotspot next week", "vehicle theft risk")):
            return "prediction", 0.94
        if any(keyword in text for keyword in ("case network", "sub graph", "subgraph", "case graph")):
            return "case_network", 0.88
        if any(keyword in text for keyword in ("accused network", "accused graph", "person network")):
            return "accused_network", 0.88
        if any(keyword in text for keyword in ("fir", "case details", "case detail", "case id")):
            return "case_lookup", 0.87

        if context.get("case_id") or context.get("fir_number"):
            return "case_lookup", 0.9
        if context.get("district"):
            return "hotspots", 0.84

        return "dashboard", 0.5

    def build_query_plan(self, intent: str, question: str, context: Dict[str, Any]) -> QueryPlan:
        case_id = self._extract_case_id(question, context)
        fir_number = self._extract_fir_number(question, context)
        district = self._extract_district(question, context)
        year = self._extract_year(question, context)
        crime_head_id = self._extract_int(context.get("crime_head_id"))
        crime_subhead_id = self._extract_int(context.get("crime_subhead_id"))
        accused_id = self._extract_int(context.get("accused_id"))

        if intent == "crime_trends":
            return QueryPlan(intent=intent, query_kind="analytics.monthly_trends", params={"year": year})
        if intent == "monthly_statistics":
            return QueryPlan(intent=intent, query_kind="analytics.monthly_statistics", params={"year": year})
        if intent == "crime_categories":
            return QueryPlan(
                intent=intent,
                query_kind="analytics.crime_categories",
                params={"crime_head_id": crime_head_id},
            )
        if intent == "hotspots":
            return QueryPlan(intent=intent, query_kind="analytics.hotspots", params={"district": district})
        if intent == "police_station_statistics":
            return QueryPlan(
                intent=intent,
                query_kind="analytics.police_station_statistics",
                params={"district": district},
            )
        if intent == "network_metrics":
            return QueryPlan(intent=intent, query_kind="network.metrics", params={})
        if intent == "case_network":
            return QueryPlan(intent=intent, query_kind="network.case", params={"case_id": case_id})
        if intent == "accused_network":
            return QueryPlan(intent=intent, query_kind="network.accused", params={"accused_id": accused_id})
        if intent == "case_lookup":
            return QueryPlan(
                intent=intent,
                query_kind="case.lookup",
                params={"case_id": case_id, "fir_number": fir_number},
            )
        if intent == "prediction":
            return QueryPlan(
                intent=intent,
                query_kind="prediction.dashboard",
                params={
                    "district": district,
                    "police_station": context.get("police_station") or context.get("unit_name"),
                    "crime_head_id": crime_head_id,
                    "crime_subhead_id": crime_subhead_id,
                    "period": context.get("period") or ("next_month" if "month" in question.lower() else "next_week"),
                },
            )
        return QueryPlan(intent="dashboard", query_kind="analytics.dashboard", params={})

    def execute_plan(self, db: Session, plan: QueryPlan) -> Dict[str, Any]:
        if plan.query_kind == "analytics.monthly_trends":
            return {"trends": analytics_service.get_monthly_trends(db, year=plan.params.get("year"))}
        if plan.query_kind == "analytics.monthly_statistics":
            return {"monthly_statistics": analytics_service.get_monthly_statistics(db, year=plan.params.get("year"))}
        if plan.query_kind == "analytics.crime_categories":
            crime_head_id = plan.params.get("crime_head_id")
            if crime_head_id:
                return {"crime_categories": analytics_service.get_crime_subtype_distribution(db, crime_head_id=crime_head_id)}
            return {"crime_categories": analytics_service.get_crime_type_distribution(db)}
        if plan.query_kind == "analytics.hotspots":
            district = plan.params.get("district")
            return {
                "district_hotspots": analytics_service.get_district_hotspots(db),
                "unit_hotspots": analytics_service.get_unit_hotspots(db, district=district),
            }
        if plan.query_kind == "analytics.police_station_statistics":
            return {"police_station_statistics": analytics_service.get_police_station_statistics(db, district=plan.params.get("district"))}
        if plan.query_kind == "analytics.dashboard":
            return {"dashboard": analytics_service.get_dashboard_summary(db)}
        if plan.query_kind == "network.metrics":
            return {"network_metrics": network_service.get_network_metrics(db)}
        if plan.query_kind == "network.case":
            case_id = plan.params.get("case_id")
            if case_id is None:
                raise LookupError("A case_id is required to build a case network.")
            return {"network": network_service.get_case_network(db, case_id)}
        if plan.query_kind == "network.accused":
            accused_id = plan.params.get("accused_id")
            if accused_id is None:
                raise LookupError("An accused_id is required to build an accused network.")
            return {"network": network_service.get_accused_network(db, accused_id)}
        if plan.query_kind == "case.lookup":
            case = None
            case_id = plan.params.get("case_id")
            fir_number = plan.params.get("fir_number")
            if case_id is not None:
                case = crime_service.get_case_by_id(db, case_id)
            elif fir_number:
                case = crime_service.get_case_by_fir(db, fir_number)

            if case is None:
                raise LookupError("No matching case was found for the provided filters.")

            return {"case": CaseDetailOut.model_validate(case).model_dump()}

        if plan.query_kind == "prediction.dashboard":
            return {
                "prediction_dashboard": prediction_service.get_dashboard(
                    db,
                    district=plan.params.get("district"),
                    police_station=plan.params.get("police_station"),
                )
            }

        raise LookupError("Unsupported query plan.")

    def summarize(self, question: str, plan: QueryPlan, data: Dict[str, Any], target_language: str = "English") -> str:
        gemini_text = self._summarize_with_gemini(question, plan, data, target_language)
        if gemini_text:
            return gemini_text
            
        fallback = self._fallback_summary(plan, data)
        if target_language == "Kannada":
            translated = self._translate_to_kannada(fallback)
            if translated:
                return translated
        return fallback

    def suggestions_for_intent(self, intent: str) -> list[str]:
        suggestions_map = {
            "dashboard": ["Show monthly statistics", "Show crime trends for 2026", "Show hotspots in Bengaluru"],
            "crime_trends": ["Show monthly statistics", "Show crime categories", "Show dashboard summary"],
            "monthly_statistics": ["Show crime trends", "Show police station statistics", "Show hotspots"],
            "crime_categories": ["Show crime trends", "Show district hotspots", "Show dashboard summary"],
            "hotspots": ["Show police station statistics", "Show crime trends", "Show network metrics"],
            "police_station_statistics": ["Show hotspots", "Show monthly statistics", "Show dashboard summary"],
            "network_metrics": ["Show case network for case 12", "Show accused network for accused 7"],
            "case_network": ["Show network metrics", "Show case details for FIR 123/2026"],
            "accused_network": ["Show network metrics", "Show case details for case 12"],
            "case_lookup": ["Show case network", "Show dashboard summary", "Show crime trends"],
        }
        return suggestions_map.get(intent, ["Show dashboard summary", "Show crime trends", "Show hotspots"])

    def _summarize_with_gemini(self, question: str, plan: QueryPlan, data: Dict[str, Any], target_language: str = "English") -> Optional[str]:
        api_key = settings.GEMINI_API_KEY.strip()
        if not api_key:
            return None

        try:
            import google.generativeai as genai
        except Exception:  # pragma: no cover - optional dependency fallback
            return None

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                "You are assisting SCRB investigators. Provide a concise, factual summary. "
                "Do not invent facts, do not mention internal chain-of-thought, and do not provide raw SQL.\n\n"
                f"Question: {question}\n"
                f"Intent: {plan.intent}\n"
                f"Data: {data}\n\n"
                f"Return a professional summary in 3-6 sentences. The response MUST be in {target_language}."
            )
            response = model.generate_content(prompt)
            text = getattr(response, "text", None)
            return text.strip() if isinstance(text, str) and text.strip() else None
        except Exception as exc:  # pragma: no cover - runtime safety
            logger.warning("Gemini summarisation failed: %s", exc)
            return None

    def _fallback_summary(self, plan: QueryPlan, data: Dict[str, Any]) -> str:
        if plan.intent == "dashboard":
            dashboard = data.get("dashboard", {})
            return (
                "Dashboard summary: "
                f"{dashboard.get('total_cases', 0)} cases, "
                f"{dashboard.get('total_accused', 0)} accused, "
                f"{dashboard.get('total_victims', 0)} victims, and "
                f"{dashboard.get('total_arrests', 0)} arrests are currently in scope."
            )
        if plan.intent in {"crime_trends", "monthly_statistics"}:
            rows = data.get("trends") or data.get("monthly_statistics") or []
            return f"Found {len(rows)} monthly data points for the requested period."
        if plan.intent == "crime_categories":
            rows = data.get("crime_categories", [])
            top = rows[:3]
            if not top:
                return "No crime category data was found for the requested filter."
            labels = ", ".join(item.get("crime_head") or item.get("crime_subhead") or "Unknown" for item in top)
            return f"Top crime categories identified: {labels}."
        if plan.intent == "hotspots":
            district_rows = data.get("district_hotspots", [])
            if not district_rows:
                return "No hotspot data was found for the requested scope."
            return f"Identified {len(district_rows)} district hotspot rows and station-level drilldown data."
        if plan.intent == "police_station_statistics":
            rows = data.get("police_station_statistics", [])
            return f"Compiled police station statistics for {len(rows)} station rows."
        if plan.intent == "network_metrics":
            metrics = data.get("network_metrics", {})
            return (
                "Network metrics generated for "
                f"{metrics.get('total_nodes', 0)} nodes and {metrics.get('total_edges', 0)} edges."
            )
        if plan.intent == "case_network":
            return "Case-centric criminal network graph generated successfully."
        if plan.intent == "accused_network":
            return "Accused-centric criminal network graph generated successfully."
        if plan.intent == "case_lookup":
            case = data.get("case", {})
            return f"Case {case.get('fir_number', 'unknown')} is available with status {case.get('status', 'unknown')}."
        if plan.intent == "prediction":
            dashboard = data.get("prediction_dashboard", {})
            hotspot = dashboard.get("hotspot_forecast", {})
            trend = dashboard.get("trend_forecast", {})
            station = dashboard.get("station_risk", {})
            if hotspot or trend or station:
                return (
                    "Prediction summary generated: "
                    f"top hotspot risk {hotspot.get('prediction', {}).get('risk_percentage', 0)}%, "
                    f"trend direction {trend.get('prediction', {}).get('trend_direction', 'stable')}, "
                    f"station risk {station.get('prediction', {}).get('risk_level', 'LOW')}."
                )
            return "Prediction dashboard generated from historical crime data."
        return "A structured answer was generated from approved analytics and network data."

    def _extract_case_id(self, question: str, context: Dict[str, Any]) -> Optional[int]:
        case_id = self._extract_int(context.get("case_id"))
        if case_id is not None:
            return case_id
        match = re.search(r"(?:case\s*id|case)\s*(\d+)", question, flags=re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _extract_fir_number(self, question: str, context: Dict[str, Any]) -> Optional[str]:
        fir_number = context.get("fir_number")
        if isinstance(fir_number, str) and fir_number.strip():
            return fir_number.strip()
        match = re.search(r"fir\s*([a-z0-9/\-]+)", question, flags=re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_district(self, question: str, context: Dict[str, Any]) -> Optional[str]:
        district = context.get("district")
        if isinstance(district, str) and district.strip():
            return district.strip()
        match = re.search(r"(?:in|for)\s+([a-z][a-z\s]+?)\s+(?:district|zone|city)", question, flags=re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_year(self, question: str, context: Dict[str, Any]) -> Optional[int]:
        year = self._extract_int(context.get("year"))
        if year is not None:
            return year
        match = re.search(r"\b(20\d{2})\b", question)
        return int(match.group(1)) if match else None

    def _extract_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _detect_language(self, text: str) -> str:
        if re.search(r'[\u0C80-\u0CFF]', text):
            return "Kannada"
        return "English"

    def _translate_to_english(self, text: str) -> Optional[str]:
        api_key = settings.GEMINI_API_KEY.strip()
        if not api_key:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Translate the following Kannada text to English. Provide ONLY the direct translation, nothing else:\n\n{text}"
            response = model.generate_content(prompt)
            translated = getattr(response, "text", None)
            return translated.strip() if isinstance(translated, str) and translated.strip() else None
        except Exception as exc:
            logger.warning("Gemini translation to English failed: %s", exc)
            return None

    def _translate_to_kannada(self, text: str) -> Optional[str]:
        api_key = settings.GEMINI_API_KEY.strip()
        if not api_key:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Translate the following English text to Kannada. Provide ONLY the direct translation, nothing else:\n\n{text}"
            response = model.generate_content(prompt)
            translated = getattr(response, "text", None)
            return translated.strip() if isinstance(translated, str) and translated.strip() else None
        except Exception as exc:
            logger.warning("Gemini translation to Kannada failed: %s", exc)
            return None


ai_service = CrimeAIService()


