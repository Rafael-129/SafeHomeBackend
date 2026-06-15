"""Politica de retencion de datos: purga de fotos de visitantes.

Por proteccion de datos (Ley 29733), las fotos de visitantes solo se conservan
un tiempo limitado. Pasado ese plazo se borran tanto la foto del registro del
visitante como las capturas del scanner asociadas a visitantes. El registro de
texto del acceso (historial) se mantiene.
"""

from datetime import date, timedelta

from .models import Scanner, Visitante

RETENCION_DIAS_DEFAULT = 30


def purgar_fotos_vencidas(dias=RETENCION_DIAS_DEFAULT):
    """Borra las fotos de visitantes con fecha de visita anterior a `dias`.

    Devuelve un resumen con la cantidad de filas afectadas.
    """
    dias = int(dias)
    cutoff = date.today() - timedelta(days=dias)

    visitantes = (
        Visitante.objects
        .filter(fecha_visita__lt=cutoff)
        .exclude(foto__isnull=True)
        .update(foto=None)
    )

    capturas = (
        Scanner.objects
        .filter(idvisitante__isnull=False, fecha__date__lt=cutoff)
        .exclude(foto_capturada__isnull=True)
        .update(foto_capturada=None)
    )

    return {
        'visitantes': visitantes,
        'capturas': capturas,
        'dias': dias,
        'cutoff': cutoff.isoformat(),
    }
