"""Log rendering helpers and the full-logs window shared by the downloader tabs."""

from __future__ import annotations

import html
from typing import Any, Optional

import qtawesome as qta
from PyQt6 import sip
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import (
    QColor,
    QGuiApplication,
    QKeySequence,
    QShortcut,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
)
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from kemonodownloader.kd_language import language_manager, translate
from kemonodownloader.kd_theme import set_role, set_tone

# Bright enough to read on the consoles' navy backgrounds.
_LEVEL_COLORS = {
    "DEBUG": "#9FB3D9",
    "INFO": "#6FD08C",
    "WARNING": "#F5C451",
    "ERROR": "#FF7A7A",
}
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
# The translation that puts each level's tag ("[DEBUG] ...") on a message.
_LEVEL_PREFIX_KEYS = {
    "DEBUG": "log_debug",
    "WARNING": "log_warning",
    "ERROR": "log_error",
}
_DEFAULT_COLOR = "#E6EDF7"

SYNC_INTERVAL_MS = 250
# How close to the bottom (in pixels) still counts as following new lines.
FOLLOW_SLACK_PX = 6
MAX_HIGHLIGHTS = 1000
COPIED_FLASH_MS = 1500


def escape_log_text(message: Any) -> str:
    """Escape text bound for a rich-text console.

    Post titles and file names come from the server; left as they are, a ``<``
    in one of them is parsed as markup and swallows the rest of the line.
    """
    return html.escape(str(message), quote=False)


def format_log_line(message: Any, level: str = "INFO") -> str:
    """Return the rich-text form of a console log line."""
    color = _LEVEL_COLORS.get(level, _DEFAULT_COLOR)
    return f"<span style='color:{color}'>{escape_log_text(message)}</span>"


def message_level(message: Any, level: Optional[str] = "INFO") -> str:
    """Return the level a console message really has.

    A message's tag wins over the level it was sent with: a few messages
    tagged [DEBUG] (or [WARNING], [ERROR]) are sent as INFO. Tags are read
    in the current language and in English.
    """
    text = str(message).lstrip()
    for name, key in _LEVEL_PREFIX_KEYS.items():
        for prefix in {
            translate(key, "").strip(),
            language_manager.get_text(key, "english", "").strip(),
        }:
            if prefix and text.startswith(prefix):
                return name
    name = str(level or "INFO").upper()
    return name if name in LOG_LEVELS else "INFO"


def log_level_shown(settings_tab: Any, level: str) -> bool:
    """Whether Settings asks for messages of *level* to be shown.

    Without a settings tab to ask (or if it can't answer), everything shows.
    """
    check = getattr(settings_tab, "is_log_level_shown", None)
    if not callable(check):
        return True
    try:
        return bool(check(level))
    except Exception:
        return True


def counted(key: str, count: int) -> str:
    """Translate *key* for *count* items, using its ``_one`` form for one."""
    if count == 1:
        return translate(f"{key}_one")
    return translate(key, f"{count:,}")


class LogsWindowBase(QDialog):
    """A full-size, live view of a downloader tab's console.

    The window keeps its own copy of the console's document and copies across
    only the lines added since the last refresh. Showing the console's own
    document instead looked cheaper, but two views of one document fight over
    its line wrapping: each relayout at the other widget's width moved the
    text under the reader, so scrolling back during a download kept jumping.

    New lines are followed while the view is at the bottom. Scroll up and the
    view stays where it is; a button offers the way back to the newest lines.
    Subclasses provide ``_console()`` and call ``refresh_now()`` once their
    own attributes are set.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(translate("full_logs"))
        self.setModal(False)
        self.resize(900, 620)
        self.setMinimumSize(560, 380)

        self._source_doc: Optional[QTextDocument] = None
        self._synced_end = 0
        self._resync = True
        self._follow = True
        self._unseen = 0
        self._restore_to: Optional[int] = None
        # Set while this window moves the view itself, so only the reader's
        # own scrolling can pause or resume following.
        self._adjusting = False
        self.needs_update = False

        self._build_ui()

        # Batch refreshes so a burst of log lines costs one copy.
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(SYNC_INTERVAL_MS)
        self.update_timer.timeout.connect(self._do_update)

        # Owned by the window, so it can't fire after the window is gone.
        self._copied_timer = QTimer(self)
        self._copied_timer.setSingleShot(True)
        self._copied_timer.setInterval(COPIED_FLASH_MS)
        self._copied_timer.timeout.connect(
            lambda: self.copy_logs_btn.setText(translate("copy_logs"))
        )

    # ----------------------------------------------------------------- UI --
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(8)
        icon = QLabel()
        icon.setPixmap(qta.icon("fa5s.stream", color="#A0C0FF").pixmap(18, 18))
        header.addWidget(icon)
        self.title_label = QLabel()
        set_role(self.title_label, "title")
        header.addWidget(self.title_label)
        self.line_count_label = QLabel()
        set_role(self.line_count_label, "muted")
        header.addWidget(self.line_count_label)
        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setClearButtonEnabled(True)
        self.search_input.addAction(
            qta.icon("fa5s.search", color="#9FB3D9"),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.search_input.setMinimumWidth(220)
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.returnPressed.connect(self._on_search_return)
        header.addWidget(self.search_input)
        self.match_label = QLabel()
        set_role(self.match_label, "muted")
        header.addWidget(self.match_label)
        self.find_prev_btn = self._icon_button("fa5s.chevron-up")
        self.find_prev_btn.clicked.connect(lambda: self.find_in_logs(backward=True))
        header.addWidget(self.find_prev_btn)
        self.find_next_btn = self._icon_button("fa5s.chevron-down")
        self.find_next_btn.clicked.connect(lambda: self.find_in_logs())
        header.addWidget(self.find_next_btn)
        layout.addLayout(header)

        self.logs_display = QTextEdit()
        set_role(self.logs_display, "console")
        self.logs_display.setReadOnly(True)
        self.logs_display.document().setDocumentMargin(10)
        layout.addWidget(self.logs_display, stretch=1)

        bar = self.logs_display.verticalScrollBar()
        bar.valueChanged.connect(self._on_scrolled)
        bar.rangeChanged.connect(self._on_range_changed)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        self.copy_logs_btn = self._text_button("fa5s.copy")
        self.copy_logs_btn.clicked.connect(self.copy_logs)
        footer.addWidget(self.copy_logs_btn)
        self.download_logs_btn = self._text_button("fa5s.save")
        self.download_logs_btn.clicked.connect(self.download_logs)
        footer.addWidget(self.download_logs_btn)
        self.clear_logs_btn = self._text_button("fa5s.trash-alt", "danger")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        footer.addWidget(self.clear_logs_btn)
        footer.addStretch()
        self.jump_btn = self._text_button("fa5s.arrow-down", "primary")
        self.jump_btn.clicked.connect(self.jump_to_latest)
        self.jump_btn.hide()
        footer.addWidget(self.jump_btn)
        layout.addLayout(footer)

        QShortcut(QKeySequence.StandardKey.Find, self, self._focus_search)
        QShortcut(QKeySequence.StandardKey.FindNext, self, self.find_in_logs)
        QShortcut(
            QKeySequence.StandardKey.FindPrevious,
            self,
            lambda: self.find_in_logs(backward=True),
        )

        self.update_ui_text()

    def _text_button(self, icon_name: str, role: Optional[str] = None) -> QPushButton:
        button = QPushButton(qta.icon(icon_name, color="white"), "")
        set_role(button, role)
        return button

    def _icon_button(self, icon_name: str) -> QPushButton:
        button = QPushButton(qta.icon(icon_name, color="white"), "")
        button.setFixedSize(30, 30)
        set_role(button, "icon")
        return button

    def update_ui_text(self) -> None:
        self.setWindowTitle(translate("full_logs"))
        self.title_label.setText(translate("full_logs"))
        self.search_input.setPlaceholderText(translate("logs_search_placeholder"))
        self.find_prev_btn.setToolTip(translate("logs_find_previous"))
        self.find_next_btn.setToolTip(translate("logs_find_next"))
        self.copy_logs_btn.setText(translate("copy_logs"))
        self.download_logs_btn.setText(translate("download_logs"))
        self.clear_logs_btn.setText(translate("clear_logs"))
        self.jump_btn.setToolTip(translate("logs_follow_tooltip"))
        self._update_jump_button()
        self._update_line_count()

    # -------------------------------------------------------------- source --
    def _console(self) -> Any:
        """Return the console widget this window mirrors (or None)."""
        return None

    @staticmethod
    def _document_of(console: Any) -> Optional[QTextDocument]:
        if not isinstance(console, QTextEdit):
            return None
        document = console.document()
        return document if isinstance(document, QTextDocument) else None

    def _bind(self, document: Optional[QTextDocument]) -> None:
        if self._source_doc is not None:
            try:
                self._source_doc.contentsChange.disconnect(self._on_source_change)
            except (TypeError, RuntimeError):
                pass
        self._source_doc = document
        self._resync = True
        if document is not None:
            document.contentsChange.connect(self._on_source_change)

    def _on_source_change(self, position: int, removed: int, added: int) -> None:
        # Anything other than text added at the end (a clear, a rewrite) means
        # the copy no longer lines up, so it is rebuilt.
        if removed or position < self._synced_end:
            self._resync = True
        if self.isVisible():
            self.update_logs()

    # ------------------------------------------------------------- refresh --
    def update_logs(self) -> None:
        """Schedule a batched refresh instead of refreshing immediately."""
        self.needs_update = True
        if not self.update_timer.isActive():
            self.update_timer.start()

    def _do_update(self) -> None:
        """Perform a scheduled refresh (called by the timer)."""
        if not self.needs_update:
            self.update_timer.stop()
            return
        self.needs_update = False
        self.refresh_now()

    def refresh_now(self) -> None:
        """Bring the window up to date with its console straight away."""
        console = self._console()
        if console is None:
            return
        document = self._document_of(console)
        if document is None:
            # Not a real text widget: copy its HTML, keeping the reader's place.
            to_html = getattr(console, "toHtml", None)
            markup = to_html() if callable(to_html) else None
            if isinstance(markup, str):
                value = self.logs_display.verticalScrollBar().value()
                self.logs_display.setHtml(markup)
                self._settle_scroll(value)
                self._update_line_count()
            return
        if document is not self._source_doc:
            self._bind(document)
        if self._resync:
            self._copy_all(document)
        else:
            self._copy_new(document)
        self._update_line_count()

    def _copy_all(self, source: QTextDocument) -> None:
        value = self.logs_display.verticalScrollBar().value()
        # Parented to the view, so the view deletes it when it is replaced.
        # PyQt also marks a clone as Python's to delete; hand it to Qt alone,
        # or the replaced copy is deleted twice and corrupts memory.
        copy = source.clone(self.logs_display)
        sip.transferto(copy, self.logs_display)
        # The font chosen in Settings, which the app applies to every widget.
        copy.setDefaultFont(self.logs_display.font())
        copy.setDocumentMargin(10)
        self._adjusting = True
        try:
            self.logs_display.setDocument(copy)
            if self._follow:
                # QTextEdit scrolls to its cursor when first shown; keep that
                # at the newest line rather than the first.
                cursor = self.logs_display.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.logs_display.setTextCursor(cursor)
        finally:
            self._adjusting = False
        self._synced_end = max(0, source.characterCount() - 1)
        self._resync = False
        self._unseen = 0
        self._settle_scroll(value)
        self._apply_highlights()

    def _copy_new(self, source: QTextDocument) -> None:
        end = max(0, source.characterCount() - 1)
        if end < self._synced_end:
            self._copy_all(source)
            return
        if end == self._synced_end:
            return
        before = self.logs_display.document().blockCount()
        selection = QTextCursor(source)
        selection.setPosition(self._synced_end)
        selection.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        fragment = selection.selection()

        bar = self.logs_display.verticalScrollBar()
        value = bar.value()
        # A cursor of our own, so the reader's cursor and selection stay put.
        target = QTextCursor(self.logs_display.document())
        target.movePosition(QTextCursor.MoveOperation.End)
        self._adjusting = True
        try:
            target.insertFragment(fragment)
        finally:
            self._adjusting = False
        self._synced_end = end

        added = self.logs_display.document().blockCount() - before
        if not self._follow:
            self._unseen += max(1, added)
        self._settle_scroll(value)
        self._update_jump_button()
        if self.search_input.text():
            self._apply_highlights()

    # -------------------------------------------------------------- scroll --
    def _settle_scroll(self, value: int) -> None:
        bar = self.logs_display.verticalScrollBar()
        self._adjusting = True
        try:
            if self._follow:
                bar.setValue(bar.maximum())
                self._restore_to = None
                return
            bar.setValue(min(value, bar.maximum()))
        finally:
            self._adjusting = False
        # Layout can finish after this call; finish the restore once it does.
        self._restore_to = value if bar.value() != value else None

    def _on_range_changed(self, _minimum: int, maximum: int) -> None:
        bar = self.logs_display.verticalScrollBar()
        self._adjusting = True
        try:
            if self._follow:
                bar.setValue(maximum)
            elif self._restore_to is not None:
                bar.setValue(min(self._restore_to, maximum))
                if bar.value() == self._restore_to:
                    self._restore_to = None
        finally:
            self._adjusting = False

    def _on_scrolled(self, value: int) -> None:
        if self._adjusting:
            return
        bar = self.logs_display.verticalScrollBar()
        following = value >= bar.maximum() - FOLLOW_SLACK_PX
        if following != self._follow:
            self._follow = following
            if following:
                self._unseen = 0
                self._restore_to = None
            self._update_jump_button()

    def is_following(self) -> bool:
        """Whether new lines scroll into view as they arrive."""
        return self._follow

    def jump_to_latest(self) -> None:
        """Scroll to the newest line and follow new lines again."""
        self._follow = True
        self._unseen = 0
        self._restore_to = None
        bar = self.logs_display.verticalScrollBar()
        bar.setValue(bar.maximum())
        self._update_jump_button()

    def _update_jump_button(self) -> None:
        if self._unseen:
            self.jump_btn.setText(counted("logs_new_lines", self._unseen))
        else:
            self.jump_btn.setText(translate("logs_jump_to_latest"))
        self.jump_btn.setVisible(not self._follow)

    def _update_line_count(self) -> None:
        document = self.logs_display.document()
        lines = 0 if document.isEmpty() else document.blockCount()
        self.line_count_label.setText(counted("logs_line_count", lines))

    # -------------------------------------------------------------- search --
    def _focus_search(self) -> None:
        self.search_input.setFocus()
        self.search_input.selectAll()

    def _on_search_return(self) -> None:
        # Enter finds the next match, Shift+Enter the previous one.
        modifiers = QGuiApplication.keyboardModifiers()
        self.find_in_logs(backward=bool(modifiers & Qt.KeyboardModifier.ShiftModifier))

    def _on_search_changed(self, _text: str) -> None:
        self._apply_highlights()
        if self.search_input.text():
            # Start each new search from the top of the visible text.
            cursor = self.logs_display.textCursor()
            cursor.clearSelection()
            self.logs_display.setTextCursor(cursor)
            self.find_in_logs()

    def find_in_logs(self, backward: bool = False) -> bool:
        """Select the next (or previous) match, wrapping around the ends."""
        needle = self.search_input.text()
        if not needle:
            return False
        flags = QTextDocument.FindFlag(0)
        if backward:
            flags |= QTextDocument.FindFlag.FindBackward
        if self.logs_display.find(needle, flags):
            return True
        cursor = self.logs_display.textCursor()
        cursor.movePosition(
            QTextCursor.MoveOperation.End
            if backward
            else QTextCursor.MoveOperation.Start
        )
        self.logs_display.setTextCursor(cursor)
        return self.logs_display.find(needle, flags)

    def _apply_highlights(self) -> None:
        needle = self.search_input.text()
        selections: list[QTextEdit.ExtraSelection] = []
        if needle:
            document = self.logs_display.document()
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("#6B5A1E"))
            fmt.setForeground(QColor("#FFFFFF"))
            cursor = document.find(needle)
            while not cursor.isNull() and len(selections) < MAX_HIGHLIGHTS:
                selection = QTextEdit.ExtraSelection()
                selection.cursor = cursor
                selection.format = fmt
                selections.append(selection)
                cursor = document.find(needle, cursor)
        self.logs_display.setExtraSelections(selections)
        self._update_match_label(needle, len(selections))

    def _update_match_label(self, needle: str, count: int) -> None:
        if not needle:
            text = ""
        elif not count:
            text = translate("logs_no_matches")
        elif count >= MAX_HIGHLIGHTS:
            text = translate("logs_match_count", f"{MAX_HIGHLIGHTS:,}+")
        else:
            text = counted("logs_match_count", count)
        self.match_label.setText(text)
        set_tone(self.match_label, "error" if needle and not count else None)

    # ------------------------------------------------------------- actions --
    def copy_logs(self) -> None:
        """Copy every log line to the clipboard as plain text."""
        text = self.logs_display.toPlainText()
        clipboard = QApplication.clipboard()
        if not text.strip() or clipboard is None:
            return
        clipboard.setText(text)
        self.copy_logs_btn.setText(translate("logs_copied"))
        self._copied_timer.start()

    def clear_logs(self) -> None:
        """Clear both this window and the console it mirrors."""
        self.logs_display.clear()
        console = self._console()
        clear = getattr(console, "clear", None)
        if callable(clear):
            clear()
        self._unseen = 0
        self.jump_to_latest()
        self._update_line_count()

    def download_logs(self) -> None:  # pragma: no cover - defined by subclasses
        raise NotImplementedError

    def closeEvent(self, a0) -> None:  # noqa: N802 (Qt API)
        """Stop refreshing once the window closes."""
        if hasattr(self, "update_timer"):
            self.update_timer.stop()
        if hasattr(self, "_copied_timer"):
            self._copied_timer.stop()
        self._bind(None)
        if a0 is not None:
            a0.accept()
