from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_permitir_desconocido'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitante',
            name='acepta_terminos',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='visitante',
            name='fecha_aceptacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
