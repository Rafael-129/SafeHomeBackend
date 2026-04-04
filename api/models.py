from django.db import models


class Departamento(models.Model):
    iddepartamento = models.AutoField(primary_key=True, db_column='iddepartamento')
    codigo = models.CharField(max_length=20, unique=True)
    torre = models.CharField(max_length=10)
    piso = models.IntegerField()
    numero = models.IntegerField()
    area_m2 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    habitaciones = models.IntegerField(null=True, blank=True)
    banos = models.IntegerField(null=True, blank=True)
    estacionamientos = models.IntegerField(default=0)
    observaciones = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'departamento'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return f"{self.codigo} - Torre {self.torre}"


class Usuario(models.Model):
    idusuario = models.AutoField(primary_key=True, db_column='idusuario')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True)
    correo = models.EmailField(max_length=150, null=True, blank=True)
    iddepartamento = models.ForeignKey(
        Departamento,
        on_delete=models.RESTRICT,
        db_column='iddepartamento',
    )
    foto = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.dni}"


class Visitante(models.Model):
    idvisitante = models.AutoField(primary_key=True, db_column='idvisitante')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=8)
    motivo = models.CharField(max_length=255, null=True, blank=True)
    fecha_visita = models.DateField()
    hora_visita = models.TimeField()
    iddepartamento = models.ForeignKey(
        Departamento,
        on_delete=models.RESTRICT,
        db_column='iddepartamento',
    )
    acepta_foto = models.BooleanField(default=True)
    observacion_privacidad = models.CharField(max_length=255, null=True, blank=True)
    foto = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'visitante'
        verbose_name = 'Visitante'
        verbose_name_plural = 'Visitantes'

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.dni}"


class PerfilAplicacion(models.Model):
    idperfil = models.AutoField(primary_key=True, db_column='idperfil')
    nombre_aplicacion = models.CharField(max_length=120, default='SafeHome Scanner')
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    version = models.CharField(max_length=20, default='1.0.0')
    contacto_soporte = models.EmailField(max_length=150, null=True, blank=True)
    permitir_registro_sin_foto = models.BooleanField(default=True)
    politica_foto_requerida = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'perfilaplicacion'
        verbose_name = 'Perfil de Aplicacion'
        verbose_name_plural = 'Perfil de Aplicacion'

    def __str__(self):
        return f"Perfil - {self.nombre_aplicacion}"


class Scanner(models.Model):
    TIPO_PERSONA_CHOICES = [
        ('residente', 'Residente'),
        ('visitante', 'Visitante'),
    ]

    idscanner = models.AutoField(primary_key=True, db_column='idscanner')
    idusuario = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='idusuario',
    )
    idvisitante = models.ForeignKey(
        'Visitante',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='idvisitante',
    )
    foto_capturada = models.TextField(null=True, blank=True)
    tipo_persona = models.CharField(max_length=20, choices=TIPO_PERSONA_CHOICES)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scanner'
        verbose_name = 'Escaneo'
        verbose_name_plural = 'Escaneos'
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(idusuario__isnull=False, idvisitante__isnull=True)
                    | models.Q(idusuario__isnull=True, idvisitante__isnull=False)
                ),
                name='chk_persona',
            ),
        ]

    def __str__(self):
        return f"Scanner {self.idscanner} - {self.tipo_persona}"


class HistorialAccesos(models.Model):
    ESTADOS = [
        ('Permitido', 'Permitido'),
        ('Denegado', 'Denegado'),
    ]

    idhistorial = models.AutoField(primary_key=True, db_column='idhistorial')
    idusuario = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='idusuario',
    )
    idvisitante = models.ForeignKey(
        'Visitante',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='idvisitante',
    )
    idscanner = models.ForeignKey(
        'Scanner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='idscanner',
    )
    fecha_entrada = models.DateField()
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS)

    class Meta:
        db_table = 'historialaccesos'
        verbose_name = 'Historial de Acceso'
        verbose_name_plural = 'Historial de Accesos'
        ordering = ['-fecha_entrada', '-hora_entrada']
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(idusuario__isnull=False, idvisitante__isnull=True)
                    | models.Q(idusuario__isnull=True, idvisitante__isnull=False)
                ),
                name='chk_acceso_persona',
            ),
        ]

    def __str__(self):
        return f"Acceso {self.idhistorial} - {self.estado}"
