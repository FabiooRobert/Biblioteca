# Biblioteca

Aplicação Django para catálogo de livros, com isolamento por organização e API REST.

## Configuração

1. Ative o ambiente virtual e instale as dependências com `pip install -r requirements.txt`.
2. Faça backup do banco antes de aplicar migrações em uma base com dados. No SQLite, copie `db.sqlite3`; no PostgreSQL, use `pg_dump`.
3. Execute `python manage.py migrate` e `python manage.py createsuperuser`.
4. No Admin, crie as organizações, os usuários e um Perfil para cada usuário, vinculando-o a uma organização.
5. Execute `python manage.py runserver` e entre em `/accounts/login/`.

Livros que já existiam recebem a organização `Organização padrão` pela migração. Depois, no Admin, associe essa organização ao perfil apropriado.

## API

A API autenticada usa sessão do Django. A interface navegável fica disponível em `/api/livros/`; o detalhe usa `/api/livros/<id>/`. O serializer lista os campos explicitamente e não aceita a organização enviada pelo cliente: ela é determinada pelo perfil autenticado.

## Roteiro de isolamento

Os testes automatizados cobrem estes cenários:

- Usuário A lista apenas os livros da organização A.
- Usuário A recebe 404 ao acessar um livro da organização B.
- Um livro criado nas páginas ou na API pertence à organização A, independentemente dos dados enviados.
- A API lista somente os registros da organização do usuário autenticado.
- A API retorna 404 para o ID de um livro da organização B e bloqueia acesso sem login.

Execute o roteiro com `python manage.py test`.

## Próximas etapas da P2

- Perfis com papéis e permissões distintas.
- Dashboard com métricas calculadas pelo ORM.
- Testes adicionais de segurança, revisão e implantação.