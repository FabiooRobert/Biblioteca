from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("acervo", "0002_livro_tipo_categoria"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="livro",
            name="organizacao",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="%(app_label)s_%(class)s_set",
                to="core.organizacao",
            ),
        ),
    ]