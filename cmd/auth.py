import logging

from tidmon.core.auth_client import build_auth_client

logger = logging.getLogger(__name__)


class Auth:
    """Maneja la autenticación y el estado de la sesión."""

    def __init__(self):
        self.client = build_auth_client()

    def login(self):
        """Inicia el flujo de autenticación por dispositivo."""
        try:
            self.client.device_flow()
        except Exception as e:
            logger.error(f"Fallo en la autenticación: {e}", exc_info=True)
            print(f"\n✗ Error durante el login: {e}")

    def logout(self):
        """Cierra la sesión y limpia el token guardado."""
        self.client.logout()
        print("\n✓ Sesión cerrada. El token ha sido eliminado.\n")

    def status(self):
        """Muestra el estado actual de la autenticación."""
        print("\n--- ESTADO DE LA AUTENTICACIÓN ---")
        token = self.client.current_token

        if not token or not token.user_data:
            print("Estado:  No autenticado")
            print("\nEjecuta 'tidmon auth' para iniciar sesión.")
            return

        print("Estado:    Autenticado ✓")
        print(f"Usuario:   {token.user_data.get('username', 'Desconocido')}")
        print(f"País:      {token.user_data.get('countryCode', 'N/A')}")

        if token.is_expired:
            print("Token:     EXPIRADO. Se intentará refrescar en la próxima operación.")
        else:
            remaining = token.time_remaining
            days  = remaining.days
            hours, rem = divmod(remaining.seconds, 3600)
            mins, _    = divmod(rem, 60)
            print(f"Token:     Expira en {days} días, {hours} horas y {mins} minutos.")
        print("-----------------------------------")