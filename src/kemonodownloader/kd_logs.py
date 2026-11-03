"""Log rendering helpers shared by the downloader tabs."""

from __future__ import annotations

import html
from typing import Any

from PyQt6.QtWidgets import QTextEdit

_LEVEL_COLORS = {"INFO": "green", "WARNING": "yellow", "ERROR": "red"}


def escape_log_text(message: Any) -> str:
    """Escape text bound for a rich-text console.

    Post titles and file names come from the server; left as they are, a ``<``
    in one of them is parsed as markup and swallows the rest of the line.
    """
    return html.escape(str(message), quote=False)


def format_log_line(message: Any, level: str = "INFO") -> str:
    """Return the rich-text form of a console log line."""
    color = _LEVEL_COLORS.get(level, "white")
    return f"<span style='color:{color}'>{escape_log_text(message)}</span>"


def share_console_document(view: QTextEdit, console: Any) -> bool:
    """Display *console*'s live document in *view*, if it has one.

    Both widgets then show one document, so the view needs no copying however
    long the log grows. Re-rendering a copy costs hundreds of milliseconds at
    tens of thousands of lines, which stalls the GUI on every refresh. Returns
    False when *console* is not a real text widget and has to be copied.
    """
    if not isinstance(console, QTextEdit):
        return False
    view.setDocument(console.document())
    return True
