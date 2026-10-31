"""instagrapi-mcp: MCP server exposing Instagram via instagrapi."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "instagram",
    instructions=(
        "Instagram tools backed by instagrapi. Login first with ig_login "
        "(username/password, verification_code if 2FA) or ig_login_sessionid, "
        "then use the ig_* tools. Write actions (like, follow, comment, post, DM) "
        "are rate-limited client-side; use them sparingly."
    ),
)

__all__ = ["mcp"]
