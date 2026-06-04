# upnote-lens-mcp

A hybrid MCP server that acts as a "lens" into your UpNote notes.

- **Read** — queries the local UpNote SQLite database **read-only** and returns
  the actual note text, so search and content reads come back as real text.
- **Write** — note creation and navigation go through the `upnote://` URL scheme
  (x-callback-url). It never writes to the database.

> The write side (URL scheme) is based on [chadthornton/upnote-mcp](https://github.com/chadthornton/upnote-mcp) (MIT).

## Why combine the two

The original upnote-mcp only uses the URL scheme, so it can create and search
notes but cannot return note content — searching just opens results in the app,
no text comes back. UpNote stores note bodies as plain text in a local SQLite
database, so this project reads directly from there for content, and leaves
writes to the safer URL scheme.

## Requirements

- macOS (the write tools launch `upnote://` via `open`)
- Python 3.10+
- UpNote desktop app installed (`com.getupnote.desktop`)

## Install & register

> **🤖 Let AI do it**: give your MCP client (Claude, etc.) a link to
> [`llms-install.md`](llms-install.md) and it will follow the steps and install
> this for you.

> The examples below assume the package is published to PyPI. **Before it is
> published**, replace `upnote-lens-mcp` with the git source — for uvx use
> `--from git+https://github.com/AwesomeHye/upnote-lens-mcp`, for pip use
> `git+https://github.com/AwesomeHye/upnote-lens-mcp`.

### Option 1 — uvx (recommended, no separate install step)

With [uv](https://docs.astral.sh/uv/) present, it runs without an install step.

Claude Desktop — `~/Library/Application Support/Claude/claude_desktop_config.json`
(copy-paste example: [`examples/mcp-config.json`](examples/mcp-config.json)):

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

Claude Code:

```bash
claude mcp add upnote-lens -- uvx upnote-lens-mcp
```

### Option 2 — pip

```bash
pip install upnote-lens-mcp
```

This installs the `upnote-lens-mcp` command (alias `upnote-lens`).

```json
{
  "mcpServers": {
    "upnote-lens": {
      "command": "upnote-lens-mcp"
    }
  }
}
```

Claude Code: `claude mcp add upnote-lens -- upnote-lens-mcp`

> If you installed into a venv, set `command` to the venv's absolute path
> (`/path/.venv/bin/upnote-lens-mcp`).

### If you don't have Python/pip

- Python but no `pip`: `python -m ensurepip --upgrade`
- No Python at all: install uv and use **Option 1** (uv brings its own Python).
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

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

If the database isn't in the default location, set an environment variable.

```
UPNOTE_LENS_DB=/path/to/upnote.sqlite3
```

Default path:
`~/Library/Containers/com.getupnote.desktop/Data/Library/Application Support/UpNote/upnote.sqlite3`

## Safety constraints (design principles)

- **Reads never modify the original.** Only a read-only connection is opened
  (`mode=ro&immutable=1`), so there is no lock/WAL conflict.
- **No INSERT/UPDATE/DELETE on the DB.** UpNote syncs to the cloud, so writing
  to the DB directly risks breaking sync. All note creation/edits go through the
  URL scheme.

## Implementation notes (verified facts)

- Valid-note filter: `trashed=0 AND deleted=0 AND COALESCE(isTemplate,0)=0`
  (`isTemplate` is NULL rather than 0, so `isTemplate=0` would drop everything).
- Timestamps are millisecond epochs: `datetime(updatedAt/1000,'unixepoch','localtime')`.
- The note↔notebook relationship lives in `notebooks.notes` (a JSON array of note
  ids) as the source of truth. `notes.notebookLinks` is empty.

## License

MIT. See [LICENSE](LICENSE) for details.
The URL-scheme formats and launch approach on the write side are adapted from
chadthornton/upnote-mcp (MIT).
