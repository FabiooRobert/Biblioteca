from rest_framework import generics
from .models import Livro
from .serializers import LivroSerializer


class LivroListCreate(generics.ListCreateAPIView):
    serializer_class = LivroSerializer

    def get_queryset(self):
        return Livro.objects.filter(organizacao=self.request.user.perfil.organizacao)

    def perform_create(self, serializer):
        serializer.save(organizacao=self.request.user.perfil.organizacao)


class LivroDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LivroSerializer

    def get_queryset(self):
        return Livro.objects.filter(organizacao=self.request.user.perfil.organizacao)