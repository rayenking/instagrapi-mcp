"""Discovery tools: hashtag info/medias, user stories."""

from .. import mcp
from .. import state
from ..resolve import resolve_user_id
from ..serializers import to_dict


@mcp.tool()
@state.tool
def ig_hashtag_info(name: str) -> dict:
    """Info hashtag: jumlah media, dll."""
    cl = state.require_client()
    return to_dict(cl.hashtag_info(name)) | {"ok": True}


@mcp.tool()
@state.tool
def ig_hashtag_medias_top(name: str, amount: int = 12) -> dict:
    """Media terpopuler pada sebuah hashtag."""
    cl = state.require_client()
    medias = cl.hashtag_medias_top(name, amount=amount)
    return {"ok": True, "count": len(medias), "medias": to_dict(medias)}


@mcp.tool()
@state.tool
def ig_hashtag_medias_recent(name: str, amount: int = 12) -> dict:
    """Media terbaru pada sebuah hashtag."""
    cl = state.require_client()
    medias = cl.hashtag_medias_recent(name, amount=amount)
    return {"ok": True, "count": len(medias), "medias": to_dict(medias)}


@mcp.tool()
@state.tool
def ig_user_stories(user: str, amount: int = 0) -> dict:
    """Daftar story aktif seorang user. amount=0 berarti semua story aktif."""
    cl = state.require_client()
    user_id = resolve_user_id(cl, user)
    stories = cl.user_stories(user_id, amount=amount if amount else None)
    return {"ok": True, "user_id": user_id, "count": len(stories), "stories": to_dict(stories)}
