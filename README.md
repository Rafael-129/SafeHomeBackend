# SafeHome Backend Azure

Copia ordenada del backend Django pensada para Azure App Service Linux F1.

## Estructura

- `service/`: configuración del proyecto Django
- `api/`: app principal con modelos, serializers, views y URLs
- `deploy/azure/`: scripts y notas de despliegue para Azure

## Arranque local

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Azure App Service F1

- Startup command recomendado: `bash deploy/azure/startup.sh`
- Variables en Application Settings: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, `DATABASE_URL`
- Ejecuta migraciones manualmente con `bash deploy/azure/predeploy.sh` o desde Cloud Shell antes del primer arranque

## Rutas principales

- `/admin/`
- `/api/`
- `/api/health/`
