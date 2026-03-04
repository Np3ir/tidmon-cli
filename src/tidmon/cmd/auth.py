import logging
import webbrowser
from datetime import datetime
from time import time, sleep

from rich.console import Console

from tidmon.core.auth_client import AuthAPI, load_auth_data, save_auth_data
from tidmon.core.auth_exceptions import AuthClientError
from tidmon.core.auth_models import AuthData

logger = logging.getLogger(__name__)
console = Console()


class Auth:
    """Handles authentication using tiddl's AuthAPI + AuthData pattern."""

    def __init__(self):
        self.auth_api = AuthAPI()

    def login(self):
        """Initiates the device authentication flow."""
        loaded = load_auth_data()

        if loaded.token:
            console.print("[cyan bold]Already logged in.")
            return

        try:
            device_auth = self.auth_api.get_device_auth()
        except Exception as e:
            logger.error(f"Failed to start device auth: {e}", exc_info=True)
            console.print(f"[bold red]Error starting authentication: {e}")
            return

        uri = f"https://{device_auth.verificationUriComplete}"
        try:
            webbrowser.open(uri)
        except Exception:
            pass

        console.print(f"\nGo to '[link]{uri}[/link]' and complete authentication!")

        auth_end_at = time() + device_auth.expiresIn
        status_text = "Authenticating..."

        with console.status(status_text) as status:
            while True:
                sleep(device_auth.interval)

                try:
                    auth = self.auth_api.get_auth(device_auth.deviceCode)
                    auth_data = AuthData(
                        token=auth.access_token,
                        refresh_token=auth.refresh_token,
                        expires_at=auth.expires_in + int(time()),
                        user_id=str(auth.user_id),
                        country_code=auth.user.countryCode,
                    )
                    save_auth_data(auth_data)
                    status.console.print("[bold green]Logged in!")
                    break

                except AuthClientError as e:
                    if e.error == "authorization_pending":
                        time_left = auth_end_at - time()
                        minutes, seconds = time_left // 60, int(time_left % 60)
                        status.update(
                            f"{status_text} time left: {minutes:.0f}:{seconds:02d}"
                        )
                        continue

                    if e.error == "expired_token":
                        status.console.print(
                            "[bold red]Authentication time expired."
                        )
                        break

                    logger.error(f"Auth error: {e}", exc_info=True)
                    status.console.print(f"[bold red]Authentication error: {e}")
                    break

    def logout(self):
        """Logs out and clears the saved token."""
        loaded = load_auth_data()

        if loaded.token:
            try:
                self.auth_api.logout_token(loaded.token)
            except Exception as e:
                logger.warning(f"Logout request failed: {e}")

        save_auth_data(AuthData())
        console.print("[bold green]Logged out!")

    def status(self):
        """Displays the current authentication status."""
        loaded = load_auth_data()
        console.print("\n--- AUTHENTICATION STATUS ---")

        if not loaded.token:
            console.print("Status:  Not authenticated")
            console.print("\nRun 'tidmon auth' to log in.")
            return

        console.print("Status:    Authenticated [green]✓[/green]")
        console.print(f"User ID:   {loaded.user_id}")
        console.print(f"Country:   {loaded.country_code}")

        if loaded.expires_at:
            expiry = datetime.fromtimestamp(loaded.expires_at)
            remaining = expiry - datetime.now()
            if remaining.total_seconds() <= 0:
                console.print("Token:     [bold red]EXPIRED[/bold red]. Run 'tidmon auth' to log in again.")
            else:
                days = remaining.days
                hours, rem = divmod(remaining.seconds, 3600)
                mins, _ = divmod(rem, 60)
                console.print(f"Token:     Expires in {days}d {hours}h {mins}m")

        console.print("-----------------------------")

    def refresh(self, force: bool = False, early_expire: int = 0):
        """Refreshes the access token using the saved refresh token."""
        loaded = load_auth_data()

        if not loaded.refresh_token:
            console.print("[bold red]Not logged in.")
            return

        if not force and loaded.expires_at and time() < (loaded.expires_at - early_expire):
            expiry = datetime.fromtimestamp(loaded.expires_at)
            remaining = expiry - datetime.now()
            days = remaining.days
            hours, rem = divmod(remaining.seconds, 3600)
            mins, _ = divmod(rem, 60)
            console.print(
                f"[green]Auth token expires in {days}d {hours}h {mins}m"
            )
            return

        try:
            auth = self.auth_api.refresh_token(loaded.refresh_token)
        except Exception as e:
            logger.error(f"Token refresh failed: {e}", exc_info=True)
            console.print(f"[bold red]Failed to refresh token: {e}")
            return

        loaded.token = auth.access_token
        loaded.expires_at = auth.expires_in + int(time())
        if auth.refresh_token:
            loaded.refresh_token = auth.refresh_token

        save_auth_data(loaded)
        console.print("[bold green]Auth token has been refreshed!")
