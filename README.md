# Biblioteca

Aplicação Django para catálogo de livros, com isolamento por organização e API REST.

## Configuração

1. Ative o ambiente virtual e instale as dependências com `pip install -r requirements.txt`.
2. Faça backup do banco antes de aplicar migrações em uma base com dados. No SQLite, copie `db.sqlite3`; no PostgreSQL, use `pg_dump`.
3. Execute `python manage.py migrate` e `python manage.py createsuperuser`.
4. No Admin, crie as organizações, os usuários e um Perfil para cada usuário, vinculando-o a uma organização e definindo o papel.
5. Execute `python manage.py runserver` e entre em `/accounts/login/`.

Livros que já existiam recebem a organização `Organização padrão` pela migração. Depois, no Admin, associe essa organização ao perfil apropriado.
Perfis existentes recebem o papel `Operador`; promova pelo Admin quem deve administrar o acervo. Livros antigos recebem como data de cadastro o momento da migração, pois a data original não existia.

## API

A API autenticada usa sessão do Django. A interface navegável fica disponível em `/api/livros/`; o detalhe usa `/api/livros/<id>/`. O serializer lista os campos explicitamente e não aceita a organização enviada pelo cliente: ela é determinada pelo perfil autenticado. Operadores podem consultar; somente administradores podem criar, editar ou excluir. Como `Livro` é o único model de negócio existente, este é o recurso disponível na API.

## Papéis e dashboard

O papel `Administrador` pode consultar e alterar livros da própria organização. O papel `Operador` pode consultar, mas recebe 403 ao tentar alterar dados. Ambos acessam `/dashboard/`, que resume livros disponíveis e indisponíveis, distribuições por tipo/categoria e autores com mais livros. O filtro aceita 30, 90, 365 dias ou todo o período.

## Roteiro de isolamento

Os testes automatizados cobrem estes cenários:

- Usuário A lista apenas os livros da organização A.
- Usuário A recebe 404 ao acessar um livro da organização B.
- Um livro criado nas páginas ou na API pertence à organização A, independentemente dos dados enviados.
- A API lista somente os registros da organização do usuário autenticado.
- A API retorna 404 para o ID de um livro da organização B e bloqueia acesso sem login.
- Operadores consultam, mas não gravam; administradores têm acesso ao CRUD.
- O dashboard agrega somente a organização do usuário e respeita o período selecionado.

Execute o roteiro com `python manage.py test`.

## Próximos passos

- Criar endpoints e métricas para novos models de negócio, quando forem adicionados ao projeto.
- Revisar configurações de produção e implantar a aplicação.