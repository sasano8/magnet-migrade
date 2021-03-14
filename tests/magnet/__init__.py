from fastapi.testclient import TestClient

from magnet.__main import app

from .conftest import override_get_db

client = TestClient(app)
