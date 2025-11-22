import json

def login(client, usuario, senha, follow_redirects=False):
    return client.post(
        "/login",
        data={"usuario": usuario, "senha": senha},
        follow_redirects=follow_redirects,
    )

# Testes de LOGIN 
def test_login_page_carrega(client):
    res = client.get("/login")
    assert res.status_code == 200
    # Só checa se tem o campo de usuário ou a palavra Login
    assert b"Login" in res.data or b"Usu" in res.data


def test_login_admin_sucesso_redireciona_e_sessao_admin_true(client):
    res = login(client, "adm", "admin123", follow_redirects=False)
    assert res.status_code == 302
    location = res.headers["Location"]
    # Pode redirecionar para "/" ou "/index"
    assert location.endswith("/") or location.endswith("/index")

    # Confere sessão
    with client.session_transaction() as sess:
        assert sess["usuario"] == "adm"
        assert sess["admin"] is True

def test_login_usuario_normal_sucesso_nao_admin(client):
    res = login(client, "Teste", "Teste", follow_redirects=False)
    assert res.status_code == 302

    with client.session_transaction() as sess:
        assert sess["usuario"] == "Teste"
        assert sess["admin"] is False

def test_login_invalido_redireciona_para_login_e_nao_seta_sessao(client):
    res = login(client, "naoexiste", "errada", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/login")

    with client.session_transaction() as sess:
        assert "usuario" not in sess
        assert "admin" not in sess

# Proteção de ROTAS 
def test_index_redireciona_para_login_quando_nao_logado(client):
    res = client.get("/", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_index_abrir_quando_logado(client):
    login(client, "Teste", "Teste")
    res = client.get("/", follow_redirects=False)
    assert res.status_code == 200


def test_historico_redireciona_para_login_quando_nao_logado(client):
    res = client.get("/historico", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_historico_redireciona_usuario_nao_admin_para_index(client):
    # login de usuário normal
    login(client, "Teste", "Teste")
    res = client.get("/historico", follow_redirects=False)
    assert res.status_code == 302
    assert "/index" in res.headers["Location"] or res.headers["Location"].endswith("/")


def test_historico_admin_acessa_ok(client):
    login(client, "adm", "admin123")
    res = client.get("/historico", follow_redirects=False)
    assert res.status_code == 200
    # Conteúdo básico da página de histórico
    assert b"Historico" in res.data or b"Lista Total" in res.data


def test_logout_limpa_sessao_e_redireciona_para_login(client):
    # Faz login primeiro
    login(client, "Teste", "Teste")
    res = client.get("/logout", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]

    with client.session_transaction() as sess:
        assert "usuario" not in sess
        assert "admin" not in sess

# Testes de API / banco 
def test_listar_produtos(client):
    res = client.get("/api/produtos")
    data = res.get_json()
    assert res.status_code == 200
    assert "Aluguel Pequeno" in data

def test_listar_roshs(client):
    res = client.get("/api/roshs")
    data = res.get_json()
    assert res.status_code == 200
    assert "Mix" in data

def test_criar_pedido(client):
    pedido = {
        "nome": "Arthur",
        "rg": "123",
        "produto": "Aluguel Pequeno",
        "rosh": "Mix",
        "essencia": "Uva",
        "observacao": "Nenhuma",
    }

    res = client.post(
        "/api/pedido",
        data=json.dumps(pedido),
        content_type="application/json",
    )

    assert res.status_code == 201
    assert res.get_json()["message"] == "Pedido criado com sucesso!"

def test_listar_pedidos(client):
    res = client.get("/api/pedidos/todos")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_atualizar_status_pedido_ativo(client):
    # cria um pedido
    client.post(
        "/api/pedido",
        data=json.dumps({
            "nome": "Arthur",
            "rg": "123",
            "produto": "Aluguel Pequeno",
            "rosh": "Mix",
            "essencia": "Uva",
            "observacao": "OK",
        }),
        content_type="application/json",
    )

    # atualiza ativo
    res = client.put(
        "/api/pedido/1/ativo",
        data=json.dumps({"ativo": 1}),
        content_type="application/json",
    )

    assert res.status_code == 200
    assert res.get_json()["message"] == "Status atualizado com sucesso"

def test_deletar_pedido(client):
    # cria um pedido
    client.post(
        "/api/pedido",
        data=json.dumps({
            "nome": "Arthur",
            "rg": "123",
            "produto": "Aluguel Pequeno",
            "rosh": "Mix",
            "essencia": "Uva",
            "observacao": "OK",
        }),
        content_type="application/json",
    )

    # deleta
    res = client.delete("/api/pedido/1")
    assert res.status_code == 200
    assert res.get_json()["message"] == "Pedido excluído com sucesso"

#  Rotas extras e ramos não cobertos
def test_index_page_route(client):
    # loga como usuário comum
    login(client, "Teste", "Teste")
    res = client.get("/index")
    assert res.status_code == 200


def test_listar_pedidos_filtrados_60_dias(client):
    # cria um pedido
    client.post(
        "/api/pedido",
        data=json.dumps({
            "nome": "Arthur",
            "rg": "123",
            "produto": "Aluguel Pequeno",
            "rosh": "Mix",
            "essencia": "Uva",
            "observacao": "OK",
        }),
        content_type="application/json",
    )

    # rota /api/pedidos (com filtro de 60 dias)
    res = client.get("/api/pedidos")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_atualizar_pedido_put(client):
    # cria um pedido
    client.post(
        "/api/pedido",
        data=json.dumps({
            "nome": "Arthur",
            "rg": "123",
            "produto": "Aluguel Pequeno",
            "rosh": "Mix",
            "essencia": "Uva",
            "observacao": "OK",
        }),
        content_type="application/json",
    )

    # atualiza o pedido via PUT /api/pedido/<id>
    res = client.put(
        "/api/pedido/1",
        data=json.dumps({
            "nome": "Arthur Editado",
            "rg": "999",
            "produto": "Aluguel Pequeno",
            "rosh": "Mix",
            "essencia": "Maçã",
            "observacao": "Alterado",
        }),
        content_type="application/json",
    )

    assert res.status_code == 200
    assert res.get_json()["message"] == "Pedido atualizado com sucesso"


def test_atualizar_ativo_valor_invalido(client):
    # cria um pedido
    client.post(
        "/api/pedido",
        data=json.dumps({
            "nome": "Arthur",
            "rg": "123",
            "produto": "Aluguel Pequeno",
            "rosh": "Mix",
            "essencia": "Uva",
            "observacao": "OK",
        }),
        content_type="application/json",
    )

    # envia ativo inválido (nem 0 nem 1)
    res = client.put(
        "/api/pedido/1/ativo",
        data=json.dumps({"ativo": 2}),
        content_type="application/json",
    )

    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data


def test_login_ja_logado_redireciona_para_index(client):
    # força sessão como se já estivesse logado
    with client.session_transaction() as sess:
        sess["usuario"] = "Teste"
        sess["admin"] = False

    res = client.get("/login", follow_redirects=False)
    assert res.status_code == 302
    assert "/index" in res.headers["Location"] or res.headers["Location"].endswith("/")
