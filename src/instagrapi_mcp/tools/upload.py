"""Upload tools: feed photo/video, story photo/video.

Semua tool upload butuh file yang ADA di mesin tempat MCP server ini berjalan.
"""

from pathlib import Path

from .. import mcp
from .. import state
from ..serializers import to_dict


def _require_file(path: str) -> Path:
    p = Path(path).expanduser()
    if not p.is_file():
        raise FileNotFoundError(f"File tidak ditemukan: {p} (harus ada di mesin tempat server MCP jalan)")
    return p


@mcp.tool()
@state.tool
def ig_upload_photo(path: str, caption: str = "") -> dict:
    """Upload foto ke feed. Format: jpg/jpeg/png/webp."""
    cl = state.require_client()
    file = _require_file(path)
    media = cl.photo_upload(file, caption)
    return to_dict(media) | {"ok": True}


@mcp.tool()
@state.tool
def ig_upload_video(path: str, caption: str = "", thumbnail: str = "") -> dict:
    """Upload video ke feed. Format: mp4. Thumbnail opsional (jpg) - kalau kosong
    dibuat otomatis (butuh dependensi imageio-ffmpeg)."""
    cl = state.require_client()
    file = _require_file(path)
    thumb = _require_file(thumbnail) if thumbnail else None
    media = cl.video_upload(file, caption, thumbnail=thumb)
    return to_dict(media) | {"ok": True}


@mcp.tool()
@state.tool
def ig_upload_story_photo(path: str, caption: str = "") -> dict:
    """Upload foto sebagai story (format jpg/jpeg/png/webp)."""
    cl = state.require_client()
    file = _require_file(path)
    story = cl.photo_upload_to_story(file, caption)
    return to_dict(story) | {"ok": True}


@mcp.tool()
@state.tool
def ig_upload_story_video(path: str, caption: str = "") -> dict:
    """Upload video sebagai story (format mp4)."""
    cl = state.require_client()
    file = _require_file(path)
    story = cl.video_upload_to_story(file, caption)
    return to_dict(story) | {"ok": True}
