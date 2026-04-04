from datetime import date, datetime

from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Departamento, HistorialAccesos, PerfilAplicacion, Scanner, Usuario, Visitante
from .serializers import (
    DepartamentoSerializer,
    HistorialAccesosSerializer,
    PerfilAplicacionSerializer,
    ScannerSerializer,
    UsuarioSerializer,
    VisitanteSerializer,
)


@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Bienvenido a la API de SafeHome',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'departamentos': '/api/departamentos/',
            'usuarios': '/api/usuarios/',
            'visitantes': '/api/visitantes/',
            'visitantes_frecuentes': '/api/visitantes/frecuentes/',
            'scanner': '/api/scanner/',
            'historial': '/api/historial/',
            'historial_estadisticas': '/api/historial/estadisticas/?desde=YYYY-MM-DD&hasta=YYYY-MM-DD',
            'perfil_actual': '/api/perfil/actual/',
            'health': '/api/health/',
        },
    })


@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'ok',
        'message': 'API funcionando correctamente',
    }, status=status.HTTP_200_OK)


class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['torre', 'piso', 'numero']
    search_fields = ['codigo', 'torre']
    ordering_fields = ['torre', 'piso', 'numero']
    ordering = ['torre', 'piso', 'numero']


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['iddepartamento', 'dni']
    search_fields = ['nombre', 'apellido', 'dni', 'correo']
    ordering_fields = ['nombre', 'apellido', 'dni']
    ordering = ['nombre', 'apellido']

    @action(detail=False, methods=['get'])
    def buscar_por_dni(self, request):
        dni = request.query_params.get('dni', None)
        if dni:
            try:
                usuario = Usuario.objects.get(dni=dni)
                serializer = self.get_serializer(usuario)
                return Response(serializer.data)
            except Usuario.DoesNotExist:
                return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'DNI no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)


class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dni', 'iddepartamento', 'fecha_visita']
    search_fields = ['nombre', 'apellido', 'dni', 'motivo']
    ordering_fields = ['nombre', 'apellido', 'fecha_visita']
    ordering = ['-fecha_visita']

    @action(detail=False, methods=['get'])
    def hoy(self, request):
        hoy = date.today()
        visitantes = self.queryset.filter(fecha_visita=hoy)
        serializer = self.get_serializer(visitantes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def frecuentes(self, request):
        top = int(request.query_params.get('top', 10))
        rows = (
            Visitante.objects.values('dni', 'nombre', 'apellido')
            .annotate(total_visitas=Count('idvisitante'))
            .order_by('-total_visitas', 'apellido', 'nombre')[:top]
        )
        return Response(list(rows), status=status.HTTP_200_OK)


class ScannerViewSet(viewsets.ModelViewSet):
    queryset = Scanner.objects.all()
    serializer_class = ScannerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_persona', 'idusuario', 'idvisitante']
    search_fields = ['tipo_persona']
    ordering_fields = ['fecha']
    ordering = ['-fecha']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        tipo_persona = request.data.get('tipo_persona') or validated.get('tipo_persona')
        dni = request.data.get('dni')

        usuario = validated.get('idusuario')
        visitante = validated.get('idvisitante')

        if not usuario and not visitante and dni:
            if tipo_persona == 'residente':
                usuario = Usuario.objects.filter(dni=dni).first()
            elif tipo_persona == 'visitante':
                visitante = Visitante.objects.filter(dni=dni).order_by('-fecha_visita', '-hora_visita').first()
            else:
                usuario = Usuario.objects.filter(dni=dni).first()
                if not usuario:
                    visitante = Visitante.objects.filter(dni=dni).order_by('-fecha_visita', '-hora_visita').first()

        if not usuario and not visitante:
            return Response(
                {
                    'autorizado': False,
                    'tipo_persona': 'desconocido',
                    'mensaje': 'No se encontro coincidencia para el escaneo.',
                    'idscanner': None,
                    'idusuario': None,
                    'idvisitante': None,
                    'usuario_info': None,
                    'visitante_info': None,
                    'foto_capturada': request.data.get('foto_capturada'),
                },
                status=status.HTTP_200_OK,
            )

        scanner = serializer.save(
            idusuario=usuario,
            idvisitante=visitante,
            tipo_persona='residente' if usuario else 'visitante',
        )

        output = self.get_serializer(scanner).data
        output['autorizado'] = True
        output['mensaje'] = 'Persona identificada correctamente.'
        return Response(output, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def recientes(self, request):
        escaneos = self.queryset.order_by('-fecha')[:50]
        serializer = self.get_serializer(escaneos, many=True)
        return Response(serializer.data)


class HistorialAccesosViewSet(viewsets.ModelViewSet):
    queryset = HistorialAccesos.objects.select_related(
        'idusuario',
        'idvisitante',
        'idusuario__iddepartamento',
        'idvisitante__iddepartamento',
    ).all()
    serializer_class = HistorialAccesosSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'fecha_entrada', 'idusuario', 'idvisitante']
    search_fields = ['estado']
    ordering_fields = ['fecha_entrada', 'hora_entrada']
    ordering = ['-fecha_entrada', '-hora_entrada']

    @action(detail=False, methods=['get'])
    def hoy(self, request):
        hoy = date.today()
        accesos = self.queryset.filter(fecha_entrada=hoy)
        serializer = self.get_serializer(accesos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def activos(self, request):
        accesos = self.queryset.filter(hora_salida__isnull=True, estado='Permitido')
        serializer = self.get_serializer(accesos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')

        qs = self.queryset
        try:
            if desde:
                qs = qs.filter(fecha_entrada__gte=datetime.strptime(desde, '%Y-%m-%d').date())
            if hasta:
                qs = qs.filter(fecha_entrada__lte=datetime.strptime(hasta, '%Y-%m-%d').date())
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD en desde/hasta.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = qs.count()
        autorizados = qs.filter(estado='Permitido').count()
        denegados = qs.filter(estado='Denegado').count()
        residentes = qs.filter(idusuario__isnull=False).count()
        visitantes = qs.filter(idvisitante__isnull=False).count()
        por_estado = list(qs.values('estado').annotate(total=Count('idhistorial')).order_by('estado'))

        return Response(
            {
                'totalAccesos': total,
                'autorizados': autorizados,
                'denegados': denegados,
                'residentes': residentes,
                'visitantes': visitantes,
                'porEstado': por_estado,
                'desde': desde,
                'hasta': hasta,
            },
            status=status.HTTP_200_OK,
        )


class PerfilAplicacionViewSet(viewsets.ModelViewSet):
    queryset = PerfilAplicacion.objects.all()
    serializer_class = PerfilAplicacionSerializer

    @action(detail=False, methods=['get', 'put', 'patch'])
    def actual(self, request):
        perfil, _ = PerfilAplicacion.objects.get_or_create(
            idperfil=1,
            defaults={
                'nombre_aplicacion': 'SafeHome Scanner',
                'descripcion': 'Sistema de control de acceso para condominio',
                'version': '1.0.0',
                'permitir_registro_sin_foto': True,
                'politica_foto_requerida': False,
            },
        )

        if request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(perfil, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(perfil)
        return Response(serializer.data)
