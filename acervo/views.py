from datetime import timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import LivroForm
from .models import Livro
from .permissions import administrador_requerido, usuario_eh_administrador


def org_atual(request):
    perfil = getattr(request.user, "perfil", None)
    if perfil is None:
        raise PermissionDenied("Usuário sem organização vinculada.")
    return perfil.organizacao


def inicio(request):
    return redirect("lista")


@login_required
def lista_livros(request):
    org = org_atual(request)
    livros = Livro.objects.filter(organizacao=org).order_by("titulo")

    pesquisa = request.GET.get("pesquisa", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    categoria = request.GET.get("categoria", "").strip()

    if pesquisa:
        livros = livros.filter(
            Q(titulo__icontains=pesquisa)
            | Q(autor__nome__icontains=pesquisa)
            | Q(autor__sobrenome__icontains=pesquisa)
        )

    if tipo:
        livros = livros.filter(tipo=tipo)

    if categoria:
        livros = livros.filter(categoria=categoria)

    return render(
        request,
        "acervo/lista.html",
        {
            "livros": livros,
            "pesquisa": pesquisa,
            "tipo_selecionado": tipo,
            "categoria_selecionada": categoria,
            "tipos": Livro.TIPOS_ACERVO,
            "categorias": Livro.CATEGORIAS_ACERVO,
            "is_admin": usuario_eh_administrador(request.user),
        },
    )


@login_required
def dashboard(request):
    org = org_atual(request)
    periodo = request.GET.get("periodo", "30")
    dias_por_periodo = {"30": 30, "90": 90, "365": 365, "todos": None}
    if periodo not in dias_por_periodo:
        periodo = "30"

    livros = Livro.objects.filter(organizacao=org)
    dias = dias_por_periodo[periodo]
    if dias is not None:
        livros = livros.filter(cadastrado_em__gte=timezone.now() - timedelta(days=dias))

    resumo = livros.aggregate(
        total=Count("id"),
        disponiveis=Count("id", filter=Q(disponivel=True)),
        indisponiveis=Count("id", filter=Q(disponivel=False)),
    )
    rotulos_tipo = dict(Livro.TIPOS_ACERVO)
    rotulos_categoria = dict(Livro.CATEGORIAS_ACERVO)
    por_tipo = [
        {"nome": rotulos_tipo.get(item["tipo"], item["tipo"]), "total": item["total"]}
        for item in livros.values("tipo").annotate(total=Count("id")).order_by("-total", "tipo")
    ]
    por_categoria = [
        {
            "nome": rotulos_categoria.get(item["categoria"], item["categoria"]),
            "total": item["total"],
        }
        for item in livros.values("categoria").annotate(total=Count("id")).order_by("-total", "categoria")
    ]
    autores = (
        livros.values("autor__nome", "autor__sobrenome")
        .annotate(total=Count("id"))
        .order_by("-total", "autor__sobrenome", "autor__nome")[:5]
    )
    autores = [
        {
            "nome": f"{item['autor__nome']} {item['autor__sobrenome']}".strip(),
            "total": item["total"],
        }
        for item in autores
    ]

    return render(
        request,
        "acervo/dashboard.html",
        {
            "resumo": resumo,
            "por_tipo": por_tipo,
            "por_categoria": por_categoria,
            "autores": autores,
            "periodo": periodo,
        },
    )


@login_required
@administrador_requerido
def novo_livro(request):
    org = org_atual(request)
    if request.method == "POST":
        form = LivroForm(request.POST, organizacao=org)
        if form.is_valid():
            livro = form.save(commit=False)
            livro.organizacao = org
            livro.save()
            return redirect("lista")
    else:
        form = LivroForm(organizacao=org)

    return render(request, "acervo/form.html", {"form": form, "titulo_pagina": "Novo livro"})


@login_required
@administrador_requerido
def editar_livro(request, pk):
    org = org_atual(request)
    livro = get_object_or_404(Livro, pk=pk, organizacao=org)

    if request.method == "POST":
        form = LivroForm(request.POST, instance=livro, organizacao=org)
        if form.is_valid():
            form.save()
            return redirect("lista")
    else:
        form = LivroForm(instance=livro, organizacao=org)

    return render(request, "acervo/form.html", {"form": form, "titulo_pagina": "Editar livro"})


@login_required
@administrador_requerido
def excluir_livro(request, pk):
    org = org_atual(request)
    livro = get_object_or_404(Livro, pk=pk, organizacao=org)
    if request.method == "POST":
        livro.delete()
        return redirect("lista")
    return redirect("lista")
