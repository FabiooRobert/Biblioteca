from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Livro
from .permissions import AdministradorPodeEscrever, TemPerfil
from .serializers import LivroSerializer


class LivroListCreate(generics.ListCreateAPIView):
    serializer_class = LivroSerializer
    permission_classes = [IsAuthenticated, TemPerfil, AdministradorPodeEscrever]

    def get_queryset(self):
        return Livro.objects.filter(organizacao=self.request.user.perfil.organizacao)

    def perform_create(self, serializer):
        serializer.save(organizacao=self.request.user.perfil.organizacao)


class LivroDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LivroSerializer
    permission_classes = [IsAuthenticated, TemPerfil, AdministradorPodeEscrever]

    def get_queryset(self):
        return Livro.objects.filter(organizacao=self.request.user.perfil.organizacao)