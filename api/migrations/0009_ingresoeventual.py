import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_visitante_terminos'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngresoEventual',
            fields=[
                ('ideventual', models.AutoField(db_column='ideventual', primary_key=True, serialize=False)),
                ('dni', models.CharField(max_length=8)),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('motivo', models.CharField(blank=True, max_length=255, null=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('iddepartamento', models.ForeignKey(
                    db_column='iddepartamento',
                    on_delete=django.db.models.deletion.RESTRICT,
                    to='api.departamento',
                )),
            ],
            options={
                'verbose_name': 'Ingreso Eventual',
                'verbose_name_plural': 'Ingresos Eventuales',
                'db_table': 'ingresoeventual',
                'ordering': ['-fecha'],
            },
        ),
        migrations.AddField(
            model_name='historialaccesos',
            name='ideventual',
            field=models.ForeignKey(
                blank=True,
                db_column='ideventual',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='api.ingresoeventual',
            ),
        ),
    ]
