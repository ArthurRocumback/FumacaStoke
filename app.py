from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

app = Flask(__name__)

DB_PATH = 'db/pedidos_db.db'

app.secret_key = 'chave-muito-secreta-uuuuuuuuuuuuuuuuhh' # Colocar em um .env para não expor no código

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

def db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', admin=session.get('admin', False))

@app.route('/index')
def index_page():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', admin=session.get('admin', False))

@app.route('/historico')
def historico():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    if not session.get('admin'):
        return redirect(url_for('index'))

    return render_template('historico.html', admin=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/produtos')
def listar_produtos():
    conn = db_connection()
    produtos = conn.execute('SELECT nome FROM produto').fetchall()
    conn.close()
    return jsonify([p['nome'] for p in produtos])

@app.route('/api/roshs')
def listar_roshs():
    conn = db_connection()
    roshs = conn.execute('SELECT nome FROM rosh').fetchall()
    conn.close()
    return jsonify([r['nome'] for r in roshs])

@app.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    conn = db_connection()
    pedidos = conn.execute("SELECT * FROM pedido WHERE criacao >= DATETIME('now', '-60 days')").fetchall()
    conn.close()
    return jsonify([dict(p) for p in pedidos])

@app.route('/api/pedidos/todos', methods=['GET'])
def listar_todos_pedidos():
    conn = db_connection()
    pedidos = conn.execute("SELECT * FROM pedido").fetchall()
    conn.close()
    return jsonify([dict(p) for p in pedidos])

@app.route('/api/pedido', methods=['POST'])
def criar_pedido():
    data = request.json
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

@app.route('/api/pedido/<int:pedido_id>', methods=['DELETE'])
def deletar_pedido(pedido_id):
    conn = db_connection()
    conn.execute('DELETE FROM pedido WHERE pedidoid = ?', (pedido_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Pedido excluído com sucesso'})

@app.route('/api/pedido/<int:pedido_id>/ativo', methods=['PUT'])
def atualizar_ativo(pedido_id):
    print(f"Received PUT request for pedido_id: {pedido_id}") # Adicione isto
    data = request.json
    ativo = data.get('ativo')

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


@app.route('/api/pedido/<int:pedido_id>', methods=['PUT'])
def atualizar_pedido(pedido_id):
    data = request.json
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
        WHERE  pedidoid = ?
    """, (nome, rg, produto, rosh, essencia, datetime.now(), observacao, pedido_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Pedido atualizado com sucesso'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nome = request.form['usuario']
        senha = request.form['senha']

        conn = db_connection()
        user = conn.execute(
            'SELECT * FROM user WHERE nome = ?',
            (nome,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['senha'], senha):
            session.permanent = True
            session['usuario'] = user['nome']
            session['admin'] = bool(user['admin'])
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos')
            return redirect(url_for('login'))

    return render_template('Login.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)