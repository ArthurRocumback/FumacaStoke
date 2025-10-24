# tests/conftest.py
import os
import sys
import pytest
import sqlite3
from werkzeug.security import generate_password_hash

# Garante que o diretório raiz está no path (para importar app.py)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app as flask_app  # importa o objeto Flask (será usado no yield)

# --- Schema do BD (baseado no app.py) ---
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    admin INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS produto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS rosh (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS pedido (
    pedidoid INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    rg TEXT,
    nome_produto TEXT,
    nome_rosh TEXT,
    essencia TEXT,
    observacao TEXT,
    ativo INTEGER DEFAULT 1,
    criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizacao DATETIME
);
"""

@pytest.fixture(scope='function')
def app(monkeypatch):
    """Configura o app Flask e um BD SQLite em memória para os testes."""

    import app as app_module  # importa o módulo (não o objeto Flask)
    TEST_DB_URI = 'file:memory?mode=memory&cache=shared'

    # Cria o schema no banco em memória
    conn = sqlite3.connect(TEST_DB_URI, uri=True)
    conn.executescript(SCHEMA_SQL)
    conn.close()

    # Monkeypatch: substitui DB_PATH e db_connection no módulo app
    monkeypatch.setattr(app_module, "DB_PATH", TEST_DB_URI)

    def mock_db_connection():
        db_conn = sqlite3.connect(TEST_DB_URI, uri=True)
        db_conn.row_factory = sqlite3.Row
        return db_conn

    monkeypatch.setattr(app_module, "db_connection", mock_db_connection)

    flask_app = app_module.app
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key"
    })

    yield flask_app


@pytest.fixture(scope='function')
def client(app):
    """Cliente de teste Flask."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_conn(app):
    """Conexão direta ao banco para verificação."""
    import app as app_module
    conn = app_module.db_connection()
    yield conn
    conn.execute("DELETE FROM pedido;")
    conn.execute("DELETE FROM user;")
    conn.execute("DELETE FROM produto;")
    conn.execute("DELETE FROM rosh;")
    conn.commit()
    conn.close()


@pytest.fixture(scope='function')
def seed_data(db_conn):
    """Popula o BD com dados básicos."""
    db_conn.execute(
        "INSERT INTO user (nome, senha, admin) VALUES (?, ?, ?)",
        ('admin', generate_password_hash('admin123'), 1)
    )
    db_conn.execute(
        "INSERT INTO user (nome, senha, admin) VALUES (?, ?, ?)",
        ('user', generate_password_hash('user123'), 0)
    )
    db_conn.execute("INSERT INTO produto (nome) VALUES (?)", ('Narguile Grande',))
    db_conn.execute("INSERT INTO rosh (nome) VALUES (?)", ('Rosh de Barro',))
    db_conn.commit()
