import logging
from typing import Optional

from .api import TidalAPI
from .client import TidalClientImproved
from .auth_client import build_auth_client

logger = logging.getLogger(__name__)


class TidalSession:
    """Manages the TIDAL API session."""

    def __init__(self):
        self.api: Optional[TidalAPI] = None
        self.auth_client = build_auth_client()

    def get_api(self) -> TidalAPI:
        """
        Returns a valid TidalAPI instance.

        Lazy initialization: current_token (which can make an HTTP refresh)
        is only called on first access, when the instance does not yet exist.
        On subsequent accesses, the cached instance is returned directly.

        The token is kept fresh by two mechanisms already encapsulated in the client:
          1. Reactive: on_token_expiry callback upon receiving a 401.
          2. Proactive: current_token refreshes the token within the callback itself
             before returning it, if expires_soon() is true.

        Note: if in the future logout/login is added within the same TidalSession
        without recreating it, the client's token would become outdated until the next
        401. In the current architecture (TidalSession is created once per CLI execution)
        this is not a practical problem.
        """
        # Early return: avoids calling current_token unnecessarily
        if self.api is not None:
            return self.api

        # First creation: verify authentication and build the instance
        token = self.auth_client.current_token
        if not token:
            raise ConnectionError("Not authenticated. Please run 'tidmon auth' first.")

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
    """Global factory to get the TidalSession."""
    return TidalSession()