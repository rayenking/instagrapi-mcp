"""Auth tools: login (password + 2FA), sessionid login, logout, session status."""

from .. import mcp
from .. import state
from ..serializers import to_dict


def _whoami_payload(cl) -> dict:
    """Best-effort identity info for the current session."""
    info: dict = {"ok": True, "user_id": cl.user_id}
    try:
        account = cl.account_info()
        info.update(
            {
                "username": account.username,
                "full_name": account.full_name,
                "is_private": account.is_private,
                "is_business": account.is_business,
                "is_verified": account.is_verified,
            }
        )
    except Exception:
        info["username"] = None
    return info


@mcp.tool()
@state.tool
def ig_login(username: str, password: str, verification_code: str = "", remember: bool = True) -> dict:
    """Login ke Instagram dengan username + password.

    Jika akun memakai 2FA, panggilan pertama akan gagal dengan pesan TwoFactorRequired;
    minta kode TOTP (atau backup code) ke user lalu panggil lagi dengan verification_code.
    remember=True menyimpan kredensial di file lokal (0600) agar session expired
    bisa relogin otomatis tanpa bertanya lagi.
    """
    cl = state._new_client()
    cl.login(username, password, verification_code=verification_code)
    state.dump_session(cl)
    if remember:
        state.write_credentials(username, password)
    return _whoami_payload(cl)


@mcp.tool()
@state.tool
def ig_login_sessionid(sessionid: str) -> dict:
    """Login pakai sessionid cookie dari browser (tanpa menyimpan password).

    Ambil nilai cookie "sessionid" dari instagram.com yang sudah login di browser,
    lalu paste di sini. Tidak ada auto-relogin saat session expired - paste ulang.
    """
    cl = state._new_client()
    cl.login_by_sessionid(sessionid)
    state.dump_session(cl)
    return _whoami_payload(cl)


@mcp.tool()
@state.tool
def ig_logout() -> dict:
    """Logout dari Instagram dan hapus session + kredensial tersimpan."""
    cl = state.get_client()
    result: dict = {}
    try:
        cl.logout()
        result["instagram_logout"] = True
    except Exception:
        result["instagram_logout"] = False
    state.clear_session()
    result["ok"] = True
    result["local_session_cleared"] = True
    return result


@mcp.tool()
@state.tool
def ig_whoami() -> dict:
    """Cek status session: siapa yang login sekarang, atau belum login sama sekali."""
    cl = state.require_client()
    return _whoami_payload(cl)


@mcp.tool()
@state.tool
def ig_check_session() -> dict:
    """Validasi session ke server Instagram (panggilan account_info ringan)."""
    cl = state.require_client()
    return to_dict(cl.account_info()) | {"ok": True}
