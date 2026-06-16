from django.core.management.base import BaseCommand

from api.retention import RETENCION_DIAS_DEFAULT, purgar_fotos_vencidas


class Command(BaseCommand):
    help = 'Borra las fotos de visitantes con mas de N dias (politica de retencion).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=RETENCION_DIAS_DEFAULT,
            help=f'Dias de retencion (por defecto {RETENCION_DIAS_DEFAULT}).',
        )

    def handle(self, *args, **options):
        dias = options['dias']
        resultado = purgar_fotos_vencidas(dias)
        self.stdout.write(self.style.SUCCESS(
            f"Purga completa (>{resultado['dias']} dias, corte {resultado['cutoff']}): "
            f"{resultado['visitantes']} fotos de visitante y "
            f"{resultado['capturas']} capturas de scanner eliminadas."
        ))
