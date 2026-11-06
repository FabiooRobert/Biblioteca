from django.urls import path

from .api_views import (
    AutorDetail,
    AutorListCreate,
    EmprestimoDetail,
    EmprestimoListCreate,
    ExemplarDetail,
    ExemplarListCreate,
    LivroDetail,
    LivroListCreate,
    MembroDetail,
    MembroListCreate,
    ReservaDetail,
    ReservaListCreate,
)


urlpatterns = [
    path("autores/", AutorListCreate.as_view(), name="api-autores-lista"),
    path("autores/<int:pk>/", AutorDetail.as_view(), name="api-autores-detalhe"),
    path("livros/", LivroListCreate.as_view(), name="api-livros-lista"),
    path("livros/<int:pk>/", LivroDetail.as_view(), name="api-livros-detalhe"),
    path("exemplares/", ExemplarListCreate.as_view(), name="api-exemplares-lista"),
    path(
        "exemplares/<int:pk>/",
        ExemplarDetail.as_view(),
        name="api-exemplares-detalhe",
    ),
    path("membros/", MembroListCreate.as_view(), name="api-membros-lista"),
    path("membros/<int:pk>/", MembroDetail.as_view(), name="api-membros-detalhe"),
    path(
        "emprestimos/",
        EmprestimoListCreate.as_view(),
        name="api-emprestimos-lista",
    ),
    path(
        "emprestimos/<int:pk>/",
        EmprestimoDetail.as_view(),
        name="api-emprestimos-detalhe",
    ),
    path("reservas/", ReservaListCreate.as_view(), name="api-reservas-lista"),
    path(
        "reservas/<int:pk>/",
        ReservaDetail.as_view(),
        name="api-reservas-detalhe",
    ),
]