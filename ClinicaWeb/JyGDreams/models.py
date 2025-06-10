from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

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
        # Calcula el total sumando el costo de todos los procedimientos de la cita
        procedimientos = self.cita.procedimientos.all()
        self.total = sum(p.costo for p in procedimientos)
        super().save(*args, **kwargs)

    def _str_(self):
        return f"Pago de {self.total} para {self.cita} el {self.fecha}"
