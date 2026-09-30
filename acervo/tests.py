from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva


class BibliotecaBusinessRulesTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(username="leitora", password="senha-forte-123")
        self.client.force_login(self.usuario)
        self.autor = Autor.objects.create(nome="George", sobrenome="Orwell")
        self.livro = Livro.objects.create(
            titulo="1984",
            tipo="revista",
            autor=self.autor,
            ano=1949,
            isbn="978-0-452-28423-4",
            categoria="800",
        )
        self.exemplar = Exemplar.objects.create(
            livro=self.livro,
            codigo="EX-001",
            status="disponivel",
        )
        self.membro = Membro.objects.create(
            nome="Ana",
            sobrenome="Silva",
            cpf="12345678900",
            email="ana@example.com",
        )
        self.membro_2 = Membro.objects.create(
            nome="Bruno",
            sobrenome="Costa",
            cpf="12345678901",
            email="bruno@example.com",
        )

    def test_calculo_multa_por_atraso(self):
        emprestimo = Emprestimo.objects.create(
            exemplar=self.exemplar,
            membro=self.membro,
            data_emprestimo=date(2026, 1, 1),
            data_devolucao_prevista=date(2026, 1, 10),
            data_devolucao_real=date(2026, 1, 15),
            status="devolvido",
        )

        self.assertEqual(emprestimo.calcular_multa(), 10.0)

    def test_multa_conta_atraso_de_emprestimo_ainda_aberto(self):
        emprestimo = Emprestimo.objects.create(
            exemplar=self.exemplar,
            membro=self.membro,
            data_emprestimo=date(2026, 1, 1),
            data_devolucao_prevista=date(2026, 1, 10),
        )

        with patch("acervo.models.timezone.localdate", return_value=date(2026, 1, 15)):
            self.assertEqual(emprestimo.dias_atraso(), 5)
            self.assertEqual(emprestimo.calcular_multa(), 10.0)

    def test_novo_emprestimo_registra_retirada_membro_e_indisponibilidade(self):
        response = self.client.post(
            reverse("novo_emprestimo"),
            {
                "exemplar": self.exemplar.pk,
                "membro": self.membro.pk,
                "data_emprestimo": "2026-02-01",
                "data_devolucao_prevista": "2026-02-08",
            },
        )

        self.assertRedirects(response, reverse("lista_emprestimos"))
        emprestimo = Emprestimo.objects.get()
        self.assertEqual(emprestimo.membro, self.membro)
        self.assertEqual(emprestimo.data_emprestimo, date(2026, 2, 1))
        self.assertEqual(self.exemplar.__class__.objects.get(pk=self.exemplar.pk).status, "emprestado")

    def test_devolucao_atrasada_calcula_multa_e_libera_exemplar(self):
        emprestimo = Emprestimo.objects.create(
            exemplar=self.exemplar,
            membro=self.membro,
            data_emprestimo=date(2026, 2, 1),
            data_devolucao_prevista=date(2026, 2, 8),
        )
        self.exemplar.status = "emprestado"
        self.exemplar.save(update_fields=["status"])

        response = self.client.post(
            reverse("registrar_devolucao", args=[emprestimo.pk]),
            {"data_devolucao_real": "2026-02-10"},
            follow=True,
        )

        emprestimo.refresh_from_db()
        self.exemplar.refresh_from_db()
        self.assertEqual(emprestimo.status, "devolvido")
        self.assertEqual(emprestimo.data_devolucao_real, date(2026, 2, 10))
        self.assertEqual(emprestimo.calcular_multa(), 4.0)
        self.assertEqual(self.exemplar.status, "disponivel")
        self.assertContains(response, "Multa: R$ 4.00")

    def test_fila_de_reserva_gera_posicao(self):
        reserva_1 = Reserva.objects.create(
            livro=self.livro,
            membro=self.membro,
            data_reserva=date(2026, 2, 1),
        )
        reserva_2 = Reserva.objects.create(
            livro=self.livro,
            membro=self.membro_2,
            data_reserva=date(2026, 2, 2),
        )

        self.assertEqual(reserva_1.posicao_na_fila(), 1)
        self.assertEqual(reserva_2.posicao_na_fila(), 2)

    def test_nao_permite_reservar_mesmo_livro_na_mesma_data(self):
        data_reserva = date(2026, 2, 1)
        Reserva.objects.create(
            livro=self.livro,
            membro=self.membro,
            data_reserva=data_reserva,
        )

        response = self.client.post(
            reverse("nova_reserva"),
            {
                "livro": self.livro.pk,
                "membro": self.membro_2.pk,
                "data_reserva": data_reserva.isoformat(),
                "status": "ativa",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este livro já está reservado nessa data.")
        self.assertEqual(Reserva.objects.count(), 1)

    def test_lista_exibe_livros(self):
        response = self.client.get(reverse("lista_livros"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1984")
        self.assertContains(response, "Literatura: Poesia")
        self.assertNotContains(response, "800 – Literatura")

    def test_lista_filtra_livros_por_nome_tipo_e_categoria(self):
        outro_livro = Livro.objects.create(
            titulo="Introdução à Biologia",
            tipo="tcc",
            autor=self.autor,
            ano=2024,
            isbn="978-1-000-00002-8",
            categoria="500",
        )

        casos = [
            ({"nome": "1984"}, self.livro, outro_livro),
            ({"tipo": "revista"}, self.livro, outro_livro),
            ({"categoria": "500"}, outro_livro, self.livro),
            ({"nome": "George", "tipo": "revista", "categoria": "800"}, self.livro, outro_livro),
        ]
        for filtros, esperado, ausente in casos:
            with self.subTest(filtros=filtros):
                response = self.client.get(reverse("lista_livros"), filtros)
                self.assertContains(response, esperado.titulo)
                self.assertNotContains(response, ausente.titulo)

    def test_visitante_e_enviado_para_login(self):
        self.client.logout()
        response = self.client.get(reverse("lista_livros"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('lista_livros')}")

    def test_exclusao_de_autor_vinculado_mostra_mensagem(self):
        response = self.client.post(reverse("excluir_autor", args=[self.autor.pk]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Não foi possível excluir este registro")
        self.assertTrue(Autor.objects.filter(pk=self.autor.pk).exists())

    def test_cadastro_cria_conta_e_autentica(self):
        self.client.logout()
        response = self.client.post(
            reverse("cadastro"),
            {"username": "nova_leitora", "password1": "Senha-segura-456", "password2": "Senha-segura-456"},
        )
        self.assertRedirects(response, reverse("lista_livros"))
        self.assertTrue(get_user_model().objects.filter(username="nova_leitora").exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_novo_livro_cria_registro(self):
        response = self.client.post(
            reverse("novo_livro"),
            {
                "titulo": "Django para Iniciantes",
                "autor": self.autor.pk,
                "ano": 2025,
                "isbn": "978-1-000-00001-1",
                "tipo": "jornal",
                "categoria": "500",
            },
        )
        self.assertEqual(response.status_code, 302)
        livro = Livro.objects.get(titulo="Django para Iniciantes")
        self.assertEqual(livro.tipo, "jornal")
        self.assertEqual(livro.categoria, "500")
