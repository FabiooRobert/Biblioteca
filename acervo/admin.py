from django.contrib import admin
from .models import Livro


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = (
        "titulo", "autor", "ano", "organizacao", "tipo", "categoria", "disponivel"
    )
    list_filter = ("organizacao", "tipo", "categoria", "disponivel", "ano")
    search_fields = ("titulo", "autor")
    list_editable = ("disponivel",)
