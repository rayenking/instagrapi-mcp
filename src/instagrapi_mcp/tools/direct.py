"""Direct Message tools: threads, messages, send text/media."""

from pathlib import Path

from .. import mcp
from .. import state
from ..resolve import to_ints
from ..serializers import to_dict


@mcp.tool()
@state.tool
def ig_dm_threads(amount: int = 10) -> dict:
    """Daftar thread DM terbaru."""
    cl = state.require_client()
    threads = cl.direct_threads(amount=amount)
    return {"ok": True, "count": len(threads), "threads": to_dict(threads)}


@mcp.tool()
@state.tool
def ig_dm_messages(thread_id: str, amount: int = 20) -> dict:
    """Ambil pesan dalam satu thread DM."""
    cl = state.require_client()
    messages = cl.direct_messages(int(thread_id), amount=amount)
    return {"ok": True, "thread_id": thread_id, "count": len(messages), "messages": to_dict(messages)}


@mcp.tool()
@state.tool
def ig_dm_send(text: str, user_ids: list[str] = [], thread_ids: list[str] = []) -> dict:
    """Kirim pesan teks DM. Isi user_ids (penerima baru) atau thread_ids (lanjut thread lama)."""
    cl = state.require_client()
    if not user_ids and not thread_ids:
        return {"ok": False, "error": "Isi minimal salah satu: user_ids atau thread_ids."}
    message = cl.direct_send(text, user_ids=to_ints(user_ids), thread_ids=to_ints(thread_ids))
    return to_dict(message) | {"ok": True}


@mcp.tool()
@state.tool
def ig_dm_reply(thread_id: str, text: str) -> dict:
    """Balas pesan terakhir dalam sebuah thread DM."""
    cl = state.require_client()
    message = cl.direct_answer(int(thread_id), text)
    return to_dict(message) | {"ok": True}


@mcp.tool()
@state.tool
def ig_dm_send_media(path: str, user_ids: list[str] = [], thread_ids: list[str] = []) -> dict:
    """Kirim file media via DM (foto: jpg/png, video: mp4). File harus ada di mesin server."""
    cl = state.require_client()
    if not user_ids and not thread_ids:
        return {"ok": False, "error": "Isi minimal salah satu: user_ids atau thread_ids."}
    file = Path(path).expanduser()
    if not file.is_file():
        raise FileNotFoundError(f"File tidak ditemukan: {file}")
    if file.suffix.lower() in (".mp4", ".mov", ".avi", ".mkv"):
        message = cl.direct_send_video(file, user_ids=to_ints(user_ids), thread_ids=to_ints(thread_ids))
    else:
        message = cl.direct_send_photo(file, user_ids=to_ints(user_ids), thread_ids=to_ints(thread_ids))
    return to_dict(message) | {"ok": True}
