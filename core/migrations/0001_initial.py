from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Organizacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Perfil",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("organizacao", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.organizacao")),
                ("usuario", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="perfil", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]