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

## One-shot prompt for your AI agent

Don't want to follow the steps manually? Copy the prompt below and send it to your agent (OpenClaw, Claude, ...). The agent will install the server, register it, and log you in — you only answer its questions.

```text
Install and connect the "instagrapi-mcp" Instagram MCP server for me.

SETUP
1. Clone and install (create the venv fresh; do not install into the repo clone of instagrapi):
     git clone https://github.com/rayenking/instagrapi-mcp ~/Tools/instagrapi-mcp
     cd ~/Tools/instagrapi-mcp
     python3 -m venv .venv
     .venv/bin/pip install -e .
2. Register the server in my MCP client config:
   - OpenClaw: add under "mcp.servers" in ~/.openclaw/openclaw.json:
       "instagram": {
         "command": "<absolute path to this project>/.venv/bin/python",
         "args": ["-m", "instagrapi_mcp"]
       }
     then restart/reload the gateway.
   - Any other MCP client (Claude Desktop, Cursor, ...): add the same command+args
     under its "mcpServers" key instead.
3. Verify: start a session, list the tools, and confirm you can see 34 tools whose
   names start with "ig_". If tools are missing, re-check the command path before
   asking me anything.

LOGIN (ask me for credentials when you get here)
4. Ask me for my Instagram username and password, then call the "ig_login" tool.
   - If the result contains "TwoFactorRequired", ask me for the 6-digit code from my
     authenticator app and immediately call ig_login again with verification_code set.
     Use each code within seconds of me sending it (TOTP expires ~30s).
   - Keep remember=true so future session expiries relogin silently without asking me.
5. Confirm with "ig_whoami" who is logged in, then give me a one-line summary of the
   tool groups (auth / user / media / upload / DM / discovery).

RULES FOR USING THE INSTAGRAM TOOLS
- Every tool returns JSON. If "ok" is false, read the "error" hint and act on it
  (e.g. rate-limit -> wait, private account -> tell me). Never retry blindly.
- After a rate-limit error, wait at least 5-10 minutes before any further call.
- Do NOT mass like / follow / comment or post in bursts. Space write actions out;
  aggressive automation can get my account limited or banned.
- Upload/download tools operate on files on this machine only.
- If a login error persists after a new verification_code, stop and tell me instead
  of guessing.
```

After that, everyday use needs no prompt — just ask naturally ("download my last 3 posts", "DM @someone hello", "post this photo as a story").

## Risks & limitations

- This uses an **unofficial API** — Instagram may trigger challenges/2FA/account blocks. Use it on your own account and avoid aggressive automation.
- Interactive features (selfie captcha, "was this you" challenges) cannot be solved server-side; resolve them in the mobile app and retry.
- Video upload auto-generates a thumbnail — this needs the `imageio-ffmpeg` dependency (`[video]` extra), or pass `thumbnail` manually.

## License

[MIT](LICENSE)
