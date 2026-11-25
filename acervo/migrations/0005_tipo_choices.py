from django.db import migrations, models


def normalize_tipo(apps, schema_editor):
    Livro = apps.get_model("acervo", "Livro")
    tipos_validos = {"revista", "jornal", "tcc", "outro"}
    equivalencias = {
        "revista": "revista",
        "jornal": "jornal",
        "tcc": "tcc",
        "tcc / trabalho acadêmico": "tcc",
        "tcc/trabalho acadêmico": "tcc",
        "trabalho acadêmico": "tcc",
        "outro": "outro",
    }

    for livro in Livro.objects.all().only("pk", "tipo").iterator():
        tipo_normalizado = equivalencias.get((livro.tipo or "").strip().casefold(), "outro")
        if tipo_normalizado in tipos_validos and livro.tipo != tipo_normalizado:
            Livro.objects.filter(pk=livro.pk).update(tipo=tipo_normalizado)


class Migration(migrations.Migration):

    dependencies = [
        ("acervo", "0004_livro_tipo"),
    ]

    operations = [
        migrations.RunPython(normalize_tipo, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="livro",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("revista", "Revista"),
                    ("jornal", "Jornal"),
                    ("tcc", "TCC / Trabalho Acadêmico"),
                    ("outro", "Outro"),
                ],
                default="outro",
                max_length=10,
            ),
        ),
    ]