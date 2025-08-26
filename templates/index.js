let pedidoEditadoId = null;

            async function carregarDropdowns() {
                const produtoRes = await fetch('/api/produtos');
                const produtos = await produtoRes.json();
                const roshRes = await fetch('/api/roshs');
                const roshs = await roshRes.json();

                const produtoSelect = document.getElementById('produtos');
                const roshSelect = document.getElementById('roshs');

                produtoSelect.innerHTML = '<option value="" hidden></option>';
                roshSelect.innerHTML = '<option value="" hidden></option>';

                produtos.forEach(prod => {
                    const option = document.createElement('option');
                    option.value = prod;
                    option.textContent = prod;
                    produtoSelect.appendChild(option);
                });

                roshs.forEach(rosh => {
                    const option = document.createElement('option');
                    option.value = rosh;
                    option.textContent = rosh;
                    roshSelect.appendChild(option);
                });
            }

            async function carregarPedidos() {
                try {
                    const res = await fetch('/api/pedidos');
                    const pedidos = await res.json();

                    pedidos.sort((a, b) => b.pedidoid - a.pedidoid);

                    pedidosArmazenados = pedidos;
                    paginaAtual = 1;
                    exibirPagina(paginaAtual);
                    Resumo(); // se você ainda usa
                } catch (error) {
                    console.error('Erro ao carregar pedidos:', error);
                }
                }

            window.onload = async () => {
                await carregarDropdowns();
                await carregarPedidos();
            }

            document.getElementById('btnEnviar').addEventListener('click', async function () {
                // Preencher os dados
                const nome = document.querySelector('[name="Nome_1"]').value;
                const rg = document.querySelector('[name="RG_1"]').value;
                const produto = document.querySelector('[name="produto_1"]').value;
                const rosh = document.querySelector('[name="Rosh_1"]').value;
                const essencia = document.querySelector('[name="Essencia"]').value;
                const observacao = document.querySelector('[name="Observação"]').value;

                // Verifica se todos os campos estão preenchidos
                if (nome && rg && produto && rosh && essencia && observacao) {
                    const pedidoData = { nome, rg, produto, rosh, essencia, observacao };
                    
                    await fetch('/api/pedido', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(pedidoData)
                    });

                    // Limpar formulário
                    document.getElementById('formPedido').reset();
                    carregarPedidos();

                } else {
                    alert('Por favor, preencha todos os campos.');
                }
            });
            // Envia os dados do formulario preenchido para o campo de pedidos
            function adicionarLinhaTabela(pedido) {
                const tbody = document.querySelector('#tabelaPedidos tbody');
                const tr = document.createElement('tr');
                const switchChecked = pedido.ativo ? 'checked' : '';

                tr.innerHTML = `
                <td>${pedido.pedidoid}</td>
                <td>${pedido.name}</td>
                <td>${pedido.rg}</td>
                <td>${pedido.nome_produto}</td>
                <td>${pedido.nome_rosh}</td>
                <td>${pedido.essencia}</td>
                <td>${pedido.observacao}</td>
                <td>${pedido.criacao}</td>
                <td>
                    <button class="btn btn-warning btn-sm" onclick="editarPedido(${pedido.pedidoid}, this)">Editar</button>
                    <button class="btn btn-danger btn-sm ml" onclick="excluirPedido(${pedido.pedidoid})">Excluir</button>
                    <button class="btn btn-info btn-sm ml" onclick='preencherFormulario(${JSON.stringify(pedido)})'>Reutilizar</button>
                    </td>
                    <td>
                    <label class="switch-toggle d-inline-block">
                    <input type="checkbox" ${switchChecked} onchange="onToggleChange(this, ${pedido.pedidoid})">
                    <span class="slider-toggle"></span>
                    </label>
                </td>
                `;
                tbody.appendChild(tr);
            }
            
                function onToggleChange(checkbox, pedidoId) {
                    const ativo = checkbox.checked ? 1 : 0;

                    fetch(`/api/pedido/${pedidoId}/ativo`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ativo })
                    })
                    .then(res => {
                        if (!res.ok) {
                            throw new Error('Falha ao atualizar');
                        }
                        return res.json();
                    })
                    .then(data => {
                        console.log('Status atualizado:', data);
                    })
                    .catch(error => {
                        alert('Erro ao atualizar o status.');
                        console.error(error);
                    });
                }

            async function editarPedido(id, btn) {
                const tr = btn.closest('tr');

                const nome = tr.cells[1].textContent;
                const rg = tr.cells[2].textContent;
                const produtoAtual = tr.cells[3].textContent;
                const roshAtual = tr.cells[4].textContent;
                const essencia = tr.cells[5].textContent;
                const observacao = tr.cells[6].textContent;

                document.getElementById('editPedidoId').value = id
                document.getElementById('editNome').value = tr.cells[1].textContent;
                document.getElementById('editRG').value = tr.cells[2].textContent;
                document.getElementById('editEssencia').value = tr.cells[5].textContent;
                document.getElementById('editObservacao').value = tr.cells[6].textContent;

                const produtoRes = await fetch('/api/produtos');
                const produtos = await produtoRes.json();
                const produtoSelect = document.getElementById('editProduto');
                produtoSelect.innerHTML = ''; // limpa antes de preencher

                produtos.forEach(prod => {
                    const option = document.createElement('option');
                    option.value = prod;
                    option.textContent = prod;
                    if (prod === produtoAtual) option.selected = true;
                    produtoSelect.appendChild(option);
                });

                const roshRes = await fetch('/api/roshs');
                const roshs = await roshRes.json();
                const roshSelect = document.getElementById('editRosh');
                roshSelect.innerHTML = ''; // limpa antes de preencher

                roshs.forEach(rosh => {
                    const option = document.createElement('option');
                    option.value = rosh;
                    option.textContent = rosh;
                    if (rosh === roshAtual) option.selected = true;
                    roshSelect.appendChild(option);
                });
                $('#editModal').modal('show');
            }
            function preencherFormulario(pedido) {
                document.querySelector('[name="Nome_1"]').value = pedido.name;
                document.querySelector('[name="RG_1"]').value = pedido.rg;
                document.querySelector('[name="Essencia"]').value = pedido.essencia;
                document.querySelector('[name="Observação"]').value = pedido.observacao;

                const produtoSelect = document.getElementById('produtos');
                const roshSelect = document.getElementById('roshs');

                for (let option of produtoSelect.options) {
                    if (option.value === 'Reposição') {
                        option.selected = true;
                        break;
                    }
                }

                // Mantém seleção do rosh conforme o pedido
                for (let option of roshSelect.options) {
                    if (option.value == pedido.nome_rosh) {
                        option.selected = true;
                        break;
                    }
                }

                document.querySelector('[name="Nome_1"]').focus();
            }

            document.getElementById('formEditar').addEventListener('submit', async function (e) {
                e.preventDefault();

                const id = document.getElementById('editPedidoId').value;
                const nome = document.getElementById('editNome').value.trim();
                const rg = document.getElementById('editRG').value.trim();
                const produto = document.getElementById('editProduto').value.trim();
                const rosh = document.getElementById('editRosh').value.trim();
                const essencia = document.getElementById('editEssencia').value.trim();
                const observacao = document.getElementById('editObservacao').value.trim();

                // Validação: verifica se os campos obrigatórios estão preenchidos
                if (!nome || !rg || !produto || !rosh || !essencia || !observacao) {
                    alert('Por favor, preencha todos os campos obrigatórios.');
                    return;
                }

                const dadosAtualizados = {
                    nome,
                    rg,
                    produto,
                    rosh,
                    essencia,
                    observacao
                };

                try {
                    const resposta = await fetch(`/api/pedido/${id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(dadosAtualizados)
                    });

                    if (resposta.ok) {
                        $('#editModal').modal('hide');
                        await carregarPedidos();
                    } else {
                        alert('Erro ao atualizar o pedido.');
                    }
                } catch (erro) {
                    console.error('Erro na atualização:', erro);
                    alert('Erro ao tentar atualizar o pedido.');
                }
            });

              let pedidoIdParaExcluir = null;
                const senhaModal = new bootstrap.Modal(document.getElementById('senhaModal'));

                async function excluirPedido(id) {
                pedidoIdParaExcluir = id;
                document.getElementById('senhaInput').value = '';
                senhaModal.show();

                setTimeout(() => {
                    document.getElementById('senhaInput').focus();
                 }, 500);
                }
                document.addEventListener("DOMContentLoaded", function () {
                    const senhaInput = document.getElementById('senhaInput');

                    senhaInput.addEventListener('keydown', function (event) {
                        if (event.key === 'Enter') {
                        event.preventDefault();
                        confirmarSenha(); 
                        }
                    });
                });

                async function confirmarSenha() {
                const senha = document.getElementById('senhaInput').value;

                if (senha === '@Re270912') {
                    try {
                    const resposta = await fetch(`/api/pedido/${pedidoIdParaExcluir}`, { method: 'DELETE' });

                    if (resposta.ok) {
                        carregarPedidos(); // Atualiza a tabela
                    } else {
                        alert('Erro ao excluir o pedido no servidor.');
                        console.error('Erro DELETE:', resposta.statusText);
                    }
                    } catch (erro) {
                    alert('Erro na conexão com o servidor.');
                    console.error(erro);
                    }
                } else {
                    alert('Senha incorreta. Exclusão cancelada.');
                }
                senhaModal.hide();
                }
            // Máscara para o campo de RG
            function aplicarMascaraRG(input) {
                input.addEventListener('input', function (e) {
                    let valor = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
                    if (valor.length > 11) {
                    valor = valor.slice(0, 11);
                    }
                    if (valor.length === 9) {
                    valor = valor.replace(/^(\d{2})(\d{3})(\d{3})(\d{1})$/, '$1.$2.$3-$4');
                    } else if (valor.length >= 10) {
                    valor = valor.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4');
                    }
                    e.target.value = valor;
                });
}
            aplicarMascaraRG(document.getElementById('RG_1'));
            aplicarMascaraRG(document.getElementById('editRG'));

            document.getElementById('formPedido').addEventListener('keydown', function (event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    document.getElementById('btnEnviar').click();
                }
            });

            let pedidosArmazenados = [];
                    let paginaAtual = 1;
                    const itensPorPagina = 10;

                function exibirPagina(pagina) {
                    const tbody = document.querySelector('#tabelaPedidos tbody');
                    tbody.innerHTML = '';

                    const inicio = (pagina - 1) * itensPorPagina;
                    const fim = inicio + itensPorPagina;
                    const pedidosPagina = pedidosArmazenados.slice(inicio, fim);

                    pedidosPagina.forEach(pedido => adicionarLinhaTabela(pedido));

                    paginaAtual = pagina;
                    atualizarPaginacao();
                    }

                function atualizarPaginacao() {
                    const totalPaginas = Math.ceil(pedidosArmazenados.length / itensPorPagina);
                    const paginacaoDiv = document.getElementById('paginacao');
                    paginacaoDiv.innerHTML = '';

                    if (totalPaginas <= 1) return;

                    const criarBotaoSeta = (simbolo, novaPagina, habilitar) => {
                        const btn = document.createElement('button');
                        btn.textContent = simbolo;
                        btn.className = 'btn btn-outline-primary btn-sm';
                        btn.disabled = !habilitar;
                        if (habilitar) {
                        btn.onclick = () => exibirPagina(novaPagina);
                        }
                        return btn;
                    };

                    const anteriorHabilitado = paginaAtual > 1;
                    paginacaoDiv.appendChild(criarBotaoSeta('‹', paginaAtual - 1, anteriorHabilitado));

                    const texto = document.createElement('span');
                    texto.textContent = `${paginaAtual} / ${totalPaginas}`;
                    texto.className = 'mx-2 fw-bold';
                    paginacaoDiv.appendChild(texto);

                    const proximoHabilitado = paginaAtual < totalPaginas;
                    paginacaoDiv.appendChild(criarBotaoSeta('›', paginaAtual + 1, proximoHabilitado));
                    }

                document.getElementById('filtroPedidos').addEventListener('input', function () {
                const termo = this.value.trim().toLowerCase();
                const tbody = document.querySelector('#tabelaPedidos tbody');
                tbody.innerHTML = '';

                if (termo === '') {
                    exibirPagina(paginaAtual);
                    return;
                }

                const resultadosFiltrados = pedidosArmazenados.filter(pedido => {
                    const texto = (
                    pedido.pedidoid +
                    pedido.name +
                    pedido.rg +
                    pedido.nome_produto +
                    pedido.nome_rosh +
                    pedido.essencia +
                    pedido.observacao +
                    pedido.criacao
                    ).toLowerCase();

                    return texto.includes(termo);
                });

                document.getElementById('paginacao').style.display = 'none';

                resultadosFiltrados.forEach(pedido => {
                    adicionarLinhaTabela(pedido);
                });
                });