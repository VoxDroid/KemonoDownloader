"""The Browser Extension tab: what the extension does and how to install it."""

import qtawesome as qta
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from kemonodownloader.kd_language import translate
from kemonodownloader.kd_notes import retranslate_notes, tip, tips
from kemonodownloader.kd_theme import color, set_role

RELEASES_URL = "https://github.com/VoxDroid/KemonoDownloader/releases"
EXTENSION_FOLDER_URL = (
    "https://github.com/VoxDroid/KemonoDownloader/tree/main/browser-extension"
)

# (title key, text key, icon) for the feature cards.
FEATURES = [
    ("ext_feature_pick_title", "ext_feature_pick_text", "fa5s.check-square"),
    ("ext_feature_zip_title", "ext_feature_zip_text", "fa5s.file-archive"),
    ("ext_feature_progress_title", "ext_feature_progress_text", "fa5s.tasks"),
    ("ext_feature_sites_title", "ext_feature_sites_text", "fa5s.globe"),
]

# (label, command) to put the right manifest in place, run in the folder.
MANIFEST_COMMANDS = [
    (
        "Chrome / Edge · PowerShell",
        "Copy-Item chrome_manifest.json manifest.json -Force",
    ),
    ("Chrome / Edge · macOS, Linux", "cp chrome_manifest.json manifest.json"),
    (
        "Firefox · PowerShell",
        "Copy-Item firefox_manifest.json manifest.json -Force",
    ),
    ("Firefox · macOS, Linux", "cp firefox_manifest.json manifest.json"),
]

COPIED_FLASH_MS = 1500


def _card() -> QFrame:
    card = QFrame()
    set_role(card, "card")
    return card


def _text(role: str = "soft") -> QLabel:
    label = QLabel()
    set_role(label, role)
    label.setWordWrap(True)
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setOpenExternalLinks(True)
    return label


class ExtensionTab(QWidget):
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

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 0, 8, 0)
        self.content_layout.setSpacing(14)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._build_header()
        self._build_features()
        self._build_steps()
        self._build_usage()

        scroll_area.setWidget(content)
        main_layout.addWidget(scroll_area)

        # Owned by the tab, so it can't fire after the tab is gone.
        self._copied_timer = QTimer(self)
        self._copied_timer.setSingleShot(True)
        self._copied_timer.setInterval(COPIED_FLASH_MS)
        self._copied_timer.timeout.connect(self._reset_copy_buttons)

        # Tooltips, for when a section's note isn't enough.
        tip(self.releases_button, "tip_open_releases")
        tip(self.folder_button, "tip_open_extension_folder")
        tips(self.copy_buttons, "tip_copy_command")
        self.update_ui_text()
        self.setMinimumSize(300, 400)

    def _build_header(self) -> None:
        header = _card()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)
        icon = QLabel()
        self.theme_icons = [(icon, "fa5s.puzzle-piece", 40)]
        icon.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(icon)

        text_column = QVBoxLayout()
        text_column.setSpacing(4)
        self.title_label = QLabel()
        set_role(self.title_label, "title")
        text_column.addWidget(self.title_label)
        self.subtitle_label = _text("muted")
        text_column.addWidget(self.subtitle_label)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        self.releases_button = QPushButton(qta.icon("fa5s.download", color="white"), "")
        set_role(self.releases_button, "primary")
        self.releases_button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(RELEASES_URL))
        )
        buttons.addWidget(self.releases_button)
        self.folder_button = QPushButton(qta.icon("fa5b.github", color="white"), "")
        self.folder_button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(EXTENSION_FOLDER_URL))
        )
        buttons.addWidget(self.folder_button)
        buttons.addStretch()
        text_column.addSpacing(6)
        text_column.addLayout(buttons)
        layout.addLayout(text_column, stretch=1)
        self.content_layout.addWidget(header)

    def _build_features(self) -> None:
        grid = QGridLayout()
        grid.setSpacing(12)
        self.feature_labels = []
        for index, (title_key, text_key, icon_name) in enumerate(FEATURES):
            card = _card()
            layout = QHBoxLayout(card)
            layout.setContentsMargins(14, 12, 14, 12)
            layout.setSpacing(12)
            icon = QLabel()
            self.theme_icons.append((icon, icon_name, 24))
            icon.setAlignment(Qt.AlignmentFlag.AlignTop)
            layout.addWidget(icon)
            column = QVBoxLayout()
            column.setSpacing(2)
            title = QLabel()
            set_role(title, "heading")
            column.addWidget(title)
            text = _text("muted")
            column.addWidget(text)
            layout.addLayout(column, stretch=1)
            self.feature_labels.append((title, text, title_key, text_key))
            grid.addWidget(card, index // 2, index % 2)
        self.content_layout.addLayout(grid)

    def _step_card(self):
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(6)
        title = QLabel()
        set_role(title, "heading")
        layout.addWidget(title)
        text = _text()
        layout.addWidget(text)
        return card, layout, title, text

    def _build_steps(self) -> None:
        self.install_heading = QLabel()
        set_role(self.install_heading, "title")
        self.content_layout.addWidget(self.install_heading)

        card, _layout, self.step_get_title, self.step_get_text = self._step_card()
        self.content_layout.addWidget(card)

        card, layout, self.step_manifest_title, self.step_manifest_text = (
            self._step_card()
        )
        self.commands_label = _text("muted")
        layout.addSpacing(4)
        layout.addWidget(self.commands_label)
        self.copy_buttons = []
        commands = QGridLayout()
        commands.setHorizontalSpacing(8)
        commands.setVerticalSpacing(6)
        for row, (label_text, command) in enumerate(MANIFEST_COMMANDS):
            label = QLabel(label_text)
            set_role(label, "muted")
            commands.addWidget(label, row, 0)
            field = QLineEdit(command)
            field.setReadOnly(True)
            field.setCursorPosition(0)
            commands.addWidget(field, row, 1)
            button = QPushButton(qta.icon("fa5s.copy", color="white"), "")
            button.clicked.connect(
                lambda _checked=False, c=command, b=button: self._copy(c, b)
            )
            commands.addWidget(button, row, 2)
            self.copy_buttons.append(button)
        commands.setColumnStretch(1, 1)
        layout.addLayout(commands)
        self.content_layout.addWidget(card)

        browsers = QHBoxLayout()
        browsers.setSpacing(12)
        card, _layout, self.step_chrome_title, self.step_chrome_text = self._step_card()
        browsers.addWidget(card)
        card, _layout, self.step_firefox_title, self.step_firefox_text = (
            self._step_card()
        )
        browsers.addWidget(card)
        self.content_layout.addLayout(browsers)

    def _build_usage(self) -> None:
        card, _layout, self.use_title, self.use_text = self._step_card()
        self.content_layout.addWidget(card)
        card, _layout, self.trouble_title, self.trouble_text = self._step_card()
        self.content_layout.addWidget(card)

    # ------------------------------------------------------------ actions --
    def _copy(self, command: str, button: QPushButton) -> None:
        clipboard = QApplication.clipboard()
        if clipboard is None:
            return
        clipboard.setText(command)
        self._reset_copy_buttons()
        button.setText(translate("ext_copied"))
        self._copied_timer.start()

    def _reset_copy_buttons(self) -> None:
        for button in self.copy_buttons:
            button.setText(translate("ext_copy_command"))

    # ---------------------------------------------------------- language --
    def update_ui_text(self):
        retranslate_notes(self)
        # Icons in the theme's accent colour, redrawn when the theme changes.
        for label, icon_name, size in self.theme_icons:
            label.setPixmap(qta.icon(icon_name, color=color("INFO")).pixmap(size, size))
        self.title_label.setText(translate("extension_title"))
        self.subtitle_label.setText(translate("ext_subtitle"))
        self.releases_button.setText(translate("ext_open_releases"))
        self.folder_button.setText(translate("ext_open_folder"))
        for title, text, title_key, text_key in self.feature_labels:
            title.setText(translate(title_key))
            text.setText(translate(text_key))
        self.install_heading.setText(translate("ext_install_heading"))
        self.step_get_title.setText(translate("ext_step_get_title"))
        self.step_get_text.setText(translate("ext_step_get_text"))
        self.step_manifest_title.setText(translate("ext_step_manifest_title"))
        self.step_manifest_text.setText(translate("ext_step_manifest_text"))
        self.commands_label.setText(translate("ext_commands_label"))
        self.step_chrome_title.setText(translate("ext_step_chrome_title"))
        self.step_chrome_text.setText(translate("ext_step_chrome_text"))
        self.step_firefox_title.setText(translate("ext_step_firefox_title"))
        self.step_firefox_text.setText(translate("ext_step_firefox_text"))
        self.use_title.setText(translate("ext_use_title"))
        self.use_text.setText(translate("ext_use_text"))
        self.trouble_title.setText(translate("ext_trouble_title"))
        self.trouble_text.setText(translate("ext_trouble_text"))
        self._reset_copy_buttons()

    def refresh_ui(self):
        self.update_ui_text()
