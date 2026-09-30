from django.db import models
from django.utils import timezone


class Autor(models.Model):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=150)

    class Meta:
        ordering = ["sobrenome", "nome"]

    def __str__(self):
        return f"{self.nome} {self.sobrenome}".strip()


class Livro(models.Model):
    TIPO_CHOICES = [
        ("revista", "Revista"),
        ("jornal", "Jornal"),
        ("tcc", "TCC / Trabalho Acadêmico"),
        ("outro", "Outro"),
    ]

    CATEGORIA_CHOICES = [
        ("000", "Generalidades e Informação: Obras gerais, enciclopédias, jornais e biblioteconomia."),
        ("100", "Filosofia e Psicologia: Ética, lógica e investigações sobre a mente humana."),
        ("200", "Religião e Teologia: Mitologia, teologia e estudos sobre crenças e religiões."),
        ("300", "Ciências Sociais e Direito: Política, economia, sociologia, educação e leis."),
        ("400", "Linguística e Idiomas: Gramáticas, dicionários e estudos de línguas."),
        ("500", "Ciências Puras (Exatas e Naturais): Matemática, física, química, biologia e astronomia."),
        ("600", "Ciências Aplicadas (Tecnologia): Medicina, engenharia, agricultura e administração."),
        ("700", "Artes e Recreação: Pintura, música, arquitetura, esportes e lazer."),
        ("800", "Literatura: Poesia, romances, contos, crônicas e crítica literária."),
        ("900", "História e Geografia: Biografias, viagens e acontecimentos históricos."),
    ]

    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="outro")
    autor = models.ForeignKey("Autor", on_delete=models.PROTECT, related_name="livros")
    ano = models.IntegerField()
    isbn = models.CharField(max_length=30, unique=True, blank=True)
    categoria = models.CharField(
        max_length=3,
        choices=CATEGORIA_CHOICES,
        default="000",
        help_text="Classificação do acervo de acordo com a tabela de categorias.",
    )

    def __str__(self):
        return self.titulo


class Exemplar(models.Model):
    STATUS_CHOICES = [
        ("disponivel", "Disponível"),
        ("emprestado", "Emprestado"),
        ("reservado", "Reservado"),
        ("manutencao", "Em manutenção"),
    ]

    livro = models.ForeignKey("Livro", on_delete=models.PROTECT, related_name="exemplares")
    codigo = models.CharField(max_length=30, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="disponivel")

    def __str__(self):
        return f"{self.livro.titulo} - {self.codigo}"


class Membro(models.Model):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} {self.sobrenome}".strip()


class Emprestimo(models.Model):
    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("devolvido", "Devolvido"),
        ("atrasado", "Atrasado"),
    ]

    exemplar = models.ForeignKey("Exemplar", on_delete=models.PROTECT, related_name="emprestimos")
    membro = models.ForeignKey("Membro", on_delete=models.PROTECT, related_name="emprestimos")
    data_emprestimo = models.DateField()
    data_devolucao_prevista = models.DateField()
    data_devolucao_real = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ativo")

    def dias_atraso(self):
        data_final = self.data_devolucao_real or timezone.localdate()
        return max((data_final - self.data_devolucao_prevista).days, 0)

    def calcular_multa(self, valor_por_dia=2.00):
        return round(self.dias_atraso() * valor_por_dia, 2)

    def __str__(self):
        return f"{self.exemplar} - {self.membro}"


class Reserva(models.Model):
    STATUS_CHOICES = [
        ("ativa", "Ativa"),
        ("cancelada", "Cancelada"),
        ("atendida", "Atendida"),
    ]

    livro = models.ForeignKey("Livro", on_delete=models.CASCADE, related_name="reservas")
    membro = models.ForeignKey("Membro", on_delete=models.CASCADE, related_name="reservas")
    data_reserva = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ativa")

    class Meta:
        ordering = ["data_reserva", "id"]

    def posicao_na_fila(self):
        fila = Reserva.objects.filter(livro=self.livro, status="ativa").order_by("data_reserva", "id")
        for indice, reserva in enumerate(fila, start=1):
            if reserva.pk == self.pk:
                return indice
        return 0

    def __str__(self):
        return f"{self.membro} reservou {self.livro}"
