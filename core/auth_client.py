import base64
import json
import time
import webbrowser
from dataclasses import dataclass
from os import environ
from pathlib import Path
from requests import Session, HTTPError
from typing import Any, Callable, Optional

from .auth_exceptions import AuthClientError
from .auth_models import TidalToken

@dataclass
class TidalCredentials:
    """Credenciales de TIDAL con validación"""
    client_id: str
    client_secret: str

    def __post_init__(self):
        if not self.client_id or not self.client_secret:
            raise ValueError("client_id and client_secret are required")

    @classmethod
    def from_base64(cls, encoded: str) -> "TidalCredentials":
        """Carga credenciales desde string base64"""
        try:
            decoded = base64.b64decode(encoded).decode()
            client_id, client_secret = decoded.split(";")
            return cls(client_id, client_secret)
        except Exception as e:
            raise ValueError(f"Failed to decode credentials: {e}")

    def to_tuple(self) -> tuple[str, str]:
        """Retorna como tupla para compatibilidad"""
        return (self.client_id, self.client_secret)

class TokenStorage:
    """Almacenamiento seguro de tokens en disco"""
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, token: TidalToken):
        self.storage_path.write_text(json.dumps(token.to_dict(), indent=2))
        try:
            self.storage_path.chmod(0o600)
        except Exception:
            pass

    def load(self) -> Optional[TidalToken]:
        if not self.storage_path.exists():
            return None
        try:
            data = json.loads(self.storage_path.read_text())
            token = TidalToken.from_dict(data)
            return None if token.is_expired else token
        except Exception:
            return None

    def clear(self):
        if self.storage_path.exists():
            self.storage_path.unlink()

class AuthClient:
    """Cliente de autenticación mejorado"""
    def __init__(self, credentials: TidalCredentials, token_storage: TokenStorage):
        self.auth_url = "https://auth.tidal.com/v1/oauth2"
        self.credentials = credentials
        self.token_storage = token_storage
        self.session = Session()
        self._current_token: Optional[TidalToken] = self.token_storage.load()

    @property
    def current_token(self) -> Optional[TidalToken]:
        if self._current_token and self._current_token.expires_soon():
            try: self.refresh_current_token()
            except Exception: pass
        return self._current_token

    def refresh_token(self, refresh_token: str) -> TidalToken:
        res = self.session.post(
            f"{self.auth_url}/token",
            data={
                "client_id": self.credentials.client_id,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
                "scope": "r_usr+w_usr+w_sub",
            },
            auth=self.credentials.to_tuple(),
        )
        self._handle_error(res)
        json_data = res.json()
        if "refresh_token" not in json_data:
            json_data["refresh_token"] = refresh_token
        token = TidalToken.from_api_response(json_data)
        self._current_token = token
        self.token_storage.save(token)
        return token

    def refresh_current_token(self) -> TidalToken:
        if not (self._current_token and self._current_token.refresh_token):
            raise ValueError("No refresh_token available")
        return self.refresh_token(self._current_token.refresh_token)

    def logout(self):
        if not self._current_token: return
        try:
            self.session.post(
                "https://api.tidal.com/v1/logout",
                headers={"authorization": f"Bearer {self._current_token.access_token}"},
            ).raise_for_status()
        except Exception as e:
            print(f"Warning: Logout request failed: {e}")
        self._current_token = None
        self.token_storage.clear()

    def device_flow(self) -> TidalToken:
        auth_data = self._start_device_auth()
        verification_uri = auth_data['verificationUri']
        user_code = auth_data['userCode']
        print(f"\n{'*'*50}")
        print("Para autorizar la aplicación, visita:")
        print(f"  {verification_uri}  y introduce el código: {user_code}")
        print(f"{'*'*50}\n")
        try: webbrowser.open(f"https://{verification_uri}")
        except Exception: pass

        return self._poll_device_auth(auth_data['deviceCode'], auth_data.get('interval', 5), auth_data['expiresIn'])

    def _start_device_auth(self) -> dict:
        res = self.session.post(
            f"{self.auth_url}/device_authorization",
            data={"client_id": self.credentials.client_id, "scope": "r_usr+w_usr+w_sub"},
        )
        self._handle_error(res)
        return res.json()

    def _poll_device_auth(self, device_code: str, interval: int, timeout: int) -> TidalToken:
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                res = self.session.post(
                    f"{self.auth_url}/token",
                    data={
                        "client_id": self.credentials.client_id,
                        "device_code": device_code,
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "scope": "r_usr+w_usr+w_sub",
                    },
                    auth=self.credentials.to_tuple(),
                )
                json_data = res.json()
                if res.status_code == 200:
                    token = TidalToken.from_api_response(json_data)
                    self._current_token = token
                    self.token_storage.save(token)
                    print("¡Autenticación exitosa!")
                    return token
                if res.status_code == 400 and json_data.get("error") == "authorization_pending":
                    time.sleep(interval)
                    continue
                self._handle_error(res)
            except (HTTPError, AuthClientError):
                raise
            except Exception as e:
                raise AuthClientError(status=500, error="unknown_error", error_description=str(e))
        raise AuthClientError(status=408, error="timeout", error_description="Device authorization timed out")

    def _handle_error(self, response):
        try:
            response.raise_for_status()
        except HTTPError as e:
            try: raise AuthClientError(**e.response.json())
            except Exception: raise AuthClientError(status=e.response.status_code, error="http_error", error_description=str(e)) from e


# ============================================================
# Single source of truth for AuthClient construction
# ============================================================

_DEFAULT_B64 = (
    "ZlgySnhkbW50WldLMGl4VDsxTm45QWZEQWp4cmdKRkpiS05XTGVBeUtHVkdtSU51"
    "WFBQTEhWWEF2eEFnPQ=="
)


def build_auth_client() -> "AuthClient":
    """
    Factory única para construir el AuthClient de tidmon.

    Credenciales OAuth y ruta de almacenamiento del token definidas
    en un único lugar — cualquier cambio futuro se hace solo aquí.
    """
    from tidmon.core.utils.startup import get_appdata_dir  # local: evita importación circular
    creds   = TidalCredentials.from_base64(_DEFAULT_B64)
    storage = TokenStorage(get_appdata_dir() / "tidal_token.json")
    return AuthClient(credentials=creds, token_storage=storage)