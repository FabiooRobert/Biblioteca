from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("acervo", "0005_tipo_choices"),
    ]

    operations = [
        migrations.AlterField(
            model_name="livro",
            name="categoria",
            field=models.CharField(
                choices=[
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
                ],
                default="000",
                help_text="Classificação do acervo de acordo com a tabela de categorias.",
                max_length=3,
            ),
        ),
    ]