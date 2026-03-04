from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from kemonodownloader.kd_language import translate


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

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background: #2A3B5A;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                border: none;
                background: #3A4B6A;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #4A5B7A;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
        )

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setSpacing(20)

        self.update_ui_text()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        self.setMinimumSize(300, 400)

    def update_ui_text(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Title
        title_label = QLabel(f"<h1>{translate('help_title')}</h1>")
        title_label.setFont(QFont(self._get_font_family(), 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(title_label)

        # Introduction
        intro_label = QLabel(translate("help_intro"))
        intro_label.setFont(QFont(self._get_font_family(), 12))
        intro_label.setStyleSheet("color: #D0D0D0; padding: 5px;")
        intro_label.setWordWrap(True)
        intro_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(intro_label)

        # Section: Getting Started
        getting_started_title = QLabel(
            f"<h2>{translate('help_getting_started_title')}</h2>"
        )
        getting_started_title.setFont(
            QFont(self._get_font_family(), 16, QFont.Weight.Bold)
        )
        getting_started_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(getting_started_title)

        getting_started_text = QLabel(translate("help_getting_started_text"))
        getting_started_text.setFont(QFont(self._get_font_family(), 12))
        getting_started_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        getting_started_text.setWordWrap(True)
        getting_started_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(getting_started_text)

        # Section: Using the Post Downloader Tab
        post_downloader_title = QLabel(
            f"<h2>{translate('help_post_downloader_title')}</h2>"
        )
        post_downloader_title.setFont(
            QFont(self._get_font_family(), 16, QFont.Weight.Bold)
        )
        post_downloader_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(post_downloader_title)

        post_downloader_text = QLabel(translate("help_post_downloader_text"))
        post_downloader_text.setFont(QFont(self._get_font_family(), 12))
        post_downloader_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        post_downloader_text.setWordWrap(True)
        post_downloader_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(post_downloader_text)

        # Section: Using the Creator Downloader Tab
        creator_downloader_title = QLabel(
            f"<h2>{translate('help_creator_downloader_title')}</h2>"
        )
        creator_downloader_title.setFont(
            QFont(self._get_font_family(), 16, QFont.Weight.Bold)
        )
        creator_downloader_title.setStyleSheet(
            "color: white; padding: 10px 5px 5px 5px;"
        )
        self.content_layout.addWidget(creator_downloader_title)

        creator_downloader_text = QLabel(translate("help_creator_downloader_text"))
        creator_downloader_text.setFont(QFont(self._get_font_family(), 12))
        creator_downloader_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        creator_downloader_text.setWordWrap(True)
        creator_downloader_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(creator_downloader_text)

        # Section: Using the Settings Tab
        settings_title = QLabel(f"<h2>{translate('help_settings_title')}</h2>")
        settings_title.setFont(QFont(self._get_font_family(), 16, QFont.Weight.Bold))
        settings_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(settings_title)

        settings_text = QLabel(translate("help_settings_text"))
        settings_text.setFont(QFont(self._get_font_family(), 12))
        settings_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        settings_text.setWordWrap(True)
        settings_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(settings_text)

        # Section: Using the Help Tab
        help_tab_title = QLabel(f"<h2>{translate('help_help_tab_title')}</h2>")
        help_tab_title.setFont(QFont(self._get_font_family(), 16, QFont.Weight.Bold))
        help_tab_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(help_tab_title)

        help_tab_text = QLabel(translate("help_help_tab_text"))
        help_tab_text.setFont(QFont(self._get_font_family(), 12))
        help_tab_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        help_tab_text.setWordWrap(True)
        help_tab_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(help_tab_text)

        # Section: Troubleshooting
        troubleshooting_title = QLabel(
            f"<h2>{translate('help_troubleshooting_title')}</h2>"
        )
        troubleshooting_title.setFont(
            QFont(self._get_font_family(), 16, QFont.Weight.Bold)
        )
        troubleshooting_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(troubleshooting_title)

        troubleshooting_text = QLabel(translate("help_troubleshooting_text"))
        troubleshooting_text.setFont(QFont(self._get_font_family(), 12))
        troubleshooting_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        troubleshooting_text.setWordWrap(True)
        troubleshooting_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(troubleshooting_text)

        # Section: Contact and Support
        support_title = QLabel(f"<h2>{translate('help_support_title')}</h2>")
        support_title.setFont(QFont(self._get_font_family(), 16, QFont.Weight.Bold))
        support_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(support_title)

        support_text = QLabel(translate("help_support_text"))
        support_text.setFont(QFont(self._get_font_family(), 12))
        support_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        support_text.setWordWrap(True)
        support_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(support_text)

        self.content_layout.addStretch()

    def refresh_ui(self):
        self.update_ui_text()
