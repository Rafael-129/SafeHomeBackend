from django.core.management.base import BaseCommand

from api import storage
from api.models import Scanner, Usuario, Visitante


class Command(BaseCommand):
    help = 'Migra las fotos base64 existentes (Supabase) a Azure Blob Storage. Idempotente.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra lo que haria sin subir ni modificar la BD.',
        )

    def _migrar(self, queryset, campo, tipo, dry_run):
        migradas = 0
        for obj in queryset.iterator():
            valor = getattr(obj, campo)
            if not valor or not storage.es_base64(valor):
                continue
            if dry_run:
                migradas += 1
                continue
            blob_name = storage.subir_foto(valor, tipo)
            if blob_name and blob_name != valor:
                setattr(obj, campo, blob_name)
                obj.save(update_fields=[campo])
                migradas += 1
        return migradas

     def _migrar_scanner(self, dry_run):
        """Capturas de desconocidos -> denegados; capturas de reconocidos -> se
        eliminan (ya no se usan en el modelo nuevo)."""
        migradas = 0
        eliminadas = 0
        qs = Scanner.objects.exclude(foto_capturada__isnull=True)
        for s in qs.iterator():
            if not s.foto_capturada or not storage.es_base64(s.foto_capturada):
                continue
            es_desconocido = s.idusuario_id is None and s.idvisitante_id is None
            if es_desconocido:
                if not dry_run:
                    s.foto_capturada = storage.subir_foto(s.foto_capturada, storage.DENEGADO)
                    s.save(update_fields=['foto_capturada'])
                migradas += 1
            else:
                if not dry_run:
                    s.foto_capturada = None
                    s.save(update_fields=['foto_capturada'])
                eliminadas += 1
        return migradas, eliminadas

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if not dry_run and not storage.configurado():
            self.stderr.write(self.style.ERROR(
                'Azure no esta configurado (falta AZURE_STORAGE_CONNECTION_STRING).'
            ))
            return

        r = self._migrar(Usuario.objects.all(), 'foto', storage.RESIDENTE, dry_run)
        v = self._migrar(Visitante.objects.all(), 'foto', storage.VISITANTE, dry_run)
        s = self._migrar(
            Scanner.objects.exclude(foto_capturada__isnull=True),
            'foto_capturada', storage.DENEGADO, dry_run,
        )

        prefijo = '[dry-run] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f"{prefijo}Migradas: {r} residentes, {v} visitantes, {s} capturas a Azure Blob."
        ))
