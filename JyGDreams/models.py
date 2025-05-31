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
    ]
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
