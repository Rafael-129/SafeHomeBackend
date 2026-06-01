from django.contrib import admin
from .models import (
    Departamento,
    EventosSistema,
    HistorialAccesos,
    PerfilAplicacion,
    Scanner,
    SesionesAdmin,
    Usuario,
    UsuarioAdmin,
    Visitante,
)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['iddepartamento', 'codigo', 'torre', 'piso', 'numero', 'habitaciones', 'estacionamientos']
    list_filter = ['torre', 'piso']
    search_fields = ['codigo', 'torre']
    ordering = ['torre', 'piso', 'numero']


@admin.register(Usuario)
class UsuarioModelAdmin(admin.ModelAdmin):
    list_display = ['idusuario', 'nombre', 'apellido', 'dni', 'correo', 'iddepartamento']
    list_filter = ['iddepartamento']
    search_fields = ['nombre', 'apellido', 'dni', 'correo']
    ordering = ['idusuario']


@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    list_display = ['idvisitante', 'nombre', 'apellido', 'dni', 'iddepartamento', 'fecha_visita', 'hora_visita', 'acepta_foto']
    list_filter = ['iddepartamento', 'fecha_visita']
    search_fields = ['nombre', 'apellido', 'dni', 'motivo']
    ordering = ['-fecha_visita']


@admin.register(Scanner)
class ScannerAdmin(admin.ModelAdmin):
    list_display = ['idscanner', 'tipo_persona', 'idusuario', 'idvisitante', 'fecha']
    list_filter = ['tipo_persona', 'fecha']
    search_fields = ['tipo_persona']
    ordering = ['-fecha']


@admin.register(HistorialAccesos)
class HistorialAccesosAdmin(admin.ModelAdmin):
    list_display = ['idhistorial', 'get_persona', 'fecha_entrada', 'hora_entrada', 'hora_salida', 'estado']
    list_filter = ['estado', 'fecha_entrada']
    search_fields = ['estado']
    ordering = ['-fecha_entrada', '-hora_entrada']

    def get_persona(self, obj):
        if obj.idusuario:
            return f"Usuario: {obj.idusuario.nombre} {obj.idusuario.apellido}"
        if obj.idvisitante:
            return f"Visitante: {obj.idvisitante.nombre} {obj.idvisitante.apellido}"
        return 'N/A'

    get_persona.short_description = 'Persona'


@admin.register(PerfilAplicacion)
class PerfilAplicacionAdmin(admin.ModelAdmin):
    list_display = ['idperfil', 'nombre_aplicacion', 'version', 'permitir_registro_sin_foto', 'politica_foto_requerida', 'updated_at']


@admin.register(UsuarioAdmin)
class UsuarioAdminSistemaAdmin(admin.ModelAdmin):
    list_display = ['idadmin', 'username', 'nombre_completo', 'email', 'rol', 'activo', 'ultimo_acceso']
    list_filter = ['rol', 'activo', 'autenticacion_2fa', 'tema']
    search_fields = ['username', 'nombre_completo', 'email']
    ordering = ['username']


@admin.register(SesionesAdmin)
class SesionesAdminModelAdmin(admin.ModelAdmin):
    list_display = ['idsesion', 'idadmin', 'ip_address', 'fecha_inicio', 'fecha_expiracion', 'activa']
    list_filter = ['activa', 'fecha_inicio']
    search_fields = ['token', 'idadmin__username', 'ip_address']
    ordering = ['-fecha_inicio']


@admin.register(EventosSistema)
class EventosSistemaAdmin(admin.ModelAdmin):
    list_display = ['idevento', 'tipo', 'nivel', 'idadmin', 'ip_address', 'fecha']
    list_filter = ['nivel', 'tipo', 'fecha']
    search_fields = ['tipo', 'descripcion', 'ip_address', 'idadmin__username']
    ordering = ['-fecha']
