import logging

from tidmon.core.auth_client import build_auth_client

logger = logging.getLogger(__name__)


class Auth:
    """Handles authentication and session status."""

    def __init__(self):
        self.client = build_auth_client()

    def login(self):
        """Initiates the device authentication flow."""
        try:
            self.client.device_flow()
        except Exception as e:
            logger.error(f"Authentication failed: {e}", exc_info=True)
            print(f"\n✗ Error during login: {e}")

    def logout(self):
        """Logs out and clears the saved token."""
        self.client.logout()
        print("\n✓ Logged out. The token has been deleted.\n")

    def status(self):
        """Displays the current authentication status."""
        print("\n--- AUTHENTICATION STATUS ---")
        token = self.client.current_token

        if not token or not token.user_data:
            print("Status:  Not authenticated")
            print("\nRun 'tidmon auth' to log in.")
            return

        print("Status:    Authenticated ✓")
        print(f"User:      {token.user_data.get('username', 'Unknown')}")
        print(f"Country:   {token.user_data.get('countryCode', 'N/A')}")

        if token.is_expired:
            print("Token:     EXPIRED. It will be refreshed on the next operation.")
        else:
            remaining = token.time_remaining
            days = remaining.days
            hours, rem = divmod(remaining.seconds, 3600)
            mins, _ = divmod(rem, 60)
            print(f"Token:     Expires in {days} days, {hours} hours, and {mins} minutes.")
        print("---------------------------------")