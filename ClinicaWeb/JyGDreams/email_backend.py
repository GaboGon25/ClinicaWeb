import ssl

from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend
from django.conf import settings


class EmailBackend(DjangoEmailBackend):
    """
    SMTP backend con manejo robusto de certificados en Windows.

    - Por defecto: verifica TLS usando certifi si está disponible.
    - Opcional (NO recomendado): desactivar verificación TLS si el entorno tiene
      certificados corporativos/rotos que disparan SSLCertVerificationError.
      Controlado por settings.EMAIL_TLS_VERIFY = False.
    """

    def _build_ssl_context(self):
        verify = getattr(settings, "EMAIL_TLS_VERIFY", True)

        # Usar contexto SSL estándar, preferentemente con el bundle de certifi
        ctx = ssl.create_default_context()

        # Si tenemos certifi, usar su CA bundle para evitar problemas de certificados
        try:
            import certifi
            ctx.load_verify_locations(cafile=certifi.where())
        except Exception:
            pass

        if not verify:
            # Desactiva la verificación (solo para entornos de prueba/diagnóstico)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        return ctx


    def open(self):
        if self.connection:
            return False

        local_hostname = getattr(self, "local_hostname", None)
        self.connection = self.connection_class(
            self.host,
            self.port,
            local_hostname=local_hostname,
            timeout=self.timeout,
        )

        if self.use_tls:
            self.connection.ehlo()
            self.connection.starttls(context=self._build_ssl_context())
            self.connection.ehlo()

        if self.username and self.password:
            self.connection.login(self.username, self.password)

        return True

