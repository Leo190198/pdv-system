# Sistema Web de PDV (Ponto de Venda)

Um sistema completo de Ponto de Venda (PDV) desenvolvido em Python com Flask, oferecendo funcionalidades para gerenciamento de vendas, controle de estoque e relatórios.

## Funcionalidades

- **Gestão de Produtos**
  - Cadastro, edição e exclusão de produtos
  - Controle de estoque com alertas para produtos com estoque baixo
  - Categorização de produtos

- **Processo de Venda**
  - Interface intuitiva para adicionar produtos à venda
  - Suporte a diferentes formas de pagamento (dinheiro, cartão, PIX)
  - Emissão de recibo
  - Atualização automática do estoque

- **Controle de Estoque**
  - Visualização do estoque atual
  - Histórico de movimentações
  - Alertas para produtos com estoque baixo

- **Relatórios**
  - Vendas por período
  - Produtos mais vendidos
  - Exportação em CSV

- **Autenticação e Segurança**
  - Sistema de login com níveis de acesso (administrador e vendedor)
  - Proteção de rotas sensíveis

## Tecnologias Utilizadas

- **Backend**: Python 3.8+ com Flask
- **ORM**: SQLAlchemy
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL ou MySQL (produção)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Autenticação**: Flask-Login

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/pdv-system.git
   cd pdv-system
   ```

2. Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   
   # No Windows
   venv\Scripts\activate
   
   # No Linux/Mac
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente (opcional):
   ```
   # No Windows
   set FLASK_APP=run.py
   set FLASK_ENV=development
   
   # No Linux/Mac
   export FLASK_APP=run.py
   export FLASK_ENV=development
   ```

5. Inicialize o banco de dados com dados de exemplo:
   ```
   python seed_db.py
   ```

6. Execute a aplicação:
   ```
   flask run
   ```
   ou
   ```
   python run.py
   ```

7. Acesse a aplicação no navegador:
   ```
   http://localhost:5000
   ```

## Credenciais Padrão

- **Administrador**:
  - Usuário: admin
  - Senha: admin123

- **Vendedor**:
  - Usuário: vendedor
  - Senha: vendedor123

## Estrutura do Projeto

```
pdv_system/
├── app/                    # Diretório principal da aplicação
│   ├── models/             # Modelos de dados
│   ├── routes/             # Rotas e controladores
│   ├── static/             # Arquivos estáticos (CSS, JS, imagens)
│   └── templates/          # Templates HTML
├── tests/                  # Testes unitários
├── config.py               # Configurações da aplicação
├── run.py                  # Script para executar a aplicação
├── seed_db.py              # Script para popular o banco de dados
└── requirements.txt        # Dependências do projeto
```

## Desenvolvimento

Para contribuir com o projeto:

1. Crie um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

## Contato

Para dúvidas ou sugestões, entre em contato através do email: seu-email@exemplo.com
