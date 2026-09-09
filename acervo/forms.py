from django import forms
from .models import Livro


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ["titulo", "autor", "ano", "disponivel"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "campo"}),
            "autor": forms.TextInput(attrs={"class": "campo"}),
            "ano": forms.NumberInput(attrs={"class": "campo"}),
            "disponivel": forms.CheckboxInput(attrs={"class": "campo-check"}),
        }
