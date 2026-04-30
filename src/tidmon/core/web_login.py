"""
tidmon auth web-login — Token capture via existing Chrome (CDP) or Playwright fallback.

Primary method: connects to Chrome running with --remote-debugging-port=9222.
Fallback: launches Playwright Chromium with persistent session.
"""
from __future__ import annotations
import asyncio
import base64
import json
import logging
import time
from rich.console import Console

from tidmon.core.auth_models import AuthData
from tidmon.core.auth_client import save_auth_data, load_auth_data
from tidmon.core.utils.startup import get_appdata_dir

console = Console()
log = logging.getLogger(__name__)

CDP_URL = "http://127.0.0.1:9222"


def _session_dir():
    return get_appdata_dir() / "browser_session"


def _session_exists() -> bool:
    d = _session_dir()
    return d.exists() and any(d.iterdir())


def _decode_jwt_payload(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.b64decode(payload).decode())
    except Exception:
        return {}


def _is_chrome_debugging_available() -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=1)
        return True
    except Exception:
        return False


async def _capture_via_cdp() -> AuthData | None:
    """Capture token from existing Chrome via CDP Network events."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return None

    captured: dict = {}

    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            contexts = browser.contexts
            if not contexts:
                await browser.close()
                return None

            context = contexts[0]
            page = next((pg for pg in context.pages if "tidal.com" in pg.url), None)
            if not page:
                page = await context.new_page()

            cdp = await context.new_cdp_session(page)
            await cdp.send("Network.enable")

            def on_network_request(event):
                url = event.get("request", {}).get("url", "")
                headers = event.get("request", {}).get("headers", {})
                if "api.tidal.com" in url and not captured:
                    auth = headers.get("authorization") or headers.get("Authorization", "")
                    if auth.startswith("Bearer "):
                        captured["token"] = auth[7:]

            cdp.on("Network.requestWillBeSent", on_network_request)
            await page.goto("https://listen.tidal.com/")

            for i in range(20):
                if captured:
                    break
                if i == 5:
                    try:
                        await page.evaluate(
                            "() => fetch('https://api.tidal.com/v1/sessions',"
                            " {credentials: 'include'})"
                        )
                    except Exception:
                        pass
                await asyncio.sleep(1)

            await cdp.detach()
            await browser.close()

    except Exception as e:
        log.debug(f"CDP capture failed: {e}")
        return None

    if not captured:
        return None

    return _build_auth_data(captured["token"])


async def _capture_via_playwright(silent: bool = False) -> AuthData | None:
    """Fallback: Playwright Chromium with persistent session."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        console.print("[red]Playwright no instalado.[/]")
        return None

    session_dir = _session_dir()
    session_dir.mkdir(parents=True, exist_ok=True)
    captured: dict = {}

    async def _run(headless: bool, timeout: int) -> bool:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
                no_viewport=True if not headless else None,
                viewport={"width": 1280, "height": 800} if headless else None,
            )
            page = context.pages[0] if context.pages else await context.new_page()

            def on_request(request):
                if "api.tidal.com" in request.url and not captured:
                    auth = request.headers.get("authorization", "")
                    if auth.startswith("Bearer "):
                        captured["token"] = auth[7:]

            context.on("request", on_request)
            await page.goto("https://listen.tidal.com/")

            for i in range(timeout):
                if captured:
                    break
                if i == 3:
                    try:
                        await page.evaluate(
                            "() => fetch('https://api.tidal.com/v1/sessions',"
                            " {credentials: 'include'})"
                        )
                    except Exception:
                        pass
                await asyncio.sleep(1)

            await context.close()
        return bool(captured)

    if silent:
        success = await _run(headless=True, timeout=15)
        if not success:
            console.print("[yellow]Token expirado — abriendo browser para re-autenticar...[/]")
            await _run(headless=False, timeout=180)
    else:
        console.print("[dim]Esperando token de api.tidal.com...[/]")
        await _run(headless=False, timeout=180)

    return _build_auth_data(captured["token"]) if captured else None


def _build_auth_data(token: str) -> AuthData | None:
    payload = _decode_jwt_payload(token)
    if not payload:
        return None
    return AuthData(
        token=token,
        refresh_token=None,
        expires_at=payload.get("exp", int(time.time()) + 14400),
        user_id=str(payload.get("uid", "")),
        country_code=payload.get("cc", "US"),
    )


_refresh_lock = asyncio.Lock()
_last_refresh_attempt: float = 0.0


async def auto_refresh_if_needed(threshold_minutes: int = 30) -> bool:
    """
    Called automatically before downloads.
    CDP first, Playwright fallback. Lock prevents concurrent refresh storms.
    """
    global _last_refresh_attempt

    auth = load_auth_data()
    if not auth.token:
        return False

    minutes_left = (auth.expires_at - time.time()) / 60
    if minutes_left > threshold_minutes:
        return False

    if time.time() - _last_refresh_attempt < 60:
        return False

    if _refresh_lock.locked():
        async with _refresh_lock:
            pass
        return False

    async with _refresh_lock:
        auth = load_auth_data()
        if (auth.expires_at - time.time()) / 60 > threshold_minutes:
            return False

        _last_refresh_attempt = time.time()
        minutes_left = (auth.expires_at - time.time()) / 60
        log.info(f"Token expira en {minutes_left:.0f}min — auto-refresh...")
        console.print(f"[yellow]Token expira en {minutes_left:.0f} min — refrescando...[/]")

        auth_data = None

        try:
            if _is_chrome_debugging_available():
                auth_data = await _capture_via_cdp()
        except Exception as e:
            log.debug(f"CDP refresh failed: {e}")

        if not auth_data and _session_exists():
            try:
                auth_data = await _capture_via_playwright(silent=True)
            except Exception as e:
                log.debug(f"Playwright refresh failed: {e}")

        if auth_data:
            save_auth_data(auth_data)
            exp_dt = time.strftime("%H:%M", time.localtime(auth_data.expires_at))
            console.print(f"[green]Token renovado (expira {exp_dt})[/]")
            return True

        log.warning("Auto-refresh fallo — continuando con token expirado.")
        return False


def web_login():
    """Login automatico via browser — captura token de tidal.com."""
    if _is_chrome_debugging_available():
        console.print("[bold cyan]Chrome detectado — capturando token via CDP...[/]\n")
        auth_data = asyncio.run(_capture_via_cdp())
        if auth_data:
            _save_and_print(auth_data)
            return
        console.print("[yellow]CDP conecto pero no capturo token. Abriendo Chromium...[/]\n")
    else:
        console.print("[cyan]Abriendo Chromium...[/]\n")

    auth_data = asyncio.run(_capture_via_playwright(silent=False))
    if not auth_data:
        console.print("[red]No se pudo capturar token.[/]")
        return
    _save_and_print(auth_data)


def _save_and_print(auth_data: AuthData):
    save_auth_data(auth_data)
    exp_dt = time.strftime("%Y-%m-%d %H:%M", time.localtime(auth_data.expires_at))
    console.print(f"\n[bold green]Token capturado![/]")
    console.print(f"  Usuario: [cyan]{auth_data.user_id}[/]  Pais: [cyan]{auth_data.country_code}[/]")
    console.print(f"  Expira:  [yellow]{exp_dt}[/]")
