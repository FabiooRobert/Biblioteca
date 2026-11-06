from rest_framework import serializers

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva


class OrganizacaoRelatedFieldsMixin:
    organizacao_related_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        perfil = getattr(getattr(request, "user", None), "perfil", None)
        organizacao = getattr(perfil, "organizacao", None)

        for field_name in self.organizacao_related_fields:
            queryset = self.fields[field_name].queryset
            self.fields[field_name].queryset = (
                queryset.filter(organizacao=organizacao)
                if organizacao is not None
                else queryset.none()
            )


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ["id", "nome", "sobrenome"]
        read_only_fields = ["id"]


class LivroSerializer(OrganizacaoRelatedFieldsMixin, serializers.ModelSerializer):
    organizacao_related_fields = ("autor",)

    class Meta:
        model = Livro
        fields = [
            "id",
            "titulo",
            "autor",
            "ano",
            "isbn",
            "tipo",
            "categoria",
            "disponivel",
            "cadastrado_em",
        ]
        read_only_fields = ["id", "cadastrado_em"]


class ExemplarSerializer(OrganizacaoRelatedFieldsMixin, serializers.ModelSerializer):
    organizacao_related_fields = ("livro",)

    class Meta:
        model = Exemplar
        fields = ["id", "livro", "codigo", "status"]
        read_only_fields = ["id"]


class MembroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membro
        fields = ["id", "nome", "sobrenome", "cpf", "email", "ativo"]
        read_only_fields = ["id"]


class EmprestimoSerializer(
    OrganizacaoRelatedFieldsMixin,
    serializers.ModelSerializer,
):
    organizacao_related_fields = ("exemplar", "membro")
    dias_atraso = serializers.SerializerMethodField()
    multa = serializers.SerializerMethodField()

    class Meta:
        model = Emprestimo
        fields = [
            "id",
            "exemplar",
            "membro",
            "data_emprestimo",
            "data_devolucao_prevista",
            "data_devolucao_real",
            "status",
            "dias_atraso",
            "multa",
        ]
        read_only_fields = ["id", "dias_atraso", "multa"]

    def get_multa(self, obj):
        return obj.calcular_multa()

    def get_dias_atraso(self, obj):
        return obj.dias_atraso()


class ReservaSerializer(OrganizacaoRelatedFieldsMixin, serializers.ModelSerializer):
    organizacao_related_fields = ("livro", "membro")
    posicao_fila = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reserva
        fields = ["id", "livro", "membro", "data_reserva", "status", "posicao_fila"]
        read_only_fields = ["id", "posicao_fila"]
