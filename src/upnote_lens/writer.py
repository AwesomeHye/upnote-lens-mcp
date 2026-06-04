"""Write side: drive UpNote through its ``upnote://`` URL scheme.

We never touch the SQLite DB for writes — UpNote syncs to the cloud, so direct
DB writes risk breaking sync. Note creation/navigation goes through the
x-callback-url endpoints instead, launched via macOS ``open``.

URL formats and the launch approach are adapted from chadthornton/upnote-mcp
(MIT). See LICENSE for attribution.
"""

from __future__ import annotations

import platform
import subprocess
from urllib.parse import quote, urlencode

_CREATE_NOTE = "upnote://x-callback-url/note/new"
_OPEN_NOTE = "upnote://x-callback-url/openNote"
_OPEN_NOTEBOOK = "upnote://x-callback-url/openNotebook"


def _build_url(base: str, params: dict) -> str:
    """Build a URL, dropping empty values and normalizing booleans."""
    clean: dict[str, str] = {}
    for key, value in params.items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            value = "true" if value else "false"
        clean[key] = str(value)
    query = urlencode(clean, quote_via=quote)
    return f"{base}?{query}" if query else base


def _open_url(url: str) -> str:
    """Hand the URL to the OS so UpNote's scheme handler picks it up."""
    if platform.system() != "Darwin":
        raise RuntimeError(
            "Launching upnote:// URLs is only supported on macOS (uses `open`)."
        )
    # Pass the URL as a separate argv entry (no shell) — it is already
    # percent-encoded, so there is nothing for a shell to misinterpret.
    subprocess.run(["open", url], check=True)
    return url


# --- write tools -----------------------------------------------------------


def create_note(
    title: str | None = None,
    content: str | None = None,
    notebook: str | None = None,
    tags: list[str] | None = None,
    markdown: bool = True,
    new_window: bool = False,
) -> str:
    """Create a note. Returns the upnote:// URL that was launched.

    UpNote's note/new endpoint has no dedicated tags parameter, so tags are
    appended to the body as ``#hashtags`` (which UpNote turns into tags when
    markdown is enabled).
    """
    text = content or ""
    if tags:
        hashtags = " ".join(f"#{t.lstrip('#')}" for t in tags if t.strip())
        text = f"{text}\n\n{hashtags}".strip() if text else hashtags

    params: dict[str, object] = {
        "title": title,
        "text": text,
        "notebook": notebook,
        "markdown": markdown,
    }
    if new_window:
        params["new_window"] = True
    return _open_url(_build_url(_CREATE_NOTE, params))


def open_note(note_id: str, new_window: bool = False) -> str:
    """Open an existing note by id. Returns the launched URL."""
    params: dict[str, object] = {"noteId": note_id}
    if new_window:
        params["new_window"] = True
    return _open_url(_build_url(_OPEN_NOTE, params))


def open_notebook(notebook_id: str) -> str:
    """Open a notebook by id. Returns the launched URL."""
    return _open_url(_build_url(_OPEN_NOTEBOOK, {"notebookId": notebook_id}))
