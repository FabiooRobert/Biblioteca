from django.contrib import admin

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nome", "sobrenome")
    search_fields = ("nome", "sobrenome")


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "ano", "isbn")
    list_filter = ("ano",)
    search_fields = ("titulo", "autor__nome", "autor__sobrenome", "isbn")


@admin.register(Exemplar)
class ExemplarAdmin(admin.ModelAdmin):
    list_display = ("codigo", "livro", "status")
    list_filter = ("status", "livro")
    search_fields = ("codigo", "livro__titulo")


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ("nome", "sobrenome", "cpf", "email", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome", "sobrenome", "cpf", "email")


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ("exemplar", "membro", "data_emprestimo", "data_devolucao_prevista", "status")
    list_filter = ("status", "data_emprestimo")
    search_fields = ("exemplar__codigo", "membro__nome", "membro__sobrenome")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("livro", "membro", "data_reserva", "status")
    list_filter = ("status", "data_reserva")
    search_fields = ("livro__titulo", "membro__nome", "membro__sobrenome")
