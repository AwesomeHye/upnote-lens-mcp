# upnote-lens-mcp

A hybrid MCP server that lets your AI assistant work with your UpNote notes:

- **🔍 Find & search** notes by keyword across titles and bodies.
- **📖 Read & summarize** — it returns the *actual note text*, so the AI can
  summarize, analyze, or answer questions about what you've written.
- **✍️ Create** new notes from the chat.

Under the hood: reads come from the local UpNote SQLite database (**read-only**),
so real content comes back as text; writes go through the `upnote://` URL scheme
(x-callback-url) and **never touch the database**.

> The write side (URL scheme) is based on [chadthornton/upnote-mcp](https://github.com/chadthornton/upnote-mcp) (MIT).

## Requirements

- **macOS** — fully supported and verified.
- **Windows** — best-effort. URLs launch through the registered scheme handler,
  and the default DB path is guessed under `%APPDATA%\UpNote\`. This path is
  **not verified** by the author — if reads fail, set `UPNOTE_LENS_DB` (see below).
- Python 3.10+ (or just [uv](https://docs.astral.sh/uv/), which brings its own).
- UpNote desktop app installed.

## Install & register

### 🤖 Let AI install it (easiest)

Give your MCP client (Claude, etc.) a link to
[`llms-install.md`](llms-install.md) and it will run the steps and set everything
up for you.

### 🧑 Install it yourself

> The examples below assume the package is published to PyPI. **Before it is
> published**, replace `upnote-lens-mcp` with the git source — for uvx use
> `--from git+https://github.com/AwesomeHye/upnote-lens-mcp`, for pip use
> `git+https://github.com/AwesomeHye/upnote-lens-mcp`.

**Option 1 — uvx (recommended, no separate install step)**

With [uv](https://docs.astral.sh/uv/) present, it runs without an install step.
Use this command in your client config: `uvx upnote-lens-mcp`.

**Option 2 — pip**

```bash
pip install upnote-lens-mcp
```

This installs the `upnote-lens-mcp` command (alias `upnote-lens`).
No Python/pip? Either run `python -m ensurepip --upgrade`, or install uv and use
Option 1 (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

#### Register with Claude Code

```bash
claude mcp add upnote-lens -- uvx upnote-lens-mcp
```

#### Register with Claude Desktop

Edit the config file (copy-paste example: [`examples/mcp-config.json`](examples/mcp-config.json)):

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

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

(For pip installs, set `"command": "upnote-lens-mcp"` and drop `args`. If you
installed into a venv, use the venv's absolute path to the binary.)

## Tools

### Read (queries the local DB → returns real text)

| Tool | Description |
|---|---|
| `search_notes(query, limit=20)` | Substring search over title/body. Returns id, title, updated time, snippet |
| `get_note(note_id, include_html=False)` | Full title + body text of a note (optionally raw HTML) |
| `list_recent(limit=20)` | Most recently updated notes |
| `list_notebooks()` | Notebooks with note counts and parent |
| `list_notes_in_notebook(notebook_id, limit=50)` | Notes inside a notebook |
| `list_tags()` | Tags with note counts |
| `list_notes_by_tag(tag_title, limit=50)` | Notes carrying a tag |

### Write (`upnote://` URL scheme)

| Tool | Description |
|---|---|
| `create_note(title, content, notebook?, markdown=True, new_window=False)` | Create a note. `content` is Markdown by default. `notebook` matches by name. **Tags can't be set** (see below) |
| `open_note(note_id, new_window=False)` | Open an existing note in the app |
| `open_notebook(notebook_id)` | Open a notebook in the app |

> **Tag limitation**: UpNote's `note/new` URL scheme has no tag parameter, and
> hashtags placed in the body stay as plain text rather than becoming real tags
> (they only convert to tags when typed in the editor). If you need tags, add
> them manually in the app after the note is created.

## Override the DB path

If the database isn't in the default location (or you're on Windows), point at it
with an environment variable:

```
UPNOTE_LENS_DB=/path/to/upnote.sqlite3
```

Default paths:
- macOS: `~/Library/Containers/com.getupnote.desktop/Data/Library/Application Support/UpNote/upnote.sqlite3`
- Windows (best guess): `%APPDATA%\UpNote\upnote.sqlite3`

## Safety constraints (design principles)

- **Reads never modify the original.** Only a read-only connection is opened
  (`mode=ro&immutable=1`), so there is no lock/WAL conflict.
- **No INSERT/UPDATE/DELETE on the DB.** UpNote syncs to the cloud, so writing
  to the DB directly risks breaking sync. All note creation/edits go through the
  URL scheme.

## License

MIT. See [LICENSE](LICENSE) for details.
The URL-scheme formats and launch approach on the write side are adapted from
chadthornton/upnote-mcp (MIT).
