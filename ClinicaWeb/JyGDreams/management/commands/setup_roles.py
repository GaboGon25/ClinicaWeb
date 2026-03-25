from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from JyGDreams.models import (
    Paciente,
    Cita,
    CitaProcedimiento,
    Pago,
    Expediente,
    Habito,
    ExpedienteBiotipo,
    ExpedienteCuidadoPiel,
)


class Command(BaseCommand):
    help = "Crea/actualiza grupos Doctor/a y Secretario/a con permisos por módulo."

    def handle(self, *args, **options):
        # Renombrar grupos antiguos (si existen) a los nombres nuevos
        for old_name, new_name in [("Doctores", "Doctor/a"), ("Secretarias", "Secretario/a")]:
            old_group = Group.objects.filter(name=old_name).first()
            if old_group:
                old_group.name = new_name
                old_group.save()

        doctor_group, _ = Group.objects.get_or_create(name="Doctor/a")
        secretaria_group, _ = Group.objects.get_or_create(name="Secretario/a")

        def perms_for(model, actions):
            ct = ContentType.objects.get_for_model(model)
            codenames = [f"{a}_{model._meta.model_name}" for a in actions]
            return Permission.objects.filter(content_type=ct, codename__in=codenames)

        # Doctor: pacientes (ver), expedientes (ver/crear/editar), citas (solo ver)
        doctor_perms = []
        doctor_perms += list(perms_for(Paciente, ["view"]))
        doctor_perms += list(perms_for(Cita, ["view"]))
        doctor_perms += list(perms_for(CitaProcedimiento, ["view"]))
        doctor_perms += list(perms_for(Expediente, ["view", "add", "change"]))
        doctor_perms += list(perms_for(Habito, ["view", "add", "change"]))
        doctor_perms += list(perms_for(ExpedienteBiotipo, ["view", "add", "change"]))
        doctor_perms += list(perms_for(ExpedienteCuidadoPiel, ["view", "add", "change"]))

        # Secretaria: pacientes (ver/crear/editar), citas (ver/crear/editar), pagos (ver/crear/editar)
        secretaria_perms = []
        secretaria_perms += list(perms_for(Paciente, ["view", "add", "change"]))
        secretaria_perms += list(perms_for(Cita, ["view", "add", "change"]))
        secretaria_perms += list(perms_for(CitaProcedimiento, ["view", "add", "change"]))
        secretaria_perms += list(perms_for(Pago, ["view", "add", "change"]))

        # Aplicar permisos (reemplazando el set actual para que sea idempotente)
        doctor_group.permissions.set(doctor_perms)
        secretaria_group.permissions.set(secretaria_perms)

        self.stdout.write(self.style.SUCCESS("Roles configurados: Doctor/a, Secretario/a."))

