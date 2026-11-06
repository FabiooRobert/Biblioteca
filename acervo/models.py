from django.db import models
from django.utils import timezone

from core.models import DaOrganizacao


class Autor(DaOrganizacao):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=150)

    class Meta:
        ordering = ["sobrenome", "nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["organizacao", "nome", "sobrenome"],
                name="autor_nome_unico_por_org",
            )
        ]

    def __str__(self):
        return f"{self.nome} {self.sobrenome}".strip()


class Livro(DaOrganizacao):
    TIPOS_ACERVO = [
        ("REVISTA", "Revista"),
        ("JORNAL", "Jornal"),
        ("TCC", "TCC / Trabalho Acadêmico"),
        ("OUTRO", "Outro"),
    ]

    CATEGORIAS_ACERVO = [
        ("000", "Generalidades e Informação"),
        ("100", "Filosofia e Psicologia"),
        ("200", "Religião e Teologia"),
        ("300", "Ciências Sociais e Direito"),
        ("400", "Linguística e Idiomas"),
        ("500", "Ciências Puras"),
        ("600", "Ciências Aplicadas"),
        ("700", "Artes e Recreação"),
        ("800", "Literatura"),
        ("900", "História e Geografia"),
    ]

    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT, related_name="livros")
    ano = models.IntegerField()
    isbn = models.CharField(max_length=30, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_ACERVO, default="OUTRO")
    categoria = models.CharField(
        max_length=3,
        choices=CATEGORIAS_ACERVO,
        default="000",
    )
    disponivel = models.BooleanField(default=True)
    cadastrado_em = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organizacao", "isbn"],
                condition=~models.Q(isbn=""),
                name="livro_isbn_unico_por_org",
            )
        ]

    def __str__(self):
        return self.titulo


class Exemplar(DaOrganizacao):
    STATUS_CHOICES = [
        ("disponivel", "Disponível"),
        ("emprestado", "Emprestado"),
        ("reservado", "Reservado"),
        ("manutencao", "Em manutenção"),
    ]

    livro = models.ForeignKey(Livro, on_delete=models.PROTECT, related_name="exemplares")
    codigo = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="disponivel")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organizacao", "codigo"],
                name="exemplar_codigo_unico_por_org",
            )
        ]

    def __str__(self):
        return f"{self.livro.titulo} - {self.codigo}"


class Membro(DaOrganizacao):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=11)
    email = models.EmailField()
    ativo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organizacao", "cpf"],
                name="membro_cpf_unico_por_org",
            ),
            models.UniqueConstraint(
                fields=["organizacao", "email"],
                name="membro_email_unico_por_org",
            ),
        ]

    def __str__(self):
        return f"{self.nome} {self.sobrenome}".strip()


class Emprestimo(DaOrganizacao):
    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("devolvido", "Devolvido"),
        ("atrasado", "Atrasado"),
    ]

    exemplar = models.ForeignKey(
        Exemplar, on_delete=models.PROTECT, related_name="emprestimos"
    )
    membro = models.ForeignKey(
        Membro, on_delete=models.PROTECT, related_name="emprestimos"
    )
    data_emprestimo = models.DateField()
    data_devolucao_prevista = models.DateField()
    data_devolucao_real = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ativo")

    def dias_atraso(self):
        data_final = self.data_devolucao_real or timezone.localdate()
        return max((data_final - self.data_devolucao_prevista).days, 0)

    def calcular_multa(self, valor_por_dia=2.50):
        return round(self.dias_atraso() * valor_por_dia, 2)

    def __str__(self):
        return f"{self.exemplar} - {self.membro}"


class Reserva(DaOrganizacao):
    STATUS_CHOICES = [
        ("ativa", "Ativa"),
        ("cancelada", "Cancelada"),
        ("atendida", "Atendida"),
    ]

    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name="reservas")
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name="reservas")
    data_reserva = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ativa")

    class Meta:
        ordering = ["data_reserva", "id"]

    def posicao_na_fila(self):
        fila = Reserva.objects.filter(
            livro=self.livro,
            organizacao=self.organizacao,
            status="ativa",
        ).order_by("data_reserva", "id")
        for indice, reserva in enumerate(fila, start=1):
            if reserva.pk == self.pk:
                return indice
        return 0

    def __str__(self):
        return f"{self.membro} reservou {self.livro}"
