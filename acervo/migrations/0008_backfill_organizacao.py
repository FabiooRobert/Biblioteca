from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def atribuir_organizacao_padrao(apps, schema_editor):
    banco = schema_editor.connection.alias
    Organizacao = apps.get_model("acervo", "Organizacao")
    OrganizacaoUsuario = apps.get_model("acervo", "OrganizacaoUsuario")
    Usuario = apps.get_model(*settings.AUTH_USER_MODEL.split("."))

    organizacao, _ = Organizacao.objects.using(banco).get_or_create(nome="Biblioteca Principal")

    for nome_modelo in ("Autor", "Livro", "Exemplar", "Membro", "Emprestimo", "Reserva"):
        Modelo = apps.get_model("acervo", nome_modelo)
        Modelo.objects.using(banco).filter(organizacao__isnull=True).update(organizacao_id=organizacao.pk)

    for usuario in Usuario.objects.using(banco).all().iterator():
        papel = "admin" if usuario.is_superuser else "membro"
        OrganizacaoUsuario.objects.using(banco).get_or_create(
            organizacao_id=organizacao.pk,
            usuario_id=usuario.pk,
            defaults={"papel": papel},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("acervo", "0007_organizacao_organizacaousuario_alter_exemplar_codigo_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(atribuir_organizacao_padrao, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="autor",
            name="organizacao",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="autores", to="acervo.organizacao"),
        ),
        migrations.AlterField(
            model_name="livro",
            name="organizacao",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="livros", to="acervo.organizacao"),
        ),
        migrations.AlterField(
            model_name="exemplar",
            name="organizacao",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="exemplares", to="acervo.organizacao"),
        ),
        migrations.AlterField(
            model_name="membro",
            name="organizacao",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="membros", to="acervo.organizacao"),
        ),
        migrations.AlterField(
            model_name="emprestimo",
            name="organizacao",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="emprestimos", to="acervo.organizacao"),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="organizacao",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reservas", to="acervo.organizacao"),
        ),
    ]