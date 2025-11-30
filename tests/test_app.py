import json

# Função auxiliar para facilitar o login durante os testes.
# Em vez de repetir client.post("/login", ...) em todo teste,
# usamos login(client, usuario, senha).
def login(client, usuario, senha, follow_redirects=False):
    return client.post(
        "/login",
        data={"usuario": usuario, "senha": senha},
        follow_redirects=follow_redirects,
    )

# -------------------------------------------------------------------
#                         TESTES DE LOGIN
# -------------------------------------------------------------------

def test_login_page_carrega(client):
    """
    Verifica se a página de login carrega corretamente (status 200)
    e se o HTML contém alguma indicação de formulário de login.
    """
    res = client.get("/login")
    assert res.status_code == 200
    # Checa se tem a palavra "Login" ou parte de "Usuário" na página
    assert b"Login" in res.data or b"Usu" in res.data


def test_login_admin_sucesso_redireciona_e_sessao_admin_true(client):
    """
    Testa login bem-sucedido do usuário ADM:
    - Faz POST com usuário 'adm' e senha 'admin123'
    - Verifica redirecionamento (302) para index
    - Checa se sessão foi preenchida com usuario='adm' e admin=True
    """
    res = login(client, "adm", "admin123", follow_redirects=False)
    assert res.status_code == 302
    location = res.headers["Location"]
    # Pode redirecionar para "/" ou "/index"
    assert location.endswith("/") or location.endswith("/index")

    # Confere sessão criada
    with client.session_transaction() as sess:
        assert sess["usuario"] == "adm"
        assert sess["admin"] is True


def test_login_usuario_normal_sucesso_nao_admin(client):
    """
    Testa login de usuário comum ('Teste'):
    - Garante que o login funciona (redireciona)
    - Garante que admin=False na sessão
    """
    res = login(client, "Teste", "Teste", follow_redirects=False)
    assert res.status_code == 302

    with client.session_transaction() as sess:
        assert sess["usuario"] == "Teste"
        assert sess["admin"] is False


def test_login_invalido_redireciona_para_login_e_nao_seta_sessao(client):
    """
    Testa tentativa de login inválido:
    - Usuário e senha errados
    - Deve redirecionar de volta para /login
    - Não deve setar 'usuario' nem 'admin' na sessão
    """
    res = login(client, "naoexiste", "errada", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/login")

    with client.session_transaction() as sess:
        assert "usuario" not in sess
        assert "admin" not in sess


# -------------------------------------------------------------------
#                    TESTES DE PROTEÇÃO DE ROTAS
# -------------------------------------------------------------------

def test_index_redireciona_para_login_quando_nao_logado(client):
    """
    Se tentar acessar "/" sem estar logado,
    o sistema deve redirecionar para /login.
    """
    res = client.get("/", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_index_abrir_quando_logado(client):
    """
    Se o usuário estiver logado, acessar "/" deve retornar 200 (OK).
    """
    login(client, "Teste", "Teste")
    res = client.get("/", follow_redirects=False)
    assert res.status_code == 200


def test_historico_redireciona_para_login_quando_nao_logado(client):
    """
    A rota /historico exige sessão.
    Se não estiver logado, deve redirecionar para /login.
    """
    res = client.get("/historico", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_historico_redireciona_usuario_nao_admin_para_index(client):
    """
    Usuário comum (não admin) não pode acessar /historico.
    Deve ser redirecionado para /index (ou /).
    """
    # login de usuário normal
    login(client, "Teste", "Teste")
    res = client.get("/historico", follow_redirects=False)
    assert res.status_code == 302
    assert "/index" in res.headers["Location"] or res.headers["Location"].endswith("/")


def test_historico_admin_acessa_ok(client):
    """
    Usuário admin ('adm') deve conseguir acessar /historico
    e receber status 200.
    """
    login(client, "adm", "admin123")
    res = client.get("/historico", follow_redirects=False)
    assert res.status_code == 200
    # Checa se o HTML contém algo típico da página de histórico
    assert b"Historico" in res.data or b"Lista Total" in res.data


def test_logout_limpa_sessao_e_redireciona_para_login(client):
    """
    Testa o fluxo de logout:
    - Faz login
    - Chama /logout
    - Verifica redirecionamento para /login
    - Confirma que a sessão foi limpa
    """
    login(client, "Teste", "Teste")
    res = client.get("/logout", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]

    with client.session_transaction() as sess:
        assert "usuario" not in sess
        assert "admin" not in sess


# -------------------------------------------------------------------
#                    TESTES DAS APIS / BANCO
# -------------------------------------------------------------------

def test_listar_produtos(client):
    """
    Verifica se a rota /api/produtos retorna status 200
    e contém o produto 'Aluguel Pequeno' inserido no banco de teste.
    """
    res = client.get("/api/produtos")
    data = res.get_json()
    assert res.status_code == 200
    assert "Aluguel Pequeno" in data


def test_listar_roshs(client):
    """
    Verifica se a rota /api/roshs retorna status 200
    e contém o rosh 'Mix' inserido no banco de teste.
    """
    res = client.get("/api/roshs")
    data = res.get_json()
    assert res.status_code == 200
    assert "Mix" in data


def test_criar_pedido(client):
    """
    Testa a criação de um pedido via POST em /api/pedido.
    Verifica:
    - status 201
    - mensagem de sucesso no JSON
    """
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
    """
    Verifica se a rota /api/pedidos/todos responde 200
    e retorna uma lista (mesmo vazia).
    """
    res = client.get("/api/pedidos/todos")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_atualizar_status_pedido_ativo(client):
    """
    Testa o fluxo:
    - Criar um pedido
    - Atualizar o campo 'ativo' via /api/pedido/<id>/ativo
    - Verificar status 200 e mensagem de sucesso
    """
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
    """
    Testa o fluxo:
    - Criar um pedido
    - Deletar via /api/pedido/<id>
    - Verificar status 200 e mensagem de sucesso
    """
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


# -------------------------------------------------------------------
#          ROTAS EXTRAS E RAMOS QUE MELHORAM A COBERTURA
# -------------------------------------------------------------------

def test_index_page_route(client):
    """
    Garante que a rota /index também funciona
    quando o usuário está logado.
    """
    login(client, "Teste", "Teste")
    res = client.get("/index")
    assert res.status_code == 200


def test_listar_pedidos_filtrados_60_dias(client):
    """
    Testa a rota /api/pedidos (que tem filtro de últimos 60 dias):
    - Cria um pedido
    - Chama /api/pedidos
    - Verifica que retorna lista com pelo menos 1 item
    """
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

    res = client.get("/api/pedidos")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_atualizar_pedido_put(client):
    """
    Testa a atualização completa de um pedido via PUT em /api/pedido/<id>.
    - Cria um pedido
    - Envia novos dados (nome, rg, produto etc.)
    - Verifica status 200 e mensagem de sucesso
    """
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
    """
    Verifica a validação da rota /api/pedido/<id>/ativo:
    - Cria um pedido
    - Envia 'ativo' com valor inválido (2)
    - Espera status 400 e mensagem de erro
    """
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

    res = client.put(
        "/api/pedido/1/ativo",
        data=json.dumps({"ativo": 2}),  # valor inválido (só aceita 0 ou 1)
        content_type="application/json",
    )

    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data


def test_login_ja_logado_redireciona_para_index(client):
    """
    Simula um usuário que já está logado e tenta acessar /login.
    O comportamento esperado é:
    - Redirecionar direto para /index (não mostrar tela de login).
    """
    # Força sessão como se já estivesse logado
    with client.session_transaction() as sess:
        sess["usuario"] = "Teste"
        sess["admin"] = False

    res = client.get("/login", follow_redirects=False)
    assert res.status_code == 302
    assert "/index" in res.headers["Location"] or res.headers["Location"].endswith("/")
