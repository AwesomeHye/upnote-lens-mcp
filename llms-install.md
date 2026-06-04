# upnote-lens-mcp — AI agent install guide

To the AI agent (Claude, etc.) reading this: follow the steps below to install
and register **upnote-lens-mcp** into the user's MCP client. If any step fails,
stop, tell the user what is blocking you, and wait for instructions. Get the
user's consent before running external commands or editing config files.

Repository: `https://github.com/AwesomeHye/upnote-lens-mcp`

---

## 0. Preconditions (stop if not met)

1. **OS**: macOS (fully supported) or Windows (best-effort). Stop on anything else.
2. **Is the UpNote desktop app installed?**
   - macOS DB: `~/Library/Containers/com.getupnote.desktop/Data/Library/Application Support/UpNote/upnote.sqlite3`
   - Windows DB (best guess, unverified): `%APPDATA%\UpNote\upnote.sqlite3`
   - If the app/DB isn't found, stop and tell the user to install UpNote (or set
     `UPNOTE_LENS_DB` to the real DB path, especially on Windows).

## 1. Get a runner (uv) — recommended path

1. Check uv with `uv --version`.
2. If missing, get the user's consent and install:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   (uv brings its own Python, so no separate Python install is needed.)

> If the user already uses pip, `pip install upnote-lens-mcp` (after publish) or
> `pip install git+https://github.com/AwesomeHye/upnote-lens-mcp` (before publish)
> also works. In that case register with `command` set to `"upnote-lens-mcp"`.

## 2. Identify the MCP client

- If the `claude` CLI exists → **Claude Code** path (3-A).
- Otherwise check for the Claude Desktop config file → **Claude Desktop** path (3-B).
  - `~/Library/Application Support/Claude/claude_desktop_config.json`
- If neither, or a different client, ask the user which client they use.

## 3. Register

The following assumes the package is **published to PyPI**. Before it is
published, replace the `upnote-lens-mcp` argument with
`--from git+https://github.com/AwesomeHye/upnote-lens-mcp upnote-lens-mcp`.

### 3-A. Claude Code

After publish:
```bash
claude mcp add upnote-lens -- uvx upnote-lens-mcp
```

Before publish (git source):
```bash
claude mcp add upnote-lens -- uvx --from git+https://github.com/AwesomeHye/upnote-lens-mcp upnote-lens-mcp
```

### 3-B. Claude Desktop

Read `claude_desktop_config.json` and **merge** into `mcpServers` (preserve
existing entries, do not overwrite). Create the file if it doesn't exist.

After publish:
```json
{
  "mcpServers": {
    "upnote-lens": {
      "command": "uvx",
      "args": ["upnote-lens-mcp"]
    }
  }
}
```

Before publish (git source):
```json
{
  "mcpServers": {
    "upnote-lens": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/AwesomeHye/upnote-lens-mcp", "upnote-lens-mcp"]
    }
  }
}
```

After editing, tell the user to restart Claude Desktop.

## 4. (Optional) Override the DB path

If the DB isn't in the default location, add it to the server's `env`:
```json
"env": { "UPNOTE_LENS_DB": "/path/to/upnote.sqlite3" }
```
For Claude Code: `claude mcp add ... -e UPNOTE_LENS_DB=/path/to/upnote.sqlite3`

## 5. Verify

- Claude Code: check that `upnote-lens` appears in `claude mcp list`.
- Once the tools are connected, call `list_recent(limit=3)` or
  `search_notes("test", 3)` and confirm real note text comes back.
- If the tools don't show up: check whether the client was restarted, look for
  typos in `command`/`args`, confirm uv is installed, and (before publish) verify
  the git source form.

When done, briefly tell the user about the available tools (7 read + 3 write) and
note that writes launch the app to create/open notes.
