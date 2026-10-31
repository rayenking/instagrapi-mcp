"""Resolve flexible references (username/@user, pk, URL, short code) to library IDs."""

from instagrapi import Client


def resolve_user_id(cl: Client, ref: str | int) -> str:
    """Accept 'username', '@username', or numeric pk; return user pk as string."""
    s = str(ref).strip().lstrip("@")
    if s.isdigit():
        return s
    return str(cl.user_id_from_username(s))


def resolve_media_pk(cl: Client, ref: str | int) -> str:
    """Accept numeric pk, a post/reel URL, or an 11-char short code."""
    s = str(ref).strip()
    if s.isdigit():
        return s
    if "instagram.com" in s or "instagr.am" in s:
        return str(cl.media_pk_from_url(s))
    return str(cl.media_pk_from_code(s))


def to_ints(values: list[str | int] | None) -> list[int]:
    return [int(v) for v in (values or [])]
