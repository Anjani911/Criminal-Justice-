"""
Professional PDF report engine.

Transforms the structured report payloads into polished PDF documents and
persists them using the configured storage adapter.
"""
from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, List, Optional

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.reports.storage import report_storage
from app.services.report_service import report_service


class ReportEngine:
    """Render report payloads into PDF documents and store the output."""

    def generate_case_report(self, db, case_id: int, ai_summary: Optional[str] = None):
        payload = report_service.generate_case_report(db, case_id, ai_summary=ai_summary)
        return self._render_and_store(payload)

    def generate_district_report(self, db, district: str, year: Optional[int] = None, ai_summary: Optional[str] = None):
        payload = report_service.generate_district_report(db, district=district, year=year, ai_summary=ai_summary)
        return self._render_and_store(payload)

    def generate_dashboard_report(self, db, ai_summary: Optional[str] = None):
        payload = report_service.generate_dashboard_report(db)
        if ai_summary:
            payload["ai_summary"] = ai_summary
        return self._render_and_store(payload)

    def _render_and_store(self, payload: Dict[str, Any]):
        pdf_bytes = self._render_pdf(payload)
        generated_at = payload.get("generated_at") or self._now_iso()
        stored = report_storage.save_pdf(payload["report_type"], pdf_bytes, generated_at)
        return {
            "report_type": payload["report_type"],
            "generated_at": generated_at,
            "storage_provider": stored.storage_provider,
            "storage_key": stored.storage_key,
            "file_name": stored.file_name,
            "download_url": stored.download_url,
            "metadata": {
                "pdf_bytes": len(pdf_bytes),
                "has_ai_summary": bool(payload.get("ai_summary")),
            },
        }

    def _render_pdf(self, payload: Dict[str, Any]) -> bytes:
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=42,
            bottomMargin=36,
            title=f"SCRB {payload['report_type']} report",
            author="SCRB Karnataka AI Crime Intelligence Platform",
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="SectionTitle", parent=styles["Heading2"], textColor=colors.HexColor("#0F4C81"), spaceAfter=10))

        story: List[Any] = []
        story.extend(self._build_cover(payload, styles))
        story.append(Spacer(1, 12))
        story.extend(self._build_ai_summary(payload, styles))

        report_type = payload["report_type"]
        if report_type == "case_investigation":
            story.extend(self._build_case_sections(payload, styles))
        elif report_type == "district_summary":
            story.extend(self._build_district_sections(payload, styles))
        else:
            story.extend(self._build_dashboard_sections(payload, styles))

        document.build(story)
        return buffer.getvalue()

    def _build_cover(self, payload: Dict[str, Any], styles) -> List[Any]:
        title_map = {
            "case_investigation": "Case Investigation Report",
            "district_summary": "District Crime Summary Report",
            "dashboard": "Operational Intelligence Dashboard Report",
        }
        story: List[Any] = [
            Paragraph("SCRB Karnataka", styles["Title"]),
            Paragraph(title_map.get(payload["report_type"], "Crime Intelligence Report"), styles["Heading1"]),
            Spacer(1, 10),
            Paragraph(f"Generated at: {payload.get('generated_at', self._now_iso())}", styles["BodyText"]),
        ]
        if payload["report_type"] == "case_investigation":
            case = payload.get("case", {})
            story.append(Paragraph(f"FIR Number: {case.get('fir_number', 'N/A')}", styles["BodyText"]))
            story.append(Paragraph(f"District: {case.get('district', 'N/A')} | Unit: {case.get('unit_name', 'N/A')}", styles["BodyText"]))
        elif payload["report_type"] == "district_summary":
            story.append(Paragraph(f"District: {payload.get('district', 'N/A')}", styles["BodyText"]))
            story.append(Paragraph(f"Year Filter: {payload.get('year') or 'All Years'}", styles["BodyText"]))
        story.append(Spacer(1, 12))
        return story

    def _build_ai_summary(self, payload: Dict[str, Any], styles) -> List[Any]:
        story = [Paragraph("AI Summary", styles["SectionTitle"])]
        summary = payload.get("ai_summary") or "AI summary not provided."
        story.append(Paragraph(summary, styles["BodyText"]))
        story.append(Spacer(1, 10))
        return story

    def _build_case_sections(self, payload: Dict[str, Any], styles) -> List[Any]:
        story: List[Any] = [Paragraph("Case Details", styles["SectionTitle"])]
        case = payload.get("case", {})
        story.append(self._table([
            ["Field", "Value"],
            ["FIR Number", case.get("fir_number", "N/A")],
            ["Status", case.get("status", "N/A")],
            ["District", case.get("district", "N/A")],
            ["Unit", case.get("unit_name", "N/A")],
            ["Incident Date", case.get("incident_date", "N/A")],
            ["Registered Date", case.get("registered_date", "N/A")],
            ["Crime Head", case.get("crime_head", "N/A")],
            ["Crime Sub Head", case.get("crime_sub_head", "N/A")],
        ]))
        story.append(Spacer(1, 8))

        story.append(Paragraph("Accused", styles["SectionTitle"]))
        story.append(self._table(self._people_rows(payload.get("accused", []), ["Name", "Age", "Gender", "Status"])))
        story.append(Spacer(1, 8))

        story.append(Paragraph("Victims", styles["SectionTitle"]))
        story.append(self._table(self._people_rows(payload.get("victims", []), ["Name", "Age", "Gender", "Injury Type"])))
        story.append(Spacer(1, 8))

        story.append(Paragraph("Arrests / Surrenders", styles["SectionTitle"]))
        story.append(self._table(self._arrest_rows(payload.get("arrests", []))))
        story.append(Spacer(1, 8))

        network = payload.get("criminal_network", {})
        story.append(Paragraph("Network Graph Metadata", styles["SectionTitle"]))
        story.append(self._table([
            ["Node Count", str(network.get("node_count", 0))],
            ["Edge Count", str(network.get("edge_count", 0))],
        ]))
        story.append(PageBreak())
        return story

    def _build_district_sections(self, payload: Dict[str, Any], styles) -> List[Any]:
        story: List[Any] = []
        story.append(Paragraph("Dashboard KPIs", styles["SectionTitle"]))
        story.append(self._table(self._dict_rows(payload.get("dashboard_kpis", {}))))
        story.append(Spacer(1, 10))

        story.append(Paragraph("Monthly Crime Trends", styles["SectionTitle"]))
        story.append(self._bar_chart(payload.get("monthly_trends", []), key="case_count", category_key="month_name"))
        story.append(Spacer(1, 10))

        story.append(Paragraph("Crime Category Distribution", styles["SectionTitle"]))
        story.append(self._pie_chart(payload.get("crime_type_distribution", []), label_key="crime_head", value_key="case_count"))
        story.append(Spacer(1, 10))

        story.append(Paragraph("Unit Hotspots", styles["SectionTitle"]))
        story.append(self._bar_chart(payload.get("unit_hotspots", []), key="case_count", category_key="unit", max_labels=10))
        story.append(PageBreak())
        return story

    def _build_dashboard_sections(self, payload: Dict[str, Any], styles) -> List[Any]:
        story: List[Any] = []
        story.append(Paragraph("Key Metrics", styles["SectionTitle"]))
        story.append(self._table(self._dict_rows(payload.get("kpis", {}))))
        story.append(Spacer(1, 10))

        story.append(Paragraph("Monthly Crime Trends", styles["SectionTitle"]))
        story.append(self._bar_chart(payload.get("monthly_trends", []), key="case_count", category_key="month_name"))
        story.append(Spacer(1, 10))

        story.append(Paragraph("District Hotspots", styles["SectionTitle"]))
        story.append(self._bar_chart(payload.get("district_hotspots", []), key="case_count", category_key="district", max_labels=10))
        story.append(Spacer(1, 10))

        story.append(Paragraph("Network Metrics", styles["SectionTitle"]))
        story.append(self._table(self._dict_rows(payload.get("network_metrics", {}))))
        story.append(PageBreak())
        return story

    def _table(self, rows: List[List[str]]) -> Table:
        table = Table(rows, colWidths=[2.3 * inch, 4.8 * inch], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEADING", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B5C7D3")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#EEF4F8")]),
        ]))
        return table

    def _dict_rows(self, data: Dict[str, Any]) -> List[List[str]]:
        rows = [["Metric", "Value"]]
        for key, value in data.items():
            rows.append([self._humanise(key), self._stringify(value)])
        if len(rows) == 1:
            rows.append(["N/A", "No data available"])
        return rows

    def _people_rows(self, items: List[Dict[str, Any]], headers: List[str]) -> List[List[str]]:
        rows = [headers]
        for item in items:
            rows.append([
                self._stringify(item.get("name")),
                self._stringify(item.get("age")),
                self._stringify(item.get("gender")),
                self._stringify(item.get("status") or item.get("injury_type")),
            ])
        if len(rows) == 1:
            rows.append(["N/A", "N/A", "N/A", "N/A"])
        return rows

    def _arrest_rows(self, items: List[Dict[str, Any]]) -> List[List[str]]:
        rows = [["Arrest Date", "Type", "Accused", "Officer", "Court"]]
        for item in items:
            rows.append([
                self._stringify(item.get("arrest_date")),
                self._stringify(item.get("arrest_type")),
                self._stringify(item.get("accused_name")),
                self._stringify(item.get("arresting_officer")),
                self._stringify(item.get("court_name")),
            ])
        if len(rows) == 1:
            rows.append(["N/A", "N/A", "N/A", "N/A", "N/A"])
        return rows

    def _bar_chart(self, items: List[Dict[str, Any]], key: str, category_key: str, max_labels: int = 12) -> Drawing:
        items = items[:max_labels]
        drawing = Drawing(520, 220)
        chart = VerticalBarChart()
        chart.x = 40
        chart.y = 35
        chart.height = 150
        chart.width = 440
        values = [float(item.get(key, 0) or 0) for item in items] or [0]
        chart.data = [values]
        chart.categoryAxis.categoryNames = [str(item.get(category_key, "N/A"))[:18] for item in items] or ["N/A"]
        chart.barWidth = 12
        chart.groupSpacing = 8
        chart.strokeColor = colors.HexColor("#0F4C81")
        chart.bars[0].fillColor = colors.HexColor("#0F4C81")
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(values) * 1.2 if values and max(values) > 0 else 1
        chart.valueAxis.valueStep = max(1, int(max(values) / 5) if max(values) else 1)
        drawing.add(chart)
        return drawing

    def _pie_chart(self, items: List[Dict[str, Any]], label_key: str, value_key: str) -> Drawing:
        drawing = Drawing(520, 220)
        pie = Pie()
        pie.x = 165
        pie.y = 20
        pie.width = 180
        pie.height = 180
        pie.data = [float(item.get(value_key, 0) or 0) for item in items] or [1]
        pie.labels = [str(item.get(label_key, "N/A"))[:16] for item in items] or ["N/A"]
        pie.slices.strokeWidth = 0.5
        if len(items) > 1:
            palette = [colors.HexColor("#0F4C81"), colors.HexColor("#2C7BE5"), colors.HexColor("#7AC36A"), colors.HexColor("#F4B400"), colors.HexColor("#D9534F")]
            for index, _ in enumerate(items):
                pie.slices[index].fillColor = palette[index % len(palette)]
        else:
            pie.slices[0].fillColor = colors.HexColor("#0F4C81")
        drawing.add(pie)
        return drawing

    def _humanise(self, value: str) -> str:
        return value.replace("_", " ").title()

    def _stringify(self, value: Any) -> str:
        if value is None:
            return "N/A"
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value)

    def _now_iso(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


report_engine = ReportEngine()
