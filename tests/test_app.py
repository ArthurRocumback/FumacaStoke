# tests/test_app.py
import json

# Função helper para facilitar o login nos testes
def login(client, username, password):
    return client.post('/login', data={'usuario': username, 'senha': password}, follow_redirects=True)

# --- Testes de Autenticação e Acesso ---

def test_login_page_get(client):
    """Testa se a página de login carrega."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data # Verifica se o HTML de Login é renderizado

def test_index_redirects_when_logged_out(client):
    """Testa se a rota principal redireciona para /login se não logado."""
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    # Verifica se fomos redirecionados para a página de login
    assert b"Login" in response.data 

def test_login_success_admin(client, seed_data):
    """Testa o login bem-sucedido de um admin."""
    # seed_data garante que o usuário 'admin' exista
    response = login(client, 'admin', 'admin123')
    assert response.status_code == 200
    assert b"Historico" in response.data # Admin vê o link do histórico
    
    # Testar se a sessão foi criada corretamente
    with client.session_transaction() as sess:
        assert sess['usuario'] == 'admin'
        assert sess['admin'] == True

def test_login_success_user(client, seed_data):
    """Testa o login bem-sucedido de um usuário comum."""
    response = login(client, 'user', 'user123')
    assert response.status_code == 200
    # Usuário comum não deve ver o link de admin
    assert b"Historico" not in response.data 
    
    with client.session_transaction() as sess:
        assert sess['usuario'] == 'user'
        assert sess['admin'] == False

def test_login_fail(client, seed_data):
    """Testa falha no login com senha errada."""
    response = login(client, 'admin', 'senhaerrada')
    assert response.status_code == 200
    # Verifica a mensagem de flash de erro
    assert b"Usuario ou senha invalidos" in response.data
    
def test_logout(client, seed_data):
    """Testa o logout."""
    login(client, 'admin', 'admin123') # Loga primeiro
    
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data # Deve voltar para a tela de login

    # Tentar acessar a home, deve ser redirecionado
    response_index = client.get('/', follow_redirects=True)
    assert b"Login" in response_index.data

# --- Testes de API ---

def test_api_list_produtos(client, seed_data):
    """Testa a API de listar produtos."""
    response = client.get('/api/produtos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert 'Narguile Grande' in data

def test_api_list_roshs(client, seed_data):
    """Testa a API de listar roshs."""
    response = client.get('/api/roshs')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Rosh de Barro' in data

def test_api_create_pedido(client, db_conn):
    """Testa a criação de um novo pedido via API."""
    pedido_data = {
        'nome': 'Cliente Teste',
        'rg': '123456',
        'produto': 'Narguile',
        'rosh': 'Rosh Barro',
        'essencia': 'Menta',
        'observacao': 'Sem gelo'
    }
    response = client.post('/api/pedido', json=pedido_data)
    assert response.status_code == 201 # 201 Created
    
    # Verifica diretamente no banco de dados
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM pedido WHERE name = ?", ('Cliente Teste',))
    pedido_db = cursor.fetchone()
    
    assert pedido_db is not None
    assert pedido_db['essencia'] == 'Menta'
    assert pedido_db['observacao'] == 'Sem gelo'

def test_api_delete_pedido(client, db_conn):
    """Testa a exclusão de um pedido via API."""
    # 1. Criar um pedido para deletar
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO pedido (name) VALUES (?)", ('Pedido a Deletar',))
    db_conn.commit()
    pedido_id = cursor.lastrowid
    
    # 2. Deletar o pedido
    response = client.delete(f'/api/pedido/{pedido_id}')
    assert response.status_code == 200
    assert b"Pedido excluido com sucesso" in response.data
    
    # 3. Verificar se foi deletado
    cursor.execute("SELECT * FROM pedido WHERE pedidoid = ?", (pedido_id,))
    pedido_db = cursor.fetchone()
    assert pedido_db is None

def test_api_update_pedido_ativo(client, db_conn):
    """Testa a atualização do status 'ativo' de um pedido."""
    # 1. Criar um pedido (ativo=1 por padrão)
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO pedido (name) VALUES (?)", ('Pedido Ativo',))
    db_conn.commit()
    pedido_id = cursor.lastrowid
    
    # 2. Atualizar para inativo (ativo=0)
    response = client.put(f'/api/pedido/{pedido_id}/ativo', json={'ativo': 0})
    assert response.status_code == 200
    
    # 3. Verificar no banco
    cursor.execute("SELECT ativo FROM pedido WHERE pedidoid = ?", (pedido_id,))
    pedido_db = cursor.fetchone()
    assert pedido_db['ativo'] == 0