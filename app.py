from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Caminho do banco de dados SQLite
DB_PATH = 'db/pedidos_db.db'

# Chave de sessão (ideal colocar em variável de ambiente)
app.secret_key = 'chave-muito-secreta-uuuuuuuuuuuuuuuuhh'

# Define o tempo máximo de sessão ativa (2 horas)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# -----------------------------------------------------------
# Conexão com o banco SQLite
# Retorna conexão configurada para acessar colunas como dicts
# -----------------------------------------------------------
def db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acessar resultado por nome da coluna
    return conn


# -----------------------------------------------------------
# Rota inicial "/"
# Exige login — se não estiver logado, redireciona ao /login
# Se logado, renderiza a página principal
# -----------------------------------------------------------
@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', admin=session.get('admin', False))


# -----------------------------------------------------------
# Rota alternativa "/index" (mesmo comportamento da "/")
# -----------------------------------------------------------
@app.route('/index')
def index_page():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', admin=session.get('admin', False))


# -----------------------------------------------------------
# Página de histórico completo de pedidos
# Apenas ADMIN pode acessar
# -----------------------------------------------------------
@app.route('/historico')
def historico():

    # Se não estiver logado → volta ao login
    if 'usuario' not in session:
        return redirect(url_for('login'))

    # Se não for admin → redireciona para a tela principal
    if not session.get('admin'):
        return redirect(url_for('index'))

    # Admin pode acessar o histórico
    return render_template('historico.html', admin=True)


# -----------------------------------------------------------
# Rota de logout
# Limpa totalmente a sessão e manda para o login
# -----------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# -----------------------------------------------------------
# API: retorna lista de produtos cadastrados
# -----------------------------------------------------------
@app.route('/api/produtos')
def listar_produtos():
    conn = db_connection()
    produtos = conn.execute('SELECT nome FROM produto').fetchall()
    conn.close()
    return jsonify([p['nome'] for p in produtos])


# -----------------------------------------------------------
# API: retorna lista de roshs cadastrados
# -----------------------------------------------------------
@app.route('/api/roshs')
def listar_roshs():
    conn = db_connection()
    roshs = conn.execute('SELECT nome FROM rosh').fetchall()
    conn.close()
    return jsonify([r['nome'] for r in roshs])


# -----------------------------------------------------------
# API: listar pedidos dos últimos 60 dias
# -----------------------------------------------------------
@app.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    conn = db_connection()
    pedidos = conn.execute(
        "SELECT * FROM pedido WHERE criacao >= DATETIME('now', '-60 days')"
    ).fetchall()
    conn.close()
    return jsonify([dict(p) for p in pedidos])


# -----------------------------------------------------------
# API: listar TODOS os pedidos do banco
# (sem filtro de data)
# -----------------------------------------------------------
@app.route('/api/pedidos/todos', methods=['GET'])
def listar_todos_pedidos():
    conn = db_connection()
    pedidos = conn.execute("SELECT * FROM pedido").fetchall()
    conn.close()
    return jsonify([dict(p) for p in pedidos])


# -----------------------------------------------------------
# API: criar um novo pedido
# Recebe JSON no corpo do POST
# -----------------------------------------------------------
@app.route('/api/pedido', methods=['POST'])
def criar_pedido():
    data = request.json

    # Extrai campos enviados pelo front-end
    nome = data.get('nome')
    rg = data.get('rg')
    produto = data.get('produto')
    rosh = data.get('rosh')
    essencia = data.get('essencia')
    observacao = data.get('observacao')

    conn = db_connection()
    conn.execute("""
        INSERT INTO pedido (name, rg, nome_produto, nome_rosh, essencia, observacao)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, rg, produto, rosh, essencia, observacao))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Pedido criado com sucesso!'}), 201


# -----------------------------------------------------------
# API: excluir pedido pelo ID
# -----------------------------------------------------------
@app.route('/api/pedido/<int:pedido_id>', methods=['DELETE'])
def deletar_pedido(pedido_id):
    conn = db_connection()
    conn.execute('DELETE FROM pedido WHERE pedidoid = ?', (pedido_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Pedido excluído com sucesso'})


# -----------------------------------------------------------
# API: atualizar o status "ativo" de um pedido (checkbox)
# Apenas aceita valores 0 ou 1
# -----------------------------------------------------------
@app.route('/api/pedido/<int:pedido_id>/ativo', methods=['PUT'])
def atualizar_ativo(pedido_id):
    print(f"Received PUT request for pedido_id: {pedido_id}")

    data = request.json
    ativo = data.get('ativo')

    # Validação: apenas 0 ou 1 são permitidos
    if ativo not in [0, 1]:
        return jsonify({'error': 'Valor de ativo inválido'}), 400

    conn = db_connection()
    conn.execute(
        "UPDATE pedido SET ativo = ?, atualizacao = ? WHERE pedidoid = ?",
        (ativo, datetime.now(), pedido_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Status atualizado com sucesso'}), 200


# -----------------------------------------------------------
# API: atualizar um pedido inteiro (PUT)
# -----------------------------------------------------------
@app.route('/api/pedido/<int:pedido_id>', methods=['PUT'])
def atualizar_pedido(pedido_id):
    data = request.json

    # Extrai os dados enviados pelo front-end
    nome = data.get('nome')
    rg = data.get('rg')
    produto = data.get('produto')
    rosh = data.get('rosh')
    essencia = data.get('essencia')
    observacao = data.get('observacao')

    conn = db_connection()
    conn.execute("""
        UPDATE pedido
        SET name = ?, rg = ?, nome_produto = ?, nome_rosh = ?, essencia = ?, atualizacao = ?, observacao = ?
        WHERE pedidoid = ?
    """, (nome, rg, produto, rosh, essencia, datetime.now(), observacao, pedido_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Pedido atualizado com sucesso'})


# -----------------------------------------------------------
# Rota de login (GET e POST)
# - GET → exibe página de login
# - POST → valida credenciais, cria sessão e redireciona
# -----------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    # Se já estiver logado, manda direto para o index
    if 'usuario' in session:
        return redirect(url_for('index'))
    
    # Processa tentativa de login
    if request.method == 'POST':
        nome = request.form['usuario']
        senha = request.form['senha']

        conn = db_connection()
        user = conn.execute(
            'SELECT * FROM user WHERE nome = ?',
            (nome,)
        ).fetchone()
        conn.close()

        # Se usuário existe e senha está correta
        if user and check_password_hash(user['senha'], senha):
            session.permanent = True
            session['usuario'] = user['nome']
            session['admin'] = bool(user['admin'])  # Pode ser admin = True/False
            return redirect(url_for('index'))

        # Login inválido
        else:
            flash('Usuário ou senha inválidos')
            return redirect(url_for('login'))

    # Exibe o template de login
    return render_template('Login.html')


# -----------------------------------------------------------
# Execução do servidor Flask
# -----------------------------------------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
