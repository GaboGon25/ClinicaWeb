from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from JyGDreams.models import Cita
from datetime import timedelta

class Command(BaseCommand):
    help = 'Envía recordatorios de citas por correo a los doctores 2 horas antes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Envía recordatorios para citas en las próximas 24 horas (para pruebas)',
        )

    def handle(self, *args, **options):
        now = timezone.localtime(timezone.now())
        self.stdout.write(f'Ahora (local): {now}')

        if options['test']:
            reminder_time = now + timedelta(hours=24)
            self.stdout.write('Modo test: enviando recordatorios para citas en las próximas 24 horas.')
        else:
            reminder_time = now + timedelta(hours=2)

        self.stdout.write(f'Recordatorio entre {now} y {reminder_time}')

        # Filtrar citas en el rango de tiempo (incluye el cruce de medianoche)
        if now.date() == reminder_time.date():
            citas = Cita.objects.filter(
                fecha=now.date(),
                hora__gte=now.time(),
                hora__lte=reminder_time.time(),
                estado__in=['AGENDADO', 'REPROGRAMADO'],
                doctor__isnull=False,
                doctor__is_active=True,
                doctor__email__isnull=False,
                doctor__email__gt='',
            )
        else:
            citas = Cita.objects.filter(
                (Q(fecha=now.date()) & Q(hora__gte=now.time())) |
                (Q(fecha=reminder_time.date()) & Q(hora__lte=reminder_time.time())),
                estado__in=['AGENDADO', 'REPROGRAMADO'],
                doctor__isnull=False,
                doctor__is_active=True,
                doctor__email__isnull=False,
                doctor__email__gt='',
            )

        citas = citas.select_related('paciente', 'doctor')

        self.stdout.write(f'Encontradas {citas.count()} citas para recordar.')

        if citas.count() == 0:
            self.stdout.write('No hay citas que cumplan los criterios. Verifica:')
            self.stdout.write('- Que haya citas agendadas para hoy.')
            self.stdout.write('- Que las citas tengan doctor asignado.')
            self.stdout.write('- Que el doctor esté activo y tenga email.')
            self.stdout.write('- Que la hora de la cita esté en el rango de recordatorio.')
            return

        for cita in citas:
            self.stdout.write(f'Procesando cita ID {cita.id}: {cita.paciente.nombre} {cita.paciente.apellido} - {cita.fecha} {cita.hora}')
            self.stdout.write(f'Doctor: {cita.doctor.username} - Email: {cita.doctor.email} - Activo: {cita.doctor.is_active}')
            context = {
                'cita': cita,
                'paciente': cita.paciente,
                'doctor': cita.doctor,
                'fecha': cita.fecha,
                'hora': cita.hora,
                'motivo': cita.motivo_cita,
                'clinic_name': 'Clínica Estética JyGDreams',
                'logo_url': settings.SITE_URL + settings.STATIC_URL + 'JyGDreams/img/icon-clinica.png',
            }

            html_body = render_to_string('email_appointment_reminder.html', context)

            subject = f'Recordatorio de cita - {cita.paciente.nombre} {cita.paciente.apellido}'
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
            to = [cita.doctor.email]

            self.stdout.write(f'Enviando email desde {from_email} a {to}')

            msg = EmailMultiAlternatives(subject, '', from_email, to)
            msg.attach_alternative(html_body, 'text/html')

            try:
                result = msg.send()
                self.stdout.write(f'Email enviado exitosamente. Resultado: {result}')
            except Exception as e:
                self.stderr.write(f'Error enviando email: {str(e)}')
                import traceback
                self.stderr.write(traceback.format_exc())