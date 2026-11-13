from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLabel, QTextBrowser, QVBoxLayout, QWidget

from kemonodownloader.kd_language import translate
from kemonodownloader.kd_theme import set_role

# (title key, body key) for each section of the manual, in order.
HELP_SECTIONS = [
    ("help_getting_started_title", "help_getting_started_text"),
    ("help_post_downloader_title", "help_post_downloader_text"),
    ("help_creator_downloader_title", "help_creator_downloader_text"),
    ("help_settings_title", "help_settings_text"),
    ("help_help_tab_title", "help_help_tab_text"),
    ("help_history_title", "help_history_text"),
    ("help_troubleshooting_title", "help_troubleshooting_text"),
    ("help_support_title", "help_support_text"),
]


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

    def setup_ui(self):
        # Main layout for the Help tab
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        panel = QFrame()
        panel.setObjectName("helpPanel")
        set_role(panel, "card")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 10, 4, 10)
        panel_layout.setSpacing(10)

        self.title_label = QLabel()
        set_role(self.title_label, "title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(self.title_label)

        # One document instead of a label per paragraph: word-wrapped labels
        # are re-measured over and over as a layout settles, which made this
        # tab take a third of a second to build and resize.
        self.manual = QTextBrowser()
        self.manual.setOpenExternalLinks(True)
        self.manual.setFrameShape(QFrame.Shape.NoFrame)
        set_role(self.manual, "plain")
        panel_layout.addWidget(self.manual, stretch=1)
        main_layout.addWidget(panel)

        self.update_ui_text()
        self.setMinimumSize(300, 400)

    def _manual_html(self):
        def paragraph(text):
            return f'<p align="justify" style="margin: 4px 5px 14px 5px;">{text}</p>'

        parts = [paragraph(translate("help_intro"))]
        for title_key, body_key in HELP_SECTIONS:
            parts.append(
                '<p style="color: white; font-size: 16pt; font-weight: bold;'
                f' margin: 18px 5px 6px 5px;">{translate(title_key)}</p>'
            )
            parts.append(paragraph(translate(body_key)))
        return f'<div style="color: #D0D0D0;">{"".join(parts)}</div>'

    def update_ui_text(self):
        family = self._get_font_family()
        self.title_label.setText(f"<h1>{translate('help_title')}</h1>")
        self.title_label.setFont(QFont(family, 20, QFont.Weight.Bold))

        scroll = self.manual.verticalScrollBar().value()
        self.manual.document().setDefaultFont(QFont(family, 12))
        self.manual.setHtml(self._manual_html())
        self.manual.verticalScrollBar().setValue(scroll)

    def refresh_ui(self):
        self.update_ui_text()
