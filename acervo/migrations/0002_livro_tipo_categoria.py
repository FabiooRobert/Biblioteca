from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("acervo", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="livro",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("REVISTA", "Revista"),
                    ("JORNAL", "Jornal"),
                    ("TCC", "TCC / Trabalho Acadêmico"),
                    ("OUTRO", "Outro"),
                ],
                default="OUTRO",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="livro",
            name="categoria",
            field=models.CharField(
                choices=[
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
                ],
                default="000",
                max_length=3,
            ),
        ),
    ]
