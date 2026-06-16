"""Almacenamiento de fotos en Azure Blob Storage.

Las fotos ya no se guardan como base64 en la BD (eso disparaba el egress de
Supabase). En su lugar se suben a containers privados de Azure y en la BD solo
queda el nombre del blob. Al leer, se genera una URL SAS temporal de lectura.

Si no hay connection string configurada (entorno de desarrollo sin Azure), las
funciones hacen passthrough para no romper el flujo local.
"""

import base64
import binascii
import datetime as dt
import os
import uuid

try:
    from azure.storage.blob import (
        BlobServiceClient,
        BlobSasPermissions,
        ContentSettings,
        generate_blob_sas,
    )
except Exception:  # azure-storage-blob no instalado todavia
    BlobServiceClient = None
    BlobSasPermissions = None
    ContentSettings = None
    generate_blob_sas = None


# Tipos de foto -> container
RESIDENTE = 'residente'
VISITANTE = 'visitante'
DENEGADO = 'denegado'

_CONTAINER_ENV = {
    RESIDENTE: ('AZURE_STORAGE_CONTAINER_RESIDENTES', 'residentes'),
    VISITANTE: ('AZURE_STORAGE_CONTAINER_VISITANTES', 'visitantes'),
    DENEGADO: ('AZURE_STORAGE_CONTAINER_DENEGADOS', 'denegados'),
}

_SAS_HORAS = 2  # validez de la URL de lectura


def _connection_string():
    return os.getenv('AZURE_STORAGE_CONNECTION_STRING')


def configurado():
    return bool(_connection_string()) and BlobServiceClient is not None


def _container(tipo):
    env_name, default = _CONTAINER_ENV[tipo]
    return os.getenv(env_name, default)


def _service():
    return BlobServiceClient.from_connection_string(_connection_string())


def es_base64(valor):
    """Heuristica: True si el valor parece base64/data-url (foto sin migrar)."""
    if not valor:
        return False
    if valor.startswith('data:'):
        return True
    # Un nombre de blob es corto (uuid.jpg ~ 40 chars). El base64 es enorme.
    return len(valor) > 200


def _decodificar(data):
    """base64/data-url -> bytes."""
    if data.startswith('data:'):
        data = data.split(',', 1)[1]
    return base64.b64decode(data)


def subir_foto(data, tipo):
    """Sube una foto (base64/data-url) al container del tipo y devuelve el nombre del blob.

    Si Azure no esta configurado, devuelve el valor tal cual (passthrough dev).
    Si ya es un nombre de blob (no base64), lo devuelve sin re-subir.
    """
    if not data:
        return data
    if not configurado():
        return data
    if not es_base64(data):
        return data

    try:
        contenido = _decodificar(data)
    except (binascii.Error, ValueError):
        return data

    blob_name = f"{uuid.uuid4().hex}.jpg"
    client = _service().get_blob_client(container=_container(tipo), blob=blob_name)
    client.upload_blob(
        contenido,
        overwrite=True,
        content_settings=ContentSettings(
            content_type='image/jpeg',
            cache_control='public, max-age=3600',
        ),
    )
    return blob_name


def url_foto(blob_name, tipo):
    """Devuelve una URL SAS de lectura para el blob, o el valor tal cual si no aplica.

    El expiry se redondea a la hora siguiente para que la URL sea estable dentro
    de la hora (el navegador la cachea y no re-descarga en cada poll).
    """
    if not blob_name:
        return blob_name
    if not configurado():
        return blob_name
    if es_base64(blob_name):
        # Foto vieja aun no migrada: devolverla tal cual (data-url valida en <img>).
        return blob_name

    cuenta = _service()
    expiry = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0) + dt.timedelta(hours=_SAS_HORAS)
    sas = generate_blob_sas(
        account_name=cuenta.account_name,
        container_name=_container(tipo),
        blob_name=blob_name,
        account_key=cuenta.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry,
    )
    return f"{cuenta.url}{_container(tipo)}/{blob_name}?{sas}"


def borrar_foto(blob_name, tipo):
    """Borra el blob (para la politica de retencion). Ignora si no existe o no aplica."""
    if not blob_name or not configurado() or es_base64(blob_name):
        return
    try:
        _service().get_blob_client(container=_container(tipo), blob=blob_name).delete_blob()
    except Exception:
        pass
