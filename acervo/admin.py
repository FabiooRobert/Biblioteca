from django.contrib import admin

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nome", "sobrenome", "organizacao")
    list_filter = ("organizacao",)
    search_fields = ("nome", "sobrenome")


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "autor",
        "ano",
        "organizacao",
        "tipo",
        "categoria",
        "disponivel",
    )
    list_filter = ("organizacao", "tipo", "categoria", "disponivel", "ano")
    search_fields = ("titulo", "autor__nome", "autor__sobrenome", "isbn")
    list_editable = ("disponivel",)


@admin.register(Exemplar)
class ExemplarAdmin(admin.ModelAdmin):
    list_display = ("codigo", "livro", "organizacao", "status")
    list_filter = ("organizacao", "status")
    search_fields = ("codigo", "livro__titulo")


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ("nome", "sobrenome", "cpf", "email", "organizacao", "ativo")
    list_filter = ("organizacao", "ativo")
    search_fields = ("nome", "sobrenome", "cpf", "email")


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = (
        "exemplar",
        "membro",
        "organizacao",
        "data_emprestimo",
        "data_devolucao_prevista",
        "status",
    )
    list_filter = ("organizacao", "status", "data_emprestimo")
    search_fields = ("exemplar__codigo", "membro__nome", "membro__sobrenome")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("livro", "membro", "organizacao", "data_reserva", "status")
    list_filter = ("organizacao", "status", "data_reserva")
    search_fields = ("livro__titulo", "membro__nome", "membro__sobrenome")
