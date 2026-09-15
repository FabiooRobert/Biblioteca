from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AutorForm,
    EmprestimoForm,
    ExemplarForm,
    LivroForm,
    MembroForm,
    ReservaForm,
)
from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva


def inicio(request):
    return redirect("lista_livros")


def lista_livros(request):
    livros = Livro.objects.select_related("autor").all().order_by("titulo")
    return render(request, "acervo/lista.html", {"itens": livros, "titulo": "Acervo de livros"})


def novo_livro(request):
    return _salvar_formulario(request, LivroForm, "Livro", "novo_livro", "lista_livros")


def editar_livro(request, pk):
    return _editar_formulario(request, Livro, LivroForm, pk, "Livro", "lista_livros")


def excluir_livro(request, pk):
    return _excluir_registro(request, Livro, pk, "lista_livros")


def lista_autores(request):
    autores = Autor.objects.all().order_by("sobrenome", "nome")
    return render(request, "acervo/lista.html", {"itens": autores, "titulo": "Autores"})


def novo_autor(request):
    return _salvar_formulario(request, AutorForm, "Autor", "novo_autor", "lista_autores")


def editar_autor(request, pk):
    return _editar_formulario(request, Autor, AutorForm, pk, "Autor", "lista_autores")


def excluir_autor(request, pk):
    return _excluir_registro(request, Autor, pk, "lista_autores")


def lista_exemplares(request):
    exemplares = Exemplar.objects.select_related("livro").all().order_by("codigo")
    return render(request, "acervo/lista.html", {"itens": exemplares, "titulo": "Exemplares"})


def novo_exemplar(request):
    return _salvar_formulario(request, ExemplarForm, "Exemplar", "novo_exemplar", "lista_exemplares")


def editar_exemplar(request, pk):
    return _editar_formulario(request, Exemplar, ExemplarForm, pk, "Exemplar", "lista_exemplares")


def excluir_exemplar(request, pk):
    return _excluir_registro(request, Exemplar, pk, "lista_exemplares")


def lista_membros(request):
    membros = Membro.objects.all().order_by("sobrenome", "nome")
    return render(request, "acervo/lista.html", {"itens": membros, "titulo": "Membros"})


def novo_membro(request):
    return _salvar_formulario(request, MembroForm, "Membro", "novo_membro", "lista_membros")


def editar_membro(request, pk):
    return _editar_formulario(request, Membro, MembroForm, pk, "Membro", "lista_membros")


def excluir_membro(request, pk):
    return _excluir_registro(request, Membro, pk, "lista_membros")


def lista_emprestimos(request):
    emprestimos = Emprestimo.objects.select_related("exemplar", "membro").all().order_by("-data_emprestimo")
    return render(request, "acervo/lista.html", {"itens": emprestimos, "titulo": "Empréstimos"})


def novo_emprestimo(request):
    return _salvar_formulario(request, EmprestimoForm, "Empréstimo", "novo_emprestimo", "lista_emprestimos")


def editar_emprestimo(request, pk):
    return _editar_formulario(request, Emprestimo, EmprestimoForm, pk, "Empréstimo", "lista_emprestimos")


def excluir_emprestimo(request, pk):
    return _excluir_registro(request, Emprestimo, pk, "lista_emprestimos")


def lista_reservas(request):
    reservas = Reserva.objects.select_related("livro", "membro").all().order_by("data_reserva")
    return render(request, "acervo/lista.html", {"itens": reservas, "titulo": "Reservas"})


def nova_reserva(request):
    return _salvar_formulario(request, ReservaForm, "Reserva", "nova_reserva", "lista_reservas")


def editar_reserva(request, pk):
    return _editar_formulario(request, Reserva, ReservaForm, pk, "Reserva", "lista_reservas")


def excluir_reserva(request, pk):
    return _excluir_registro(request, Reserva, pk, "lista_reservas")


def _salvar_formulario(request, form_class, nome_entidade, nome_url, nome_lista):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(nome_lista)
    else:
        form = form_class()

    return render(request, "acervo/form.html", {"form": form, "titulo_pagina": f"Novo {nome_entidade}"})


def _editar_formulario(request, model_class, form_class, pk, nome_entidade, nome_lista):
    registro = get_object_or_404(model_class, pk=pk)

    if request.method == "POST":
        form = form_class(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            return redirect(nome_lista)
    else:
        form = form_class(instance=registro)

    return render(request, "acervo/form.html", {"form": form, "titulo_pagina": f"Editar {nome_entidade}"})


def _excluir_registro(request, model_class, pk, nome_lista):
    registro = get_object_or_404(model_class, pk=pk)
    if request.method == "POST":
        registro.delete()
    return redirect(nome_lista)
