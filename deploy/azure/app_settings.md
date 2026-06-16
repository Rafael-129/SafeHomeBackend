# Azure App Service Settings

Use these values in Application Settings for the Azure App Service:

- `SECRET_KEY`: generate a new secure value
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app.azurewebsites.net,.azurewebsites.net`
- `CSRF_TRUSTED_ORIGINS`: `https://your-app.azurewebsites.net`
- `CORS_ALLOWED_ORIGINS`: your frontend URL and local dev URLs
- `DATABASE_URL`: PostgreSQL connection string
- `DJANGO_LOG_LEVEL`: `INFO`
- `AZURE_STORAGE_CONNECTION_STRING`: connection string de la cuenta de Storage (Access keys)
- `AZURE_STORAGE_CONTAINER_RESIDENTES`: `residentes`
- `AZURE_STORAGE_CONTAINER_VISITANTES`: `visitantes`
- `AZURE_STORAGE_CONTAINER_DENEGADOS`: `denegados`
- `PURGE_TOKEN` (opcional): token compartido con la Raspberry Pi para el endpoint de purga

Migracion de fotos existentes (una vez, tras configurar las variables):

```bash
python manage.py migrar_fotos_a_blob
```

Startup command:

```bash
bash deploy/azure/startup.sh
```
