from django import forms
from .models import Livro


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ["titulo", "autor", "ano", "tipo", "categoria", "disponivel"]
        labels = {
            "titulo": "Título / Nome",
            "autor": "Autor",
            "ano": "Ano",
            "tipo": "Tipo do acervo",
            "categoria": "Categoria",
            "disponivel": "Disponível",
        }
        widgets = {
            "titulo": forms.TextInput(
                attrs={"class": "campo", "placeholder": "Digite o título ou nome"}
            ),
            "autor": forms.TextInput(
                attrs={"class": "campo", "placeholder": "Digite o autor"}
            ),
            "ano": forms.NumberInput(attrs={"class": "campo"}),
            "tipo": forms.Select(attrs={"class": "campo"}),
            "categoria": forms.Select(attrs={"class": "campo"}),
            "disponivel": forms.CheckboxInput(attrs={"class": "campo-check"}),
        }
