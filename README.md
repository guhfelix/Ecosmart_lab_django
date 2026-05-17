# EcoSmart Lab - Django

EcoSmart Lab é uma aplicação web em Django para incentivar o descarte correto de resíduos. O sistema permite que cidadãos registrem descartes em pontos de coleta, acumulem pontos e resgatem benefícios. Gestores e administradores conseguem acompanhar relatórios, gerenciar usuários e consultar auditoria.

Este projeto está em formato de MVP funcional, usando SQLite para desenvolvimento local.

## Sumário

- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Regras de negocio](#regras-de-negocio)
- [Instalacao](#instalacao)
- [Configuracao do ambiente](#configuracao-do-ambiente)
- [Banco de dados](#banco-de-dados)
- [Como executar](#como-executar)
- [Rotas principais](#rotas-principais)
- [Papeis de usuario](#papeis-de-usuario)
- [Dados iniciais](#dados-iniciais)
- [Testes e validacao](#testes-e-validacao)
- [Checklist de MVP](#checklist-de-mvp)
- [Observacoes para producao](#observacoes-para-producao)

## Funcionalidades

### Cidadão

- Cadastro e login por e-mail.
- Edição de perfil.
- Visualização de pontos de coleta ativos.
- Registro de descarte com tipo de resíduo, peso e ponto de coleta.
- Geração automática de pontos.
- Dashboard com resumo pessoal.
- Relatório pessoal de descartes.
- Exportação de relatório pessoal em CSV.
- Catálogo de benefícios ativos.
- Resgate de benefícios com desconto automático de pontos.
- Histórico de resgates.

### Gestor

- Acesso a relatórios globais de descarte.
- Filtros por ponto de coleta, tipo de resíduo e período.
- Exportação de relatórios em CSV.
- Ranking/resumo por ponto de coleta.

### Administrador

- Gestão de usuários.
- Alteração de papel e status dos usuários.
- Consulta de auditoria.
- Gestão de pontos de coleta, descartes, benefícios e resgates via Django Admin.

## Tecnologias

- Python 3.11+
- Django 5.2
- SQLite para desenvolvimento/MVP local
- Bootstrap 5
- Bootstrap Icons
- Chart.js
- django-crispy-forms
- crispy-bootstrap5
- python-dotenv

## Estrutura do projeto

```text
Ecosmart_lab_django-main/
├── accounts/             # Usuários, autenticação, perfil e papéis
├── coleta/               # Pontos de coleta, descartes e relatórios
├── core/                 # Página inicial, dashboard e APIs públicas
├── recompensas/          # Benefícios, resgates e auditoria
├── ecosmart_django/      # Configurações principais do Django
├── templates/            # Templates HTML globais
├── static/               # CSS e arquivos estáticos
├── db.sqlite3            # Banco local SQLite
├── manage.py
├── requirements.txt
└── README.md
```

## Regras de negocio

- Apenas usuários autenticados podem acessar dashboard, pontos de coleta, descarte, relatórios, benefícios e resgates.
- Apenas pontos de coleta ativos aparecem para o usuário registrar descarte.
- A pontuação é calculada automaticamente:

```text
1 kg de resíduo = 10 pontos
```

- Exemplo: um descarte de `2.5 kg` gera `25 pontos`.
- O saldo do usuário é atualizado quando um descarte é criado.
- A edição posterior de um descarte não adiciona pontos novamente.
- Benefícios só podem ser resgatados se estiverem ativos.
- O resgate desconta os pontos do saldo do usuário.
- Cada resgate gera um código de voucher.
- A operação de resgate usa transação para evitar inconsistências no saldo.
- Usuários com papel `GESTOR` ou `ADMIN` acessam relatórios globais.
- Apenas usuários `ADMIN` acessam gestão de usuários e auditoria.

## Instalacao

Clone o repositório:

```bash
git clone https://github.com/guhfelix/Ecosmart_lab_django.git
cd Ecosmart_lab_django
```

Crie e ative um ambiente virtual.

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuracao do ambiente

Copie o arquivo de exemplo:

```bash
copy .env.example .env
```

No Linux/macOS:

```bash
cp .env.example .env
```

Configuração recomendada para desenvolvimento local:

```env
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
DEBUG=True

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
```

## Banco de dados

O MVP usa SQLite por padrão:

```env
DATABASE_URL=sqlite:///db.sqlite3
```

Execute as migrations:

```bash
python manage.py migrate
```

O arquivo local do banco é:

```text
db.sqlite3
```

Para este MVP, continuar com SQLite é suficiente. Para produção com muitos usuários, o projeto já aceita configuração via `DATABASE_URL`, mas seria necessário instalar um driver PostgreSQL e ajustar o ambiente.

Exemplo de URL para PostgreSQL:

```env
DATABASE_URL=postgresql://usuario:senha@host:5432/nome_db
```

## Como executar

Inicie o servidor:

```bash
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

Se a porta `8000` estiver ocupada, use outra porta:

```bash
python manage.py runserver 127.0.0.1:8001
```

## Rotas principais

### Páginas públicas

| Rota | Descrição |
|------|-----------|
| `/` | Página inicial |
| `/login/` | Login |
| `/register/` | Cadastro |

### Área autenticada

| Rota | Descrição |
|------|-----------|
| `/dashboard/` | Dashboard do cidadão |
| `/perfil/` | Perfil do usuário |
| `/pontos/` | Pontos de coleta disponíveis |
| `/descarte/` | Registro de descarte |
| `/relatorio/` | Relatório pessoal |
| `/relatorio/exportar/` | Exportação CSV do relatório pessoal |
| `/beneficios/` | Lista e resgate de benefícios |
| `/meus-resgates/` | Histórico de resgates |

### Gestor

| Rota | Descrição |
|------|-----------|
| `/admin/relatorios/` | Relatórios globais |
| `/admin/relatorios/exportar/` | Exportação CSV detalhada |
| `/admin/relatorios/resumo/` | Exportação CSV por ponto de coleta |

### Administrador EcoSmart

| Rota | Descrição |
|------|-----------|
| `/admin/usuarios/` | Gestão de usuários |
| `/admin/usuarios/<id>/papel/` | Alteração de papel |
| `/admin/usuarios/<id>/status/` | Ativação/desativação de usuário |
| `/admin/auditoria/` | Auditoria |
| `/django-admin/` | Django Admin |

### API v1

| Rota | Descrição |
|------|-----------|
| `/api/v1/pontos/` | Lista pontos de coleta ativos |
| `/api/v1/beneficios/` | Lista benefícios ativos |
| `/api/v1/estatisticas/` | Estatísticas globais |

## Papeis de usuario

| Papel | Permissões |
|-------|------------|
| `CIDADAO` | Registra descartes, consulta relatórios pessoais e resgata benefícios |
| `GESTOR` | Permissões de cidadão + relatórios globais |
| `ADMIN` | Permissões de gestor + gestão de usuários e auditoria |
| `PARCEIRO` | Papel disponível no modelo para evolução futura |

## Dados iniciais

O projeto possui um comando para popular dados básicos:

```bash
python manage.py seed
```

Esse comando cria, quando ainda não existem registros:

- 3 pontos de coleta.
- 3 benefícios.

Para criar um administrador do Django:

```bash
python manage.py createsuperuser
```

Depois, acesse:

```text
http://127.0.0.1:8000/django-admin/
```

## Testes e validacao

Rodar checagem geral do Django:

```bash
python manage.py check
```

Verificar se existem migrations pendentes:

```bash
python manage.py makemigrations --check --dry-run
```

Rodar todos os testes:

```bash
python manage.py test
```

Rodar checagem de produção simulada:

```bash
python manage.py check --deploy
```

Observação: para `check --deploy` sem avisos, use variáveis de ambiente de produção, como `DEBUG=False`, `SECRET_KEY` forte, `ALLOWED_HOSTS` definido e flags de HTTPS habilitadas.

## Checklist de MVP

Fluxo recomendado para validar a aplicação manualmente:

1. Criar um usuário em `/register/`.
2. Fazer login em `/login/`.
3. Acessar `/pontos/` e conferir os pontos de coleta.
4. Registrar um descarte em `/descarte/`.
5. Conferir o saldo no `/dashboard/`.
6. Acessar `/relatorio/` e validar o descarte registrado.
7. Acessar `/beneficios/`.
8. Resgatar um benefício com saldo suficiente.
9. Conferir o resgate em `/meus-resgates/`.
10. Acessar `/django-admin/` com superusuário e conferir os dados.

## Observacoes para producao

Antes de publicar o projeto em produção:

- Definir `DEBUG=False`.
- Usar `SECRET_KEY` forte e secreta.
- Configurar `ALLOWED_HOSTS` com o domínio real.
- Habilitar HTTPS.
- Avaliar troca de SQLite para PostgreSQL.
- Configurar arquivos estáticos com `collectstatic`.
- Criar política de backup do banco.
- Revisar permissões de usuários e acessos administrativos.
- Revisar LGPD/privacidade de dados pessoais.

## Status do projeto

O projeto está pronto para apresentação como MVP local. Ele cobre o fluxo principal de descarte, pontuação e resgate, com separação por apps, validações de formulário, testes automatizados e dados iniciais via seed.
