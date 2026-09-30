from django import forms
from django.db import transaction

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva


class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ["nome", "sobrenome"]


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ["titulo", "tipo", "autor", "ano", "isbn", "categoria"]


class ExemplarForm(forms.ModelForm):
    class Meta:
        model = Exemplar
        fields = ["livro", "codigo", "status"]


class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = ["nome", "sobrenome", "cpf", "email", "ativo"]


class EmprestimoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_exemplar_id = self.instance.exemplar_id
        exemplares_disponiveis = Exemplar.objects.filter(status="disponivel")
        membros_ativos = Membro.objects.filter(ativo=True)

        if self.instance.pk:
            exemplares_disponiveis = exemplares_disponiveis | Exemplar.objects.filter(
                pk=self.instance.exemplar_id
            )
            membros_ativos = membros_ativos | Membro.objects.filter(pk=self.instance.membro_id)

        self.fields["exemplar"].queryset = exemplares_disponiveis
        self.fields["membro"].queryset = membros_ativos
        self.fields["data_emprestimo"].label = "Data de retirada"
        self.fields["data_devolucao_prevista"].label = "Data prevista para entrega"

    class Meta:
        model = Emprestimo
        fields = [
            "exemplar",
            "membro",
            "data_emprestimo",
            "data_devolucao_prevista",
        ]
        widgets = {
            "data_emprestimo": forms.DateInput(attrs={"type": "date"}),
            "data_devolucao_prevista": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        dados = super().clean()
        retirada = dados.get("data_emprestimo")
        entrega_prevista = dados.get("data_devolucao_prevista")
        if retirada and entrega_prevista and entrega_prevista < retirada:
            self.add_error("data_devolucao_prevista", "A data prevista deve ser igual ou posterior à retirada.")
        return dados

    def save(self, commit=True):
        emprestimo = super().save(commit=False)
        if not commit:
            return emprestimo

        with transaction.atomic():
            emprestimo.save()
            if self._original_exemplar_id and self._original_exemplar_id != emprestimo.exemplar_id:
                exemplar_anterior = Exemplar.objects.get(pk=self._original_exemplar_id)
                emprestimos_ativos = Emprestimo.objects.filter(
                    exemplar=exemplar_anterior,
                    status__in=["ativo", "atrasado"],
                ).exclude(pk=emprestimo.pk)
                if not emprestimos_ativos.exists():
                    exemplar_anterior.status = "disponivel"
                    exemplar_anterior.save(update_fields=["status"])

            if emprestimo.status != "devolvido":
                emprestimo.exemplar.status = "emprestado"
                emprestimo.exemplar.save(update_fields=["status"])

        return emprestimo


class DevolucaoForm(forms.Form):
    data_devolucao_real = forms.DateField(
        label="Data de entrega",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, emprestimo, **kwargs):
        self.emprestimo = emprestimo
        super().__init__(*args, **kwargs)

    def clean_data_devolucao_real(self):
        data_devolucao = self.cleaned_data["data_devolucao_real"]
        if data_devolucao < self.emprestimo.data_emprestimo:
            raise forms.ValidationError("A data de entrega não pode ser anterior à retirada.")
        return data_devolucao


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["livro", "membro", "data_reserva", "status"]
        widgets = {
            "data_reserva": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        dados = super().clean()
        livro = dados.get("livro")
        data_reserva = dados.get("data_reserva")
        status = dados.get("status")

        if livro and data_reserva and status == "ativa":
            reservas_conflitantes = Reserva.objects.filter(
                livro=livro,
                data_reserva=data_reserva,
                status="ativa",
            )
            if self.instance.pk:
                reservas_conflitantes = reservas_conflitantes.exclude(pk=self.instance.pk)
            if reservas_conflitantes.exists():
                self.add_error("livro", "Este livro já está reservado nessa data.")

        return dados
