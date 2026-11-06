from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva
from .permissions import AdministradorPodeEscrever, TemPerfil
from .serializers import (
    AutorSerializer,
    EmprestimoSerializer,
    ExemplarSerializer,
    LivroSerializer,
    MembroSerializer,
    ReservaSerializer,
)


class OrganizacaoListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, TemPerfil, AdministradorPodeEscrever]
    model = None

    def get_queryset(self):
        return self.model.objects.filter(
            organizacao=self.request.user.perfil.organizacao
        )

    def perform_create(self, serializer):
        serializer.save(organizacao=self.request.user.perfil.organizacao)


class OrganizacaoDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, TemPerfil, AdministradorPodeEscrever]
    model = None

    def get_queryset(self):
        return self.model.objects.filter(
            organizacao=self.request.user.perfil.organizacao
        )


class AutorListCreate(OrganizacaoListCreate):
    model = Autor
    serializer_class = AutorSerializer


class AutorDetail(OrganizacaoDetail):
    model = Autor
    serializer_class = AutorSerializer


class LivroListCreate(OrganizacaoListCreate):
    model = Livro
    serializer_class = LivroSerializer


class LivroDetail(OrganizacaoDetail):
    model = Livro
    serializer_class = LivroSerializer


class ExemplarListCreate(OrganizacaoListCreate):
    model = Exemplar
    serializer_class = ExemplarSerializer


class ExemplarDetail(OrganizacaoDetail):
    model = Exemplar
    serializer_class = ExemplarSerializer


class MembroListCreate(OrganizacaoListCreate):
    model = Membro
    serializer_class = MembroSerializer


class MembroDetail(OrganizacaoDetail):
    model = Membro
    serializer_class = MembroSerializer


class EmprestimoListCreate(OrganizacaoListCreate):
    model = Emprestimo
    serializer_class = EmprestimoSerializer


class EmprestimoDetail(OrganizacaoDetail):
    model = Emprestimo
    serializer_class = EmprestimoSerializer


class ReservaListCreate(OrganizacaoListCreate):
    model = Reserva
    serializer_class = ReservaSerializer


class ReservaDetail(OrganizacaoDetail):
    model = Reserva
    serializer_class = ReservaSerializer
