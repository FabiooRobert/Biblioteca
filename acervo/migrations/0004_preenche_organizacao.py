from django.db import migrations, models
import django.db.models.deletion


def atribuir_organizacao_padrao(apps, schema_editor):
    Organizacao = apps.get_model("core", "Organizacao")
    Livro = apps.get_model("acervo", "Livro")
    banco = schema_editor.connection.alias
    organizacao, _ = Organizacao.objects.using(banco).get_or_create(
        nome="Organização padrão"
    )
    Livro.objects.using(banco).filter(organizacao__isnull=True).update(
        organizacao=organizacao
    )


class Migration(migrations.Migration):
    dependencies = [
        ("acervo", "0003_livro_organizacao"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            atribuir_organizacao_padrao,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="livro",
            name="organizacao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="%(app_label)s_%(class)s_set",
                to="core.organizacao",
            ),
        ),
    ]