# Biblioteca

Aplicação Django para catálogo de livros, com isolamento por organização e API REST.

## Configuração

1. Ative o ambiente virtual e instale as dependências com `pip install -r requirements.txt`.
2. Faça backup do banco antes de aplicar migrações em uma base com dados. No SQLite, copie `db.sqlite3`; no PostgreSQL, use `pg_dump`.
3. Execute `python manage.py migrate` e `python manage.py createsuperuser`.
4. No Admin, crie as organizações, os usuários e um Perfil para cada usuário, vinculando-o a uma organização e definindo o papel.
5. Execute `python manage.py runserver` e entre em `/accounts/login/`.

Livros que já existiam recebem a organização `Organização padrão` pela migração. A migração seguinte preserva o texto do autor e o transforma em um registro de autor associado à mesma organização. Depois, no Admin, associe a organização apropriada ao perfil dos usuários.
Perfis existentes recebem o papel `Operador`; promova pelo Admin quem deve administrar o acervo. Livros antigos recebem como data de cadastro o momento da migração, pois a data original não existia.

## API

A API autenticada usa sessão do Django. A interface navegável do DRF fica disponível nos seguintes recursos:

| Recurso | Lista/criação | Detalhe/edição/exclusão |
|---|---|---|
| Autores | `/api/autores/` | `/api/autores/<id>/` |
| Livros | `/api/livros/` | `/api/livros/<id>/` |
| Exemplares | `/api/exemplares/` | `/api/exemplares/<id>/` |
| Membros | `/api/membros/` | `/api/membros/<id>/` |
| Empréstimos | `/api/emprestimos/` | `/api/emprestimos/<id>/` |
| Reservas | `/api/reservas/` | `/api/reservas/<id>/` |

Cada serializer declara os campos explicitamente e não aceita a organização enviada pelo cliente: ela sempre vem do perfil autenticado. IDs de relacionamentos (por exemplo, autor do livro, livro do exemplar ou membro do empréstimo) são aceitos somente quando pertencem à mesma organização. Operadores podem consultar; somente administradores podem criar, editar ou excluir.

Empréstimos retornam os campos calculados `dias_atraso` e `multa`; reservas retornam `posicao_fila`. ISBN, código do exemplar, CPF e e-mail do membro têm unicidade por organização, permitindo que organizações diferentes usem os mesmos valores.

## Papéis e dashboard

O papel `Administrador` pode consultar e alterar livros da própria organização. O papel `Operador` pode consultar, mas recebe 403 ao tentar alterar dados. Ambos acessam `/dashboard/`, que resume livros disponíveis e indisponíveis, distribuições por tipo/categoria e autores com mais livros. O filtro aceita 30, 90, 365 dias ou todo o período.

## Roteiro de isolamento

Os testes automatizados cobrem estes cenários:

- Usuário A lista apenas os livros da organização A.
- Usuário A recebe 404 ao acessar um livro da organização B.
- Um livro criado nas páginas ou na API pertence à organização A, independentemente dos dados enviados.
- A API lista somente os registros da organização do usuário autenticado e retorna 404 para IDs de outra organização.
- A API rejeita relacionamentos com objetos de outras organizações e bloqueia acesso sem login.
- Operadores consultam, mas não gravam; administradores têm acesso ao CRUD dos seis recursos.
- O dashboard agrega somente a organização do usuário e respeita o período selecionado.

Execute o roteiro com `python manage.py test`.

## Escopo da P2

O domínio da biblioteca inclui autores, livros, exemplares, membros, empréstimos e reservas. O backlog de acompanhamento está nas [issues da P2](https://github.com/FabiooRobert/Biblioteca/issues).