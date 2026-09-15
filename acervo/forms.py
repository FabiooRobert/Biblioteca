from django import forms

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva


class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ["nome", "sobrenome"]


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ["titulo", "autor", "ano", "isbn"]


class ExemplarForm(forms.ModelForm):
    class Meta:
        model = Exemplar
        fields = ["livro", "codigo", "status"]


class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = ["nome", "sobrenome", "cpf", "email", "ativo"]


class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = [
            "exemplar",
            "membro",
            "data_emprestimo",
            "data_devolucao_prevista",
            "data_devolucao_real",
            "status",
        ]
        widgets = {
            "data_emprestimo": forms.DateInput(attrs={"type": "date"}),
            "data_devolucao_prevista": forms.DateInput(attrs={"type": "date"}),
            "data_devolucao_real": forms.DateInput(attrs={"type": "date"}),
        }


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["livro", "membro", "data_reserva", "status"]
        widgets = {
            "data_reserva": forms.DateInput(attrs={"type": "date"}),
        }
