from django.contrib import admin
from .models import Livro


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin)
    list_display = ("titulo", "autor", "ano", "disponivel")
    list_filter = ("disponivel", "ano")
    search_fields = ("titulo", "autor")
    list_editable = ("disponivel",)
