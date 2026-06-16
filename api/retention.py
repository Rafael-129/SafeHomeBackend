"""Politica de retencion de datos: purga de fotos de visitantes.

Por proteccion de datos (Ley 29733), las fotos de visitantes solo se conservan
un tiempo limitado. Pasado ese plazo se borran tanto la foto del registro del
visitante como las capturas del scanner asociadas a visitantes. El registro de
texto del acceso (historial) se mantiene.
"""

from datetime import date, timedelta

from . import storage
from .models import Scanner, Visitante

RETENCION_DIAS_DEFAULT = 30


def purgar_fotos_vencidas(dias=RETENCION_DIAS_DEFAULT):
    """Borra las fotos de visitantes/desconocidos con mas de `dias`.

    Elimina el blob en Azure (si aplica) y limpia el campo en la BD.
    Devuelve un resumen con la cantidad de filas afectadas.
    """
    dias = int(dias)
    cutoff = date.today() - timedelta(days=dias)

    visitantes = 0
    for v in Visitante.objects.filter(fecha_visita__lt=cutoff).exclude(foto__isnull=True):
        storage.borrar_foto(v.foto, storage.VISITANTE)
        v.foto = None
        v.save(update_fields=['foto'])
        visitantes += 1

    capturas = 0
    desconocidos = (
        Scanner.objects
        .filter(idusuario__isnull=True, idvisitante__isnull=True, fecha__date__lt=cutoff)
        .exclude(foto_capturada__isnull=True)
    )
    for s in desconocidos:
        storage.borrar_foto(s.foto_capturada, storage.DENEGADO)
        s.foto_capturada = None
        s.save(update_fields=['foto_capturada'])
        capturas += 1

    return {
        'visitantes': visitantes,
        'capturas': capturas,
        'dias': dias,
        'cutoff': cutoff.isoformat(),
    }
