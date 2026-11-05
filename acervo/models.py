from django.db import models
from core.models import DaOrganizacao


class Livro(DaOrganizacao):
    TIPOS_ACERVO = [
        ("REVISTA", "Revista"),
        ("JORNAL", "Jornal"),
        ("TCC", "TCC / Trabalho Acadêmico"),
        ("OUTRO", "Outro"),
    ]

    CATEGORIAS_ACERVO = [
        ("000", "Generalidades e Informação"),
        ("100", "Filosofia e Psicologia"),
        ("200", "Religião e Teologia"),
        ("300", "Ciências Sociais e Direito"),
        ("400", "Linguística e Idiomas"),
        ("500", "Ciências Puras"),
        ("600", "Ciências Aplicadas"),
        ("700", "Artes e Recreação"),
        ("800", "Literatura"),
        ("900", "História e Geografia"),
    ]

    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    ano = models.IntegerField()
    tipo = models.CharField(max_length=20, choices=TIPOS_ACERVO, default="OUTRO")
    categoria = models.CharField(
        max_length=3,
        choices=CATEGORIAS_ACERVO,
        default="000",
    )
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo
