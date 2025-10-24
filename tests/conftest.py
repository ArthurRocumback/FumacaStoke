# tests/conftest.py
import pytest
import sqlite3
from werkzeug.security import generate_password_hash

# O pytest.ini vai cuidar para que esta importação funcione
from app import app as flask_app

# --- Schema do BD (Inferido do seu app.py e sqlite_db_setup.py) ---
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

@pytest.fixture(scope='session')
def app(monkeypatch):
    """
    Fixture de sessão que configura o app Flask e um BD em memória.
    """
    
    # 1. Usar um banco de dados em memória "nomeado" (URI) para que 
    # ele persista durante toda a sessão de teste (entre conexões).
    TEST_DB_URI = 'file:memory?mode=memory&cache=shared'
    
    # 2. Criar a conexão e o schema inicial
    conn = sqlite3.connect(TEST_DB_URI, uri=True)
    conn.executescript(SCHEMA_SQL)
    conn.close()

    # 3. Monkeypatch!
    # Substituímos o DB_PATH no módulo 'app' para apontar para o BD em memória
    monkeypatch.setattr(flask_app, "DB_PATH", TEST_DB_URI)
    
    # 4. Sobrescrever a função de conexão para usar o URI
    # Isso é crucial para que todas as chamadas à db_connection()
    # no app usem nosso banco em memória.
    def mock_db_connection():
        db_conn = sqlite3.connect(TEST_DB_URI, uri=True)
        db_conn.row_factory = sqlite3.Row
        return db_conn
        
    monkeypatch.setattr(flask_app, "db_connection", mock_db_connection)

    # 5. Configurar app para teste
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key" # Chave para testar sessões
    })

    yield flask_app


@pytest.fixture(scope='function')
def client(app):
    """ Cliente de teste para cada função. """
    return app.test_client()


@pytest.fixture(scope='function')
def db_conn(app):
    """
    Fixture que fornece uma conexão ao BD de teste
    e limpa as tabelas APÓS cada teste para garantir isolamento.
    """
    from app import db_connection # Pega a função "monkeypatched"
    
    conn = db_connection()
    yield conn
    
    # --- Limpeza (Teardown pós-teste) ---
    conn.execute("DELETE FROM pedido;")
    conn.execute("DELETE FROM user;")
    conn.execute("DELETE FROM produto;")
    conn.execute("DELETE FROM rosh;")
    conn.commit()
    conn.close()

@pytest.fixture(scope='function')
def seed_data(db_conn):
    """
    Fixture para popular o banco com dados básicos para testes.
    Roda por função, garantindo dados limpos.
    """
    try:
        # Criar um usuário admin e um normal
        db_conn.execute(
            "INSERT INTO user (nome, senha, admin) VALUES (?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 1)
        )
        db_conn.execute(
            "INSERT INTO user (nome, senha, admin) VALUES (?, ?, ?)",
            ('user', generate_password_hash('user123'), 0)
        )
        
        # Criar produtos e roshs
        db_conn.execute("INSERT INTO produto (nome) VALUES (?)", ('Narguile Grande',))
        db_conn.execute("INSERT INTO rosh (nome) VALUES (?)", ('Rosh de Barro',))
        
        db_conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao popular dados: {e}")
        db_conn.rollback()
        raise