import uuid
from datetime import date, timedelta

from django.contrib.auth import login
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    AutorForm,
    CadastroForm,
    DevolucaoForm,
    EmprestimoForm,
    ExemplarForm,
    FiltroMetricasForm,
    LivroForm,
    MembroForm,
    OrganizacaoCriarForm,
    OrganizacaoEntrarForm,
    ReservaForm,
)
from .middleware import organizacao_required
from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Organizacao, OrganizacaoUsuario, Reserva


def cadastro(request):
    if request.user.is_authenticated:
        return redirect("painel")

    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                usuario = form.save()
                codigo_convite = form.cleaned_data["codigo_convite"]
                if codigo_convite:
                    organizacao = Organizacao.objects.get(codigo_convite=codigo_convite)
                    papel = "membro"
                else:
                    organizacao = Organizacao.objects.create(
                        nome=form.cleaned_data["nome_organizacao"]
                    )
                    papel = "admin"
                OrganizacaoUsuario.objects.create(
                    organizacao=organizacao,
                    usuario=usuario,
                    papel=papel,
                )
            login(request, usuario)
            request.session["organizacao_id"] = organizacao.pk
            return redirect("painel")
    else:
        form = CadastroForm()

    return render(request, "acervo/cadastro.html", {"form": form})


def organizacoes(request):
    form_criar = OrganizacaoCriarForm()
    form_entrar = OrganizacaoEntrarForm()

    if request.method == "POST":
        acao = request.POST.get("acao")

        if acao == "criar":
            form_criar = OrganizacaoCriarForm(request.POST)
            if form_criar.is_valid():
                with transaction.atomic():
                    organizacao = Organizacao.objects.create(
                        nome=form_criar.cleaned_data["nome"].strip()
                    )
                    OrganizacaoUsuario.objects.create(
                        organizacao=organizacao,
                        usuario=request.user,
                        papel="admin",
                    )
                request.session["organizacao_id"] = organizacao.pk
                messages.success(request, f"Biblioteca {organizacao.nome} criada.")
                return redirect("organizacoes")

        elif acao == "entrar":
            form_entrar = OrganizacaoEntrarForm(request.POST)
            if form_entrar.is_valid():
                organizacao = Organizacao.objects.filter(
                    codigo_convite=form_entrar.cleaned_data["codigo_convite"]
                ).first()
                if organizacao is None:
                    form_entrar.add_error("codigo_convite", "Código de convite não encontrado.")
                else:
                    _, criada = OrganizacaoUsuario.objects.get_or_create(
                        organizacao=organizacao,
                        usuario=request.user,
                        defaults={"papel": "membro"},
                    )
                    request.session["organizacao_id"] = organizacao.pk
                    if criada:
                        messages.success(request, f"Você entrou em {organizacao.nome}.")
                    else:
                        messages.info(request, f"Você já participa de {organizacao.nome}.")
                    return redirect("organizacoes")

        elif acao == "trocar":
            vinculo = get_object_or_404(
                OrganizacaoUsuario,
                organizacao_id=request.POST.get("organizacao_id"),
                usuario=request.user,
            )
            request.session["organizacao_id"] = vinculo.organizacao_id
            messages.success(request, f"Organização ativa: {vinculo.organizacao.nome}.")
            return redirect("organizacoes")

        elif acao == "renovar_convite":
            vinculo = request.vinculo_organizacao
            if vinculo and vinculo.papel == "admin":
                request.organizacao.codigo_convite = uuid.uuid4()
                request.organizacao.save(update_fields=["codigo_convite"])
                messages.success(request, "Código de convite renovado.")
            else:
                messages.error(request, "Somente administradores podem renovar o convite.")
            return redirect("organizacoes")

    return render(request, "acervo/organizacoes.html", {
        "form_criar": form_criar,
        "form_entrar": form_entrar,
    })


@organizacao_required
def inicio(request):
    return redirect("painel")


@organizacao_required
def painel(request):
    hoje = timezone.localdate()
    organizacao = request.organizacao
    filtro_periodo_form = FiltroMetricasForm(request.GET or None)
    filtro_valido = filtro_periodo_form.is_bound and filtro_periodo_form.is_valid()
    dados_filtro = filtro_periodo_form.cleaned_data if filtro_valido else {}
    granularidade = dados_filtro.get("granularidade") or request.GET.get("granularidade", "mes")
    if granularidade not in {"mes", "dia"}:
        granularidade = "mes"

    emprestimos_org = Emprestimo.objects.filter(organizacao=organizacao)
    emprestimos_abertos = emprestimos_org.filter(data_devolucao_real__isnull=True)
    total_emprestimos_abertos = emprestimos_abertos.count()
    total_emprestimos_atrasados = emprestimos_abertos.filter(
        data_devolucao_prevista__lt=hoje
    ).count()

    mes_selecionado = dados_filtro.get("mes")
    data_inicio = dados_filtro.get("data_inicio")
    data_fim = dados_filtro.get("data_fim")
    nomes_meses = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")

    if mes_selecionado:
        inicio_periodo = mes_selecionado.replace(day=1)
        proximo_mes = (inicio_periodo + timedelta(days=32)).replace(day=1)
        fim_periodo = min(proximo_mes - timedelta(days=1), hoje)
        periodo_label = f"{nomes_meses[inicio_periodo.month - 1].capitalize()} de {inicio_periodo.year}"
    elif data_inicio and data_fim:
        inicio_periodo = data_inicio
        fim_periodo = data_fim
        periodo_label = f"{inicio_periodo:%d/%m/%Y} a {fim_periodo:%d/%m/%Y}"
    elif granularidade == "dia":
        inicio_periodo = hoje - timedelta(days=29)
        fim_periodo = hoje
        periodo_label = "Últimos 30 dias"
    else:
        indice_mes_atual = hoje.year * 12 + hoje.month - 1
        indice_mes_inicial = indice_mes_atual - 11
        ano_inicial, mes_inicial_zero = divmod(indice_mes_inicial, 12)
        inicio_periodo = date(ano_inicial, mes_inicial_zero + 1, 1)
        fim_periodo = hoje
        periodo_label = "Últimos 12 meses"

    emprestimos_periodo = emprestimos_org.filter(
        data_emprestimo__gte=inicio_periodo,
        data_emprestimo__lte=fim_periodo,
    )

    if granularidade == "dia":
        datas = [
            inicio_periodo + timedelta(days=offset)
            for offset in range((fim_periodo - inicio_periodo).days + 1)
        ]
        contagens = {
            linha["data_emprestimo"]: linha["total"]
            for linha in emprestimos_periodo.values("data_emprestimo").annotate(total=Count("pk"))
        }
        serie = [
            {
                "rotulo": data.strftime("%d/%m") if indice % 5 == 0 or indice == 29 else "",
                "descricao": data.strftime("%d/%m/%Y"),
                "total": contagens.get(data, 0),
            }
            for indice, data in enumerate(datas)
        ]
    else:
        indice_mes_inicial = inicio_periodo.year * 12 + inicio_periodo.month - 1
        indice_mes_final = fim_periodo.year * 12 + fim_periodo.month - 1
        contagens = {
            (linha["periodo"].year, linha["periodo"].month): linha["total"]
            for linha in emprestimos_periodo.annotate(
                periodo=TruncMonth("data_emprestimo")
            ).values("periodo").annotate(total=Count("pk"))
        }
        serie = []
        meses_abreviados = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
        for indice in range(indice_mes_inicial, indice_mes_final + 1):
            ano, mes_zero = divmod(indice, 12)
            mes = mes_zero + 1
            serie.append({
                "rotulo": f"{meses_abreviados[mes - 1]}/{str(ano)[-2:]}",
                "descricao": f"{nomes_meses[mes - 1].capitalize()} de {ano}",
                "total": contagens.get((ano, mes), 0),
            })

    maior_serie = max((item["total"] for item in serie), default=0)
    for item in serie:
        item["percentual"] = round(item["total"] / maior_serie * 100) if maior_serie else 0

    parametros_mes = request.GET.copy()
    parametros_mes["granularidade"] = "mes"
    parametros_dia = request.GET.copy()
    parametros_dia["granularidade"] = "dia"

    ranking = list(
        emprestimos_periodo.values("exemplar__livro__titulo")
        .annotate(total=Count("pk"))
        .order_by("-total", "exemplar__livro__titulo")[:5]
    )
    maior_ranking = max((item["total"] for item in ranking), default=0)
    for item in ranking:
        item["percentual"] = round(item["total"] / maior_ranking * 100) if maior_ranking else 0

    total_devolvidos = emprestimos_org.filter(data_devolucao_real__isnull=False).count()
    total_em_dia = emprestimos_abertos.filter(data_devolucao_prevista__gte=hoje).count()
    distribuicao = [
        {"rotulo": "Em dia", "total": total_em_dia, "classe": "em-dia"},
        {"rotulo": "Atrasados", "total": total_emprestimos_atrasados, "classe": "atrasados"},
        {"rotulo": "Devolvidos", "total": total_devolvidos, "classe": "devolvidos"},
    ]
    total_situacoes = sum(item["total"] for item in distribuicao)
    for item in distribuicao:
        item["percentual"] = round(item["total"] / total_situacoes * 100) if total_situacoes else 0

    emprestimos_recentes = []
    registros_recentes = Emprestimo.objects.select_related(
        "exemplar__livro", "membro"
    ).filter(organizacao=organizacao).order_by("-data_emprestimo", "-pk")[:6]

    for emprestimo in registros_recentes:
        if emprestimo.data_devolucao_real:
            situacao, classe_status = "Devolvido", "devolvido"
        elif emprestimo.data_devolucao_prevista < hoje:
            situacao, classe_status = "Atrasado", "atrasado"
        else:
            situacao, classe_status = "Em aberto", "aberto"

        emprestimos_recentes.append({
            "registro": emprestimo,
            "situacao": situacao,
            "classe_status": classe_status,
        })

    return render(request, "acervo/painel.html", {
        "total_livros": Livro.objects.filter(organizacao=organizacao).count(),
        "total_exemplares_disponiveis": Exemplar.objects.filter(organizacao=organizacao, status="disponivel").count(),
        "total_membros_ativos": Membro.objects.filter(organizacao=organizacao, ativo=True).count(),
        "total_reservas_ativas": Reserva.objects.filter(organizacao=organizacao, status="ativa").count(),
        "total_emprestimos_abertos": total_emprestimos_abertos,
        "total_emprestimos_atrasados": total_emprestimos_atrasados,
        "emprestimos_recentes": emprestimos_recentes,
        "granularidade": granularidade,
        "periodo_label": periodo_label,
        "total_emprestimos_periodo": emprestimos_periodo.count(),
        "serie_emprestimos": serie,
        "ranking_emprestimos": ranking,
        "distribuicao_emprestimos": distribuicao,
        "filtro_periodo_form": filtro_periodo_form,
        "link_granularidade_mes": f"?{parametros_mes.urlencode()}",
        "link_granularidade_dia": f"?{parametros_dia.urlencode()}",
    })


@organizacao_required
def lista_livros(request):
    livros = Livro.objects.filter(organizacao=request.organizacao).select_related("autor").order_by("titulo")
    nome = request.GET.get("nome", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    categoria = request.GET.get("categoria", "").strip()

    if nome:
        livros = livros.filter(
            Q(titulo__icontains=nome)
            | Q(autor__nome__icontains=nome)
            | Q(autor__sobrenome__icontains=nome)
        )
    if tipo:
        livros = livros.filter(tipo=tipo)
    if categoria:
        livros = livros.filter(categoria=categoria)

    return render(
        request,
        "acervo/lista.html",
        {
            "itens": livros,
            "titulo": "Acervo de livros",
            "tipos": Livro.TIPO_CHOICES,
            "categorias": Livro.CATEGORIA_CHOICES,
            "filtro_nome": nome,
            "filtro_tipo": tipo,
            "filtro_categoria": categoria,
        },
    )


@organizacao_required
def novo_livro(request):
    return _salvar_formulario(request, LivroForm, "Livro", "novo_livro", "lista_livros")


@organizacao_required
def editar_livro(request, pk):
    return _editar_formulario(request, Livro, LivroForm, pk, "Livro", "lista_livros")


@organizacao_required
def excluir_livro(request, pk):
    return _excluir_registro(request, Livro, pk, "lista_livros")


@organizacao_required
def lista_autores(request):
    autores = Autor.objects.filter(organizacao=request.organizacao).order_by("sobrenome", "nome")
    return render(request, "acervo/lista.html", {"itens": autores, "titulo": "Autores"})


@organizacao_required
def novo_autor(request):
    return _salvar_formulario(request, AutorForm, "Autor", "novo_autor", "lista_autores")


@organizacao_required
def editar_autor(request, pk):
    return _editar_formulario(request, Autor, AutorForm, pk, "Autor", "lista_autores")


@organizacao_required
def excluir_autor(request, pk):
    return _excluir_registro(request, Autor, pk, "lista_autores")


@organizacao_required
def lista_exemplares(request):
    exemplares = Exemplar.objects.filter(organizacao=request.organizacao).select_related("livro").order_by("codigo")
    return render(request, "acervo/lista.html", {"itens": exemplares, "titulo": "Exemplares"})


@organizacao_required
def novo_exemplar(request):
    return _salvar_formulario(request, ExemplarForm, "Exemplar", "novo_exemplar", "lista_exemplares")


@organizacao_required
def editar_exemplar(request, pk):
    return _editar_formulario(request, Exemplar, ExemplarForm, pk, "Exemplar", "lista_exemplares")


@organizacao_required
def excluir_exemplar(request, pk):
    return _excluir_registro(request, Exemplar, pk, "lista_exemplares")


@organizacao_required
def lista_membros(request):
    membros = Membro.objects.filter(organizacao=request.organizacao).order_by("sobrenome", "nome")
    return render(request, "acervo/lista.html", {"itens": membros, "titulo": "Membros"})


@organizacao_required
def novo_membro(request):
    return _salvar_formulario(request, MembroForm, "Membro", "novo_membro", "lista_membros")


@organizacao_required
def editar_membro(request, pk):
    return _editar_formulario(request, Membro, MembroForm, pk, "Membro", "lista_membros")


@organizacao_required
def excluir_membro(request, pk):
    return _excluir_registro(request, Membro, pk, "lista_membros")


@organizacao_required
def lista_emprestimos(request):
    emprestimos = Emprestimo.objects.filter(organizacao=request.organizacao).select_related(
        "exemplar", "membro"
    ).order_by("-data_emprestimo")
    return render(request, "acervo/lista.html", {"itens": emprestimos, "titulo": "Empréstimos"})


@organizacao_required
def novo_emprestimo(request):
    return _salvar_formulario(request, EmprestimoForm, "Empréstimo", "novo_emprestimo", "lista_emprestimos")


@organizacao_required
def editar_emprestimo(request, pk):
    return _editar_formulario(request, Emprestimo, EmprestimoForm, pk, "Empréstimo", "lista_emprestimos")


@organizacao_required
def registrar_devolucao(request, pk):
    emprestimo = get_object_or_404(
        Emprestimo.objects.select_related("exemplar", "membro"),
        pk=pk,
        organizacao=request.organizacao,
    )
    if request.method != "POST":
        return redirect("lista_emprestimos")
    if emprestimo.status == "devolvido":
        messages.error(request, "Este empréstimo já foi devolvido.")
        return redirect("lista_emprestimos")

    form = DevolucaoForm(request.POST, emprestimo=emprestimo)
    if not form.is_valid():
        for erro in form.errors.get("data_devolucao_real", []):
            messages.error(request, erro)
        return redirect("lista_emprestimos")

    with transaction.atomic():
        emprestimo.data_devolucao_real = form.cleaned_data["data_devolucao_real"]
        emprestimo.status = "devolvido"
        emprestimo.save(update_fields=["data_devolucao_real", "status"])
        emprestimo.exemplar.status = "disponivel"
        emprestimo.exemplar.save(update_fields=["status"])

    multa = emprestimo.calcular_multa()
    if multa:
        messages.success(request, f"Devolução registrada para {emprestimo.membro}. Multa: R$ {multa:.2f}.")
    else:
        messages.success(request, f"Devolução registrada para {emprestimo.membro}. Sem multa.")
    return redirect("lista_emprestimos")


@organizacao_required
def excluir_emprestimo(request, pk):
    return _excluir_registro(request, Emprestimo, pk, "lista_emprestimos")


@organizacao_required
def lista_reservas(request):
    reservas = Reserva.objects.filter(organizacao=request.organizacao).select_related(
        "livro", "membro"
    ).order_by("data_reserva")
    return render(request, "acervo/lista.html", {"itens": reservas, "titulo": "Reservas"})


@organizacao_required
def nova_reserva(request):
    return _salvar_formulario(request, ReservaForm, "Reserva", "nova_reserva", "lista_reservas")


@organizacao_required
def editar_reserva(request, pk):
    return _editar_formulario(request, Reserva, ReservaForm, pk, "Reserva", "lista_reservas")


@organizacao_required
def excluir_reserva(request, pk):
    return _excluir_registro(request, Reserva, pk, "lista_reservas")


def _salvar_formulario(request, form_class, nome_entidade, nome_url, nome_lista):
    if request.method == "POST":
        form = form_class(request.POST, organizacao=request.organizacao)
        if form.is_valid():
            form.save()
            return redirect(nome_lista)
    else:
        form = form_class(organizacao=request.organizacao)

    return render(request, "acervo/form.html", {"form": form, "titulo_pagina": f"Novo {nome_entidade}"})


def _editar_formulario(request, model_class, form_class, pk, nome_entidade, nome_lista):
    registro = get_object_or_404(model_class, pk=pk, organizacao=request.organizacao)

    if request.method == "POST":
        form = form_class(request.POST, instance=registro, organizacao=request.organizacao)
        if form.is_valid():
            form.save()
            return redirect(nome_lista)
    else:
        form = form_class(instance=registro, organizacao=request.organizacao)

    return render(request, "acervo/form.html", {"form": form, "titulo_pagina": f"Editar {nome_entidade}"})


def _excluir_registro(request, model_class, pk, nome_lista):
    registro = get_object_or_404(model_class, pk=pk, organizacao=request.organizacao)
    if request.method == "POST":
        try:
            registro.delete()
        except ProtectedError:
            messages.error(
                request,
                "Não foi possível excluir este registro porque ele está vinculado a outros dados. "
                "Remova ou altere os vínculos antes de tentar novamente.",
            )
        else:
            messages.success(request, "Registro excluído com sucesso.")
    return redirect(nome_lista)
