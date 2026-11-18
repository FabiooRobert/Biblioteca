from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Organizacao, OrganizacaoUsuario, Reserva


class BibliotecaBusinessRulesTests(TestCase):
    def setUp(self):
        self.organizacao = Organizacao.objects.create(nome="Biblioteca de testes")
        self.usuario = get_user_model().objects.create_user(username="leitora", password="senha-forte-123")
        OrganizacaoUsuario.objects.create(
            organizacao=self.organizacao,
            usuario=self.usuario,
            papel="admin",
        )
        self.client.force_login(self.usuario)
        self.autor = Autor.objects.create(
            organizacao=self.organizacao,
            nome="George",
            sobrenome="Orwell",
        )
        self.livro = Livro.objects.create(
            organizacao=self.organizacao,
            titulo="1984",
            tipo="revista",
            autor=self.autor,
            ano=1949,
            isbn="978-0-452-28423-4",
            categoria="800",
        )
        self.exemplar = Exemplar.objects.create(
            organizacao=self.organizacao,
            livro=self.livro,
            codigo="EX-001",
            status="disponivel",
        )
        self.membro = Membro.objects.create(
            organizacao=self.organizacao,
            nome="Ana",
            sobrenome="Silva",
            cpf="12345678900",
            email="ana@example.com",
        )
        self.membro_2 = Membro.objects.create(
            organizacao=self.organizacao,
            nome="Bruno",
            sobrenome="Costa",
            cpf="12345678901",
            email="bruno@example.com",
        )

    def test_calculo_multa_por_atraso(self):
        emprestimo = Emprestimo.objects.create(
            organizacao=self.organizacao,
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
            organizacao=self.organizacao,
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
            organizacao=self.organizacao,
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
            organizacao=self.organizacao,
            livro=self.livro,
            membro=self.membro,
            data_reserva=date(2026, 2, 1),
        )
        reserva_2 = Reserva.objects.create(
            organizacao=self.organizacao,
            livro=self.livro,
            membro=self.membro_2,
            data_reserva=date(2026, 2, 2),
        )

        self.assertEqual(reserva_1.posicao_na_fila(), 1)
        self.assertEqual(reserva_2.posicao_na_fila(), 2)

    def test_nao_permite_reservar_mesmo_livro_na_mesma_data(self):
        data_reserva = date(2026, 2, 1)
        Reserva.objects.create(
            organizacao=self.organizacao,
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
            organizacao=self.organizacao,
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

    def test_lista_e_edicao_nao_acessam_outra_organizacao(self):
        outra_organizacao = Organizacao.objects.create(nome="Biblioteca vizinha")
        outro_autor = Autor.objects.create(
            organizacao=outra_organizacao,
            nome="Autora",
            sobrenome="Externa",
        )
        outro_livro = Livro.objects.create(
            organizacao=outra_organizacao,
            titulo="Registro de outra biblioteca",
            tipo="outro",
            autor=outro_autor,
            ano=2026,
            isbn="ISBN-OUTRA-ORG",
        )

        lista = self.client.get(reverse("lista_livros"))
        edicao = self.client.get(reverse("editar_livro", args=[outro_livro.pk]))
        painel = self.client.get(reverse("painel"))

        self.assertContains(lista, self.livro.titulo)
        self.assertNotContains(lista, outro_livro.titulo)
        self.assertEqual(edicao.status_code, 404)
        self.assertEqual(painel.context["total_livros"], 1)

        resposta_formulario = self.client.post(
            reverse("novo_livro"),
            {
                "titulo": "Tentativa de vínculo externo",
                "tipo": "outro",
                "autor": outro_autor.pk,
                "ano": 2026,
                "isbn": "ISBN-INVASAO",
                "categoria": "800",
            },
        )
        self.assertEqual(resposta_formulario.status_code, 200)
        self.assertFalse(
            Livro.objects.filter(
                organizacao=self.organizacao,
                titulo="Tentativa de vínculo externo",
            ).exists()
        )

    def test_painel_calcula_kpis_ranking_serie_e_distribuicao(self):
        hoje = date(2026, 6, 15)
        livro_popular = Livro.objects.create(
            organizacao=self.organizacao,
            titulo="Animal Farm",
            tipo="outro",
            autor=self.autor,
            ano=1945,
            isbn="ISBN-ANIMAL-FARM",
        )
        exemplar_popular = Exemplar.objects.create(
            organizacao=self.organizacao,
            livro=livro_popular,
            codigo="EX-002",
        )
        Emprestimo.objects.create(
            organizacao=self.organizacao,
            exemplar=self.exemplar,
            membro=self.membro,
            data_emprestimo=date(2026, 6, 14),
            data_devolucao_prevista=date(2026, 6, 30),
        )
        Emprestimo.objects.create(
            organizacao=self.organizacao,
            exemplar=exemplar_popular,
            membro=self.membro_2,
            data_emprestimo=date(2026, 6, 10),
            data_devolucao_prevista=date(2026, 6, 12),
        )
        Emprestimo.objects.create(
            organizacao=self.organizacao,
            exemplar=exemplar_popular,
            membro=self.membro_2,
            data_emprestimo=date(2026, 6, 2),
            data_devolucao_prevista=date(2026, 6, 5),
            data_devolucao_real=date(2026, 6, 6),
            status="devolvido",
        )

        with patch("acervo.views.timezone.localdate", return_value=hoje):
            mensal = self.client.get(reverse("painel"), {"granularidade": "mes"})
            diaria = self.client.get(reverse("painel"), {"granularidade": "dia"})
            mes_selecionado = self.client.get(
                reverse("painel"),
                {"granularidade": "mes", "mes": "2026-06"},
            )
            intervalo = self.client.get(
                reverse("painel"),
                {
                    "granularidade": "dia",
                    "data_inicio": "2026-06-02",
                    "data_fim": "2026-06-10",
                },
            )

        self.assertEqual(mensal.context["total_emprestimos_periodo"], 3)
        self.assertEqual(mensal.context["total_emprestimos_abertos"], 2)
        self.assertEqual(mensal.context["total_emprestimos_atrasados"], 1)
        self.assertContains(mensal, "Livros mais emprestados")
        self.assertContains(mensal, "Evolução de empréstimos")
        self.assertContains(mensal, "Por situação")
        self.assertContains(mensal, 'type="month"')
        self.assertContains(mensal, 'name="data_inicio"')
        self.assertContains(mensal, 'name="data_fim"')
        self.assertContains(diaria, "granularidade=dia")
        self.assertEqual(mensal.context["ranking_emprestimos"][0]["exemplar__livro__titulo"], "Animal Farm")
        self.assertEqual(mensal.context["ranking_emprestimos"][0]["total"], 2)
        mes_atual = next(item for item in mensal.context["serie_emprestimos"] if item["rotulo"] == "jun/26")
        self.assertEqual(mes_atual["total"], 3)
        self.assertEqual(sum(item["total"] for item in diaria.context["serie_emprestimos"]), 3)
        self.assertEqual(mes_selecionado.context["periodo_label"], "Junho de 2026")
        self.assertEqual(mes_selecionado.context["total_emprestimos_periodo"], 3)
        self.assertEqual(len(mes_selecionado.context["serie_emprestimos"]), 1)
        self.assertEqual(intervalo.context["periodo_label"], "02/06/2026 a 10/06/2026")
        self.assertEqual(intervalo.context["total_emprestimos_periodo"], 2)
        self.assertEqual(
            sum(item["total"] for item in intervalo.context["serie_emprestimos"]),
            2,
        )
        self.assertEqual(
            {item["rotulo"]: item["total"] for item in mensal.context["distribuicao_emprestimos"]},
            {"Em dia": 1, "Atrasados": 1, "Devolvidos": 1},
        )

    def test_emprestimo_rejeita_membro_de_outra_organizacao(self):
        outra_organizacao = Organizacao.objects.create(nome="Biblioteca de outro membro")
        outro_membro = Membro.objects.create(
            organizacao=outra_organizacao,
            nome="Pessoa",
            sobrenome="Externa",
            cpf="12345678999",
            email="externa@example.com",
        )

        response = self.client.post(
            reverse("novo_emprestimo"),
            {
                "exemplar": self.exemplar.pk,
                "membro": outro_membro.pk,
                "data_emprestimo": "2026-02-01",
                "data_devolucao_prevista": "2026-02-08",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Emprestimo.objects.exists())

    def test_entrar_por_convite_troca_organizacao_ativa(self):
        outra_organizacao = Organizacao.objects.create(nome="Biblioteca convidada")

        response = self.client.post(
            reverse("organizacoes"),
            {
                "acao": "entrar",
                "codigo_convite": str(outra_organizacao.codigo_convite),
            },
        )
        painel = self.client.get(reverse("painel"))

        self.assertRedirects(response, reverse("organizacoes"))
        self.assertTrue(
            OrganizacaoUsuario.objects.filter(
                organizacao=outra_organizacao,
                usuario=self.usuario,
                papel="membro",
            ).exists()
        )
        self.assertEqual(painel.context["total_livros"], 0)

    def test_usuario_cria_organizacao_e_alterna_contexto(self):
        response = self.client.post(
            reverse("organizacoes"),
            {"acao": "criar", "nome": "Biblioteca nova"},
        )
        nova_organizacao = Organizacao.objects.get(nome="Biblioteca nova")
        painel_novo = self.client.get(reverse("painel"))

        self.assertRedirects(response, reverse("organizacoes"))
        self.assertTrue(
            OrganizacaoUsuario.objects.filter(
                organizacao=nova_organizacao,
                usuario=self.usuario,
                papel="admin",
            ).exists()
        )
        self.assertEqual(painel_novo.context["total_livros"], 0)

        self.client.post(
            reverse("organizacoes"),
            {"acao": "trocar", "organizacao_id": self.organizacao.pk},
        )
        painel_original = self.client.get(reverse("painel"))
        self.assertEqual(painel_original.context["total_livros"], 1)

    def test_codigo_de_convite_inexistente_mostra_erro(self):
        response = self.client.post(
            reverse("organizacoes"),
            {
                "acao": "entrar",
                "codigo_convite": "00000000-0000-0000-0000-000000000000",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Código de convite não encontrado.")

    def test_isbn_pode_repetir_em_outra_organizacao(self):
        outra_organizacao = Organizacao.objects.create(nome="Biblioteca ISBN")
        outro_autor = Autor.objects.create(
            organizacao=outra_organizacao,
            nome="Outro",
            sobrenome="Autor",
        )

        outro_livro = Livro.objects.create(
            organizacao=outra_organizacao,
            titulo="Mesmo ISBN, outro acervo",
            tipo="outro",
            autor=outro_autor,
            ano=2026,
            isbn=self.livro.isbn,
        )

        self.assertNotEqual(outro_livro.organizacao, self.livro.organizacao)
        self.assertEqual(outro_livro.isbn, self.livro.isbn)

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
            {
                "username": "nova_leitora",
                "password1": "Senha-segura-456",
                "password2": "Senha-segura-456",
                "nome_organizacao": "Biblioteca da nova leitora",
            },
        )
        self.assertRedirects(response, reverse("painel"))
        self.assertTrue(get_user_model().objects.filter(username="nova_leitora").exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTrue(
            OrganizacaoUsuario.objects.filter(
                usuario__username="nova_leitora",
                organizacao__nome="Biblioteca da nova leitora",
                papel="admin",
            ).exists()
        )

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
