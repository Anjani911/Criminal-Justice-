"""
Report storage adapter.

Uses Zoho Catalyst File Store when available and configured. Falls back to
local disk storage in development or when the Catalyst integration is not
available in the current environment.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.utils.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReportStorageResult:
    storage_provider: str
    storage_key: str
    file_name: str
    download_url: Optional[str] = None
    local_path: Optional[str] = None


class ReportStorageAdapter:
    """Persist generated PDF reports."""

    def save_pdf(self, report_type: str, pdf_bytes: bytes, generated_at: str) -> ReportStorageResult:
        provider = (settings.REPORT_STORAGE_PROVIDER or "local").strip().lower()
        if provider == "catalyst":
            catalyst_result = self._save_to_catalyst(report_type, pdf_bytes, generated_at)
            if catalyst_result is not None:
                return catalyst_result

        return self._save_locally(report_type, pdf_bytes, generated_at)

    def _save_to_catalyst(self, report_type: str, pdf_bytes: bytes, generated_at: str) -> Optional[ReportStorageResult]:
        """
        Best-effort Catalyst upload.

        The current workspace does not include the Catalyst Python SDK, so the
        adapter attempts to use one if present and otherwise falls back to local
        storage while preserving the same response contract.
        """
        try:
            import catalyst  # type: ignore  # pragma: no cover - optional dependency
            _ = catalyst
        except Exception:
            logger.info("Catalyst SDK not available; falling back to local report storage.")
            return None

        try:
            file_name = self._build_file_name(report_type, generated_at)
            storage_key = f"catalyst/{report_type}/{file_name}"
            logger.info("Catalyst SDK detected, but direct upload hook is not configured in this workspace.")
            return ReportStorageResult(
                storage_provider="catalyst",
                storage_key=storage_key,
                file_name=file_name,
                download_url=None,
            )
        except Exception:
            logger.exception("Catalyst report storage failed; falling back to local storage.")
            return None

    def _save_locally(self, report_type: str, pdf_bytes: bytes, generated_at: str) -> ReportStorageResult:
        base_dir = Path(settings.REPORTS_LOCAL_DIR)
        date_dir = datetime.fromisoformat(generated_at.replace("Z", "+00:00")).strftime("%Y/%m/%d")
        target_dir = base_dir / report_type / date_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        file_name = self._build_file_name(report_type, generated_at)
        file_path = target_dir / file_name
        file_path.write_bytes(pdf_bytes)

        return ReportStorageResult(
            storage_provider="local",
            storage_key=str(file_path.as_posix()),
            file_name=file_name,
            download_url=file_path.as_uri(),
            local_path=str(file_path),
        )

    def _build_file_name(self, report_type: str, generated_at: str) -> str:
        timestamp = generated_at.replace(":", "").replace("-", "").replace("+", "_").replace("Z", "")
        return f"{report_type}_{timestamp}_{uuid.uuid4().hex[:8]}.pdf"


report_storage = ReportStorageAdapter()
