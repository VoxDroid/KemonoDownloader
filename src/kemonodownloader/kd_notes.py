"""Short guide notes shown at the top of each section of the interface.

A note is a muted, word-wrapped label that says what a section is for, like
the explanation under Use Proxy in Settings. It remembers its translation
key, so ``retranslate_notes`` can update every note under a widget when the
language changes.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QBoxLayout,
    QLabel,
    QLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from kemonodownloader.kd_language import translate
from kemonodownloader.kd_theme import set_role

NOTE_KEY_PROPERTY = "kdNoteKey"


class NoteLabel(QLabel):
    """A word-wrapped label that asks for the height its text needs.

    Qt sizes a word-wrapped label from a guessed, narrow width, so a section
    holding one asked for far more height than it used and spread the spare
    room between its controls. A note reports its height at its real width,
    and lays out again when that width changes.
    """

    def _height_at_width(self, fallback: int) -> int:
        width = self.width() if self.width() > 0 else 0
        height = self.heightForWidth(width) if width else -1
        return height if height > 0 else fallback

    def sizeHint(self) -> QSize:  # noqa: N802 (Qt API)
        hint = super().sizeHint()
        return QSize(hint.width(), self._height_at_width(hint.height()))

    def minimumSizeHint(self) -> QSize:  # noqa: N802 (Qt API)
        hint = super().minimumSizeHint()
        return QSize(hint.width(), self._height_at_width(hint.height()))

    def resizeEvent(self, a0) -> None:  # noqa: N802 (Qt API)
        old_width = a0.oldSize().width() if a0 is not None else -1
        super().resizeEvent(a0)
        if a0 is not None and a0.size().width() != old_width:
            self.updateGeometry()


def section_note(key: str, parent: Optional[QWidget] = None) -> QLabel:
    """Return a note label showing the translation of *key*."""
    note = NoteLabel(translate(key), parent)
    note.setProperty(NOTE_KEY_PROPERTY, key)
    note.setWordWrap(True)
    # As tall as its text, never stretched to fill a section.
    note.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
    set_role(note, "note")
    return note


def add_note(layout: QBoxLayout, key: str, index: int = 0) -> QLabel:
    """Insert a note into a box layout, at the top by default."""
    note = section_note(key)
    layout.insertWidget(index, note)
    return note


def with_note(layout: QLayout, key: str) -> QVBoxLayout:
    """Wrap *layout* in a column that starts with a note.

    For sections whose controls sit in a grid, which has no "insert at the
    top": the group gets the column, the grid keeps its rows.
    """
    column = QVBoxLayout()
    column.addWidget(section_note(key))
    column.addLayout(layout)
    return column


def retranslate_notes(root: QWidget) -> None:
    """Show every note under *root* in the current language."""
    for note in root.findChildren(QLabel):
        key = note.property(NOTE_KEY_PROPERTY)
        if key:
            note.setText(translate(key))
