from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("livros/", views.lista_livros, name="lista"),
    path("livros/novo/", views.novo_livro, name="novo"),
    path("livros/<int:pk>/editar/", views.editar_livro, name="editar"),
    path("livros/<int:pk>/excluir/", views.excluir_livro, name="excluir"),
]
