"""User tools: profile info, search, followers/following, follow/unfollow."""

from .. import mcp
from .. import state
from ..resolve import resolve_user_id
from ..serializers import to_dict


@mcp.tool()
@state.tool
def ig_user_info(user: str) -> dict:
    """Info lengkap profil Instagram. Terima username ('natgeo', '@natgeo') atau user ID numerik."""
    cl = state.require_client()
    if str(user).strip().lstrip("@").isdigit():
        return to_dict(cl.user_info(str(user).strip())) | {"ok": True}
    return to_dict(cl.user_info_by_username(str(user).strip().lstrip("@"))) | {"ok": True}


@mcp.tool()
@state.tool
def ig_user_id_from_username(username: str) -> dict:
    """Konversi username ke user ID (pk) numerik."""
    cl = state.require_client()
    return {"ok": True, "username": username, "user_id": str(cl.user_id_from_username(username))}


@mcp.tool()
@state.tool
def ig_search_users(query: str, count: int = 20) -> dict:
    """Cari user berdasarkan nama/username. Return daftar user singkat."""
    cl = state.require_client()
    return {"ok": True, "users": to_dict(cl.search_users(query, count=count))}


@mcp.tool()
@state.tool
def ig_user_followers(user: str, amount: int = 100) -> dict:
    """Daftar followers. amount=0 berarti SEMUA (respons bisa sangat besar) - hati-hati."""
    cl = state.require_client()
    user_id = resolve_user_id(cl, user)
    followers = cl.user_followers(user_id, amount=amount)
    return {"ok": True, "user_id": user_id, "count": len(followers), "followers": to_dict(list(followers.values()))}


@mcp.tool()
@state.tool
def ig_user_following(user: str, amount: int = 100) -> dict:
    """Daftar akun yang di-follow. amount=0 berarti SEMUA (respons bisa sangat besar)."""
    cl = state.require_client()
    user_id = resolve_user_id(cl, user)
    following = cl.user_following(user_id, amount=amount)
    return {"ok": True, "user_id": user_id, "count": len(following), "following": to_dict(list(following.values()))}


@mcp.tool()
@state.tool
def ig_follow(user: str) -> dict:
    """Follow user (username atau ID)."""
    cl = state.require_client()
    user_id = resolve_user_id(cl, user)
    return {"ok": bool(cl.user_follow(user_id)), "user_id": user_id}


@mcp.tool()
@state.tool
def ig_unfollow(user: str) -> dict:
    """Unfollow user (username atau ID)."""
    cl = state.require_client()
    user_id = resolve_user_id(cl, user)
    return {"ok": bool(cl.user_unfollow(user_id)), "user_id": user_id}
