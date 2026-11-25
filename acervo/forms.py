from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Organizacao, Reserva


class CadastroForm(UserCreationForm):
    nome_organizacao = forms.CharField(
        label="Nome da biblioteca",
        max_length=120,
        required=False,
        help_text="Preencha apenas para criar uma biblioteca nova.",
    )
    codigo_convite = forms.UUIDField(
        label="Código de convite",
        required=False,
        help_text="Use no lugar do nome para entrar em uma biblioteca existente.",
    )

    def clean(self):
        dados = super().clean()
        nome = (dados.get("nome_organizacao") or "").strip()
        codigo = dados.get("codigo_convite")

        if bool(nome) == bool(codigo):
            raise ValidationError("Informe o nome de uma nova biblioteca ou um código de convite, não os dois.")
        if codigo and not Organizacao.objects.filter(codigo_convite=codigo).exists():
            self.add_error("codigo_convite", "Código de convite inválido.")

        dados["nome_organizacao"] = nome
        return dados


class OrganizacaoCriarForm(forms.Form):
    nome = forms.CharField(label="Nome da biblioteca", max_length=120)


class OrganizacaoEntrarForm(forms.Form):
    codigo_convite = forms.UUIDField(label="Código de convite")


class FiltroMetricasForm(forms.Form):
    granularidade = forms.ChoiceField(
        choices=[("mes", "Mês"), ("dia", "Dia")],
        required=False,
        initial="mes",
    )
    mes = forms.DateField(
        label="Mês específico",
        required=False,
        input_formats=["%Y-%m"],
        widget=forms.DateInput(attrs={"type": "month"}, format="%Y-%m"),
    )
    data_inicio = forms.DateField(
        label="De",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    data_fim = forms.DateField(
        label="Até",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def clean(self):
        dados = super().clean()
        mes = dados.get("mes")
        inicio = dados.get("data_inicio")
        fim = dados.get("data_fim")
        granularidade = dados.get("granularidade") or "mes"
        hoje = timezone.localdate()

        if mes and (inicio or fim):
            raise ValidationError("Escolha um mês específico ou um intervalo de datas, não ambos.")
        if bool(inicio) != bool(fim):
            raise ValidationError("Informe as duas datas do intervalo.")
        if inicio and fim and inicio > fim:
            self.add_error("data_fim", "A data final deve ser igual ou posterior à inicial.")
        if fim and fim > hoje:
            self.add_error("data_fim", "A consulta não pode incluir datas futuras.")
        if mes and mes.replace(day=1) > hoje.replace(day=1):
            self.add_error("mes", "Selecione um mês que já começou.")
        if inicio and fim and granularidade == "dia" and (fim - inicio).days > 365:
            raise ValidationError("A consulta diária aceita intervalos de até um ano.")

        return dados


class OrganizacaoModelForm(forms.ModelForm):
    organizacao_campos_unicos = ()

    def __init__(self, *args, organizacao=None, **kwargs):
        self.organizacao = organizacao
        super().__init__(*args, **kwargs)

        if organizacao:
            if not self.instance.pk:
                self.instance.organizacao = organizacao
            for campo in self.fields.values():
                queryset = getattr(campo, "queryset", None)
                if queryset is not None and any(
                    field.name == "organizacao" for field in queryset.model._meta.fields
                ):
                    campo.queryset = queryset.filter(organizacao=organizacao)

    def clean(self):
        dados = super().clean()
        if self.organizacao is None:
            return dados

        for nome_campo in self.organizacao_campos_unicos:
            valor = dados.get(nome_campo)
            if valor is None:
                continue

            registros = self._meta.model.objects.filter(
                organizacao=self.organizacao,
                **{nome_campo: valor},
            )
            if self.instance.pk:
                registros = registros.exclude(pk=self.instance.pk)
            if registros.exists():
                self.add_error(nome_campo, "Este valor já está cadastrado nesta organização.")

        return dados

    def save(self, commit=True):
        if self.organizacao is None:
            raise ValueError("A organização ativa é obrigatória para salvar este formulário.")

        instancia = super().save(commit=False)
        instancia.organizacao = self.organizacao
        if commit:
            instancia.save()
            self.save_m2m()
        return instancia


class AutorForm(OrganizacaoModelForm):
    class Meta:
        model = Autor
        fields = ["nome", "sobrenome"]


class LivroForm(OrganizacaoModelForm):
    organizacao_campos_unicos = ("isbn",)

    class Meta:
        model = Livro
        fields = ["titulo", "tipo", "autor", "ano", "isbn", "categoria"]


class ExemplarForm(OrganizacaoModelForm):
    organizacao_campos_unicos = ("codigo",)

    class Meta:
        model = Exemplar
        fields = ["livro", "codigo", "status"]


class MembroForm(OrganizacaoModelForm):
    organizacao_campos_unicos = ("cpf", "email")

    class Meta:
        model = Membro
        fields = ["nome", "sobrenome", "cpf", "email", "ativo"]


class EmprestimoForm(OrganizacaoModelForm):
    def __init__(self, *args, **kwargs):
        organizacao = kwargs.pop("organizacao", None)
        self.organizacao = organizacao
        super().__init__(*args, organizacao=organizacao, **kwargs)
        self._original_exemplar_id = self.instance.exemplar_id
        exemplares_disponiveis = Exemplar.objects.filter(
            organizacao=organizacao,
        ).filter(Q(status="disponivel") | Q(pk=self.instance.exemplar_id))
        membros_ativos = Membro.objects.filter(
            organizacao=organizacao,
        ).filter(Q(ativo=True) | Q(pk=self.instance.membro_id))

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
        emprestimo.organizacao = self.organizacao
        if not commit:
            return emprestimo

        with transaction.atomic():
            emprestimo.save()
            if self._original_exemplar_id and self._original_exemplar_id != emprestimo.exemplar_id:
                exemplar_anterior = Exemplar.objects.get(
                    pk=self._original_exemplar_id,
                    organizacao=self.organizacao,
                )
                emprestimos_ativos = Emprestimo.objects.filter(
                    organizacao=self.organizacao,
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


class ReservaForm(OrganizacaoModelForm):
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
                organizacao=self.organizacao,
                livro=livro,
                data_reserva=data_reserva,
                status="ativa",
            )
            if self.instance.pk:
                reservas_conflitantes = reservas_conflitantes.exclude(pk=self.instance.pk)
            if reservas_conflitantes.exists():
                self.add_error("livro", "Este livro já está reservado nessa data.")

        return dados
