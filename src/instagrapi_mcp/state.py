"""Client lifecycle, session persistence, and the error-capturing tool wrapper."""

import functools
import json
import os
import secrets
from pathlib import Path
from typing import Any, Callable

from instagrapi import Client
from instagrapi import exceptions as igx

from .errors import friendly_error, not_logged_in

DATA_DIR = Path(os.environ.get("INSTAGRAPI_MCP_DATA_DIR", "~/.instagrapi-mcp")).expanduser()
SESSION_FILE = DATA_DIR / "session.json"
CREDENTIALS_FILE = DATA_DIR / "credentials.json"
DOWNLOADS_DIR = DATA_DIR / "downloads"

_client: Client | None = None


class NotLoggedIn(Exception):
    """Raised when a tool needs a session but none exists."""


def _new_client() -> Client:
    """Fresh client with gentle delays and no-stdin challenge handlers.

    Handlers return "" so nothing ever blocks on stdin inside an MCP server;
    the resulting failure is surfaced to the chat as an error instead.
    """
    cl = Client(delay_range=[1, 3])
    cl.challenge_code_handler = lambda username, choice: ""
    cl.change_password_handler = lambda username: ""
    return cl


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path, 0o700)
    except OSError:
        pass
    return path


def get_client() -> Client:
    """Lazily build the client and load the persisted session if present."""
    global _client
    if _client is None:
        _client = _new_client()
        if SESSION_FILE.exists():
            try:
                _client.load_settings(str(SESSION_FILE))
            except Exception:
                pass  # corrupt/unreadable session -> start clean
    return _client


def require_client() -> Client:
    """Client expected to hold a session; raise NotLoggedIn when nothing is stored."""
    cl = get_client()
    if not SESSION_FILE.exists() and not cl.user_id:
        raise NotLoggedIn()
    return cl


def dump_session(cl: Client) -> None:
    _ensure_dir(DATA_DIR)
    cl.dump_settings(str(SESSION_FILE))
    try:
        os.chmod(SESSION_FILE, 0o600)  # berisi cookie sessionid = akses akun
    except OSError:
        pass


def clear_session() -> None:
    """Forget session and stored credentials."""
    for path in (SESSION_FILE, CREDENTIALS_FILE):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
    global _client
    _client = None


def write_credentials(username: str, password: str) -> None:
    _ensure_dir(DATA_DIR)
    fd = os.open(CREDENTIALS_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, json.dumps({"username": username, "password": password}).encode())
    finally:
        os.close(fd)


def read_credentials() -> dict[str, str] | None:
    try:
        data = json.loads(CREDENTIALS_FILE.read_text())
        if data.get("username") and data.get("password"):
            return data
    except (OSError, ValueError):
        pass
    return None


def _try_relogin() -> bool:
    """Silent relogin using stored credentials (called after LoginRequired)."""
    creds = read_credentials()
    if not creds:
        return False
    cl = get_client()
    try:
        if cl.login(creds["username"], creds["password"]):
            dump_session(cl)
            return True
    except Exception:
        return False
    return False


def tool(fn: Callable) -> Callable:
    """Wrap an MCP tool: catch instagrapi errors, auto-relogin once on expired session.

    Tools return plain content on success and {"ok": false, "error": "..."} on failure,
    so the agent can always read and react to the message.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except NotLoggedIn:
            return {"ok": False, "error": not_logged_in()}
        except igx.LoginRequired as exc:
            if _try_relogin():
                try:
                    return fn(*args, **kwargs)
                except Exception as retry_exc:
                    return {"ok": False, "error": friendly_error(retry_exc)}
            return {"ok": False, "error": friendly_error(exc)}
        except Exception as exc:
            return {"ok": False, "error": friendly_error(exc)}

    return wrapper


def downloads_dir() -> Path:
    return _ensure_dir(DOWNLOADS_DIR)


def random_suffix() -> str:
    return secrets.token_hex(3)
