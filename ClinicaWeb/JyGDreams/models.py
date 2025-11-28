from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    ocupacion = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Cita(models.Model):
    ESTADO_CHOICES = [
        ('AGENDADO', 'Agendado'),
        ('REPROGRAMADO', 'Reprogramado'),
        ('REALIZADO', 'Realizado'),
        ('INASISTENCIA', 'Inasistencia'),  # Nueva opción agregada
    ]
    procedimientos = models.ManyToManyField('Procedimiento', through='CitaProcedimiento')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo_cita = models.CharField(max_length=100)
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES, default='AGENDADO')

    def clean(self):
        if self.fecha < timezone.localdate():
            raise ValidationError("No se pueden programar citas para fechas pasadas.")

    def __str__(self):
        return f"Cita de {self.paciente} el {self.fecha} a las {self.hora} ({self.get_estado_display()})" 


class Procedimiento(models.Model):
    titulo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    duracion = models.CharField(max_length=50)
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.costo < 0:
            raise ValidationError("El costo no puede ser negativo.")

    def __str__(self):
        return self.titulo

class CitaProcedimiento(models.Model):
    cita = models.ForeignKey('Cita', on_delete=models.CASCADE)
    procedimiento = models.ForeignKey('Procedimiento', on_delete=models.CASCADE)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        if self.descuento < 0:
            raise ValidationError("El descuento no puede ser negativo.")
        if self.descuento > self.procedimiento.costo:
            raise ValidationError("El descuento no puede exceder el costo del procedimiento.")

    @property
    def subtotal(self):
        """Calcula el subtotal del procedimiento (costo - descuento)"""
        return max(Decimal('0'), self.procedimiento.costo - self.descuento)

    def __str__(self):
        return f"{self.cita} - {self.procedimiento}"

class Pago(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.total < 0:
            raise ValidationError("El total no puede ser negativo.")

    def save(self, *args, **kwargs):
        # Calcula el total sumando los subtotales de todos los procedimientos de la cita
        # Cada procedimiento tiene su propio descuento aplicado
        cita_procedimientos = CitaProcedimiento.objects.filter(cita=self.cita)
        self.total = sum(cp.subtotal for cp in cita_procedimientos)
        # Asegura que el total no sea negativo usando Decimal
        self.total = max(Decimal('0'), self.total)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago de {self.total} para {self.cita} el {self.fecha}"
    

class Expediente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha_registro = models.DateField()
    usa_marcapasos = models.CharField(max_length=2, choices=[('si', 'Sí'), ('no', 'No')])
    historial_clinico = models.TextField()

    def __str__(self):
        return f"Expediente de {self.paciente} - {self.fecha_registro}"

class Habito(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    vasos_agua = models.CharField(max_length=100)
    trasnoche = models.CharField(max_length=100)
    tabaco = models.CharField(max_length=100)
    cafe = models.CharField(max_length=100)
    licor = models.CharField(max_length=100)
    medicamentos = models.CharField(max_length=100)
    suplementos = models.CharField(max_length=100)

class BiotipoCutaneo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class ExpedienteBiotipo(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    biotipo = models.ForeignKey(BiotipoCutaneo, on_delete=models.PROTECT)

class CuidadoPiel(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class ExpedienteCuidadoPiel(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE)
    cuidado = models.ForeignKey(CuidadoPiel, on_delete=models.PROTECT)
    otro = models.CharField(max_length=100, blank=True)  # Para el campo "Otros"
