from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Organizacao, Perfil
from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva


class LivroCrudTests(TestCase):
    def setUp(self):
        self.organizacao = Organizacao.objects.create(nome="Biblioteca A")
        self.autor = Autor.objects.create(
            nome="Maria",
            sobrenome="Silva",
            organizacao=self.organizacao,
        )
        self.usuario = get_user_model().objects.create_user(
            username="usuario-a", password="senha-teste"
        )
        Perfil.objects.create(
            usuario=self.usuario,
            organizacao=self.organizacao,
            papel="admin",
        )
        self.client.login(username="usuario-a", password="senha-teste")
        self.livro = Livro.objects.create(
            titulo="Django para Iniciantes",
            autor=self.autor,
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
                "autor": self.autor.pk,
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
                "autor": self.autor.pk,
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
        outro_autor = Autor.objects.create(
            nome="Outro",
            sobrenome="Autor",
            organizacao=outra_org,
        )
        Livro.objects.create(
            titulo="Livro da outra biblioteca",
            autor=outro_autor,
            ano=2025,
            organizacao=outra_org,
        )

        response = self.client.get(reverse("lista"))

        self.assertContains(response, "Django para Iniciantes")
        self.assertNotContains(response, "Livro da outra biblioteca")

    def test_usuario_nao_edita_livro_de_outra_organizacao(self):
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        outro_autor = Autor.objects.create(
            nome="Outro",
            sobrenome="Autor",
            organizacao=outra_org,
        )
        livro = Livro.objects.create(
            titulo="Livro da outra biblioteca",
            autor=outro_autor,
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
                "autor": self.autor.pk,
                "ano": 2025,
                "tipo": "OUTRO",
                "categoria": "000",
                "disponivel": True,
            },
        )

        self.assertEqual(response.status_code, 302)
        livro = Livro.objects.get(titulo="Livro da Biblioteca A")
        self.assertEqual(livro.organizacao, self.organizacao)

    def test_formulario_nao_aceita_autor_de_outra_organizacao(self):
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        outro_autor = Autor.objects.create(
            nome="Outro",
            sobrenome="Autor",
            organizacao=outra_org,
        )

        response = self.client.post(
            reverse("novo"),
            {
                "titulo": "Livro inválido",
                "autor": outro_autor.pk,
                "ano": 2025,
                "tipo": "OUTRO",
                "categoria": "000",
                "disponivel": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Livro.objects.filter(titulo="Livro inválido").exists())


class LivroApiTests(TestCase):
    def setUp(self):
        self.organizacao = Organizacao.objects.create(nome="Biblioteca A")
        self.autor = Autor.objects.create(
            nome="Autor",
            sobrenome="A",
            organizacao=self.organizacao,
        )
        usuario = get_user_model().objects.create_user(
            username="api-a", password="senha-teste"
        )
        Perfil.objects.create(
            usuario=usuario,
            organizacao=self.organizacao,
            papel="admin",
        )
        self.client.login(username="api-a", password="senha-teste")
        self.url = "/api/livros/"

    def test_api_lista_apenas_livros_da_organizacao(self):
        Livro.objects.create(
            titulo="Livro A", autor=self.autor, ano=2025,
            organizacao=self.organizacao,
        )
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        outro_autor = Autor.objects.create(
            nome="Autor",
            sobrenome="B",
            organizacao=outra_org,
        )
        Livro.objects.create(
            titulo="Livro B", autor=outro_autor, ano=2025,
            organizacao=outra_org,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["titulo"] for item in response.json()], ["Livro A"])

    def test_api_nao_revela_livro_de_outra_organizacao(self):
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        outro_autor = Autor.objects.create(
            nome="Autor",
            sobrenome="B",
            organizacao=outra_org,
        )
        livro = Livro.objects.create(
            titulo="Livro B",
            autor=outro_autor,
            ano=2025,
            organizacao=outra_org,
        )

        response = self.client.get(f"{self.url}{livro.pk}/")

        self.assertEqual(response.status_code, 404)

    def test_api_exige_autenticacao(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertIn(response.status_code, (401, 403))

    def test_api_exige_perfil_organizacional(self):
        usuario_sem_perfil = get_user_model().objects.create_user(
            username="sem-perfil-api",
        )
        self.client.force_login(usuario_sem_perfil)

        response = self.client.get("/api/autores/")

        self.assertEqual(response.status_code, 403)

    def test_api_cria_livro_na_organizacao_do_usuario(self):
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        response = self.client.post(
            self.url,
            {
                "titulo": "Livro criado pela API",
                "autor": self.autor.pk,
                "ano": 2025,
                "tipo": "OUTRO",
                "categoria": "000",
                "disponivel": True,
                "organizacao": outra_org.pk,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        livro = Livro.objects.get(titulo="Livro criado pela API")
        self.assertEqual(livro.organizacao, self.organizacao)
        self.assertNotIn("organizacao", response.json())

    def test_operador_pode_consultar_mas_nao_criar_pela_api(self):
        operador = get_user_model().objects.create_user(
            username="operador", password="senha-teste"
        )
        Perfil.objects.create(
            usuario=operador,
            organizacao=self.organizacao,
            papel="operador",
        )
        self.client.force_login(operador)

        leitura = self.client.get(self.url)
        escrita = self.client.post(
            self.url,
            {"titulo": "Negado", "autor": "Autor", "ano": 2025},
            content_type="application/json",
        )

        self.assertEqual(leitura.status_code, 200)
        self.assertEqual(escrita.status_code, 403)

    def test_api_isola_e_executa_crud_de_todos_os_recursos(self):
        outra_org = Organizacao.objects.create(nome="Biblioteca B")

        def criar_recursos(organizacao, sufixo):
            autor = Autor.objects.create(
                nome="Pessoa",
                sobrenome=sufixo,
                organizacao=organizacao,
            )
            livro = Livro.objects.create(
                titulo=f"Livro {sufixo}",
                autor=autor,
                ano=2025,
                organizacao=organizacao,
            )
            exemplar = Exemplar.objects.create(
                livro=livro,
                codigo=f"EX-{sufixo}",
                organizacao=organizacao,
            )
            membro = Membro.objects.create(
                nome="Membro",
                sobrenome=sufixo,
                cpf=f"1234567890{1 if sufixo == 'A' else 2}",
                email=f"{sufixo.lower()}@example.com",
                organizacao=organizacao,
            )
            emprestimo = Emprestimo.objects.create(
                exemplar=exemplar,
                membro=membro,
                data_emprestimo="2026-01-01",
                data_devolucao_prevista="2026-01-10",
                organizacao=organizacao,
            )
            reserva = Reserva.objects.create(
                livro=livro,
                membro=membro,
                data_reserva="2026-01-02",
                organizacao=organizacao,
            )
            return {
                "autores": autor,
                "livros": livro,
                "exemplares": exemplar,
                "membros": membro,
                "emprestimos": emprestimo,
                "reservas": reserva,
            }

        meus_recursos = criar_recursos(self.organizacao, "A")
        recursos_alheios = criar_recursos(outra_org, "B")

        for recurso, meu_objeto in meus_recursos.items():
            with self.subTest(recurso=recurso):
                lista = self.client.get(f"/api/{recurso}/")
                detalhe_alheio = self.client.get(
                    f"/api/{recurso}/{recursos_alheios[recurso].pk}/"
                )

                self.assertEqual(lista.status_code, 200)
                expected_ids = [meu_objeto.pk]
                if recurso == "autores":
                    expected_ids.append(self.autor.pk)
                self.assertCountEqual(
                    [item["id"] for item in lista.json()],
                    expected_ids,
                )
                self.assertEqual(detalhe_alheio.status_code, 404)

        atualizacoes = {
            "autores": {"sobrenome": "Atualizado"},
            "livros": {"titulo": "Livro atualizado"},
            "exemplares": {"status": "manutencao"},
            "membros": {"ativo": False},
            "emprestimos": {"status": "devolvido"},
            "reservas": {"status": "cancelada"},
        }
        for recurso, meu_objeto in meus_recursos.items():
            with self.subTest(atualizacao=recurso):
                resposta = self.client.patch(
                    f"/api/{recurso}/{meu_objeto.pk}/",
                    atualizacoes[recurso],
                    content_type="application/json",
                )
                self.assertEqual(resposta.status_code, 200)

        for recurso in (
            "emprestimos",
            "reservas",
            "exemplares",
            "livros",
            "membros",
            "autores",
        ):
            with self.subTest(exclusao=recurso):
                resposta = self.client.delete(
                    f"/api/{recurso}/{meus_recursos[recurso].pk}/"
                )
                self.assertEqual(resposta.status_code, 204)

    def test_api_cria_recursos_na_organizacao_autenticada(self):
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        autor_response = self.client.post(
            "/api/autores/",
            {
                "nome": "Nova",
                "sobrenome": "Autora",
                "organizacao": outra_org.pk,
            },
            content_type="application/json",
        )
        self.assertEqual(autor_response.status_code, 201)
        autor = Autor.objects.get(pk=autor_response.json()["id"])
        self.assertEqual(autor.organizacao, self.organizacao)

        livro_response = self.client.post(
            self.url,
            {
                "titulo": "Novo livro",
                "autor": autor.pk,
                "ano": 2025,
                "isbn": "9780000000001",
                "organizacao": outra_org.pk,
            },
            content_type="application/json",
        )
        self.assertEqual(livro_response.status_code, 201)
        livro = Livro.objects.get(pk=livro_response.json()["id"])

        exemplar_response = self.client.post(
            "/api/exemplares/",
            {"livro": livro.pk, "codigo": "EX-NOVO"},
            content_type="application/json",
        )
        membro_response = self.client.post(
            "/api/membros/",
            {
                "nome": "Ana",
                "sobrenome": "Silva",
                "cpf": "12345678910",
                "email": "ana@example.com",
                "organizacao": outra_org.pk,
            },
            content_type="application/json",
        )
        self.assertEqual(exemplar_response.status_code, 201)
        self.assertEqual(membro_response.status_code, 201)
        exemplar = Exemplar.objects.get(pk=exemplar_response.json()["id"])
        membro = Membro.objects.get(pk=membro_response.json()["id"])

        emprestimo_response = self.client.post(
            "/api/emprestimos/",
            {
                "exemplar": exemplar.pk,
                "membro": membro.pk,
                "data_emprestimo": "2026-01-01",
                "data_devolucao_prevista": "2026-01-10",
            },
            content_type="application/json",
        )
        reserva_response = self.client.post(
            "/api/reservas/",
            {
                "livro": livro.pk,
                "membro": membro.pk,
                "data_reserva": "2026-01-02",
            },
            content_type="application/json",
        )
        self.assertEqual(emprestimo_response.status_code, 201)
        self.assertEqual(reserva_response.status_code, 201)

        for recurso in (livro, exemplar, membro):
            self.assertEqual(recurso.organizacao, self.organizacao)
        self.assertEqual(
            Emprestimo.objects.get(pk=emprestimo_response.json()["id"]).organizacao,
            self.organizacao,
        )
        self.assertEqual(
            Reserva.objects.get(pk=reserva_response.json()["id"]).organizacao,
            self.organizacao,
        )

    def test_api_rejeita_relacionamentos_de_outra_organizacao(self):
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        autor_alheio = Autor.objects.create(
            nome="Autor",
            sobrenome="B",
            organizacao=outra_org,
        )
        livro_alheio = Livro.objects.create(
            titulo="Livro B",
            autor=autor_alheio,
            ano=2025,
            organizacao=outra_org,
        )

        resposta = self.client.post(
            "/api/exemplares/",
            {"livro": livro_alheio.pk, "codigo": "EX-NEGADO"},
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertFalse(Exemplar.objects.filter(codigo="EX-NEGADO").exists())
        resposta_livro = self.client.post(
            self.url,
            {
                "titulo": "Livro inválido",
                "autor": autor_alheio.pk,
                "ano": 2025,
            },
            content_type="application/json",
        )
        self.assertEqual(resposta_livro.status_code, 400)

        membro = Membro.objects.create(
            nome="Membro",
            sobrenome="B",
            cpf="12345678902",
            email="membro-b@example.com",
            organizacao=outra_org,
        )
        exemplar = Exemplar.objects.create(
            livro=livro_alheio,
            codigo="EX-B",
            organizacao=outra_org,
        )
        resposta_emprestimo = self.client.post(
            "/api/emprestimos/",
            {
                "exemplar": exemplar.pk,
                "membro": membro.pk,
                "data_emprestimo": "2026-01-01",
                "data_devolucao_prevista": "2026-01-10",
            },
            content_type="application/json",
        )
        resposta_reserva = self.client.post(
            "/api/reservas/",
            {
                "livro": livro_alheio.pk,
                "membro": membro.pk,
                "data_reserva": "2026-01-02",
            },
            content_type="application/json",
        )

        self.assertEqual(resposta_emprestimo.status_code, 400)
        self.assertEqual(resposta_reserva.status_code, 400)

    def test_api_de_emprestimo_expoe_multa_e_atraso_calculados(self):
        exemplar = Exemplar.objects.create(
            livro=Livro.objects.create(
                titulo="Livro atrasado",
                autor=self.autor,
                ano=2025,
                organizacao=self.organizacao,
            ),
            codigo="EX-ATRASADO",
            organizacao=self.organizacao,
        )
        membro = Membro.objects.create(
            nome="Ana",
            sobrenome="Silva",
            cpf="12345678910",
            email="ana-atraso@example.com",
            organizacao=self.organizacao,
        )
        emprestimo = Emprestimo.objects.create(
            exemplar=exemplar,
            membro=membro,
            data_emprestimo=date(2026, 1, 1),
            data_devolucao_prevista=date(2026, 1, 10),
            data_devolucao_real=date(2026, 1, 15),
            status="devolvido",
            organizacao=self.organizacao,
        )

        resposta = self.client.get(f"/api/emprestimos/{emprestimo.pk}/")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["dias_atraso"], 5)
        self.assertEqual(resposta.json()["multa"], 12.5)

    def test_operador_nao_pode_escrever_em_nenhum_recurso_da_api(self):
        operador = get_user_model().objects.create_user(
            username="operador-api",
        )
        Perfil.objects.create(
            usuario=operador,
            organizacao=self.organizacao,
            papel="operador",
        )
        self.client.force_login(operador)

        for recurso in (
            "autores",
            "livros",
            "exemplares",
            "membros",
            "emprestimos",
            "reservas",
        ):
            with self.subTest(recurso=recurso):
                resposta = self.client.post(
                    f"/api/{recurso}/",
                    {},
                    content_type="application/json",
                )
                self.assertEqual(resposta.status_code, 403)


class DashboardTests(TestCase):
    def setUp(self):
        self.organizacao = Organizacao.objects.create(nome="Biblioteca A")
        self.autor = Autor.objects.create(
            nome="Autora",
            sobrenome="A",
            organizacao=self.organizacao,
        )
        usuario = get_user_model().objects.create_user(
            username="operador-painel", password="senha-teste"
        )
        Perfil.objects.create(
            usuario=usuario,
            organizacao=self.organizacao,
            papel="operador",
        )
        self.client.login(username="operador-painel", password="senha-teste")

    def test_dashboard_agrega_apenas_a_organizacao_e_aplica_periodo(self):
        Livro.objects.create(
            titulo="Livro atual",
            autor=self.autor,
            ano=2025,
            disponivel=True,
            organizacao=self.organizacao,
        )
        antigo = Livro.objects.create(
            titulo="Livro antigo",
            autor=self.autor,
            ano=2000,
            disponivel=False,
            organizacao=self.organizacao,
        )
        Livro.objects.filter(pk=antigo.pk).update(
            cadastrado_em=timezone.now() - timedelta(days=60)
        )
        outra_org = Organizacao.objects.create(nome="Biblioteca B")
        outro_autor = Autor.objects.create(
            nome="Outro",
            sobrenome="Autor",
            organizacao=outra_org,
        )
        Livro.objects.create(
            titulo="Livro de outra organização",
            autor=outro_autor,
            ano=2025,
            organizacao=outra_org,
        )

        response = self.client.get(reverse("dashboard"), {"periodo": "30"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["resumo"]["total"], 1)
        self.assertEqual(response.context["resumo"]["disponiveis"], 1)
        self.assertEqual(
            response.context["autores"],
            [{"nome": "Autora A", "total": 1}],
        )

    def test_operador_nao_pode_criar_livro_pela_tela(self):
        response = self.client.post(
            reverse("novo"),
            {"titulo": "Negado", "autor": "Autor", "ano": 2025},
        )

        self.assertEqual(response.status_code, 403)


class BibliotecaBusinessRulesTests(TestCase):
    def test_calcula_multa_de_emprestimo_atrasado(self):
        organizacao = Organizacao.objects.create(nome="Biblioteca")
        autor = Autor.objects.create(
            nome="George",
            sobrenome="Orwell",
            organizacao=organizacao,
        )
        livro = Livro.objects.create(
            titulo="1984",
            autor=autor,
            ano=1949,
            organizacao=organizacao,
        )
        exemplar = Exemplar.objects.create(
            livro=livro,
            codigo="EX-001",
            organizacao=organizacao,
        )
        membro = Membro.objects.create(
            nome="Ana",
            sobrenome="Silva",
            cpf="12345678900",
            email="ana@example.com",
            organizacao=organizacao,
        )
        emprestimo = Emprestimo.objects.create(
            exemplar=exemplar,
            membro=membro,
            data_emprestimo=date(2026, 1, 1),
            data_devolucao_prevista=date(2026, 1, 10),
            data_devolucao_real=date(2026, 1, 15),
            status="devolvido",
            organizacao=organizacao,
        )

        self.assertEqual(emprestimo.dias_atraso(), 5)
        self.assertEqual(emprestimo.calcular_multa(), 12.5)

    def test_reserva_calcula_posicao_somente_na_fila_ativa_do_livro(self):
        organizacao = Organizacao.objects.create(nome="Biblioteca")
        autor = Autor.objects.create(
            nome="George",
            sobrenome="Orwell",
            organizacao=organizacao,
        )
        livro = Livro.objects.create(
            titulo="1984",
            autor=autor,
            ano=1949,
            organizacao=organizacao,
        )
        membro_1 = Membro.objects.create(
            nome="Ana",
            sobrenome="Silva",
            cpf="12345678900",
            email="ana@example.com",
            organizacao=organizacao,
        )
        membro_2 = Membro.objects.create(
            nome="Bruno",
            sobrenome="Costa",
            cpf="12345678901",
            email="bruno@example.com",
            organizacao=organizacao,
        )
        reserva_1 = Reserva.objects.create(
            livro=livro,
            membro=membro_1,
            data_reserva=date(2026, 2, 1),
            organizacao=organizacao,
        )
        reserva_2 = Reserva.objects.create(
            livro=livro,
            membro=membro_2,
            data_reserva=date(2026, 2, 2),
            organizacao=organizacao,
        )
        Reserva.objects.create(
            livro=livro,
            membro=membro_2,
            data_reserva=date(2026, 2, 3),
            status="cancelada",
            organizacao=organizacao,
        )

        self.assertEqual(reserva_1.posicao_na_fila(), 1)
        self.assertEqual(reserva_2.posicao_na_fila(), 2)
