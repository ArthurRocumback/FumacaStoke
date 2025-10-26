# tests/conftest.py
import os
import sys
import pytest
from unittest.mock import MagicMock

# Garante que o diretório raiz está no path (para importar app.py)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app as flask_app

@pytest.fixture(scope='function')
def app(monkeypatch):
    """Cria uma versão do app Flask sem acessar o banco de dados."""
    import app as app_module

    fake_cursor = MagicMock()
    fake_cursor.fetchall.return_value = []
    fake_cursor.fetchone.return_value = None

    fake_conn = MagicMock()
    fake_conn.execute.return_value = fake_cursor
    fake_conn.cursor.return_value = fake_cursor
    fake_conn.commit.return_value = None
    fake_conn.close.return_value = None

    monkeypatch.setattr(app_module, "db_connection", lambda: fake_conn)

    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
    })
    yield flask_app


@pytest.fixture(scope='function')
def client(app):
    """Cliente de teste Flask."""
    return app.test_client()
