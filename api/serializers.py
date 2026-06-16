from django.utils import timezone
from rest_framework import serializers

from . import storage
from .models import (
    Configuracion,
    Departamento,
    EventosSistema,
    HistorialAccesos,
    IngresoEventual,
    Notificaciones,
    PerfilAplicacion,
    Scanner,
    SesionesAdmin,
    Usuario,
    UsuarioAdmin,
    Visitante,
    Incidentes,
)


class FotoBlobSerializerMixin:
    """Sube fotos base64 a Azure Blob al escribir y devuelve URL SAS al leer.

    La subclase define `foto_field` (campo del modelo) y `foto_tipo`
    (storage.RESIDENTE / VISITANTE / DENEGADO).
    """

    foto_field = None
    foto_tipo = None

    def _subir_foto(self, validated_data):
        valor = validated_data.get(self.foto_field)
        if valor:
            validated_data[self.foto_field] = storage.subir_foto(valor, self.foto_tipo)

    def create(self, validated_data):
        self._subir_foto(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if self.foto_field in validated_data and validated_data.get(self.foto_field):
            anterior = getattr(instance, self.foto_field, None)
            validated_data[self.foto_field] = storage.subir_foto(
                validated_data[self.foto_field], self.foto_tipo
            )
            if anterior and anterior != validated_data[self.foto_field]:
                storage.borrar_foto(anterior, self.foto_tipo)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.foto_field in data:
            data[self.foto_field] = storage.url_foto(
                getattr(instance, self.foto_field, None), self.foto_tipo
            )
        return data


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'
        read_only_fields = ['iddepartamento', 'created_at']


class UsuarioSerializer(FotoBlobSerializerMixin, serializers.ModelSerializer):
    foto_field = 'foto'
    foto_tipo = storage.RESIDENTE

    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['idusuario']


class VisitanteSerializer(FotoBlobSerializerMixin, serializers.ModelSerializer):
    foto_field = 'foto'
    foto_tipo = storage.VISITANTE

    depart_visita = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Visitante
        fields = [
            'idvisitante', 'nombre', 'apellido', 'dni', 'motivo', 'fecha_visita',
            'hora_visita', 'iddepartamento', 'acepta_foto', 'observacion_privacidad',
            'acepta_terminos', 'fecha_aceptacion', 'foto', 'depart_visita',
        ]
        read_only_fields = ['idvisitante', 'fecha_aceptacion']
        extra_kwargs = {
            'iddepartamento': {'required': False},
            'acepta_foto': {'required': False},
        }

    def create(self, validated_data):
        if validated_data.get('acepta_terminos') is not True:
            raise serializers.ValidationError({
                'acepta_terminos': 'Debe aceptar los terminos y condiciones para registrar al visitante.',
            })
        validated_data['fecha_aceptacion'] = timezone.now()

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


class IngresoEventualSerializer(serializers.ModelSerializer):
    depart_visita = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = IngresoEventual
        fields = [
            'ideventual', 'dni', 'nombre', 'apellido', 'iddepartamento',
            'motivo', 'fecha', 'depart_visita',
        ]
        read_only_fields = ['ideventual', 'fecha']
        extra_kwargs = {
            'iddepartamento': {'required': False},
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


class ScannerSerializer(FotoBlobSerializerMixin, serializers.ModelSerializer):
    foto_field = 'foto_capturada'
    foto_tipo = storage.DENEGADO

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
    eventual_info = serializers.SerializerMethodField()
    scanner_info = serializers.SerializerMethodField()
    foto_url = serializers.SerializerMethodField()

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

    def get_eventual_info(self, obj):
        if obj.ideventual:
            eventual = obj.ideventual
            return {
                'nombre': eventual.nombre,
                'apellido': eventual.apellido,
                'dni': eventual.dni,
                'motivo': eventual.motivo,
                'depart_visita': eventual.iddepartamento.codigo if eventual.iddepartamento else 'N/A',
            }
        return None

    def get_scanner_info(self, obj):
        if obj.idscanner:
            scanner = obj.idscanner
            return {
                'tipo_persona': scanner.tipo_persona,
                'fecha': scanner.fecha,
                'foto_capturada': storage.url_foto(scanner.foto_capturada, storage.DENEGADO),
            }
        return None

    def get_foto_url(self, obj):
        """Foto a mostrar en 'Ultimo Acceso': enrolada si es reconocido,
        captura si es desconocido."""
        if obj.idusuario:
            return storage.url_foto(obj.idusuario.foto, storage.RESIDENTE)
        if obj.idvisitante:
            return storage.url_foto(obj.idvisitante.foto, storage.VISITANTE)
        if obj.idscanner and obj.idscanner.foto_capturada:
            return storage.url_foto(obj.idscanner.foto_capturada, storage.DENEGADO)
        return None
