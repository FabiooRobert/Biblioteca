from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("acervo", "0003_livro_categoria"),
    ]

    operations = [
        migrations.AddField(
            model_name="livro",
            name="tipo",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]