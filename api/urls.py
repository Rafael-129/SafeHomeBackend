from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'departamentos', views.DepartamentoViewSet, basename='departamento')
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'visitantes', views.VisitanteViewSet, basename='visitante')
router.register(r'scanner', views.ScannerViewSet, basename='scanner')
router.register(r'historial', views.HistorialAccesosViewSet, basename='historial')
router.register(r'perfil', views.PerfilAplicacionViewSet, basename='perfil')

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('health/', views.health_check, name='health-check'),
    path('', include(router.urls)),
]
