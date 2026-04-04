# Azure App Service Settings

Use these values in Application Settings for the Azure App Service:

- `SECRET_KEY`: generate a new secure value
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app.azurewebsites.net,.azurewebsites.net`
- `CSRF_TRUSTED_ORIGINS`: `https://your-app.azurewebsites.net`
- `CORS_ALLOWED_ORIGINS`: your frontend URL and local dev URLs
- `DATABASE_URL`: PostgreSQL connection string
- `DJANGO_LOG_LEVEL`: `INFO`

Startup command:

```bash
bash deploy/azure/startup.sh
```
