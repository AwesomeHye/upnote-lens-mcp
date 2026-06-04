"""MCP server wiring: expose the read (DB) and write (URL scheme) tools.

Reads return real text pulled from the local SQLite DB. Writes go through the
``upnote://`` URL scheme. Run over stdio via the ``upnote-lens-mcp`` entry point.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import db, writer

mcp = FastMCP("upnote-lens")


# --- read tools (local SQLite, read-only) ----------------------------------


@mcp.tool()
def search_notes(query: str, limit: int = 20) -> list[dict]:
    """Search notes by title/body (case-insensitive substring match).

    Returns matching notes with id, title, last-updated time, and a text
    snippet around the match — actual content, read from the local DB.
    """
    return db.search_notes(query, limit)


@mcp.tool()
def get_note(note_id: str, include_html: bool = False) -> dict:
    """Return a single note's full title and body text by its id.

    Set include_html=true to also get the raw HTML body.
    """
    note = db.get_note(note_id, include_html=include_html)
    return note if note is not None else {"error": f"note not found: {note_id}"}


@mcp.tool()
def list_recent(limit: int = 20) -> list[dict]:
    """List the most recently updated notes (id, title, updated time)."""
    return db.list_recent(limit)


@mcp.tool()
def list_notebooks() -> list[dict]:
    """List all notebooks with their note counts and parent id."""
    return db.list_notebooks()


@mcp.tool()
def list_notes_in_notebook(notebook_id: str, limit: int = 50) -> list[dict]:
    """List notes inside a notebook (resolved via the notebook's note list)."""
    return db.list_notes_in_notebook(notebook_id, limit)


@mcp.tool()
def list_tags() -> list[dict]:
    """List all tags with their note counts."""
    return db.list_tags()


@mcp.tool()
def list_notes_by_tag(tag_title: str, limit: int = 50) -> list[dict]:
    """List notes carrying a given tag, matched by tag title."""
    return db.list_notes_by_tag(tag_title, limit)


# --- write tools (upnote:// URL scheme) -------------------------------------


@mcp.tool()
def create_note(
    title: str | None = None,
    content: str | None = None,
    notebook: str | None = None,
    tags: list[str] | None = None,
    markdown: bool = True,
    new_window: bool = False,
) -> dict:
    """Create a new note in UpNote via the URL scheme.

    content is treated as Markdown by default. tags are appended to the body
    as #hashtags (UpNote has no dedicated tags URL parameter). notebook matches
    by name. Returns the launched upnote:// URL.
    """
    url = writer.create_note(
        title=title,
        content=content,
        notebook=notebook,
        tags=tags,
        markdown=markdown,
        new_window=new_window,
    )
    return {"status": "launched", "url": url}


@mcp.tool()
def open_note(note_id: str, new_window: bool = False) -> dict:
    """Open an existing note in the UpNote app by its id."""
    return {"status": "launched", "url": writer.open_note(note_id, new_window)}


@mcp.tool()
def open_notebook(notebook_id: str) -> dict:
    """Open a notebook in the UpNote app by its id."""
    return {"status": "launched", "url": writer.open_notebook(notebook_id)}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
