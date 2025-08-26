# Projeto de Gerenciamento de Pedidos

Este projeto é uma aplicação web para gerenciar pedidos, utilizando **Flask** no backend e **HTML/CSS/JavaScript** no frontend. O banco de dados utilizado é o **SQLite**.

## Estrutura do Projeto

### Backend
O backend foi desenvolvido com **Flask** e possui as seguintes funcionalidades:
- Listar produtos e roshs disponíveis.
- Criar, listar, atualizar e excluir pedidos.

### Frontend
O frontend utiliza **Bootstrap** para estilização e **JavaScript** para interações dinâmicas. Ele permite:
- Preencher formulários para criar pedidos.
- Visualizar pedidos enviados.
- Editar ou excluir pedidos existentes.

### Banco de Dados
O banco de dados **SQLite** contém três tabelas:
- `produto`: Armazena os produtos disponíveis.
- `rosh`: Armazena os tipos de rosh disponíveis.
- `pedido`: Armazena os pedidos realizados.

## Configuração do Ambiente

### 1. Criar e Ativar o Ambiente Virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar o Banco de Dados
Execute o script `DB` para criar e popular as tabelas no banco de dados SQLite:
```bash
python db_setup.py
```

### 4. Executar o Servidor
Inicie o servidor Flask:
```bash
python app.py
```

### 5. Acessar a Aplicação
Abra o navegador e acesse: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Estrutura de Arquivos
Ainda não sendo utilizado desta forma
```
VHGL/
├── app.py          # Código do backend
├── db_setup.py     # Script para configurar o banco de dados
├── templates/
│   └── index.html  # Página principal
├── static/
│   ├── css/        # Arquivos CSS
│   └── js/         # Arquivos JavaScript
└── pedidos_db.db   # Banco de dados SQLite
```

## Funcionalidades
- **Listar Produtos/Roshs**: Dropdowns dinâmicos carregados do banco de dados.
- **Criar Pedido**: Formulário para adicionar novos pedidos.
- **Editar Pedido**: Modal para atualizar informações de um pedido.
- **Excluir Pedido**: Botão para remover pedidos.

## Tecnologias Utilizadas
- **Backend**: Flask
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Banco de Dados**: SQLite

## Observações
Certifique-se de que o ambiente virtual está ativado antes de executar o projeto. Para dúvidas ou melhorias, contribua com o repositório.
