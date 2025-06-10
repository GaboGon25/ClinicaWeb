from django.contrib import admin
from .models import Paciente, Procedimiento, Cita, Pago 

# Register your models here.
#Nota de Gabo: Aca en el admin.py se registran los modelos que queremos que aparezcan en el panel de administración de Django.
admin.site.register(Paciente)
admin.site.register(Procedimiento)
admin.site.register(Cita)
admin.site.register(Pago)  # Si tienes un modelo de Pago, también lo registras aquí
