from django.contrib import admin
from .models import Paciente, Procedimiento, Cita, Pago, Expediente, BiotipoCutaneo, CuidadoPiel, Habito, ExpedienteBiotipo, ExpedienteCuidadoPiel 

# Register your models here.
#Nota de Gabo: Aca en el admin.py se registran los modelos que queremos que aparezcan en el panel de administración de Django.
admin.site.register(Paciente)
admin.site.register(Procedimiento)
admin.site.register(Cita)
admin.site.register(Pago)  # Si tienes un modelo de Pago, también lo registras aquí
admin.site.register(Expediente)
admin.site.register(BiotipoCutaneo)
admin.site.register(CuidadoPiel)
admin.site.register(Habito)
admin.site.register(ExpedienteBiotipo)
admin.site.register(ExpedienteCuidadoPiel)  # Si tienes un modelo de ExpedienteCuidadoPiel, también lo registras aquí
