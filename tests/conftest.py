import os
import sys
import tempfile
import pytest
import sqlite3
from werkzeug.security import generate_password_hash

# Descobre o diretório raiz do projeto (pasta um nível acima de "tests")
# Ex: .../FumaçaStoke/tests  -> PROJECT_ROOT = .../FumaçaStoke
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Garante que o diretório raiz do projeto esteja no sys.path
# para que possamos fazer "import app" normalmente.
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Importa o módulo completo "app" (para acessar DB_PATH, etc.)
import app as app_module
# Importa somente a instância Flask chamada "app" de dentro do módulo
from app import app as flask_app


@pytest.fixture
def app():
    """
    Fixture principal do pytest que configura uma instância do app Flask
    apontando para um BANCO DE DADOS TEMPORÁRIO (isolado para testes).

    Ela:
    - Cria um arquivo .db temporário
    - Ajusta o DB_PATH do app para usar esse arquivo
    - Cria as tabelas necessárias (produto, rosh, pedido, user)
    - Popula dados mínimos de teste (1 produto, 1 rosh, admin e user)
    - Entrega o app configurado para os testes
    - Remove o banco temporário no final
    """

    # Cria um arquivo de banco SQLite temporário
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()  # fecha o handle, mas mantém o arquivo no disco

    # Faz o app usar esse banco de dados temporário
    app_module.DB_PATH = temp_db.name
    flask_app.config["TESTING"] = True  # ativa modo de teste no Flask

    conn = sqlite3.connect(temp_db.name)
    cursor = conn.cursor()

    # Cria a estrutura mínima de tabelas necessária para os testes.
    # Isso é baseado no sqlite_db_setup.py, mas simplificado para o ambiente de teste.
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

    # Insere dados básicos necessários para o funcionamento do sistema nos testes

    # 1 produto padrão para os testes de listagem e criação de pedidos
    cursor.execute("INSERT INTO produto (nome) VALUES (?)", ("Aluguel Pequeno",))

    # 1 rosh padrão
    cursor.execute("INSERT INTO rosh (nome) VALUES (?)", ("Mix",))

    # Cria hashes de senha compatíveis com o login do app
    senha_admin = generate_password_hash("admin123")  # senha do usuário admin
    senha_user = generate_password_hash("Teste")      # senha do usuário comum

    # Insere dois usuários:
    # - "adm": admin=1 (tem acesso a /historico)
    # - "Teste": admin=0 (usuário comum, sem acesso ao histórico total)
    cursor.executemany(
        "INSERT INTO user (nome, senha, admin) VALUES (?, ?, ?)",
        [
            ("adm", senha_admin, 1),   # usuário administrador
            ("Teste", senha_user, 0),  # usuário normal
        ],
    )

    conn.commit()
    conn.close()

    # Entrega o app já configurado para o pytest usar
    yield flask_app

    # Após todos os testes que usam essa fixture terminarem,
    # remove o arquivo de banco de dados temporário.
    os.unlink(temp_db.name)


@pytest.fixture
def client(app):
    """
    Fixture "client" que retorna o test_client() do Flask.

    É o objeto utilizado para simular requisições HTTP às rotas do app,
    como se fosse um navegador ou um frontend chamando a API.
    """
    return app.test_client()
