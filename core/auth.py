import logging
from typing import Optional

from .api import TidalAPI
from .client import TidalClientImproved
from .auth_client import build_auth_client

logger = logging.getLogger(__name__)


class TidalSession:
    """Gestiona la sesión de la API de TIDAL."""

    def __init__(self):
        self.api: Optional[TidalAPI] = None
        self.auth_client = build_auth_client()

    def get_api(self) -> TidalAPI:
        """
        Devuelve una instancia válida de TidalAPI.

        Lazy initialization: current_token (que puede hacer un refresh HTTP)
        solo se llama en el primer acceso, cuando la instancia aún no existe.
        En accesos posteriores se devuelve la instancia cacheada directamente.

        El token se mantiene fresco por dos mecanismos ya encapsulados en el cliente:
          1. Reactivo: on_token_expiry callback al recibir un 401.
          2. Proactivo: current_token refresca el token dentro del propio callback
             antes de devolverlo, si expires_soon() es verdadero.

        Nota: si en el futuro se añade logout/login dentro de la misma TidalSession
        sin recrearla, el token del cliente quedaría desactualizado hasta el próximo
        401. En la arquitectura actual (TidalSession se crea una vez por ejecución
        del CLI) esto no es un problema práctico.
        """
        # Early return: evita llamar a current_token innecesariamente
        if self.api is not None:
            return self.api

        # Primera creación: verificar autenticación y construir la instancia
        token = self.auth_client.current_token
        if not token:
            raise ConnectionError("No autenticado. Por favor, ejecuta 'tidmon auth' primero.")

        logger.debug("Creating new TidalAPI instance with refresh callback.")

        def _on_token_expiry(force: bool = False) -> Optional[str]:
            """Token refresh callback for TidalClientImproved.

            Called when:
              - 401 received (force=True)  → always refresh regardless of expiry clock
              - Proactive check (force=False) → refresh only if expires_soon()
            """
            try:
                logger.info(f"Token refresh callback triggered (force={force}).")
                if force:
                    # Server says token is invalid — force a network refresh
                    # regardless of what our local expiry clock says.
                    new_token = self.auth_client.refresh_current_token()
                    return new_token.access_token if new_token else None
                else:
                    new_token = self.auth_client.current_token
                    return new_token.access_token if new_token else None
            except Exception as e:
                logger.error(f"Error during token refresh callback: {e}", exc_info=True)
                return None

        client = TidalClientImproved(
            token=token.access_token,
            on_token_expiry=_on_token_expiry,
        )

        user_data    = token.user_data or {}
        user_id      = str(user_data.get("userId", ""))
        country_code = user_data.get("countryCode", "US")

        self.api = TidalAPI(
            client=client,
            user_id=user_id,
            country_code=country_code,
        )
        return self.api


def get_session() -> TidalSession:
    """Factory global para obtener la TidalSession."""
    return TidalSession()