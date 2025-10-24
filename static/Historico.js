          function renderEmptyTableMessage(tbody, message) {

                const colunas = document.querySelectorAll('#tabelaPedidos thead th').length;
                
                if (colunas === 0) return; 

                const tr = document.createElement('tr');
                const td = document.createElement('td');
                

                td.setAttribute('colspan', colunas);
                td.classList.add('text-center', 'py-4', 'text-muted', 'lead', 'font-italic', 'msg-vazio'); // Adiciona classe 'msg-vazio'
                td.innerHTML = `<i class="fas fa-info-circle mr-2"></i> ${message}`;

                tr.appendChild(td);
                tbody.appendChild(tr);
            }

            const valorPorProduto = {
                'Aluguel Médio': 50,
                'Aluguel Pequeno': 40,
                'Reposição': 25,
                'Funcionário': 20,
                'Da casa':0
            };
            
            let pedidosArmazenados = []; 

            async function carregarPedidos(){
                const res = await fetch('/api/pedidos/todos');
                const pedidos = await res.json();
                const tbody = document.querySelector('#tabelaPedidos tbody');
                tbody.innerHTML = '';
                
                pedidosArmazenados = pedidos;


                if (pedidos.length === 0) {
                    renderEmptyTableMessage(tbody, 'Não há histórico de pedidos registrado.');
                    Resumo(); 
                    return; 
                }

                pedidos.forEach(pedido => {
                    adicionarLinhaTabela(pedido);
                });
                
                Resumo(); 
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
                // Insere no final (Append) ou no início (Prepend). Mantendo o Prepend original, mas geralmente histórico é por ordem de data.
                tbody.prepend(tr); 
            }

            function Resumo() {
                const linhas = Array.from(document.querySelectorAll('#tabelaPedidos tbody tr'));
                
                const resumo = {};
                let totalGeral = 0;
                let quantidadeGeral = 0;

                linhas.forEach(linha => {

                    if (linha.style.display === 'none' || linha.classList.contains('msg-vazio')) {
                        return;
                    }
                    
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

                if (quantidadeGeral === 0) {
                     const trVazio = document.createElement('tr');
                     trVazio.innerHTML = `<td colspan="3" class="text-center text-muted">Resumo indisponível ou filtro ativo.</td>`;
                     tbodyResumo.appendChild(trVazio);
                     return;
                }

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
                trTotal.classList.add('table-total'); 

                trTotal.innerHTML = `
                <td>Total Geral</td>
                <td>${quantidadeGeral}</td>
                <td>R$ ${totalGeral.toFixed(2)}</td>
                `;
                tbodyResumo.appendChild(trTotal);
            }

            document.getElementById('filtroPedidos').addEventListener('input', function () {
                const filtro = this.value.toLowerCase();
                const tbody = document.querySelector('#tabelaPedidos tbody');
                const linhas = document.querySelectorAll('#tabelaPedidos tbody tr');
                let linhasVisiveis = 0;

                // Remove a mensagem de "vazio" anterior se houver
                document.querySelectorAll('#tabelaPedidos tbody .msg-vazio').forEach(el => el.remove()); 

                linhas.forEach(linha => {
                    // Ignora a linha da mensagem vazia se ela existir (previne erros)
                    if (linha.classList.contains('msg-vazio')) return; 

                    const textoLinha = linha.textContent.toLowerCase();
                    const corresponde = textoLinha.includes(filtro);
                    linha.style.display = corresponde ? '' : 'none';
                    if (corresponde) {
                        linhasVisiveis++;
                    }
                });

                if (linhasVisiveis === 0) {
                    renderEmptyTableMessage(tbody, 'Nenhum registro de pedido encontrado com base neste filtro.');
                }
                
                Resumo();
            });

            document.querySelectorAll('#tabelaPedidos th').forEach((th, index) => {
                th.style.cursor = 'pointer';
                let ascendente = true;

                th.addEventListener('click', () => {
                    const tbody = document.querySelector('#tabelaPedidos tbody');
                    const linhas = Array.from(tbody.querySelectorAll('tr')).filter(tr => !tr.classList.contains('msg-vazio')); 

                    document.querySelectorAll('#tabelaPedidos th').forEach(th => {
                        th.textContent = th.textContent.replace(/[\u2191\u2193]/g, '').trim();
                    });

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

                    const mensagemVazia = tbody.querySelector('.msg-vazio');
                    tbody.innerHTML = '';
                    linhas.forEach(tr => tbody.appendChild(tr));
                    if (mensagemVazia) {
                        tbody.appendChild(mensagemVazia);
                    }

                    const seta = ascendente ? ' \u2191' : ' \u2193'; // ↑ ou ↓
                    th.textContent = nomeColuna + seta;

                    ascendente = !ascendente;
                });
            });