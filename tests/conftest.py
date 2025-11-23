import os
import sys
import tempfile
import pytest
import sqlite3
from werkzeug.security import generate_password_hash

# Descobre o diretório raiz do projeto (um nível acima da pasta tests)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Garante que o raiz esteja no sys.path para que 'import app' funcione
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import app as app_module           # módulo completo
from app import app as flask_app   # instância Flask


@pytest.fixture
def app():
    # Cria um banco SQLite temporário
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()

    # Aponta o app para o banco temporário
    app_module.DB_PATH = temp_db.name
    flask_app.config["TESTING"] = True

    conn = sqlite3.connect(temp_db.name)
    cursor = conn.cursor()

    # Estrutura mínima das tabelas (baseado no sqlite_db_setup.py)
    cursor.executescript(
        """
        CREATE TABLE produto (
            produtoid INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        );

        CREATE TABLE rosh (
            roshid INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        );

        CREATE TABLE pedido (
            pedidoid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rg TEXT NOT NULL,
            nome_produto TEXT,
            nome_rosh TEXT,
            essencia TEXT,
            criacao DATETIME DEFAULT (DATETIME('now')),
            atualizacao DATETIME DEFAULT (DATETIME('now')),
            observacao TEXT,
            ativo INTEGER DEFAULT 0
        );

        CREATE TABLE user(
            userid INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL,
            admin INTEGER DEFAULT 0
        );
        """
    )

    # Dados básicos para os testes
    cursor.execute("INSERT INTO produto (nome) VALUES (?)", ("Aluguel Pequeno",))
    cursor.execute("INSERT INTO rosh (nome) VALUES (?)", ("Mix",))

    # Usuários de teste (adm e normal)
    senha_admin = generate_password_hash("admin123")
    senha_user = generate_password_hash("Teste")

    cursor.executemany(
        "INSERT INTO user (nome, senha, admin) VALUES (?, ?, ?)",
        [
            ("adm", senha_admin, 1),   # admin
            ("Teste", senha_user, 0),  # usuário normal
        ],
    )

    conn.commit()
    conn.close()

    yield flask_app

    # Remove o arquivo de banco temporário ao final
    os.unlink(temp_db.name)


@pytest.fixture
def client(app):
    return app.test_client()
