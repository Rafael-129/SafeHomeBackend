from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'departamentos', views.DepartamentoViewSet, basename='departamento')
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'visitantes', views.VisitanteViewSet, basename='visitante')
router.register(r'scanner', views.ScannerViewSet, basename='scanner')
router.register(r'ingresos-eventuales', views.IngresoEventualViewSet, basename='ingreso-eventual')
router.register(r'historial', views.HistorialAccesosViewSet, basename='historial')
router.register(r'perfil', views.PerfilAplicacionViewSet, basename='perfil')
router.register(r'admins', views.UsuarioAdminViewSet, basename='admins')
router.register(r'sesiones-admin', views.SesionesAdminViewSet, basename='sesiones-admin')
router.register(r'eventos-sistema', views.EventosSistemaViewSet, basename='eventos-sistema')
router.register(r'configuracion', views.ConfiguracionViewSet, basename='configuracion')
router.register(r'notificaciones', views.NotificacionesViewSet, basename='notificaciones')
router.register(r'incidentes', views.IncidentesViewSet, basename='incidentes')

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('health/', views.health_check, name='health-check'),
    path('reportes/', views.generar_reporte, name='generar-reporte'),
    path('', include(router.urls)),
]
