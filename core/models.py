from django.conf import settings
from django.db import models


class Organizacao(models.Model):
    nome = models.CharField(max_length=120)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class DaOrganizacao(models.Model):
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_set",
    )

    class Meta:
        abstract = True


class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    organizacao = models.ForeignKey(Organizacao, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.usuario} - {self.organizacao}"