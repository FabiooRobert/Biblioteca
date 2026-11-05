from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from .forms import LivroForm
from .models import Livro


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
            Q(titulo__icontains=pesquisa) | Q(autor__icontains=pesquisa)
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
        },
    )


@login_required
def novo_livro(request):
    org = org_atual(request)
    if request.method == "POST":
        form = LivroForm(request.POST)
        if form.is_valid():
            livro = form.save(commit=False)
            livro.organizacao = org
            livro.save()
            return redirect("lista")
    else:
        form = LivroForm()

    return render(request, "acervo/form.html", {"form": form, "titulo_pagina": "Novo livro"})


@login_required
def editar_livro(request, pk):
    org = org_atual(request)
    livro = get_object_or_404(Livro, pk=pk, organizacao=org)

    if request.method == "POST":
        form = LivroForm(request.POST, instance=livro)
        if form.is_valid():
            form.save()
            return redirect("lista")
    else:
        form = LivroForm(instance=livro)

    return render(request, "acervo/form.html", {"form": form, "titulo_pagina": "Editar livro"})


@login_required
def excluir_livro(request, pk):
    org = org_atual(request)
    livro = get_object_or_404(Livro, pk=pk, organizacao=org)
    if request.method == "POST":
        livro.delete()
        return redirect("lista")
    return redirect("lista")
