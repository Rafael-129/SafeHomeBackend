from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_incidentes'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='scanner',
            name='chk_persona',
        ),
        migrations.RemoveConstraint(
            model_name='historialaccesos',
            name='chk_acceso_persona',
        ),
        migrations.AlterField(
            model_name='scanner',
            name='tipo_persona',
            field=models.CharField(
                choices=[
                    ('residente', 'Residente'),
                    ('visitante', 'Visitante'),
                    ('desconocido', 'Desconocido'),
                ],
                max_length=20,
            ),
        ),
        migrations.AddConstraint(
            model_name='scanner',
            constraint=models.CheckConstraint(
                check=models.Q(idusuario__isnull=True) | models.Q(idvisitante__isnull=True),
                name='chk_persona',
            ),
        ),
        migrations.AddConstraint(
            model_name='historialaccesos',
            constraint=models.CheckConstraint(
                check=models.Q(idusuario__isnull=True) | models.Q(idvisitante__isnull=True),
                name='chk_acceso_persona',
            ),
        ),
    ]
