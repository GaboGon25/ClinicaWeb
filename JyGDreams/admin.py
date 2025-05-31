from django.contrib import admin
from .models import Paciente

# Register your models here.
#Nota de Gabo: Aca en el admin.py se registran los modelos que queremos que aparezcan en el panel de administración de Django.
admin.site.register(Paciente)
