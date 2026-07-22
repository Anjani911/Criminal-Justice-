from app.ai import CrimeAIService, ai_service


def test_ai_service_is_exported_and_instantiated():
    assert isinstance(ai_service, CrimeAIService)
