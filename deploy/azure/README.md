# Azure Deployment Notes

This folder contains the Azure-specific scripts for the Azure-ready SafeHome backend copy.

Recommended flow:

1. Set the Azure App Service application settings.
2. Run `deploy/azure/predeploy.sh` once for the target database.
3. Use `deploy/azure/startup.sh` as the startup command.
