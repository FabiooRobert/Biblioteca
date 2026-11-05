from django.urls import path
from .api_views import LivroDetail, LivroListCreate


urlpatterns = [
    path("livros/", LivroListCreate.as_view(), name="api-livros-lista"),
    path("livros/<int:pk>/", LivroDetail.as_view(), name="api-livros-detalhe"),
]