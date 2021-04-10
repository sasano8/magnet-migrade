from fastapi.testclient import TestClient

from magnet.__main import app

if False:
    # sqlalchemy-utilsがsqlalchemy1.4に対応するまで無効
    from .conftest import override_get_db

    client = TestClient(app)

client = None
