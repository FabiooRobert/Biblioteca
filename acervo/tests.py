from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Organizacao, Perfil
from .models import Livro


class LivroCrudTests(TestCase):
    def setUp(self):
        self.organizacao = Organizacao.objects.create(nome="Biblioteca A")
        self.usuario = get_user_model().objects.create_user(
            username="usuario-a", password="senha-teste"
        )
        Perfil.objects.create(usuario=self.usuario, organizacao=self.organizacao)
        self.client.login(username="usuario-a", password="senha-teste")
        self.livro = Livro.objects.create(
            titulo="Django para Iniciantes",
            autor="Maria Silva",
            ano=2024,
            disponivel=True,
            organizacao=self.organizacao,
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
                "tipo": "OUTRO",
                "categoria": "000",
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
                "tipo": "OUTRO",
                "categoria": "000",
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

    def test_lista_nao_exibe_livros_de_outra_organizacao(self):
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        Livro.objects.create(
            titulo="Livro da outra biblioteca",
            autor="Outro autor",
            ano=2025,
            organizacao=outra_org,
        )

        response = self.client.get(reverse("lista"))

        self.assertContains(response, "Django para Iniciantes")
        self.assertNotContains(response, "Livro da outra biblioteca")

    def test_usuario_nao_edita_livro_de_outra_organizacao(self):
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        livro = Livro.objects.create(
            titulo="Livro da outra biblioteca",
            autor="Outro autor",
            ano=2025,
            organizacao=outra_org,
        )

        response = self.client.get(reverse("editar", args=[livro.pk]))

        self.assertEqual(response.status_code, 404)

    def test_novo_livro_recebe_organizacao_do_usuario(self):
        response = self.client.post(
            reverse("novo"),
            {
                "titulo": "Livro da Biblioteca A",
                "autor": "Maria Silva",
                "ano": 2025,
                "tipo": "OUTRO",
                "categoria": "000",
                "disponivel": True,
            },
        )

        self.assertEqual(response.status_code, 302)
        livro = Livro.objects.get(titulo="Livro da Biblioteca A")
        self.assertEqual(livro.organizacao, self.organizacao)


class LivroApiTests(TestCase):
    def setUp(self):
        self.organizacao = Organizacao.objects.create(nome="Biblioteca A")
        usuario = get_user_model().objects.create_user(
            username="api-a", password="senha-teste"
        )
        Perfil.objects.create(usuario=usuario, organizacao=self.organizacao)
        self.client.login(username="api-a", password="senha-teste")
        self.url = "/api/livros/"

    def test_api_lista_apenas_livros_da_organizacao(self):
        Livro.objects.create(
            titulo="Livro A", autor="Autor A", ano=2025,
            organizacao=self.organizacao,
        )
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        Livro.objects.create(
            titulo="Livro B", autor="Autor B", ano=2025,
            organizacao=outra_org,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["titulo"] for item in response.json()], ["Livro A"])

    def test_api_nao_revela_livro_de_outra_organizacao(self):
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        livro = Livro.objects.create(
            titulo="Livro B",
            autor="Autor B",
            ano=2025,
            organizacao=outra_org,
        )

        response = self.client.get(f"{self.url}{livro.pk}/")

        self.assertEqual(response.status_code, 404)

    def test_api_exige_autenticacao(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertIn(response.status_code, (401, 403))

    def test_api_cria_livro_na_organizacao_do_usuario(self):
        response = self.client.post(
            self.url,
            {
                "titulo": "Livro criado pela API",
                "autor": "Autor A",
                "ano": 2025,
                "tipo": "OUTRO",
                "categoria": "000",
                "disponivel": True,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        livro = Livro.objects.get(titulo="Livro criado pela API")
        self.assertEqual(livro.organizacao, self.organizacao)
        self.assertNotIn("organizacao", response.json())
