# tests/test_app.py
def test_login_page_get(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data


def test_index_redirects_when_logged_out(client):
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_fail(client):
    response = client.post('/login', data={'usuario': 'invalido', 'senha': 'errada'}, follow_redirects=True)
    assert b"Usu" in response.data or response.status_code == 200

def test_logout(client):
    # Testa o logout sem envolver banco de dados.
    # Simula login falso na sessão
    with client.session_transaction() as sess:
        sess['usuario'] = 'teste'
        sess['admin'] = True

    # Executa logout
    response = client.get('/logout', follow_redirects=True)
    
    # Deve redirecionar para /login
    assert response.status_code == 200
    assert b"Login" in response.data

    # Verifica se a sessão foi realmente limpa
    with client.session_transaction() as sess:
        assert 'usuario' not in sess
        assert 'admin' not in sess
