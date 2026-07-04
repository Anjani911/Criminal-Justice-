import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.database import get_db
from app.main import app


class _MockDB:
    def execute(self, *args, **kwargs):
        return None

    def close(self):
        return None


def _override_get_db():
    db = _MockDB()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture()
def client():
    return TestClient(app)
