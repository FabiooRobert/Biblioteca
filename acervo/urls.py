from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("livros/", views.lista_livros, name="lista_livros"),
    path("livros/novo/", views.novo_livro, name="novo_livro"),
    path("livros/<int:pk>/editar/", views.editar_livro, name="editar_livro"),
    path("livros/<int:pk>/excluir/", views.excluir_livro, name="excluir_livro"),
    path("autores/", views.lista_autores, name="lista_autores"),
    path("autores/novo/", views.novo_autor, name="novo_autor"),
    path("autores/<int:pk>/editar/", views.editar_autor, name="editar_autor"),
    path("autores/<int:pk>/excluir/", views.excluir_autor, name="excluir_autor"),
    path("exemplares/", views.lista_exemplares, name="lista_exemplares"),
    path("exemplares/novo/", views.novo_exemplar, name="novo_exemplar"),
    path("exemplares/<int:pk>/editar/", views.editar_exemplar, name="editar_exemplar"),
    path("exemplares/<int:pk>/excluir/", views.excluir_exemplar, name="excluir_exemplar"),
    path("membros/", views.lista_membros, name="lista_membros"),
    path("membros/novo/", views.novo_membro, name="novo_membro"),
    path("membros/<int:pk>/editar/", views.editar_membro, name="editar_membro"),
    path("membros/<int:pk>/excluir/", views.excluir_membro, name="excluir_membro"),
    path("emprestimos/", views.lista_emprestimos, name="lista_emprestimos"),
    path("emprestimos/novo/", views.novo_emprestimo, name="novo_emprestimo"),
    path("emprestimos/<int:pk>/editar/", views.editar_emprestimo, name="editar_emprestimo"),
    path("emprestimos/<int:pk>/excluir/", views.excluir_emprestimo, name="excluir_emprestimo"),
    path("reservas/", views.lista_reservas, name="lista_reservas"),
    path("reservas/novo/", views.nova_reserva, name="nova_reserva"),
    path("reservas/<int:pk>/editar/", views.editar_reserva, name="editar_reserva"),
    path("reservas/<int:pk>/excluir/", views.excluir_reserva, name="excluir_reserva"),
]
