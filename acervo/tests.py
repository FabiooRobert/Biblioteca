from django.test import TestCase
from django.urls import reverse

from .models import Livro


class LivroCrudTests(TestCase):
    def setUp(self):
        self.livro = Livro.objects.create(
            titulo="Django para Iniciantes",
            autor="Maria Silva",
            ano=2024,
            disponivel=True,
        )

    def test_lista_exibe_livros(self):
        response = self.client.get(reverse("lista"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django para Iniciantes")

    def test_novo_livro_cria_registro(self):
        response = self.client.post(
            reverse("novo"),
            {
                "titulo": "Python Avançado",
                "autor": "João Souza",
                "ano": 2025,
                "disponivel": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Livro.objects.filter(titulo="Python Avançado").exists())

    def test_editar_livro_atualiza_registro(self):
        response = self.client.post(
            reverse("editar", args=[self.livro.pk]),
            {
                "titulo": "Django Atualizado",
                "autor": "Maria Silva",
                "ano": 2025,
                "disponivel": False,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.titulo, "Django Atualizado")
        self.assertFalse(self.livro.disponivel)

    def test_excluir_livro_remove_registro(self):
        response = self.client.post(reverse("excluir", args=[self.livro.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Livro.objects.filter(pk=self.livro.pk).exists())
