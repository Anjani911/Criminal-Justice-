"""
AI orchestration package.

Provides the validated chat workflow for intent detection, safe query
planning, analytics retrieval, and summarisation.
"""

from app.ai.engine import ai_service, CrimeAIService

__all__ = ["CrimeAIService", "ai_service"]
