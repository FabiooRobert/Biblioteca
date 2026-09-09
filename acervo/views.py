from django.shortcuts import get_object_or_404, redirect, render
from .forms import LivroForm
from .models import Livro


def inicio(request):
    return redirect("lista")


def lista_livros(request):
    livros = Livro.objects.all().order_by("titulo")
    return render(request, "acervo/lista.html", {"livros": livros})


def novo_livro(request):
    if request.method == "POST":
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista")
    else:
        form = LivroForm()

    return render(request, "acervo/form.html", {"form": form, "titulo_pagina": "Novo livro"})


def editar_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk)

    if request.method == "POST":
        form = LivroForm(request.POST, instance=livro)
        if form.is_valid():
            form.save()
            return redirect("lista")
    else:
        form = LivroForm(instance=livro)

    return render(request, "acervo/form.html", {"form": form, "titulo_pagina": "Editar livro"})


def excluir_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    if request.method == "POST":
        livro.delete()
        return redirect("lista")
    return redirect("lista")
