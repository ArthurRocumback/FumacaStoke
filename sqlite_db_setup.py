import sqlite3
import os
from werkzeug.security import generate_password_hash

senha_admin = generate_password_hash('admin123')
senha_user = generate_password_hash('Teste')

sql_recreate_db = """
    DROP TABLE IF EXISTS produto;
    CREATE TABLE IF NOT EXISTS produto (
        produtoid INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT
    );
    INSERT INTO produto (nome)
    VALUES ('Aluguel Pequeno'),
           ('Aluguel Médio'),
           ('Reposição'),
           ('Funcionário'),
           ('Da casa');

    DROP TABLE IF EXISTS rosh;
    CREATE TABLE IF NOT EXISTS rosh (
        roshid INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT
    );

    INSERT INTO rosh (nome)
    VALUES ('Mix'),
           ('Único');
           
 DROP TABLE IF EXISTS pedido;
    CREATE TABLE IF NOT EXISTS pedido (
        pedidoid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rg TEXT NOT NULL,
        nome_produto INTEGER,
        nome_rosh INTEGER,
        essencia TEXT,
        criacao DATETIME DEFAULT (DATETIME('now', '-3 hours')),
        atualizacao DATETIME DEFAULT (DATETIME('now', '-3 hours')),
        observacao TEXT,
        ativo INTEGER DEFAULT 0,
        FOREIGN KEY(nome_produto) REFERENCES produto(produtoid),
        FOREIGN KEY(nome_rosh) REFERENCES rosh(roshid)
    );
        CREATE TABLE IF NOT EXISTS user(
        userid INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        senha TEXT NOT NULL,
        admin INTEGER DEFAULT 0
    );

"""

db_path = 'db/pedidos_db.db'

# Recria o Banco de dados
# if os.path.exists(db_path):
#     print(f"Database {db_path} já existe. Removendo para recriar...")
#     os.remove(db_path)
# else:
#     print(f"Criando database {db_path}...")

# os.makedirs(os.path.dirname(db_path), exist_ok=True)

# with sqlite3.connect(db_path) as conn:
#     cursor = conn.cursor()

#     cursor.executescript(sql_recreate_db)
#     cursor.execute("INSERT INTO user (nome, senha, admin) VALUES (?, ?, ?), (?, ?, ?)",
#                    ('adm', senha_admin, 1, 'Teste', senha_user, 0))
#     conn.commit()
#     print("Database criado e populado com sucesso!")

#     Não recria o banco de dados se ele já existir
if not os.path.exists(db_path):
    print(f"Criando database {db_path}...")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executescript(sql_recreate_db)
        cursor.execute("INSERT INTO user (nome, senha, admin) VALUES (?, ?, ?), (?, ?, ?)",
                   ('adm', senha_admin, 1, 'Teste', senha_user, 0))
        conn.commit()
        print("Database criado e populado com sucesso!")
else:
    print(f"Database {db_path} já existe. Nenhuma ação necessária.")