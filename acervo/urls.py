from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("login/", LoginView.as_view(template_name="acervo/login.html", redirect_authenticated_user=True), name="login"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", login_required(views.inicio), name="inicio"),
    path("livros/", login_required(views.lista_livros), name="lista_livros"),
    path("livros/novo/", login_required(views.novo_livro), name="novo_livro"),
    path("livros/<int:pk>/editar/", login_required(views.editar_livro), name="editar_livro"),
    path("livros/<int:pk>/excluir/", login_required(views.excluir_livro), name="excluir_livro"),
    path("autores/", login_required(views.lista_autores), name="lista_autores"),
    path("autores/novo/", login_required(views.novo_autor), name="novo_autor"),
    path("autores/<int:pk>/editar/", login_required(views.editar_autor), name="editar_autor"),
    path("autores/<int:pk>/excluir/", login_required(views.excluir_autor), name="excluir_autor"),
    path("exemplares/", login_required(views.lista_exemplares), name="lista_exemplares"),
    path("exemplares/novo/", login_required(views.novo_exemplar), name="novo_exemplar"),
    path("exemplares/<int:pk>/editar/", login_required(views.editar_exemplar), name="editar_exemplar"),
    path("exemplares/<int:pk>/excluir/", login_required(views.excluir_exemplar), name="excluir_exemplar"),
    path("membros/", login_required(views.lista_membros), name="lista_membros"),
    path("membros/novo/", login_required(views.novo_membro), name="novo_membro"),
    path("membros/<int:pk>/editar/", login_required(views.editar_membro), name="editar_membro"),
    path("membros/<int:pk>/excluir/", login_required(views.excluir_membro), name="excluir_membro"),
    path("emprestimos/", login_required(views.lista_emprestimos), name="lista_emprestimos"),
    path("emprestimos/novo/", login_required(views.novo_emprestimo), name="novo_emprestimo"),
    path("emprestimos/<int:pk>/editar/", login_required(views.editar_emprestimo), name="editar_emprestimo"),
    path("emprestimos/<int:pk>/excluir/", login_required(views.excluir_emprestimo), name="excluir_emprestimo"),
    path("reservas/", login_required(views.lista_reservas), name="lista_reservas"),
    path("reservas/novo/", login_required(views.nova_reserva), name="nova_reserva"),
    path("reservas/<int:pk>/editar/", login_required(views.editar_reserva), name="editar_reserva"),
    path("reservas/<int:pk>/excluir/", login_required(views.excluir_reserva), name="excluir_reserva"),
]
