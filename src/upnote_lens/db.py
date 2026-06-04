"""Read-only access to the local UpNote SQLite database.

Everything here is read-only by design. The connection is opened with
``mode=ro&immutable=1`` so we never take a write lock or risk corrupting the
file that UpNote keeps in sync with the cloud.

Facts verified against a real UpNote DB (macOS, ~5.7k notes):
- A note is "valid" when ``trashed=0 AND deleted=0 AND COALESCE(isTemplate,0)=0``.
  ``isTemplate`` is usually NULL (not 0), so ``isTemplate=0`` would drop everything.
- Timestamps (``updatedAt``/``createdAt``) are millisecond epochs stored as DOUBLE.
- ``notes.notebookLinks`` is empty for every row. The real note<->notebook
  relationship lives in ``notebooks.notes`` (a JSON array of note ids).
- ``tags.notes`` is likewise a JSON array of note ids.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote

DEFAULT_DB_PATH = (
    Path.home()
    / "Library/Containers/com.getupnote.desktop/Data/Library/Application Support"
    / "UpNote/upnote.sqlite3"
)

# A valid, user-facing note: not trashed, not deleted, not a template.
VALID_NOTE = "trashed = 0 AND deleted = 0 AND COALESCE(isTemplate, 0) = 0"

# Human-readable local time derived from the millisecond epoch.
_UPDATED_AT = "datetime(updatedAt / 1000, 'unixepoch', 'localtime')"


def db_path() -> Path:
    """Resolve the DB path, allowing an override via UPNOTE_LENS_DB."""
    override = os.environ.get("UPNOTE_LENS_DB")
    return Path(override).expanduser() if override else DEFAULT_DB_PATH


@contextmanager
def _connect():
    path = db_path()
    if not path.exists():
        raise FileNotFoundError(
            f"UpNote database not found at: {path}\n"
            "Set UPNOTE_LENS_DB to point at your upnote.sqlite3 if it lives elsewhere."
        )
    uri = "file:" + quote(str(path)) + "?mode=ro&immutable=1"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _escape_like(term: str) -> str:
    """Escape LIKE wildcards so user input is matched literally."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _snippet(text: str | None, query: str, width: int = 160) -> str:
    """A short context window around the first match of `query`."""
    if not text:
        return ""
    flat = " ".join(text.split())
    pos = flat.lower().find(query.lower())
    if pos < 0:
        return flat[:width] + ("…" if len(flat) > width else "")
    start = max(0, pos - width // 3)
    end = min(len(flat), start + width)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(flat) else ""
    return prefix + flat[start:end] + suffix


def _ids_in_clause(ids: list[str]) -> tuple[str, list[str]]:
    placeholders = ",".join("?" for _ in ids)
    return placeholders, ids


# --- read tools ------------------------------------------------------------


def search_notes(query: str, limit: int = 20) -> list[dict]:
    """LIKE search over title and body; returns id/title/updated_at/snippet."""
    like = f"%{_escape_like(query)}%"
    sql = f"""
        SELECT id, title, {_UPDATED_AT} AS updated_at, text
        FROM notes
        WHERE {VALID_NOTE}
          AND (title LIKE ? ESCAPE '\\' OR text LIKE ? ESCAPE '\\')
        ORDER BY updatedAt DESC
        LIMIT ?
    """
    with _connect() as conn:
        rows = conn.execute(sql, (like, like, limit)).fetchall()
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "updated_at": r["updated_at"],
            "snippet": _snippet(r["text"], query),
        }
        for r in rows
    ]


def get_note(note_id: str, include_html: bool = False) -> dict | None:
    """Full title + body text of a single note (optionally raw HTML too)."""
    sql = f"""
        SELECT id, title, text, html, {_UPDATED_AT} AS updated_at
        FROM notes
        WHERE id = ?
    """
    with _connect() as conn:
        r = conn.execute(sql, (note_id,)).fetchone()
    if r is None:
        return None
    result = {
        "id": r["id"],
        "title": r["title"],
        "text": r["text"],
        "updated_at": r["updated_at"],
    }
    if include_html:
        result["html"] = r["html"]
    return result


def list_recent(limit: int = 20) -> list[dict]:
    """Most recently updated valid notes."""
    sql = f"""
        SELECT id, title, {_UPDATED_AT} AS updated_at
        FROM notes
        WHERE {VALID_NOTE}
        ORDER BY updatedAt DESC
        LIMIT ?
    """
    with _connect() as conn:
        rows = conn.execute(sql, (limit,)).fetchall()
    return [dict(r) for r in rows]


def list_notebooks() -> list[dict]:
    """All notebooks with their note counts (from notebooks.notes JSON)."""
    sql = """
        SELECT id, title, notes, parent
        FROM notebooks
        WHERE deleted = 0
        ORDER BY title COLLATE NOCASE
    """
    with _connect() as conn:
        rows = conn.execute(sql).fetchall()
    out = []
    for r in rows:
        try:
            note_ids = json.loads(r["notes"]) if r["notes"] else []
        except (ValueError, TypeError):
            note_ids = []
        out.append(
            {
                "id": r["id"],
                "title": r["title"],
                "note_count": len(note_ids),
                "parent": r["parent"] or None,
            }
        )
    return out


def list_notes_in_notebook(notebook_id: str, limit: int = 50) -> list[dict]:
    """Notes belonging to a notebook, resolved via notebooks.notes JSON."""
    with _connect() as conn:
        nb = conn.execute(
            "SELECT id, title, notes FROM notebooks WHERE id = ?", (notebook_id,)
        ).fetchone()
        if nb is None:
            return []
        try:
            note_ids = json.loads(nb["notes"]) if nb["notes"] else []
        except (ValueError, TypeError):
            note_ids = []
        if not note_ids:
            return []
        placeholders, params = _ids_in_clause(note_ids)
        sql = f"""
            SELECT id, title, {_UPDATED_AT} AS updated_at
            FROM notes
            WHERE id IN ({placeholders}) AND {VALID_NOTE}
            ORDER BY updatedAt DESC
            LIMIT ?
        """
        rows = conn.execute(sql, [*params, limit]).fetchall()
    return [dict(r) for r in rows]


def list_tags() -> list[dict]:
    """All tags with their note counts (from tags.notes JSON)."""
    sql = """
        SELECT id, title, notes
        FROM tags
        WHERE deleted = 0
        ORDER BY title COLLATE NOCASE
    """
    with _connect() as conn:
        rows = conn.execute(sql).fetchall()
    out = []
    for r in rows:
        try:
            note_ids = json.loads(r["notes"]) if r["notes"] else []
        except (ValueError, TypeError):
            note_ids = []
        out.append(
            {"id": r["id"], "title": r["title"], "note_count": len(note_ids)}
        )
    return out


def list_notes_by_tag(tag_title: str, limit: int = 50) -> list[dict]:
    """Notes carrying a tag, matched by tag title (via tags.notes JSON)."""
    with _connect() as conn:
        tag = conn.execute(
            "SELECT id, title, notes FROM tags WHERE title = ? COLLATE NOCASE",
            (tag_title,),
        ).fetchone()
        if tag is None:
            return []
        try:
            note_ids = json.loads(tag["notes"]) if tag["notes"] else []
        except (ValueError, TypeError):
            note_ids = []
        if not note_ids:
            return []
        placeholders, params = _ids_in_clause(note_ids)
        sql = f"""
            SELECT id, title, {_UPDATED_AT} AS updated_at
            FROM notes
            WHERE id IN ({placeholders}) AND {VALID_NOTE}
            ORDER BY updatedAt DESC
            LIMIT ?
        """
        rows = conn.execute(sql, [*params, limit]).fetchall()
    return [dict(r) for r in rows]
