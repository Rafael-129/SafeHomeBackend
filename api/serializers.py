from rest_framework import serializers

from .models import (
    Configuracion,
    Departamento,
    EventosSistema,
    HistorialAccesos,
    Notificaciones,
    PerfilAplicacion,
    Scanner,
    SesionesAdmin,
    Usuario,
    UsuarioAdmin,
    Visitante,
    Incidentes,
)


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'
        read_only_fields = ['iddepartamento', 'created_at']


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['idusuario']


class VisitanteSerializer(serializers.ModelSerializer):
    depart_visita = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Visitante
        fields = [
            'idvisitante', 'nombre', 'apellido', 'dni', 'motivo', 'fecha_visita',
            'hora_visita', 'iddepartamento', 'acepta_foto', 'observacion_privacidad',
            'foto', 'depart_visita',
        ]
        read_only_fields = ['idvisitante']
        extra_kwargs = {
            'iddepartamento': {'required': False},
            'acepta_foto': {'required': False},
        }

    def create(self, validated_data):
        depart_codigo = validated_data.pop('depart_visita', None)
        if depart_codigo:
            try:
                departamento = Departamento.objects.get(codigo=depart_codigo)
                validated_data['iddepartamento'] = departamento
            except Departamento.DoesNotExist as exc:
                raise serializers.ValidationError({
                    'depart_visita': f'Departamento {depart_codigo} no existe',
                }) from exc

        if 'iddepartamento' not in validated_data:
            raise serializers.ValidationError({'depart_visita': 'Debe proporcionar un departamento'})

        if validated_data.get('acepta_foto') is False:
            validated_data['foto'] = None
            if not validated_data.get('observacion_privacidad'):
                validated_data['observacion_privacidad'] = 'Visitante no autoriza captura de foto.'

        return super().create(validated_data)


class PerfilAplicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilAplicacion
        fields = '__all__'
        read_only_fields = ['idperfil', 'updated_at']


class UsuarioAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioAdmin
        fields = '__all__'
        read_only_fields = ['idadmin', 'created_at']


class SesionesAdminSerializer(serializers.ModelSerializer):
    admin_info = serializers.SerializerMethodField()

    class Meta:
        model = SesionesAdmin
        fields = '__all__'
        read_only_fields = ['idsesion', 'fecha_inicio']

    def get_admin_info(self, obj):
        admin = obj.idadmin
        return {
            'username': admin.username,
            'nombre_completo': admin.nombre_completo,
            'rol': admin.rol,
        }


class EventosSistemaSerializer(serializers.ModelSerializer):
    admin_info = serializers.SerializerMethodField()

    class Meta:
        model = EventosSistema
        fields = '__all__'
        read_only_fields = ['idevento', 'fecha']

    def get_admin_info(self, obj):
        if not obj.idadmin:
            return None

        admin = obj.idadmin
        return {
            'username': admin.username,
            'nombre_completo': admin.nombre_completo,
            'rol': admin.rol,
        }


class ConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuracion
        fields = '__all__'
        read_only_fields = ['idconfig', 'ultima_modificacion']


class NotificacionesSerializer(serializers.ModelSerializer):
    usuario_info = serializers.SerializerMethodField()

    class Meta:
        model = Notificaciones
        fields = '__all__'
        read_only_fields = ['idnotificacion', 'fecha']

    def get_usuario_info(self, obj):
        if not obj.idusuario:
            return None

        usuario = obj.idusuario
        return {
            'idusuario': usuario.idusuario,
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'dni': usuario.dni,
        }


class IncidentesSerializer(serializers.ModelSerializer):
    scanner_info = serializers.SerializerMethodField()

    class Meta:
        model = Incidentes
        fields = '__all__'
        read_only_fields = ['idincidente', 'fecha']

    def get_scanner_info(self, obj):
        if not obj.idscanner:
            return None
        scanner = obj.idscanner
        return {
            'idscanner': scanner.idscanner,
            'tipo_persona': scanner.tipo_persona,
            'fecha': scanner.fecha,
        }


class ScannerSerializer(serializers.ModelSerializer):
    usuario_info = serializers.SerializerMethodField()
    visitante_info = serializers.SerializerMethodField()

    class Meta:
        model = Scanner
        fields = '__all__'
        read_only_fields = ['idscanner', 'fecha']

    def get_usuario_info(self, obj):
        if obj.idusuario:
            usuario = obj.idusuario
            return {
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'departamento': usuario.iddepartamento.codigo if usuario.iddepartamento else 'N/A',
            }
        return None

    def get_visitante_info(self, obj):
        if obj.idvisitante:
            visitante = obj.idvisitante
            return {
                'nombre': visitante.nombre,
                'apellido': visitante.apellido,
                'depart_visita': visitante.iddepartamento.codigo if visitante.iddepartamento else 'N/A',
            }
        return None


class HistorialAccesosSerializer(serializers.ModelSerializer):
    usuario_info = serializers.SerializerMethodField()
    visitante_info = serializers.SerializerMethodField()
    scanner_info = serializers.SerializerMethodField()

    class Meta:
        model = HistorialAccesos
        fields = '__all__'
        read_only_fields = ['idhistorial']

    def get_usuario_info(self, obj):
        if obj.idusuario:
            usuario = obj.idusuario
            return {
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'departamento': usuario.iddepartamento.codigo if usuario.iddepartamento else 'N/A',
            }
        return None

    def get_visitante_info(self, obj):
        if obj.idvisitante:
            visitante = obj.idvisitante
            return {
                'nombre': visitante.nombre,
                'apellido': visitante.apellido,
                'depart_visita': visitante.iddepartamento.codigo if visitante.iddepartamento else 'N/A',
            }
        return None

    def get_scanner_info(self, obj):
        if obj.idscanner:
            scanner = obj.idscanner
            return {
                'tipo_persona': scanner.tipo_persona,
                'fecha': scanner.fecha,
                'foto_capturada': scanner.foto_capturada,
            }
        return None
