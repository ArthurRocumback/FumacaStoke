document.getElementById('filtroPedidos').addEventListener('input', function () {
                const filtro = this.value.toLowerCase();
                const linhas = document.querySelectorAll('#tabelaPedidos tbody tr');

                linhas.forEach(linha => {
                    const textoLinha = linha.textContent.toLowerCase();
                    const corresponde = textoLinha.includes(filtro);
                    linha.style.display = corresponde ? '' : 'none';
                });
                });

                document.querySelectorAll('#tabelaPedidos th').forEach((th, index) => {
                    th.style.cursor = 'pointer';
                    let ascendente = true;

                    th.addEventListener('click', () => {
                        const tbody = document.querySelector('#tabelaPedidos tbody');
                        const linhas = Array.from(tbody.querySelectorAll('tr'));

                        // Remove setas de todos os ths
                        document.querySelectorAll('#tabelaPedidos th').forEach(th => {
                        th.textContent = th.textContent.replace(/[\u2191\u2193]/g, '').trim();
                        });

                        // Pega o nome original da coluna (antes de alterar)
                        const nomeColuna = th.textContent.replace(/[\u2191\u2193]/g, '').trim();

                        linhas.sort((a, b) => {
                        const valA = a.children[index].textContent.trim().toLowerCase();
                        const valB = b.children[index].textContent.trim().toLowerCase();

                        const aNum = parseFloat(valA.replace(',', '.'));
                        const bNum = parseFloat(valB.replace(',', '.'));
                        const isNumero = !isNaN(aNum) && !isNaN(bNum);

                        if (isNumero) {
                            return ascendente ? aNum - bNum : bNum - aNum;
                        } else {
                            return ascendente ? valA.localeCompare(valB) : valB.localeCompare(valA);
                        }
                        });

                        // Reinsere linhas ordenadas
                        tbody.innerHTML = '';
                        linhas.forEach(tr => tbody.appendChild(tr));

                        // Adiciona seta na coluna clicada
                        const seta = ascendente ? ' \u2191' : ' \u2193'; // ↑ ou ↓
                        th.textContent = nomeColuna + seta;

                        ascendente = !ascendente;
                    });
                    });


            const valorPorProduto = {
                'Aluguel Médio': 40,
                'Aluguel Pequeno': 35,
                'Reposição': 20,
                'Funcionário': 10,
                'Da casa':0
                };

           async function carregarPedidos(){
                const res = await fetch('/api/pedidos/todos');
                const pedidos = await res.json();
                const tbody = document.querySelector('#tabelaPedidos tbody');
                tbody.innerHTML = '';

                pedidos.forEach(pedido => {
                    adicionarLinhaTabela(pedido);
                });
            }

            window.onload = async () => {
                await carregarPedidos();
            }

            function adicionarLinhaTabela(pedido) {
                const tbody = document.querySelector('#tabelaPedidos tbody');
                const tr = document.createElement('tr');
                const valor = valorPorProduto[pedido.nome_produto] || 0;

                tr.innerHTML = `
                    <td>${pedido.pedidoid}</td>
                    <td>${pedido.name}</td>
                    <td>${pedido.rg}</td>
                    <td>${pedido.nome_produto}</td>
                    <td>${pedido.nome_rosh}</td>
                    <td>${pedido.essencia}</td>
                    <td>${pedido.observacao}</td>
                    <td>${pedido.criacao}</td>
                    <td>${valor}</td>
                    `;
                tbody.prepend(tr);

                Resumo();
            }

                function Resumo() {
                const linhas = document.querySelectorAll('#tabelaPedidos tbody tr');
                const resumo = {};
                let totalGeral = 0;
                let quantidadeGeral = 0;

                linhas.forEach(linha => {
                    const produto = linha.children[3].textContent;
                    const valor = parseFloat(linha.children[8].textContent) || 0;

                    if (!resumo[produto]) {
                    resumo[produto] = { quantidade: 0, total: 0 };
                    }

                    resumo[produto].quantidade += 1;
                    resumo[produto].total += valor;

                    quantidadeGeral += 1;
                    totalGeral += valor;
                });

                const ordemProdutos = [
                    'Aluguel Pequeno',
                    'Aluguel Médio',
                    'Reposição',
                    'Funcionário',
                    'Da casa'
                    ];
                const tbodyResumo = document.querySelector('#tabelaResumo tbody');
                tbodyResumo.innerHTML = '';

                ordemProdutos.forEach(produto => {
                    const dados = resumo[produto];
                    if (dados) {
                        const { quantidade, total } = dados;

                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                        <td>${produto}</td>
                        <td>${quantidade}</td>
                        <td>R$ ${total.toFixed(2)}</td>
                        `;
                        tbodyResumo.appendChild(tr);
                    }
                    });

                // Adiciona linha de total geral
                const trTotal = document.createElement('tr');
                    trTotal.classList.add('table-secondary', 'fw-bold'); // fundo cinza + negrito

                    trTotal.innerHTML = `
                    <td>Total Geral</td>
                    <td>${quantidadeGeral}</td>
                    <td>R$ ${totalGeral.toFixed(2)}</td>
                    `;
                    tbodyResumo.appendChild(trTotal);
                }