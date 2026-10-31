# instagrapi-mcp

An MCP (Model Context Protocol) server that wraps [instagrapi](https://github.com/subzeroid/instagrapi) — the unofficial Instagram private API — into 34 ready-to-use tools for AI agents. Works with OpenClaw, Claude Desktop, Cursor, and any MCP client. Transport: **stdio**.

## Setup

```bash
git clone https://github.com/rayenking/instagrapi-mcp
cd instagrapi-mcp
python3 -m venv .venv
.venv/bin/pip install -e .
```

Requires Python ≥ 3.11.

### Data & session

All state lives in `~/.instagrapi-mcp/` (override with the `INSTAGRAPI_MCP_DATA_DIR` env var):

| File | Contents |
|---|---|
| `session.json` | instagrapi session (cookies, device, uuids) |
| `credentials.json` | username + password (chmod 600) — only written by `ig_login(remember=true)`, used for silent relogin |
| `downloads/` | output of `ig_media_download` |

## Usage

1. The agent calls `ig_login(username, password)` — if the account has 2FA enabled, the tool responds with instructions; ask the user for their TOTP code and call again with `verification_code`. Password-free alternative: `ig_login_sessionid(sessionid)`.
2. All `ig_*` tools are then available. On session expiry the server auto-relogs-in (when credentials are stored); otherwise the agent is asked to log in again.
3. `ig_logout()` clears both the Instagram session and locally stored credentials.

## Tools (34)

| Group | Tools |
|---|---|
| Auth | `ig_login`, `ig_login_sessionid`, `ig_logout`, `ig_whoami`, `ig_check_session` |
| User | `ig_user_info`, `ig_user_id_from_username`, `ig_search_users`, `ig_user_followers`, `ig_user_following`, `ig_follow`, `ig_unfollow` |
| Media | `ig_user_medias`, `ig_media_info`, `ig_media_download`, `ig_media_likers`, `ig_media_comments`, `ig_media_like`, `ig_media_unlike`, `ig_comment`, `ig_media_delete` |
| Upload | `ig_upload_photo`, `ig_upload_video`, `ig_upload_story_photo`, `ig_upload_story_video` |
| DM | `ig_dm_threads`, `ig_dm_messages`, `ig_dm_send`, `ig_dm_reply`, `ig_dm_send_media` |
| Discovery | `ig_hashtag_info`, `ig_hashtag_medias_top`, `ig_hashtag_medias_recent`, `ig_user_stories` |

Behavior notes:

- **Agent-readable errors**: every failure returns `{"ok": false, "error": "<message + suggested action>"}` (rate limit, 2FA, private account, …) — never a raw traceback.
- **Flexible references**: the `user`/`media` parameters accept a username (`@natgeo`), numeric ID, post URL, or short code.
- **Local files**: uploads require files on the machine running the server; downloads are written to the server's data folder.
- **Throttling**: the client is created with `delay_range=[1, 3]` seconds between requests. Write actions (like/follow/comment/post/DM) can still trigger Instagram limits if used aggressively — use sparingly.

## OpenClaw integration

Add to `openclaw.json` (the `mcp.servers` block; adjust the absolute path):

```json
{
  "mcp": {
    "servers": {
      "instagram": {
        "command": "/path/to/instagrapi-mcp/.venv/bin/python",
        "args": ["-m", "instagrapi_mcp"]
      }
    }
  }
}
```

Or via CLI: `openclaw mcp add instagram -- /path/to/instagrapi-mcp/.venv/bin/python -m instagrapi_mcp`, then verify with `openclaw mcp probe instagram`.

## Other MCP clients (Claude Desktop, Cursor, etc.)

```json
{
  "mcpServers": {
    "instagram": {
      "command": "/path/to/instagrapi-mcp/.venv/bin/python",
      "args": ["-m", "instagrapi_mcp"]
    }
  }
}
```

## Risks & limitations

- This uses an **unofficial API** — Instagram may trigger challenges/2FA/account blocks. Use it on your own account and avoid aggressive automation.
- Interactive features (selfie captcha, "was this you" challenges) cannot be solved server-side; resolve them in the mobile app and retry.
- Video upload auto-generates a thumbnail — this needs the `imageio-ffmpeg` dependency (`[video]` extra), or pass `thumbnail` manually.

## License

[MIT](LICENSE)
