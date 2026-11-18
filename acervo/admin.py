from django.contrib import admin

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Organizacao, OrganizacaoUsuario, Reserva


@admin.register(Organizacao)
class OrganizacaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo_convite", "criada_em")
    search_fields = ("nome", "codigo_convite")


@admin.register(OrganizacaoUsuario)
class OrganizacaoUsuarioAdmin(admin.ModelAdmin):
    list_display = ("organizacao", "usuario", "papel", "criado_em")
    list_filter = ("papel", "organizacao")
    search_fields = ("organizacao__nome", "usuario__username")


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("organizacao", "nome", "sobrenome")
    search_fields = ("nome", "sobrenome")


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("organizacao", "titulo", "tipo", "autor", "ano", "isbn", "categoria")
    list_filter = ("organizacao", "ano", "tipo", "categoria")
    search_fields = ("titulo", "tipo", "autor__nome", "autor__sobrenome", "isbn", "categoria")


@admin.register(Exemplar)
class ExemplarAdmin(admin.ModelAdmin):
    list_display = ("organizacao", "codigo", "livro", "status")
    list_filter = ("organizacao", "status", "livro")
    search_fields = ("codigo", "livro__titulo")


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ("organizacao", "nome", "sobrenome", "cpf", "email", "ativo")
    list_filter = ("organizacao", "ativo")
    search_fields = ("nome", "sobrenome", "cpf", "email")


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ("organizacao", "exemplar", "membro", "data_emprestimo", "data_devolucao_prevista", "status")
    list_filter = ("organizacao", "status", "data_emprestimo")
    search_fields = ("exemplar__codigo", "membro__nome", "membro__sobrenome")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("organizacao", "livro", "membro", "data_reserva", "status")
    list_filter = ("organizacao", "status", "data_reserva")
    search_fields = ("livro__titulo", "membro__nome", "membro__sobrenome")
