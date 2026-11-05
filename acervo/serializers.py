from rest_framework import serializers
from .models import Livro


class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = [
            "id",
            "titulo",
            "autor",
            "ano",
            "tipo",
            "categoria",
            "disponivel",
            "cadastrado_em",
        ]
        read_only_fields = ["id", "cadastrado_em"]