# Biblioteca / Acervo

Sistema de gerenciamento de acervo com cadastro de livros, autores, exemplares,
membros, empréstimos e reservas. O projeto permite criar bibliotecas separadas
por organização.

## Requisitos

- Python 3.10 ou superior
- pip

## Executar localmente

No Windows, abra o terminal na pasta do projeto e execute:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abra <http://127.0.0.1:8000/> e crie uma conta. Ao informar o nome da biblioteca,
a conta será administradora dessa organização. Para acessar o painel técnico do
Django, crie um superusuário com `python manage.py createsuperuser` e acesse
<http://127.0.0.1:8000/admin/>.

Por padrão, o projeto usa SQLite e cria o banco local `db.sqlite3` ao aplicar as
migrações. O banco, as senhas locais e o ambiente virtual não são enviados ao Git.

## Testes

```powershell
python manage.py test
```

## PostgreSQL (opcional)

Copie `.env.example` para `.env` e preencha as credenciais do PostgreSQL local.
Sem `DB_NAME` no `.env`, o projeto continua usando SQLite.
