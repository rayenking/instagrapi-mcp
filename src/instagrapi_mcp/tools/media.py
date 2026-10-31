"""Media tools: feed medias, info, download, likers, comments, like/unlike, delete."""

from pathlib import Path

from .. import mcp
from .. import state
from ..resolve import resolve_media_pk, resolve_user_id
from ..serializers import to_dict


@mcp.tool()
@state.tool
def ig_user_medias(user: str, amount: int = 12) -> dict:
    """Ambil postingan (feed) terbaru seorang user. Return daftar Media."""
    cl = state.require_client()
    user_id = resolve_user_id(cl, user)
    medias = cl.user_medias(user_id, amount=amount)
    return {"ok": True, "user_id": user_id, "count": len(medias), "medias": to_dict(medias)}


@mcp.tool()
@state.tool
def ig_media_info(media: str) -> dict:
    """Info detail satu media. Terima pk numerik, URL post/reel, atau short code."""
    cl = state.require_client()
    pk = resolve_media_pk(cl, media)
    return to_dict(cl.media_info(pk)) | {"ok": True}


@mcp.tool()
@state.tool
def ig_media_download(media: str, folder: str = "") -> dict:
    """Download media (foto/video/album) ke folder lokal.

    Default ke folder downloads milik server. Return daftar path file yang tersimpan.
    """
    cl = state.require_client()
    pk = resolve_media_pk(cl, media)
    target = Path(folder).expanduser() if folder else state.downloads_dir()
    target.mkdir(parents=True, exist_ok=True)
    info = cl.media_info(pk)
    media_type = info.media_type  # 1=photo, 2=video, 8=album
    if media_type == 1:
        files = [cl.photo_download(pk, folder=target)]
    elif media_type == 2:
        files = [cl.video_download(pk, folder=target)]
    elif media_type == 8:
        files = cl.album_download(pk, folder=target)
    else:
        return {"ok": False, "error": f"Tipe media {media_type} belum didukung download di tool ini."}
    return {"ok": True, "media_type": media_type, "files": [str(f) for f in files if f]}


@mcp.tool()
@state.tool
def ig_media_likers(media: str) -> dict:
    """Daftar user yang like sebuah media."""
    cl = state.require_client()
    pk = resolve_media_pk(cl, media)
    likers = cl.media_likers(pk)
    return {"ok": True, "count": len(likers), "likers": to_dict(likers)}


@mcp.tool()
@state.tool
def ig_media_comments(media: str, amount: int = 20) -> dict:
    """Daftar komentar pada sebuah media."""
    cl = state.require_client()
    pk = resolve_media_pk(cl, media)
    comments = cl.media_comments(pk, amount=amount)
    return {"ok": True, "count": len(comments), "comments": to_dict(comments)}


@mcp.tool()
@state.tool
def ig_media_like(media: str) -> dict:
    """Like sebuah media. Gunakan bijak - jangan spam."""
    cl = state.require_client()
    pk = resolve_media_pk(cl, media)
    return {"ok": bool(cl.media_like(pk)), "media_pk": pk}


@mcp.tool()
@state.tool
def ig_media_unlike(media: str) -> dict:
    """Batalkan like pada sebuah media."""
    cl = state.require_client()
    pk = resolve_media_pk(cl, media)
    return {"ok": bool(cl.media_unlike(pk)), "media_pk": pk}


@mcp.tool()
@state.tool
def ig_comment(media: str, text: str, replied_to_comment_id: str = "") -> dict:
    """Post komentar pada sebuah media. replied_to_comment_id opsional untuk reply."""
    cl = state.require_client()
    pk = resolve_media_pk(cl, media)
    comment = cl.media_comment(
        pk, text, replied_to_comment_id=int(replied_to_comment_id) if replied_to_comment_id else None
    )
    return to_dict(comment) | {"ok": True}


@mcp.tool()
@state.tool
def ig_media_delete(media: str) -> dict:
    """Hapus media milik sendiri. Tindakan permanen - pastikan dulu sebelum dipanggil."""
    cl = state.require_client()
    pk = resolve_media_pk(cl, media)
    return {"ok": bool(cl.media_delete(pk)), "media_pk": pk}
