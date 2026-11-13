"""The Help tab: a guide to every part of the app, one topic at a time."""

import re

import qtawesome as qta
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QTextCharFormat
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from kemonodownloader.kd_language import translate
from kemonodownloader.kd_theme import INFO, TEXT, TEXT_MUTED, TEXT_SOFT, set_role

# (title key, body key) for each topic of the guide, in order.
HELP_SECTIONS = [
    ("guide_start_title", "guide_start_text"),
    ("guide_post_title", "guide_post_text"),
    ("guide_creator_title", "guide_creator_text"),
    ("guide_thumbnails_title", "guide_thumbnails_text"),
    ("guide_history_title", "guide_history_text"),
    ("guide_settings_title", "guide_settings_text"),
    ("guide_proxy_title", "guide_proxy_text"),
    ("guide_logs_title", "guide_logs_text"),
    ("guide_troubleshooting_title", "guide_troubleshooting_text"),
    ("guide_support_title", "guide_support_text"),
]

# The icon of each topic, matching the tab it describes where there is one.
HELP_ICONS = {
    "guide_start_title": "fa5s.rocket",
    "guide_post_title": "fa5s.download",
    "guide_creator_title": "fa5s.user-edit",
    "guide_thumbnails_title": "fa5s.images",
    "guide_history_title": "fa5s.history",
    "guide_settings_title": "fa5s.cog",
    "guide_proxy_title": "fa5s.user-secret",
    "guide_logs_title": "fa5s.stream",
    "guide_troubleshooting_title": "fa5s.tools",
    "guide_support_title": "fa5s.life-ring",
}

NAV_WIDTH = 250
MAX_HIGHLIGHTS = 500

_DOCUMENT_STYLE = f"""
p, li {{ color: {TEXT_SOFT}; }}
b {{ color: {TEXT}; }}
h3 {{ color: {TEXT}; margin-top: 16px; margin-bottom: 4px; }}
a {{ color: {INFO}; text-decoration: none; }}
li {{ margin-bottom: 4px; }}
"""


def _plain(html: str) -> str:
    """Text of *html* without tags, for searching."""
    return re.sub(r"<[^>]+>", " ", html)


class HelpTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()
        self.parent.settings_tab.language_changed.connect(self.update_ui_text)
        self.parent.settings_tab.font_changed.connect(self._on_font_changed)

    def _get_font_family(self):
        """Get the current font family from settings."""
        return self.parent.settings_tab.get_font()

    def _on_font_changed(self, font_family):
        """Refresh UI when font changes."""
        self.update_ui_text()

    # ----------------------------------------------------------------- UI --
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        header = QVBoxLayout()
        header.setSpacing(2)
        self.title_label = QLabel()
        set_role(self.title_label, "title")
        header.addWidget(self.title_label)
        self.subtitle_label = QLabel()
        set_role(self.subtitle_label, "muted")
        header.addWidget(self.subtitle_label)
        main_layout.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(12)

        # Topics and search
        nav_column = QVBoxLayout()
        nav_column.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setFixedWidth(NAV_WIDTH)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.addAction(
            qta.icon("fa5s.search", color=TEXT_MUTED),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.search_input.textChanged.connect(self._on_search_changed)
        nav_column.addWidget(self.search_input)

        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(NAV_WIDTH)
        self.nav_list.setSpacing(2)
        set_role(self.nav_list, "roomy")
        for title_key, _body_key in HELP_SECTIONS:
            item = QListWidgetItem(qta.icon(HELP_ICONS[title_key], color="white"), "")
            item.setData(Qt.ItemDataRole.UserRole, title_key)
            self.nav_list.addItem(item)
        nav_column.addWidget(self.nav_list, stretch=1)

        self.no_results_label = QLabel()
        set_role(self.no_results_label, "muted")
        self.no_results_label.setWordWrap(True)
        self.no_results_label.setFixedWidth(NAV_WIDTH)
        self.no_results_label.hide()
        nav_column.addWidget(self.no_results_label)
        body.addLayout(nav_column)

        # The open topic
        panel = QFrame()
        panel.setObjectName("helpPanel")
        set_role(panel, "card")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 14, 8, 12)
        panel_layout.setSpacing(6)

        section_header = QHBoxLayout()
        self.section_icon = QLabel()
        section_header.addWidget(self.section_icon)
        self.section_title = QLabel()
        set_role(self.section_title, "title")
        section_header.addWidget(self.section_title, stretch=1)
        self.section_position = QLabel()
        set_role(self.section_position, "muted")
        section_header.addWidget(self.section_position)
        section_header.addSpacing(10)
        panel_layout.addLayout(section_header)

        # One document per topic instead of a label per paragraph:
        # word-wrapped labels are re-measured over and over as a layout
        # settles, which made this tab slow to build and resize.
        self.manual = QTextBrowser()
        self.manual.setOpenExternalLinks(True)
        self.manual.setFrameShape(QFrame.Shape.NoFrame)
        self.manual.document().setDefaultStyleSheet(_DOCUMENT_STYLE)
        set_role(self.manual, "plain")
        panel_layout.addWidget(self.manual, stretch=1)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 10, 0)
        self.prev_button = QPushButton(qta.icon("fa5s.chevron-left", color="white"), "")
        self.prev_button.clicked.connect(lambda: self._step(-1))
        footer.addWidget(self.prev_button)
        footer.addStretch()
        self.next_button = QPushButton(
            qta.icon("fa5s.chevron-right", color="white"), ""
        )
        # Arrow after the text, pointing the way the button goes.
        self.next_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.next_button.clicked.connect(lambda: self._step(1))
        footer.addWidget(self.next_button)
        panel_layout.addLayout(footer)

        body.addWidget(panel, stretch=1)
        main_layout.addLayout(body, stretch=1)

        self.nav_list.currentRowChanged.connect(self._show_section)
        self.nav_list.setCurrentRow(0)
        self.update_ui_text()
        self.setMinimumSize(300, 400)

    # ------------------------------------------------------------- topics --
    def _show_section(self, row: int) -> None:
        if not 0 <= row < len(HELP_SECTIONS):
            return
        title_key, body_key = HELP_SECTIONS[row]
        self.section_icon.setPixmap(
            qta.icon(HELP_ICONS[title_key], color=INFO).pixmap(22, 22)
        )
        self.section_title.setText(translate(title_key))
        self.section_position.setText(f"{row + 1} / {len(HELP_SECTIONS)}")
        self.manual.setHtml(translate(body_key))
        self.manual.verticalScrollBar().setValue(0)
        self._highlight_matches()
        self._update_steps()

    def current_section(self) -> str:
        """Title key of the topic on show."""
        return HELP_SECTIONS[max(0, self.nav_list.currentRow())][0]

    def _visible_rows(self):
        return [
            row
            for row in range(self.nav_list.count())
            if not self.nav_list.item(row).isHidden()
        ]

    def _step(self, direction: int) -> None:
        rows = self._visible_rows()
        current = self.nav_list.currentRow()
        if current not in rows:
            return
        target = rows.index(current) + direction
        if 0 <= target < len(rows):
            self.nav_list.setCurrentRow(rows[target])

    def _update_steps(self) -> None:
        rows = self._visible_rows()
        current = self.nav_list.currentRow()
        position = rows.index(current) if current in rows else -1
        self.prev_button.setEnabled(position > 0)
        self.next_button.setEnabled(0 <= position < len(rows) - 1)

    # ------------------------------------------------------------- search --
    def _matches(self, row: int, needle: str) -> bool:
        title_key, body_key = HELP_SECTIONS[row]
        haystack = f"{translate(title_key)} {_plain(translate(body_key))}"
        return needle.casefold() in haystack.casefold()

    def _on_search_changed(self, text: str) -> None:
        needle = text.strip()
        first_visible = None
        for row in range(self.nav_list.count()):
            visible = not needle or self._matches(row, needle)
            self.nav_list.item(row).setHidden(not visible)
            if visible and first_visible is None:
                first_visible = row
        self.no_results_label.setVisible(first_visible is None)
        current = self.nav_list.currentRow()
        if first_visible is not None and (
            current < 0 or self.nav_list.item(current).isHidden()
        ):
            self.nav_list.setCurrentRow(first_visible)
        else:
            self._highlight_matches()
            self._update_steps()

    def _highlight_matches(self) -> None:
        needle = self.search_input.text().strip()
        selections: list[QTextEdit.ExtraSelection] = []
        if needle:
            document = self.manual.document()
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("#6B5A1E"))
            fmt.setForeground(QColor(TEXT))
            cursor = document.find(needle)
            first = None
            while not cursor.isNull() and len(selections) < MAX_HIGHLIGHTS:
                selection = QTextEdit.ExtraSelection()
                selection.cursor = cursor
                selection.format = fmt
                selections.append(selection)
                if first is None:
                    first = cursor
                cursor = document.find(needle, cursor)
            if first is not None:
                # Bring the first match into view.
                self.manual.setTextCursor(first)
                self.manual.ensureCursorVisible()
        self.manual.setExtraSelections(selections)

    # ---------------------------------------------------------- language --
    def update_ui_text(self):
        family = self._get_font_family()
        self.title_label.setText(translate("help_title"))
        self.subtitle_label.setText(translate("help_subtitle"))
        self.search_input.setPlaceholderText(translate("help_search_placeholder"))
        self.no_results_label.setText(translate("help_no_results"))
        self.prev_button.setText(translate("help_previous"))
        self.next_button.setText(translate("help_next"))
        for row, (title_key, _body_key) in enumerate(HELP_SECTIONS):
            self.nav_list.item(row).setText(translate(title_key))

        self.manual.document().setDefaultFont(QFont(family, 11))
        current = self.nav_list.currentRow()
        if current >= 0:
            self._show_section(current)
        if self.search_input.text().strip():
            self._on_search_changed(self.search_input.text())

    def refresh_ui(self):
        self.update_ui_text()
