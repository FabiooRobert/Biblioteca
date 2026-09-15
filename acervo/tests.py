from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva


class BibliotecaBusinessRulesTests(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nome="George", sobrenome="Orwell")
        self.livro = Livro.objects.create(
            titulo="1984",
            autor=self.autor,
            ano=1949,
            isbn="978-0-452-28423-4",
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

        self.assertEqual(emprestimo.calcular_multa(), 12.5)

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

    def test_lista_exibe_livros(self):
        response = self.client.get(reverse("lista_livros"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1984")

    def test_novo_livro_cria_registro(self):
        response = self.client.post(
            reverse("novo_livro"),
            {
                "titulo": "Django para Iniciantes",
                "autor": self.autor.pk,
                "ano": 2025,
                "isbn": "978-1-000-00001-1",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Livro.objects.filter(titulo="Django para Iniciantes").exists())
