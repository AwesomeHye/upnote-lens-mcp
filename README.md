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

## Usage

Once it's registered, just talk to your AI assistant in plain language — it
picks the right tool for you. No commands or syntax to memorize. For example:

- "Summarize my UpNote notes about the Q3 roadmap."
- "Find notes where I mentioned Postgres tuning and pull out the key points."
- "What did I write about onboarding last month?"
- "Show me my 5 most recent notes."
- "Create a note titled 'Standup 6/4' with today's three priorities."

Reading, searching, summarizing, and creating all happen through natural
conversation.

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

Pick the first option that fits what you already have. Each option includes how
to register it in Claude.

> **Claude Desktop config file** (referenced in each option):
> - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
> - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

#### Option 1 — with uv (recommended)

Requires [uv](https://docs.astral.sh/uv/) installed once
(`brew install uv`, or `curl -LsSf https://astral.sh/uv/install.sh | sh`).
After that there's **no package install step** — `uvx` downloads, caches, and
runs upnote-lens-mcp on demand.

Claude Code:
```bash
claude mcp add upnote-lens -- uvx upnote-lens-mcp
```
Claude Desktop:
```json
{ "mcpServers": { "upnote-lens": { "command": "uvx", "args": ["upnote-lens-mcp"] } } }
```

#### Option 2 — with pip (if you don't have uv)

```bash
pip install upnote-lens-mcp
```

Claude Code:
```bash
claude mcp add upnote-lens -- upnote-lens-mcp
```
Claude Desktop:
```json
{ "mcpServers": { "upnote-lens": { "command": "upnote-lens-mcp" } } }
```

#### Option 3 — from GitHub over HTTPS (if you don't have pip)

When you can't use PyPI/pip, install straight from the repo with uv. (No uv yet?
`curl -LsSf https://astral.sh/uv/install.sh | sh`.)

Claude Code:
```bash
claude mcp add upnote-lens -- uvx --from git+https://github.com/AwesomeHye/upnote-lens-mcp upnote-lens-mcp
```
Claude Desktop:
```json
{ "mcpServers": { "upnote-lens": { "command": "uvx", "args": ["--from", "git+https://github.com/AwesomeHye/upnote-lens-mcp", "upnote-lens-mcp"] } } }
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

If the database isn't in the default location (or you're on Windows), point at it
with an environment variable:

```
UPNOTE_LENS_DB=/path/to/upnote.sqlite3
```

Default paths:
- macOS: `~/Library/Containers/com.getupnote.desktop/Data/Library/Application Support/UpNote/upnote.sqlite3`
- Windows (best guess): `%APPDATA%\UpNote\upnote.sqlite3`

## License

MIT. See [LICENSE](LICENSE) for details.
The URL-scheme formats and launch approach on the write side are adapted from
chadthornton/upnote-mcp (MIT).
