# EcoSmart Lab — Django

Versao Django do projeto EcoSmart Solutions, migrado a partir do Flask seguindo o cronograma incremental de desenvolvimento.

## Tecnologias

- Python 3.11+
- Django 5.2
- SQLite (desenvolvimento) / PostgreSQL (producao)
- Bootstrap 5
- Chart.js

## Estrutura do Projeto

```
ecosmart_django/
├── accounts/        # Fase 1 — Autenticacao e perfis de usuarios
├── coleta/          # Fases 2 e 3 — Pontos de coleta e registro de descarte
├── recompensas/     # Fase 4 — Sistema de recompensas, beneficios e auditoria
├── core/            # Dashboard, pagina inicial e API REST v1
├── templates/       # Templates HTML (Jinja2 adaptado para Django)
├── static/          # CSS e assets estaticos
└── manage.py
```

## Instalacao

```bash
# 1. Clone o repositorio
git clone https://github.com/guhfelix/Ecosmart_lab_django.git
cd ecosmart_django

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instale as dependencias
pip install -r requirements.txt

# 4. Configure as variaveis de ambiente
cp .env.example .env
# Edite o .env com suas configuracoes

# 5. Execute as migracoes
python manage.py migrate

# 6. Popule os dados iniciais
python manage.py seed

# 7. Crie um superusuario (admin)
python manage.py createsuperuser

# 8. Inicie o servidor
python manage.py runserver
```

## Acesso

| URL | Descricao |
|-----|-----------|
| `http://localhost:8000/` | Pagina inicial |
| `http://localhost:8000/login/` | Login |
| `http://localhost:8000/register/` | Cadastro |
| `http://localhost:8000/dashboard/` | Dashboard do cidadao |
| `http://localhost:8000/django-admin/` | Painel Django Admin |
| `http://localhost:8000/api/v1/pontos/` | API — Pontos de Coleta |
| `http://localhost:8000/api/v1/beneficios/` | API — Beneficios |
| `http://localhost:8000/api/v1/estatisticas/` | API — Estatisticas |

## Papeis de Usuario

| Papel | Permissoes |
|-------|-----------|
| CIDADAO | Registrar descartes, ver relatorios pessoais, resgatar beneficios |
| GESTOR | Tudo do cidadao + gerir pontos de coleta, beneficios e relatorios globais |
| ADMIN | Tudo do gestor + gerir usuarios e ver auditoria |

## Cronograma de Migracao

| Fase | Semana | Status |
|------|--------|--------|
| Autenticacao | 1 | Concluido |
| Pontos de Coleta | 3 | Concluido |
| Registro de Descarte | 6 | Concluido |
| Sistema de Recompensas | 9 | Concluido |
| Funcionalidades Extras | 9+ | Concluido |
