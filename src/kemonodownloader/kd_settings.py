import os
import socket
import subprocess
import sys

import qtawesome as qta
from PyQt6.QtCore import QProcess, QSettings, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from kemonodownloader.history_store import HistoryStore
from kemonodownloader.kd_language import language_manager, translate
from kemonodownloader.kd_notes import retranslate_notes, tip, tips, with_note
from kemonodownloader.kd_theme import (
    DEFAULT_THEME,
    THEMES,
    set_role,
    set_tone,
    theme_name,
)

# The SOCKS port configured for the Tor process this app starts (and Tor's
# default). socks5h makes Tor resolve host names too, so DNS doesn't leak.
TOR_SOCKS_PROXY = "socks5h://127.0.0.1:9050"

# Which console messages to show: log level -> (setting, label, default).
# Debug details are mostly of use when reporting a problem, so they start off.
LOG_LEVEL_SETTINGS = {
    "DEBUG": ("show_debug_logs", "log_level_debug", False),
    "INFO": ("show_info_logs", "log_level_info", True),
    "WARNING": ("show_warning_logs", "log_level_warning", True),
    "ERROR": ("show_error_logs", "log_level_error", True),
}

FOLDER_STRATEGY_LABELS = {
    "per_post": "per_post_folders",
    "single_folder": "single_creator_folder",
    "by_file_type": "subfolders_by_file_type",
}

# Every setting Apply Changes applies, as (key, label key), in the order the
# tab shows them; the confirmation lists the changed ones in this order.
SETTING_LABELS = [
    ("base_folder_name", "folder_name"),
    ("base_directory", "save_directory"),
    ("simultaneous_downloads", "simultaneous_downloads"),
    ("save_preview_images", "save_preview_images"),
    ("creator_posts_max_attempts", "creator_posts_max_attempts"),
    ("post_data_max_retries", "post_data_max_retries"),
    ("file_download_max_retries", "file_download_max_retries"),
    ("api_request_max_retries", "api_request_max_retries"),
    ("creator_filename_template", "filename_template"),
    ("creator_folder_strategy", "folder_strategy"),
    ("auto_check_updates", "auto_check_updates"),
    *[(key, label) for key, label, _default in LOG_LEVEL_SETTINGS.values()],
    ("language", "language"),
    ("font", "font"),
    ("theme", "theme_label"),
    ("use_proxy", "use_proxy"),
    ("proxy_type", "proxy_type"),
    ("custom_proxy_url", "custom_proxy_url"),
    ("tor_path", "tor_path"),
]

# Where Tor listens: the Tor this tab starts, or a Tor service of the user's.
TOR_SOCKS_ADDRESS = ("127.0.0.1", 9050)

# What applying a new proxy route should do about Tor (_prepare_route).
ROUTE_OK = "ok"
ROUTE_STOP_TOR = "stop_tor"

# Tor Expert Bundle fetched by "Download Tor", and the SHA-256 of each archive.
# The hashes are copied from the release's sha256sums-signed-build.txt after
# checking its signature against the Tor Browser Developers signing key
# (EF6E 286D DA85 EA2A 4BA7 DE68 4E2C 6E87 9329 8290). To update, change the
# version and copy the new hashes the same way; a download whose hash doesn't
# match is refused.
TOR_BUNDLE_VERSION = "16.0.1"
TOR_BUNDLE_SHA256 = {
    "windows-x86_64": "9eed3c3ff1fe43df034ce360196c9ec95472560d77ff55614d0cd5120edea27b",
    "macos-aarch64": "0b7d022017c31e3f972d06465bcd7ac50feb66ac825547419a934914fe4bb156",
    "macos-x86_64": "15464d99adc3bb4de1308260d79878336b04a1ac1aeff83e10f192de7d235946",
    "linux-x86_64": "7039cb16060ab22e669852e55774d894b55f25ea8bd0ab7194d3478429a58725",
    "linux-aarch64": "67040520d44c87ccaaf5aa7df0dc1ff122eb938dbb600ae7722e8b6b75282a4b",
}
TOR_ARCHIVE_URL = "https://archive.torproject.org/tor-package-archive/torbrowser"


def tor_bundle_platform(sys_platform=None, machine=None):
    """Return the expert-bundle platform name for this computer, or None."""
    import platform

    sys_platform = sys.platform if sys_platform is None else sys_platform
    machine = (platform.machine() if machine is None else machine).lower()
    if machine in ("amd64", "x86_64", "x64"):
        arch = "x86_64"
    elif machine in ("arm64", "aarch64"):
        arch = "aarch64"
    else:
        return None
    if sys_platform == "win32":
        # There is no Windows Arm build; Windows 11 on Arm runs x64 programs.
        name = "windows-x86_64"
    elif sys_platform == "darwin":
        name = f"macos-{arch}"
    elif sys_platform.startswith("linux"):
        name = f"linux-{arch}"
    else:
        return None
    return name if name in TOR_BUNDLE_SHA256 else None


class SettingsTab(QWidget):
    settings_applied = pyqtSignal()
    language_changed = pyqtSignal()
    font_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    download_started = pyqtSignal()
    download_finished = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.qsettings = QSettings("VoxDroid", "KemonoDownloader")
        self.default_settings = {
            "base_folder_name": "Kemono Downloader",
            "base_directory": self.get_default_base_directory(),
            "simultaneous_downloads": 5,
            "auto_check_updates": True,
            # Save the preview image of files the site only has previews of.
            "save_preview_images": False,
            **{key: default for key, _label, default in LOG_LEVEL_SETTINGS.values()},
            "language": "english",
            "creator_posts_max_attempts": 200,
            "post_data_max_retries": 7,
            "file_download_max_retries": 50,
            "api_request_max_retries": 3,
            "use_proxy": False,
            "proxy_type": "tor",  # "custom", "tor"
            "custom_proxy_url": "",
            "tor_path": "",
            # Creator downloader filename/folder customization
            "creator_filename_template": "{post_id}_{orig_name}",
            "creator_folder_strategy": "per_post",  # per_post|single_folder|by_file_type
            # Font setting
            "font": "JetBrains Mono",  # "JetBrains Mono", "Poppins"
            "theme": DEFAULT_THEME,  # a key of kd_theme.THEMES
        }
        self.settings = self.load_settings()
        self.temp_settings = self.settings.copy()

        # Tor process management
        self.tor_process = None
        self.tor_data_dir = None
        self.tor_config_file = None

        language_manager.set_language(self.settings["language"])

        self.setup_ui()

    def get_default_base_directory(self):
        """Return a platform-appropriate default directory for app data."""
        if sys.platform == "win32":  # Windows
            return os.path.join(
                os.getenv("APPDATA", os.path.expanduser("~")), "Kemono Downloader"
            )
        elif sys.platform == "darwin":  # macOS
            return os.path.expanduser("~/Library/Application Support/Kemono Downloader")
        else:  # Linux and others
            fallback_data_home = os.path.join(os.path.expanduser("~"), ".local/share")
            return os.path.join(
                os.getenv("XDG_DATA_HOME", fallback_data_home),
                "Kemono Downloader",
            )

    def load_settings(self):
        settings_dict = {}
        settings_dict["base_folder_name"] = self.qsettings.value(
            "base_folder_name", self.default_settings["base_folder_name"], type=str
        )
        settings_dict["base_directory"] = self.qsettings.value(
            "base_directory", self.default_settings["base_directory"], type=str
        )
        settings_dict["simultaneous_downloads"] = self.qsettings.value(
            "simultaneous_downloads",
            self.default_settings["simultaneous_downloads"],
            type=int,
        )
        settings_dict["auto_check_updates"] = self.qsettings.value(
            "auto_check_updates", self.default_settings["auto_check_updates"], type=bool
        )
        settings_dict["save_preview_images"] = self.qsettings.value(
            "save_preview_images",
            self.default_settings.get("save_preview_images", False),
            type=bool,
        )
        for key, _label, default in LOG_LEVEL_SETTINGS.values():
            settings_dict[key] = self.qsettings.value(
                key, self.default_settings.get(key, default), type=bool
            )
        settings_dict["language"] = self.qsettings.value(
            "language", self.default_settings["language"], type=str
        )
        settings_dict["creator_posts_max_attempts"] = self.qsettings.value(
            "creator_posts_max_attempts",
            self.default_settings["creator_posts_max_attempts"],
            type=int,
        )
        settings_dict["post_data_max_retries"] = self.qsettings.value(
            "post_data_max_retries",
            self.default_settings["post_data_max_retries"],
            type=int,
        )
        settings_dict["file_download_max_retries"] = self.qsettings.value(
            "file_download_max_retries",
            self.default_settings["file_download_max_retries"],
            type=int,
        )
        settings_dict["api_request_max_retries"] = self.qsettings.value(
            "api_request_max_retries",
            self.default_settings["api_request_max_retries"],
            type=int,
        )
        settings_dict["use_proxy"] = False  # Always start with proxy disabled
        settings_dict["proxy_type"] = self.qsettings.value(
            "proxy_type", self.default_settings["proxy_type"], type=str
        )
        # Convert old "none" proxy type to "tor" for backward compatibility
        if settings_dict["proxy_type"] == "none":
            settings_dict["proxy_type"] = "tor"
        settings_dict["custom_proxy_url"] = self.qsettings.value(
            "custom_proxy_url", self.default_settings["custom_proxy_url"], type=str
        )
        settings_dict["tor_path"] = self.qsettings.value(
            "tor_path", self.default_settings["tor_path"], type=str
        )
        # Creator downloader settings
        settings_dict["creator_filename_template"] = self.qsettings.value(
            "creator_filename_template",
            self.default_settings.get(
                "creator_filename_template", "{post_id}_{orig_name}"
            ),
            type=str,
        )
        settings_dict["creator_folder_strategy"] = self.qsettings.value(
            "creator_folder_strategy",
            self.default_settings.get("creator_folder_strategy", "per_post"),
            type=str,
        )
        # Font setting
        settings_dict["font"] = self.qsettings.value(
            "font", self.default_settings.get("font", "JetBrains Mono"), type=str
        )
        settings_dict["theme"] = theme_name(
            self.qsettings.value("theme", DEFAULT_THEME, type=str)
        )
        return settings_dict

    def save_settings(self):
        self.qsettings.setValue("base_folder_name", self.settings["base_folder_name"])
        self.qsettings.setValue("base_directory", self.settings["base_directory"])
        self.qsettings.setValue(
            "simultaneous_downloads", self.settings["simultaneous_downloads"]
        )
        self.qsettings.setValue(
            "auto_check_updates", self.settings["auto_check_updates"]
        )
        self.qsettings.setValue(
            "save_preview_images", self.settings.get("save_preview_images", False)
        )
        for key, _label, default in LOG_LEVEL_SETTINGS.values():
            self.qsettings.setValue(key, self.settings.get(key, default))
        self.qsettings.setValue("language", self.settings["language"])
        self.qsettings.setValue(
            "creator_posts_max_attempts", self.settings["creator_posts_max_attempts"]
        )
        self.qsettings.setValue(
            "post_data_max_retries", self.settings["post_data_max_retries"]
        )
        self.qsettings.setValue(
            "file_download_max_retries", self.settings["file_download_max_retries"]
        )
        self.qsettings.setValue(
            "api_request_max_retries", self.settings["api_request_max_retries"]
        )
        self.qsettings.setValue("proxy_type", self.settings["proxy_type"])
        self.qsettings.setValue("custom_proxy_url", self.settings["custom_proxy_url"])
        self.qsettings.setValue("tor_path", self.settings["tor_path"])
        # Creator downloader settings
        self.qsettings.setValue(
            "creator_filename_template",
            self.settings.get("creator_filename_template", "{post_id}_{orig_name}"),
        )
        self.qsettings.setValue(
            "creator_folder_strategy",
            self.settings.get("creator_folder_strategy", "per_post"),
        )
        # Font setting
        self.qsettings.setValue(
            "font",
            self.settings.get("font", "JetBrains Mono"),
        )
        self.qsettings.setValue("theme", self.settings.get("theme", DEFAULT_THEME))
        self.qsettings.sync()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Folder Settings Group
        self.folder_group = QGroupBox()
        folder_layout = QGridLayout()

        self.folder_name_label = QLabel()
        folder_layout.addWidget(self.folder_name_label, 0, 0)
        self.folder_name_input = QLineEdit(self.temp_settings["base_folder_name"])
        self.folder_name_input.textChanged.connect(
            lambda: self.update_temp_setting(
                "base_folder_name", self.folder_name_input.text()
            )
        )
        folder_layout.addWidget(self.folder_name_input, 0, 1)

        self.directory_label = QLabel()
        folder_layout.addWidget(self.directory_label, 1, 0)
        self.directory_input = QLineEdit(self.temp_settings["base_directory"])
        self.directory_input.textChanged.connect(
            lambda: self.update_temp_setting(
                "base_directory", self.directory_input.text()
            )
        )
        folder_layout.addWidget(self.directory_input, 1, 1)

        self.browse_button = QPushButton()
        self.browse_button.clicked.connect(self.browse_directory)
        folder_layout.addWidget(self.browse_button, 1, 2)

        self.open_directory_button = QPushButton()
        self.open_directory_button.clicked.connect(self.open_app_directory)
        folder_layout.addWidget(self.open_directory_button, 1, 3)

        self.folder_group.setLayout(with_note(folder_layout, "note_folder_settings"))
        layout.addWidget(self.folder_group)

        # Download Settings Group
        self.download_group = QGroupBox()
        download_layout = QGridLayout()

        self.simultaneous_downloads_label = QLabel()
        download_layout.addWidget(self.simultaneous_downloads_label, 0, 0)
        self.download_slider = QSlider(Qt.Orientation.Horizontal)
        self.download_slider.setRange(1, 20)
        self.download_slider.setValue(self.temp_settings["simultaneous_downloads"])
        self.download_slider.valueChanged.connect(self.update_simultaneous_downloads)
        download_layout.addWidget(self.download_slider, 0, 1)
        self.download_spinbox = QSpinBox()
        self.download_spinbox.setRange(1, 20)
        self.download_spinbox.setValue(self.temp_settings["simultaneous_downloads"])
        self.download_spinbox.valueChanged.connect(self.update_simultaneous_downloads)
        download_layout.addWidget(self.download_spinbox, 0, 2)

        self.pawchive_policy_info_button = QPushButton(
            qta.icon("fa5s.info-circle", color="#A0C0FF"), ""
        )
        self.pawchive_policy_info_button.setFixedSize(28, 28)
        set_role(self.pawchive_policy_info_button, "icon")
        self.pawchive_policy_info_button.clicked.connect(self.show_pawchive_policy_info)
        download_layout.addWidget(self.pawchive_policy_info_button, 0, 3)

        self.save_previews_checkbox = QCheckBox()
        self.save_previews_checkbox.setChecked(
            self.temp_settings.get("save_preview_images", False)
        )
        self.save_previews_checkbox.stateChanged.connect(
            lambda state: self.update_temp_setting(
                "save_preview_images", state == Qt.CheckState.Checked.value
            )
        )
        download_layout.addWidget(self.save_previews_checkbox, 1, 0, 1, 4)

        self.download_group.setLayout(
            with_note(download_layout, "note_download_settings")
        )
        layout.addWidget(self.download_group)

        # Retry Settings Group
        self.retry_group = QGroupBox()
        retry_layout = QGridLayout()

        self.creator_posts_max_attempts_label = QLabel()
        retry_layout.addWidget(self.creator_posts_max_attempts_label, 0, 0)
        self.creator_posts_max_attempts_spinbox = QSpinBox()
        self.creator_posts_max_attempts_spinbox.setRange(1, 1000)
        self.creator_posts_max_attempts_spinbox.setValue(
            self.temp_settings["creator_posts_max_attempts"]
        )
        self.creator_posts_max_attempts_spinbox.valueChanged.connect(
            lambda value: self.update_temp_setting("creator_posts_max_attempts", value)
        )
        retry_layout.addWidget(self.creator_posts_max_attempts_spinbox, 0, 1)

        self.post_data_max_retries_label = QLabel()
        retry_layout.addWidget(self.post_data_max_retries_label, 1, 0)
        self.post_data_max_retries_spinbox = QSpinBox()
        self.post_data_max_retries_spinbox.setRange(1, 100)
        self.post_data_max_retries_spinbox.setValue(
            self.temp_settings["post_data_max_retries"]
        )
        self.post_data_max_retries_spinbox.valueChanged.connect(
            lambda value: self.update_temp_setting("post_data_max_retries", value)
        )
        retry_layout.addWidget(self.post_data_max_retries_spinbox, 1, 1)

        self.file_download_max_retries_label = QLabel()
        retry_layout.addWidget(self.file_download_max_retries_label, 2, 0)
        self.file_download_max_retries_spinbox = QSpinBox()
        self.file_download_max_retries_spinbox.setRange(1, 200)
        self.file_download_max_retries_spinbox.setValue(
            self.temp_settings["file_download_max_retries"]
        )
        self.file_download_max_retries_spinbox.valueChanged.connect(
            lambda value: self.update_temp_setting("file_download_max_retries", value)
        )
        retry_layout.addWidget(self.file_download_max_retries_spinbox, 2, 1)

        self.api_request_max_retries_label = QLabel()
        retry_layout.addWidget(self.api_request_max_retries_label, 3, 0)
        self.api_request_max_retries_spinbox = QSpinBox()
        self.api_request_max_retries_spinbox.setRange(1, 50)
        self.api_request_max_retries_spinbox.setValue(
            self.temp_settings["api_request_max_retries"]
        )
        self.api_request_max_retries_spinbox.valueChanged.connect(
            lambda value: self.update_temp_setting("api_request_max_retries", value)
        )
        retry_layout.addWidget(self.api_request_max_retries_spinbox, 3, 1)

        self.retry_group.setLayout(with_note(retry_layout, "note_retry_settings"))
        layout.addWidget(self.retry_group)

        # Creator downloader customization group
        self.creator_custom_group = QGroupBox()
        creator_custom_layout = QGridLayout()

        self.creator_custom_label = QLabel()
        creator_custom_layout.addWidget(self.creator_custom_label, 0, 0)

        # Filename template combo (preset selections + editable custom)
        self.creator_filename_combo = QComboBox()
        self.creator_filename_combo.setEditable(True)
        # Preset templates (label_key, template_string)
        self._template_presets = [
            ("tmpl_postid_orig", "{post_id}_{orig_name}"),
            ("tmpl_posttitle_postid_orig", "{post_title}-{post_id}-{orig_name}"),
            ("tmpl_postid_posttitle", "{post_id}_{post_title}"),
            ("tmpl_index_posttitle", "{file_index}_{post_title}_{orig_name}"),
        ]
        for label_key, tpl in self._template_presets:
            self.creator_filename_combo.addItem(translate(label_key), tpl)
        # Add a custom option at the end
        self.creator_filename_combo.addItem(
            translate("tmpl_custom"), "{post_id}_{orig_name}"
        )
        # Set current or custom text
        current_tpl = self.temp_settings.get(
            "creator_filename_template", "{post_id}_{orig_name}"
        )
        found_index = None
        for i in range(self.creator_filename_combo.count()):
            if self.creator_filename_combo.itemData(i) == current_tpl:
                found_index = i
                break
        if found_index is not None:
            self.creator_filename_combo.setCurrentIndex(found_index)
        else:
            # Use custom editable text
            self.creator_filename_combo.setCurrentIndex(
                self.creator_filename_combo.count() - 1
            )
            self.creator_filename_combo.setEditText(current_tpl)

        # Connect both change events
        self.creator_filename_combo.currentIndexChanged.connect(
            self._on_template_choice
        )
        self.creator_filename_combo.lineEdit().textChanged.connect(
            self._on_template_text
        )
        creator_custom_layout.addWidget(self.creator_filename_combo, 0, 1)

        # Help button for template variables
        self.creator_template_help_btn = QPushButton("?")
        set_role(self.creator_template_help_btn, "icon")
        self.creator_template_help_btn.setFixedSize(30, 30)
        self.creator_template_help_btn.clicked.connect(self.show_template_help)
        creator_custom_layout.addWidget(self.creator_template_help_btn, 0, 2)

        self.creator_folder_strategy_label = QLabel()
        creator_custom_layout.addWidget(self.creator_folder_strategy_label, 1, 0)

        self.creator_folder_strategy_combo = QComboBox()
        self.creator_folder_strategy_combo.addItem(
            translate("per_post_folders"), "per_post"
        )
        self.creator_folder_strategy_combo.addItem(
            translate("single_creator_folder"), "single_folder"
        )
        self.creator_folder_strategy_combo.addItem(
            translate("subfolders_by_file_type"), "by_file_type"
        )
        # Set current index based on temp setting
        strategy = self.temp_settings.get("creator_folder_strategy", "per_post")
        for i in range(self.creator_folder_strategy_combo.count()):
            if self.creator_folder_strategy_combo.itemData(i) == strategy:
                self.creator_folder_strategy_combo.setCurrentIndex(i)
                break
        self.creator_folder_strategy_combo.currentIndexChanged.connect(
            lambda idx: self.update_temp_setting(
                "creator_folder_strategy",
                self.creator_folder_strategy_combo.itemData(idx),
            )
        )
        creator_custom_layout.addWidget(self.creator_folder_strategy_combo, 1, 1)

        self.creator_custom_group.setLayout(
            with_note(creator_custom_layout, "note_creator_settings")
        )
        layout.addWidget(self.creator_custom_group)

        # Update Settings Group
        self.update_group = QGroupBox()
        update_layout = QGridLayout()

        self.auto_update_label = QLabel()
        update_layout.addWidget(self.auto_update_label, 0, 0)
        self.auto_update_checkbox = QCheckBox()
        self.auto_update_checkbox.setChecked(self.temp_settings["auto_check_updates"])
        self.auto_update_checkbox.stateChanged.connect(
            lambda state: self.update_temp_setting(
                "auto_check_updates", state == Qt.CheckState.Checked.value
            )
        )
        update_layout.addWidget(self.auto_update_checkbox, 0, 1)

        self.update_group.setLayout(with_note(update_layout, "note_update_settings"))
        layout.addWidget(self.update_group)

        # Log Settings Group: which messages the consoles show.
        self.log_group = QGroupBox()
        log_layout = QHBoxLayout()
        log_layout.setSpacing(18)
        self.log_level_checkboxes = {}
        for level, (key, _label, default) in LOG_LEVEL_SETTINGS.items():
            checkbox = QCheckBox()
            checkbox.setChecked(bool(self.temp_settings.get(key, default)))
            checkbox.stateChanged.connect(
                lambda state, k=key: self.set_log_level_shown(
                    k, state == Qt.CheckState.Checked.value
                )
            )
            log_layout.addWidget(checkbox)
            self.log_level_checkboxes[level] = checkbox
        log_layout.addStretch()
        self.log_group.setLayout(with_note(log_layout, "note_log_settings"))
        layout.addWidget(self.log_group)

        # Language Settings Group
        self.language_group = QGroupBox()
        language_layout = QGridLayout()

        self.language_label = QLabel()
        language_layout.addWidget(self.language_label, 0, 0)

        self.language_combo = QComboBox()
        self.update_language_combo()

        self.language_combo.currentIndexChanged.connect(self.update_language)
        language_layout.addWidget(self.language_combo, 0, 1)

        self.language_group.setLayout(
            with_note(language_layout, "note_language_settings")
        )
        layout.addWidget(self.language_group)

        # Font Settings Group
        self.font_group = QGroupBox()
        font_layout = QGridLayout()

        self.font_label = QLabel()
        font_layout.addWidget(self.font_label, 0, 0)

        self.font_combo = QComboBox()
        self._available_fonts = [
            ("JetBrains Mono", "JetBrains Mono"),
            ("Poppins", "Poppins"),
        ]
        for display_name, font_family in self._available_fonts:
            self.font_combo.addItem(display_name, font_family)

        # Set current font selection
        current_font = self.temp_settings.get("font", "JetBrains Mono")
        for i in range(self.font_combo.count()):
            if self.font_combo.itemData(i) == current_font:
                self.font_combo.setCurrentIndex(i)
                break
        self.font_combo.currentIndexChanged.connect(self.update_font)
        font_layout.addWidget(self.font_combo, 0, 1)

        self.font_group.setLayout(with_note(font_layout, "note_font_settings"))
        layout.addWidget(self.font_group)

        # Appearance Group: the colour theme, switched on Apply Changes.
        self.appearance_group = QGroupBox()
        appearance_layout = QGridLayout()
        self.theme_label = QLabel()
        appearance_layout.addWidget(self.theme_label, 0, 0)
        self.theme_combo = QComboBox()
        for name in THEMES:
            self.theme_combo.addItem(translate(f"theme_{name}"), name)
        self.theme_combo.setCurrentIndex(
            max(0, self.theme_combo.findData(self.temp_settings.get("theme")))
        )
        self.theme_combo.currentIndexChanged.connect(self.update_theme)
        appearance_layout.addWidget(self.theme_combo, 0, 1)
        self.appearance_group.setLayout(
            with_note(appearance_layout, "note_appearance_settings")
        )
        layout.addWidget(self.appearance_group)

        # Proxy Settings Group. The switch and a short explanation are always
        # visible; the options below them only while the switch is on.
        self.network_group = QGroupBox()
        network_layout = QVBoxLayout(self.network_group)
        network_layout.setSpacing(8)

        self.use_proxy_checkbox = QCheckBox()
        set_role(self.use_proxy_checkbox, "heading")
        self.use_proxy_checkbox.stateChanged.connect(self.on_use_proxy_changed)
        network_layout.addWidget(self.use_proxy_checkbox)

        self.proxy_intro_label = QLabel()
        set_role(self.proxy_intro_label, "note")
        self.proxy_intro_label.setWordWrap(True)
        network_layout.addWidget(self.proxy_intro_label)

        # Options shown while the proxy is on (kept as proxy_group).
        self.proxy_group = QWidget()
        self.proxy_group.setVisible(False)  # shown by on_use_proxy_changed
        proxy_layout = QVBoxLayout(self.proxy_group)
        proxy_layout.setContentsMargins(0, 6, 0, 0)
        proxy_layout.setSpacing(10)

        # Proxy type selection
        proxy_type_layout = QHBoxLayout()
        self.proxy_type_label = QLabel()
        proxy_type_layout.addWidget(self.proxy_type_label)

        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.setMinimumWidth(220)
        self.proxy_type_combo.addItem(translate("custom_proxy"), "custom")
        self.proxy_type_combo.addItem("Tor", "tor")
        self.proxy_type_combo.currentIndexChanged.connect(self.on_proxy_type_changed)

        # Block signals during initialization to prevent premature UI updates
        self.use_proxy_checkbox.blockSignals(True)
        self.proxy_type_combo.blockSignals(True)

        # Set initial values
        self.use_proxy_checkbox.setChecked(self.temp_settings["use_proxy"])
        self.proxy_type_combo.setCurrentIndex(
            self.get_proxy_type_index(self.temp_settings["proxy_type"])
        )

        # Unblock signals
        self.use_proxy_checkbox.blockSignals(False)
        self.proxy_type_combo.blockSignals(False)

        proxy_type_layout.addWidget(self.proxy_type_combo)
        proxy_type_layout.addStretch()
        proxy_layout.addLayout(proxy_type_layout)

        # Custom proxy: address, test button and the accepted formats.
        self.custom_proxy_panel = QWidget()
        custom_panel_layout = QVBoxLayout(self.custom_proxy_panel)
        custom_panel_layout.setContentsMargins(0, 0, 0, 0)
        custom_panel_layout.setSpacing(6)

        self.custom_proxy_layout = QHBoxLayout()
        self.custom_proxy_label = QLabel()
        self.custom_proxy_layout.addWidget(self.custom_proxy_label)

        self.custom_proxy_input = QLineEdit(self.temp_settings["custom_proxy_url"])
        self.custom_proxy_input.setPlaceholderText("127.0.0.1:8080")
        self.custom_proxy_input.textChanged.connect(
            lambda: self.update_temp_setting(
                "custom_proxy_url", self.custom_proxy_input.text()
            )
        )
        self.custom_proxy_layout.addWidget(self.custom_proxy_input, stretch=1)

        self.test_custom_proxy_button = QPushButton()
        self.test_custom_proxy_button.clicked.connect(self.test_custom_proxy)
        self.custom_proxy_layout.addWidget(self.test_custom_proxy_button)
        custom_panel_layout.addLayout(self.custom_proxy_layout)

        self.custom_proxy_hint_label = QLabel()
        set_role(self.custom_proxy_hint_label, "muted")
        self.custom_proxy_hint_label.setWordWrap(True)
        custom_panel_layout.addWidget(self.custom_proxy_hint_label)
        proxy_layout.addWidget(self.custom_proxy_panel)

        # Tor: path and status, then the controls, then download progress
        # and Tor's own output.
        self.tor_panel = QWidget()
        self.tor_layout = QVBoxLayout(self.tor_panel)
        self.tor_layout.setContentsMargins(0, 0, 0, 0)
        self.tor_layout.setSpacing(8)

        tor_header_layout = QHBoxLayout()
        self.tor_label = QLabel()
        tor_header_layout.addWidget(self.tor_label)
        tor_header_layout.addStretch()
        self.tor_status_label = QLabel(translate("tor_status_stopped"))
        set_role(self.tor_status_label, "pill")
        set_tone(self.tor_status_label, "error")
        self.tor_status_label.setVisible(False)
        tor_header_layout.addWidget(self.tor_status_label)
        self.tor_layout.addLayout(tor_header_layout)

        tor_path_layout = QHBoxLayout()
        self.tor_path_input = QLineEdit(self.temp_settings["tor_path"])
        self.tor_path_input.setReadOnly(True)
        self.tor_path_input.textChanged.connect(self.update_tor_button_states)
        tor_path_layout.addWidget(self.tor_path_input, stretch=1)

        self.browse_tor_button = QPushButton()
        self.browse_tor_button.clicked.connect(self.browse_tor_executable)
        tor_path_layout.addWidget(self.browse_tor_button)

        self.download_tor_button = QPushButton()
        self.download_tor_button.clicked.connect(self.download_tor)
        tor_path_layout.addWidget(self.download_tor_button)
        self.tor_layout.addLayout(tor_path_layout)

        tor_actions_layout = QHBoxLayout()
        self.start_tor_button = QPushButton()
        set_role(self.start_tor_button, "primary")
        self.start_tor_button.clicked.connect(self.start_tor)
        tor_actions_layout.addWidget(self.start_tor_button)

        self.stop_tor_button = QPushButton()
        set_role(self.stop_tor_button, "danger")
        self.stop_tor_button.clicked.connect(self.stop_tor)
        tor_actions_layout.addWidget(self.stop_tor_button)

        self.test_tor_button = QPushButton()
        self.test_tor_button.clicked.connect(self.test_tor)
        tor_actions_layout.addWidget(self.test_tor_button)
        tor_actions_layout.addStretch()

        self.help_tor_button = QPushButton(translate("help_button"))
        self.help_tor_button.clicked.connect(self.show_tor_help)
        tor_actions_layout.addWidget(self.help_tor_button)
        self.tor_layout.addLayout(tor_actions_layout)

        self.tor_hint_label = QLabel()
        set_role(self.tor_hint_label, "muted")
        self.tor_hint_label.setWordWrap(True)
        self.tor_layout.addWidget(self.tor_hint_label)

        # Tor download progress bar
        self.tor_progress_bar = QProgressBar()
        self.tor_progress_bar.setVisible(False)
        self.tor_layout.addWidget(self.tor_progress_bar)

        # Tor output text area
        self.tor_output_label = QLabel("Tor Output:")
        set_role(self.tor_output_label, "heading")
        self.tor_output_label.setVisible(False)
        self.tor_layout.addWidget(self.tor_output_label)

        self.tor_output_text = QTextEdit()
        self.tor_output_text.setMaximumHeight(150)
        set_role(self.tor_output_text, "console")
        self.tor_output_text.setReadOnly(True)
        self.tor_output_text.setVisible(False)
        self.tor_layout.addWidget(self.tor_output_text)

        proxy_layout.addWidget(self.tor_panel)
        network_layout.addWidget(self.proxy_group)
        layout.addWidget(self.network_group)

        # Initialize proxy UI state - hide widgets by default
        self.custom_proxy_label.setVisible(False)
        self.custom_proxy_input.setVisible(False)
        self.test_custom_proxy_button.setVisible(False)
        self.tor_label.setVisible(False)
        self.tor_path_input.setVisible(False)
        self.browse_tor_button.setVisible(False)
        self.start_tor_button.setVisible(False)
        self.stop_tor_button.setVisible(False)
        self.download_tor_button.setVisible(False)
        self.test_tor_button.setVisible(False)
        self.help_tor_button.setVisible(False)
        self.tor_status_label.setVisible(False)
        self.tor_progress_bar.setVisible(False)
        self.tor_output_label.setVisible(False)
        self.tor_output_text.setVisible(False)
        self.on_use_proxy_changed(self.temp_settings["use_proxy"])

        # Buttons Layout. Nothing above takes effect until Apply Changes; the
        # pill says when something is waiting, and Discard puts it back.
        buttons_layout = QHBoxLayout()

        self.apply_button = QPushButton()
        self.apply_button.clicked.connect(self.confirm_and_apply_settings)
        buttons_layout.addWidget(self.apply_button)

        self.discard_button = QPushButton()
        self.discard_button.clicked.connect(self.discard_changes)
        buttons_layout.addWidget(self.discard_button)

        self.reset_button = QPushButton(translate("reset_to_defaults"))
        set_role(self.reset_button, "danger")
        self.reset_button.clicked.connect(self.confirm_and_reset_settings)
        buttons_layout.addWidget(self.reset_button)

        buttons_layout.addStretch()
        self.pending_label = QLabel()
        set_role(self.pending_label, "pill")
        set_tone(self.pending_label, "warning")
        buttons_layout.addWidget(self.pending_label)

        layout.addLayout(buttons_layout)
        layout.addStretch()
        self._refresh_pending_state()

        # Make the settings page scrollable
        container = QWidget()
        container.setLayout(layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(container)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

        # Tooltips, for when a section's note isn't enough.
        tip(self.folder_name_input, "tip_folder_name")
        tip(self.directory_input, "tip_save_directory")
        tip(self.browse_button, "tip_browse_directory")
        tip(self.open_directory_button, "tip_open_directory")
        tips(
            (self.download_slider, self.download_spinbox), "tip_simultaneous_downloads"
        )
        tip(self.creator_posts_max_attempts_spinbox, "tip_creator_posts_attempts")
        tip(self.post_data_max_retries_spinbox, "tip_post_data_retries")
        tip(self.file_download_max_retries_spinbox, "tip_file_retries")
        tip(self.api_request_max_retries_spinbox, "tip_api_retries")
        tip(self.creator_filename_combo, "tip_filename_template")
        tip(self.creator_folder_strategy_combo, "tip_folder_strategy")
        tip(self.auto_update_checkbox, "tip_auto_update")
        for level, key in (
            ("DEBUG", "tip_log_debug"),
            ("INFO", "tip_log_info"),
            ("WARNING", "tip_log_warning"),
            ("ERROR", "tip_log_error"),
        ):
            tip(self.log_level_checkboxes[level], key)
        tip(self.language_combo, "tip_language")
        tip(self.font_combo, "tip_font")
        tip(self.theme_combo, "tip_theme")
        tip(self.use_proxy_checkbox, "tip_use_proxy")
        tip(self.proxy_type_combo, "tip_proxy_type")
        tip(self.custom_proxy_input, "tip_custom_proxy")
        tip(self.test_custom_proxy_button, "tip_test_proxy")
        tip(self.tor_path_input, "tip_tor_path")
        tip(self.browse_tor_button, "tip_browse_tor")
        tip(self.download_tor_button, "tip_download_tor")
        tip(self.start_tor_button, "tip_start_tor")
        tip(self.stop_tor_button, "tip_stop_tor")
        tip(self.test_tor_button, "tip_test_tor")
        tip(self.help_tor_button, "tip_tor_help")
        tip(self.apply_button, "tip_apply_changes")
        tip(self.discard_button, "tip_discard_changes")
        tip(self.reset_button, "tip_reset_defaults")
        self.update_ui_text()

        # Initialize Tor button states
        self.update_tor_button_states()

    def _on_template_choice(self, index):
        combo = self.creator_filename_combo
        if index < combo.count() - 1:
            self.update_temp_setting("creator_filename_template", combo.itemData(index))
            return
        # "Custom...": start editing from the template in use. The combo has
        # just put the label "Custom..." in the box, which used to become the
        # template itself, naming every downloaded file "Custom...".
        combo.setEditText(
            self.temp_settings.get("creator_filename_template")
            or "{post_id}_{orig_name}"
        )

    def _on_template_text(self, text):
        if text == translate("tmpl_custom"):
            return  # the "Custom..." label, not a template (see above)
        self.update_temp_setting("creator_filename_template", text)

    def update_language_combo(self):
        self.language_combo.blockSignals(True)
        current_language = self.temp_settings["language"]
        self.language_combo.clear()
        self.language_combo.addItem(translate("english"), "english")
        self.language_combo.addItem(translate("japanese"), "japanese")
        self.language_combo.addItem(translate("korean"), "korean")
        self.language_combo.addItem(
            translate("chinese-simplified"), "chinese-simplified"
        )

        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_language:
                self.language_combo.setCurrentIndex(i)
                break
        self.language_combo.blockSignals(False)

    def update_language(self, index):
        language = self.language_combo.itemData(index)
        self.update_temp_setting("language", language)

    def update_font(self, index):
        font_family = self.font_combo.itemData(index)
        self.update_temp_setting("font", font_family)

    def show_template_help(self):
        """Show help text explaining the available filename template placeholders."""
        try:
            QMessageBox.information(
                self,
                translate("filename_template_help_title"),
                translate("filename_template_help_text"),
            )
        except Exception:
            # In case translation lookup or UI fails, fall back to a simple message
            QMessageBox.information(
                self,
                "Template Help",
                "Use placeholders like {post_title}, {post_id}, {orig_name}, {ext}, {creator_name}, {creator_id}, {file_index}, {total_files}",
            )

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, translate("browse"), self.temp_settings["base_directory"]
        )
        if directory:
            self.directory_input.setText(directory)
            self.update_temp_setting("base_directory", directory)

    def open_app_directory(self):
        """Open the current app directory in the system file explorer."""
        directory = os.path.join(
            self.temp_settings["base_directory"], self.temp_settings["base_folder_name"]
        )

        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError:
                QMessageBox.warning(
                    self,
                    translate("error"),
                    translate("could_not_create_directory", directory),
                )
                return

        try:
            if sys.platform == "win32":  # Windows
                os.startfile(directory)
            elif sys.platform == "darwin":  # macOS
                subprocess.call(["open", directory])
            else:  # Linux and other Unix-like systems
                subprocess.call(["xdg-open", directory])
        except Exception as e:
            QMessageBox.warning(
                self, translate("error"), translate("could_not_open_directory", str(e))
            )

    def browse_tor_executable(self):
        """Browse for Tor executable file."""
        if sys.platform == "win32":
            file_filter = "Executable files (*.exe);;All files (*.*)"
            initial_path = self.temp_settings["tor_path"] or "C:\\"
        else:
            file_filter = "All files (*.*)"
            initial_path = self.temp_settings["tor_path"] or "/"

        tor_exe_path, _ = QFileDialog.getOpenFileName(
            self, translate("select_tor_executable"), initial_path, file_filter
        )

        if tor_exe_path:
            self.update_temp_setting("tor_path", tor_exe_path)
            self.tor_path_input.setText(tor_exe_path)

    def auto_detect_tor(self):
        """Try to auto-detect Tor executable in common locations.

        Enhanced detection: in addition to well-known system locations, search
        the current app base directory and download folders so that Tor can be
        detected when installed within the app's own directory (e.g. in
        AppData/Roaming on Windows).
        """
        common_paths = []

        if sys.platform == "win32":
            # Windows common paths
            common_paths.extend(
                [
                    r"C:\Users\Drei\Downloads\Kemono Downloader\Tor\tor\tor.exe",  # User's known location
                    os.path.join(
                        os.getenv("PROGRAMFILES", "C:\\Program Files"),
                        "Tor Browser",
                        "Browser",
                        "TorBrowser",
                        "Tor",
                        "tor.exe",
                    ),
                    os.path.join(
                        os.getenv("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
                        "Tor Browser",
                        "Browser",
                        "TorBrowser",
                        "Tor",
                        "tor.exe",
                    ),
                    os.path.join(
                        os.path.expanduser("~"),
                        "Desktop",
                        "Tor Browser",
                        "Browser",
                        "TorBrowser",
                        "Tor",
                        "tor.exe",
                    ),
                    os.path.join(
                        os.path.expanduser("~"),
                        "Downloads",
                        "Tor Browser",
                        "Browser",
                        "TorBrowser",
                        "Tor",
                        "tor.exe",
                    ),
                ]
            )
        elif sys.platform == "darwin":
            # macOS common paths
            common_paths.extend(
                [
                    "/Applications/Tor Browser.app/Contents/MacOS/Tor/tor",
                    os.path.join(
                        os.path.expanduser("~"),
                        "Applications",
                        "Tor Browser.app",
                        "Contents",
                        "MacOS",
                        "Tor",
                        "tor",
                    ),
                    os.path.join(
                        os.path.expanduser("~"),
                        "Desktop",
                        "Tor Browser.app",
                        "Contents",
                        "MacOS",
                        "Tor",
                        "tor",
                    ),
                    os.path.join(
                        os.path.expanduser("~"),
                        "Downloads",
                        "Tor Browser.app",
                        "Contents",
                        "MacOS",
                        "Tor",
                        "tor",
                    ),
                ]
            )
        else:
            # Linux common paths
            common_paths.extend(
                [
                    "/usr/bin/tor",
                    "/usr/local/bin/tor",
                    "/opt/tor-browser/Browser/TorBrowser/Tor/tor",
                    os.path.join(
                        os.path.expanduser("~"),
                        "tor-browser",
                        "Browser",
                        "TorBrowser",
                        "Tor",
                        "tor",
                    ),
                    os.path.join(
                        os.path.expanduser("~"),
                        "Desktop",
                        "tor-browser",
                        "Browser",
                        "TorBrowser",
                        "Tor",
                        "tor",
                    ),
                    os.path.join(
                        os.path.expanduser("~"),
                        "Downloads",
                        "tor-browser",
                        "Browser",
                        "TorBrowser",
                        "Tor",
                        "tor",
                    ),
                ]
            )

        # Also look for Tor inside the app's base directory / download folders
        try:
            base_dir = self.temp_settings.get("base_directory")
            base_name = self.temp_settings.get("base_folder_name")
        except Exception:
            base_dir = None
            base_name = None

        candidate_roots = []
        if base_dir:
            candidate_roots.extend(
                [
                    base_dir,
                    os.path.join(base_dir, base_name) if base_name else base_dir,
                    os.path.join(base_dir, "Tor"),
                    (
                        os.path.join(base_dir, base_name, "Tor")
                        if base_name
                        else os.path.join(base_dir, "Tor")
                    ),
                    os.path.join(base_dir, "Downloads"),
                    os.path.join(base_dir, "Downloads", "Tor"),
                ]
            )

        # If parent (app) provides download_folder use that too
        if hasattr(self, "parent") and getattr(self.parent, "download_folder", None):
            df = getattr(self.parent, "download_folder")
            candidate_roots.extend([df, os.path.join(df, "Tor")])

        # Prefer searching the app's candidate roots first (so app-local Tor is detected before system-wide installs),
        # then fall back to common system locations
        search_roots = [
            p for p in candidate_roots if p not in common_paths
        ] + common_paths

        for path in search_roots:
            # If path is a file directly, test it
            if os.path.exists(path) and os.path.isfile(path):
                try:
                    result = subprocess.run(
                        [path, "--version"], capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0 and "Tor" in result.stdout:
                        return path
                except Exception:
                    continue

            # If path is a directory, walk it and look for tor executable
            if os.path.exists(path) and os.path.isdir(path):
                try:
                    for root, dirs, files in os.walk(path):
                        for f in files:
                            if f.lower() in ("tor.exe", "tor"):
                                candidate = os.path.join(root, f)
                                try:
                                    result = subprocess.run(
                                        [candidate, "--version"],
                                        capture_output=True,
                                        text=True,
                                        timeout=5,
                                    )
                                    if (
                                        result.returncode == 0
                                        and "Tor" in result.stdout
                                    ):
                                        return candidate
                                except Exception:
                                    # Continue searching other files
                                    continue
                except Exception:
                    # ignore and move to next root
                    continue

        return None

    def update_temp_setting(self, key, value):
        """Record a pending change; nothing takes effect before Apply Changes."""
        self.temp_settings[key] = value
        self._refresh_pending_state()

    # ----------------------------------------------------- pending changes --

    def pending_changes(self):
        """Keys whose value differs from what is applied, in on-screen order."""
        return [
            key
            for key, _label in SETTING_LABELS
            if self.temp_settings.get(key) != self.settings.get(key)
        ]

    def has_pending_changes(self):
        return bool(self.pending_changes())

    def _refresh_pending_state(self):
        """Show whether anything is waiting for Apply Changes."""
        label = getattr(self, "pending_label", None)
        if label is None:
            return  # still building the tab
        pending = self.has_pending_changes()
        label.setVisible(pending)
        self.discard_button.setEnabled(pending)
        set_role(self.apply_button, "primary" if pending else None)

    def _display_value(self, key, value):
        """*value* of setting *key* as the user knows it."""
        if isinstance(value, bool):
            return translate("enabled" if value else "disabled")
        if key == "language":
            return translate(value)
        if key == "theme":
            return translate(f"theme_{theme_name(value)}")
        if key == "creator_folder_strategy":
            return translate(FOLDER_STRATEGY_LABELS.get(value, "per_post_folders"))
        if key == "proxy_type":
            return translate("custom_proxy") if value == "custom" else "Tor"
        text = "" if value is None else str(value)
        return text if text.strip() else "—"

    def describe_changes(self, keys):
        """One "Label: before → after" line per changed setting."""
        labels = dict(SETTING_LABELS)
        lines = []
        for key in keys:
            label = translate(labels[key]).strip().rstrip(":：")
            before = self._display_value(key, self.settings.get(key))
            after = self._display_value(key, self.temp_settings.get(key))
            lines.append(f"• {label}: {before} → {after}")
        return "\n".join(lines)

    def update_simultaneous_downloads(self, value):
        self.update_temp_setting("simultaneous_downloads", value)
        self.download_slider.blockSignals(True)
        self.download_spinbox.blockSignals(True)
        self.download_slider.setValue(value)
        self.download_spinbox.setValue(value)
        self.download_slider.blockSignals(False)
        self.download_spinbox.blockSignals(False)

    def show_pawchive_policy_info(self):
        QMessageBox.information(
            self,
            translate("pawchive_policy_info_title"),
            translate("pawchive_policy_info_text"),
        )

    def confirm_and_apply_settings(self):
        """Apply Changes: list what changed, check it, then apply it."""
        self.apply_pending_settings(confirm=True)

    def apply_pending_settings(self, confirm=True, closing=False):
        """Apply every pending change. True when applied, or nothing to do.

        *confirm* asks first, listing the changes, and reports the result.
        *closing* is Apply from the close-the-app prompt, which has listed
        the changes already; the proxy switch isn't remembered between
        launches, so nothing about Tor needs deciding then.
        """
        changes = self.pending_changes()
        if not changes:
            if confirm:
                QMessageBox.information(
                    self, translate("apply_changes"), translate("nothing_to_apply")
                )
            return True
        route_changes = not closing and self._route_changes()
        if confirm:
            message = translate(
                "confirm_changes_message", self.describe_changes(changes)
            )
            if route_changes and self._downloads_running():
                message += "\n\n" + translate("route_change_during_downloads")
            reply = QMessageBox.question(
                self,
                translate("confirm_settings_change"),
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return False
        if not self._check_pending():
            return False
        applied = self.describe_changes(changes)  # before they stop being changes
        stop_tor_after = False
        if route_changes:
            outcome = self._prepare_route()
            if outcome is None:
                return False
            stop_tor_after = outcome == ROUTE_STOP_TOR
        self._commit_pending()
        if stop_tor_after:
            self.stop_tor()
        if confirm:
            QMessageBox.information(
                self,
                translate("settings_applied"),
                translate("settings_applied_list", applied),
            )
        return True

    def _check_pending(self):
        """Refuse pending values that can't work, explaining why."""
        values = self.temp_settings
        if not values["base_folder_name"].strip():
            QMessageBox.warning(
                self, translate("invalid_input"), translate("folder_name_empty")
            )
            # Both: setText alone does nothing when the box already shows it.
            self.update_temp_setting(
                "base_folder_name", self.settings["base_folder_name"]
            )
            self.folder_name_input.setText(self.settings["base_folder_name"])
            return False
        base_dir = values["base_directory"]
        if not os.path.isdir(base_dir):
            try:
                os.makedirs(base_dir, exist_ok=True)
            except OSError as e:
                QMessageBox.warning(
                    self,
                    translate("invalid_input"),
                    translate("directory_creation_failed", str(e)),
                )
                self.update_temp_setting(
                    "base_directory", self.settings["base_directory"]
                )
                self.directory_input.setText(self.settings["base_directory"])
                return False
        if (
            values.get("use_proxy")
            and values.get("proxy_type") == "custom"
            and not (values.get("custom_proxy_url") or "").strip()
        ):
            # Applied as is, an empty address would mean no proxy at all: a
            # direct connection while the user believes one is in use.
            QMessageBox.warning(
                self, translate("invalid_input"), translate("custom_proxy_url_required")
            )
            return False
        return True

    def _route_changes(self):
        """Whether applying would change how requests reach the sites."""
        return proxies_for(self.temp_settings) != proxies_for(self.settings)

    def _downloads_running(self):
        window = self.parent
        for name in ("post_tab", "creator_tab"):
            if getattr(getattr(window, name, None), "downloading", False) is True:
                return True
        thumbnails = getattr(window, "thumbnail_tab", None)
        thread = getattr(thumbnails, "download_thread", None)
        is_running = getattr(thread, "isRunning", None)
        return bool(callable(is_running) and is_running())

    def _uses_tor(self, values):
        return bool(values.get("use_proxy")) and values.get("proxy_type") == "tor"

    def _prepare_route(self):
        """Settle Tor before a new route takes effect.

        Returns ROUTE_OK, ROUTE_STOP_TOR (stop the app's Tor once applied),
        or None to cancel applying.
        """
        if self._uses_tor(self.temp_settings):
            if self.is_tor_running() or tor_is_listening():
                return ROUTE_OK
            return self._ask_about_stopped_tor()
        if self._uses_tor(self.settings) and self.is_tor_running():
            reply = QMessageBox.question(
                self,
                translate("stop_tor_after_apply_title"),
                translate("stop_tor_after_apply"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                return ROUTE_STOP_TOR
        return ROUTE_OK

    def _ask_about_stopped_tor(self):
        """Tor is about to be used but nothing listens on its port."""
        tor_path = self.temp_settings.get("tor_path") or ""
        can_start = bool(tor_path and os.path.exists(tor_path))
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(translate("tor_not_running_title"))
        text = translate("tor_not_running_apply")
        if not can_start:
            text += "\n\n" + translate("tor_not_set_up_apply")
        box.setText(text)
        start = None
        if can_start:
            start = box.addButton(
                translate("start_tor_and_apply"), QMessageBox.ButtonRole.AcceptRole
            )
        anyway = box.addButton(
            translate("apply_anyway"), QMessageBox.ButtonRole.DestructiveRole
        )
        cancel = box.addButton(QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(start if start is not None else cancel)
        box.exec()
        clicked = box.clickedButton()
        if start is not None and clicked == start:
            self.start_tor()
            # start_tor explains itself when it can't start.
            return ROUTE_OK if self.tor_process is not None else None
        if clicked == anyway:
            return ROUTE_OK
        return None

    def _commit_pending(self):
        """Make the pending values the applied ones, and act on them."""
        old = self.settings
        language_changed = old.get("language") != self.temp_settings.get("language")
        font_changed = old.get("font") != self.temp_settings.get("font")
        theme_changed = theme_name(old.get("theme")) != theme_name(
            self.temp_settings.get("theme")
        )

        self.settings = self.temp_settings.copy()
        self.save_settings()

        window = self.parent
        if hasattr(window, "ensure_folders_exist"):
            old_base_folder = window.base_folder
            window.base_folder = os.path.join(
                self.settings["base_directory"], self.settings["base_folder_name"]
            )
            window.download_folder = os.path.join(window.base_folder, "Downloads")
            window.cache_folder = os.path.join(window.base_folder, "Cache")
            window.other_files_folder = os.path.join(window.base_folder, "Other Files")
            window.ensure_folders_exist()
            if old_base_folder != window.base_folder:
                self._move_to_new_folder()

        if language_changed:
            language_manager.set_language(self.settings["language"])
            self.language_changed.emit()
            log = getattr(window, "log", None)
            if callable(log):
                log(translate("language_changed"))
            self.update_ui_text()
        if font_changed:
            self.font_changed.emit(self.settings.get("font", "JetBrains Mono"))
        if theme_changed:
            self.theme_changed.emit(self.get_theme())

        self.settings_applied.emit()
        self._refresh_pending_state()

    def discard_changes(self):
        """Put every control back to the applied values."""
        self.temp_settings = self.settings.copy()
        self._show_values()

    def confirm_close_with_pending_changes(self):
        """Before the app closes: apply, discard or keep unapplied changes.

        True when the app may close. The proxy switch is left out: it is
        never remembered between launches anyway.
        """
        changes = [key for key in self.pending_changes() if key != "use_proxy"]
        if not changes:
            return True
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle(translate("unapplied_changes_title"))
        box.setText(translate("unapplied_on_close", self.describe_changes(changes)))
        apply = box.addButton(
            translate("apply_changes"), QMessageBox.ButtonRole.AcceptRole
        )
        discard = box.addButton(
            translate("discard_changes"), QMessageBox.ButtonRole.DestructiveRole
        )
        box.addButton(QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(apply)
        box.exec()
        clicked = box.clickedButton()
        if clicked == apply:
            return self.apply_pending_settings(confirm=False, closing=True)
        return clicked == discard

    def _move_to_new_folder(self):
        """Point every tab and the library at the save folder just applied."""
        window = self.parent
        for name in ("post_tab", "creator_tab", "thumbnail_tab"):
            tab = getattr(window, name, None)
            if tab is not None:
                tab.cache_dir = window.cache_folder
                tab.other_files_dir = window.other_files_folder
        # History and favorites live in the save folder too. Without this they
        # kept being written to the old folder for the rest of the session,
        # and the next launch opened the new, empty one.
        store = getattr(window, "history_store", None)
        if isinstance(store, HistoryStore) and not store.relocate(
            window.other_files_folder
        ):
            QMessageBox.warning(
                self,
                translate("library_move_failed_title"),
                translate(
                    "library_move_failed", window.other_files_folder, store.error or ""
                ),
            )

    def confirm_and_reset_settings(self):
        """Confirm and reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            translate("reset_to_defaults"),
            translate("confirm_reset_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.reset_to_defaults()

    def reset_to_defaults(self):
        """Fill in the default values, pending until Apply Changes."""
        self.temp_settings = self.default_settings.copy()
        self._show_values()
        QMessageBox.information(
            self, translate("reset_to_defaults"), translate("settings_reset_message")
        )

    def _show_values(self):
        """Make every control show the pending values (temp_settings).

        Signals are blocked while filling them in: the values are already in
        temp_settings, and the handlers would only repeat that (or, for the
        proxy type, offer to detect Tor).
        """
        values = self.temp_settings
        combo = self.creator_filename_combo
        widgets = [
            self.folder_name_input,
            self.directory_input,
            self.download_slider,
            self.download_spinbox,
            self.save_previews_checkbox,
            self.creator_posts_max_attempts_spinbox,
            self.post_data_max_retries_spinbox,
            self.file_download_max_retries_spinbox,
            self.api_request_max_retries_spinbox,
            combo,
            combo.lineEdit(),
            self.creator_folder_strategy_combo,
            self.auto_update_checkbox,
            *self.log_level_checkboxes.values(),
            self.font_combo,
            self.theme_combo,
            self.use_proxy_checkbox,
            self.proxy_type_combo,
            self.custom_proxy_input,
            self.tor_path_input,
        ]
        for widget in widgets:
            widget.blockSignals(True)
        try:
            self.folder_name_input.setText(values["base_folder_name"])
            self.directory_input.setText(values["base_directory"])
            self.download_slider.setValue(values["simultaneous_downloads"])
            self.download_spinbox.setValue(values["simultaneous_downloads"])
            self.save_previews_checkbox.setChecked(
                values.get("save_preview_images", False) is True
            )
            self.creator_posts_max_attempts_spinbox.setValue(
                values["creator_posts_max_attempts"]
            )
            self.post_data_max_retries_spinbox.setValue(values["post_data_max_retries"])
            self.file_download_max_retries_spinbox.setValue(
                values["file_download_max_retries"]
            )
            self.api_request_max_retries_spinbox.setValue(
                values["api_request_max_retries"]
            )
            template = (
                values.get("creator_filename_template") or "{post_id}_{orig_name}"
            )
            preset = next(
                (i for i in range(combo.count() - 1) if combo.itemData(i) == template),
                None,
            )
            if preset is not None:
                combo.setCurrentIndex(preset)
            else:
                combo.setCurrentIndex(combo.count() - 1)
                combo.setEditText(template)
            strategy = self.creator_folder_strategy_combo.findData(
                values.get("creator_folder_strategy", "per_post")
            )
            self.creator_folder_strategy_combo.setCurrentIndex(max(0, strategy))
            self.auto_update_checkbox.setChecked(values["auto_check_updates"])
            for level, (key, _label, default) in LOG_LEVEL_SETTINGS.items():
                self.log_level_checkboxes[level].setChecked(
                    bool(values.get(key, default))
                )
            font = self.font_combo.findData(values.get("font", "JetBrains Mono"))
            self.font_combo.setCurrentIndex(max(0, font))
            self.theme_combo.setCurrentIndex(
                max(0, self.theme_combo.findData(theme_name(values.get("theme"))))
            )
            self.use_proxy_checkbox.setChecked(bool(values["use_proxy"]))
            self.proxy_type_combo.setCurrentIndex(
                self.get_proxy_type_index(values["proxy_type"])
            )
            self.custom_proxy_input.setText(values["custom_proxy_url"])
            self.tor_path_input.setText(values["tor_path"])
        finally:
            for widget in widgets:
                widget.blockSignals(False)
        self.update_language_combo()  # reads temp_settings itself
        self._update_proxy_ui()
        self._refresh_pending_state()

    def update_ui_text(self):
        retranslate_notes(self)
        self.folder_group.setTitle(translate("folder_settings"))
        self.folder_name_label.setText(translate("folder_name"))
        self.directory_label.setText(translate("save_directory"))
        self.browse_button.setText(translate("browse"))
        self.open_directory_button.setText(
            translate("open_directory")
        )  # Added text for open directory button

        self.download_group.setTitle(translate("download_settings"))
        self.save_previews_checkbox.setText(translate("save_preview_images"))
        self.save_previews_checkbox.setToolTip(translate("save_preview_images_tooltip"))
        self.simultaneous_downloads_label.setText(translate("simultaneous_downloads"))
        self.pawchive_policy_info_button.setToolTip(
            translate("pawchive_policy_info_title")
        )

        self.retry_group.setTitle(translate("retry_settings"))
        self.creator_posts_max_attempts_label.setText(
            translate("creator_posts_max_attempts")
        )
        self.post_data_max_retries_label.setText(translate("post_data_max_retries"))
        self.file_download_max_retries_label.setText(
            translate("file_download_max_retries")
        )
        self.api_request_max_retries_label.setText(translate("api_request_max_retries"))

        self.update_group.setTitle(translate("update_settings"))
        self.log_group.setTitle(translate("log_settings"))
        for level, (_key, label, _default) in LOG_LEVEL_SETTINGS.items():
            self.log_level_checkboxes[level].setText(translate(label))

        # Creator downloader customization texts
        self.creator_custom_group.setTitle(translate("creator_downloader_settings"))
        self.creator_custom_label.setText(translate("filename_template"))
        self.creator_folder_strategy_label.setText(translate("folder_strategy"))

        # Update template presets display (support language change)
        try:
            current_text = (
                self.creator_filename_combo.currentText()
                if hasattr(self, "creator_filename_combo")
                else ""
            )
            # Clear and re-add with translated labels but preserve data values
            if hasattr(self, "creator_filename_combo"):
                self.creator_filename_combo.blockSignals(True)
                self.creator_filename_combo.clear()
                for label_key, tpl in self._template_presets:
                    self.creator_filename_combo.addItem(translate(label_key), tpl)
                self.creator_filename_combo.addItem(
                    translate("tmpl_custom"), "{post_id}_{orig_name}"
                )
                # Restore selection
                found_index = None
                for i in range(self.creator_filename_combo.count()):
                    if self.creator_filename_combo.itemData(
                        i
                    ) == self.temp_settings.get(
                        "creator_filename_template", "{post_id}_{orig_name}"
                    ):
                        found_index = i
                        break
                if found_index is not None:
                    self.creator_filename_combo.setCurrentIndex(found_index)
                else:
                    self.creator_filename_combo.setCurrentIndex(
                        self.creator_filename_combo.count() - 1
                    )
                    self.creator_filename_combo.setEditText(current_text)
                self.creator_filename_combo.blockSignals(False)
        except Exception:
            pass

        # Ensure folder strategy combo labels are localized
        try:
            if hasattr(self, "creator_folder_strategy_combo"):
                current_data = self.creator_folder_strategy_combo.itemData(
                    self.creator_folder_strategy_combo.currentIndex()
                )
                self.creator_folder_strategy_combo.blockSignals(True)
                self.creator_folder_strategy_combo.clear()
                self.creator_folder_strategy_combo.addItem(
                    translate("per_post_folders"), "per_post"
                )
                self.creator_folder_strategy_combo.addItem(
                    translate("single_creator_folder"), "single_folder"
                )
                self.creator_folder_strategy_combo.addItem(
                    translate("subfolders_by_file_type"), "by_file_type"
                )
                # restore selection based on data
                for i in range(self.creator_folder_strategy_combo.count()):
                    if (
                        self.creator_folder_strategy_combo.itemData(i) == current_data
                    ):  # pragma: no cover - trivial UI restore
                        self.creator_folder_strategy_combo.setCurrentIndex(i)
                        break
                self.creator_folder_strategy_combo.blockSignals(False)
        except Exception:
            pass

        # Tooltip/help for template
        if hasattr(self, "creator_template_help_btn"):
            self.creator_template_help_btn.setToolTip(
                translate("filename_template_help_title")
            )

        # Update proxy and other text

        self.auto_update_label.setText(translate("auto_check_updates"))

        self.language_group.setTitle(translate("language_settings"))
        self.language_label.setText(translate("language"))
        self.update_language_combo()

        self.font_group.setTitle(translate("font_settings"))
        self.font_label.setText(translate("font"))
        self.appearance_group.setTitle(translate("appearance_settings"))
        self.theme_label.setText(translate("theme_label"))
        for index in range(self.theme_combo.count()):
            name = self.theme_combo.itemData(index)
            self.theme_combo.setItemText(index, translate(f"theme_{name}"))

        self.network_group.setTitle(translate("proxy_settings"))
        self.proxy_intro_label.setText(translate("proxy_intro"))
        self.custom_proxy_hint_label.setText(translate("custom_proxy_hint"))
        self.tor_hint_label.setText(translate("tor_hint"))
        self.use_proxy_checkbox.setText(translate("use_proxy"))
        self.proxy_type_label.setText(translate("proxy_type"))
        self.custom_proxy_label.setText(translate("custom_proxy_url"))
        self.test_custom_proxy_button.setText(translate("test_proxy"))
        self.tor_label.setText(translate("tor_path"))
        self.browse_tor_button.setText(translate("browse"))
        self.start_tor_button.setText(translate("start_tor"))
        self.stop_tor_button.setText(translate("stop_tor"))
        self.download_tor_button.setText(translate("download_tor"))
        self.test_tor_button.setText(translate("test_tor"))
        self.help_tor_button.setText(translate("help_button"))
        custom_index = self.proxy_type_combo.findData("custom")
        if custom_index >= 0:
            self.proxy_type_combo.setItemText(custom_index, translate("custom_proxy"))
        self.tor_output_label.setText(translate("tor_output"))
        # Keep the status true to the process: changing the language while Tor
        # runs used to show "Stopped".
        tor_running = (
            self.tor_process is not None
            and self.tor_process.state() == QProcess.ProcessState.Running
        )
        self.tor_status_label.setText(
            translate("tor_status_running" if tor_running else "tor_status_stopped")
        )

        self.apply_button.setText(translate("apply_changes"))
        self.discard_button.setText(translate("discard_changes"))
        self.reset_button.setText(translate("reset_to_defaults"))
        self.pending_label.setText(translate("unapplied_changes"))

    def get_simultaneous_downloads(self):
        return self.settings["simultaneous_downloads"]

    def set_log_level_shown(self, key, shown):
        """Choose whether one level of console messages shows (on Apply)."""
        self.update_temp_setting(key, shown)

    def is_log_level_shown(self, level):
        """Whether the consoles show messages of *level* (DEBUG, INFO, ...)."""
        entry = LOG_LEVEL_SETTINGS.get(str(level).upper())
        if entry is None:
            return True
        key, _label, default = entry
        return bool(self.settings.get(key, default))

    def is_auto_check_updates_enabled(self):
        return self.settings["auto_check_updates"]

    def is_save_preview_images_enabled(self):
        return self.settings.get("save_preview_images", False) is True

    def get_creator_posts_max_attempts(self):
        return self.settings["creator_posts_max_attempts"]

    def get_post_data_max_retries(self):
        return self.settings["post_data_max_retries"]

    def get_file_download_max_retries(self):
        return self.settings["file_download_max_retries"]

    def get_api_request_max_retries(self):
        return self.settings["api_request_max_retries"]

    def get_creator_filename_template(self):
        return self.settings.get("creator_filename_template", "{post_id}_{orig_name}")

    def get_creator_folder_strategy(self):
        return self.settings.get("creator_folder_strategy", "per_post")

    def get_font(self):
        return self.settings.get("font", "JetBrains Mono")

    def get_theme(self):
        """The colour theme (a key of kd_theme.THEMES)."""
        return theme_name(self.settings.get("theme"))

    def update_theme(self, index):
        """Choose a theme; the app switches to it on Apply Changes."""
        self.update_temp_setting("theme", theme_name(self.theme_combo.itemData(index)))

    def get_proxy_type_index(self, proxy_type):
        type_map = {"custom": 0, "tor": 1}
        return type_map.get(proxy_type, 1)  # Default to tor

    def is_tor_running(self):
        """Check if Tor process is currently running."""
        return (
            self.tor_process is not None
            and self.tor_process.state() == QProcess.ProcessState.Running
        )

    def on_use_proxy_changed(self, state):
        """Turn the proxy on or off (on Apply); show its options meanwhile."""
        # A check state from the box, or a plain bool from code.
        enabled = state is True or state == Qt.CheckState.Checked.value
        self.update_temp_setting("use_proxy", enabled)

        if enabled and self.temp_settings["proxy_type"] not in ["custom", "tor"]:
            # Default to Tor when nothing valid was chosen before.
            self.update_temp_setting("proxy_type", "tor")
            self.proxy_type_combo.blockSignals(True)
            self.proxy_type_combo.setCurrentIndex(1)  # Tor index
            self.proxy_type_combo.blockSignals(False)

        self._update_proxy_ui(auto_detect=enabled)

    def on_proxy_type_changed(self, index):
        """Choose custom proxy or Tor (on Apply); show that type's options."""
        proxy_type = self.proxy_type_combo.itemData(index)
        self.update_temp_setting("proxy_type", proxy_type)
        self._update_proxy_ui(auto_detect=True)

    def _update_proxy_ui(self, auto_detect=False):
        """Show the options of the proxy being set up (pending values)."""
        enabled = self.temp_settings["use_proxy"]
        proxy_type = self.temp_settings["proxy_type"]
        # Show/hide the proxy settings group (checkbox stays visible)
        self.proxy_group.setVisible(enabled)

        # Show/hide widgets based on proxy type
        if proxy_type == "custom":
            self.custom_proxy_label.setVisible(enabled)
            self.custom_proxy_input.setVisible(enabled)
            self.test_custom_proxy_button.setVisible(enabled)
            # Hide Tor widgets
            self.tor_label.setVisible(False)
            self.tor_path_input.setVisible(False)
            self.browse_tor_button.setVisible(False)
            self.start_tor_button.setVisible(False)
            self.stop_tor_button.setVisible(False)
            self.download_tor_button.setVisible(False)
            self.test_tor_button.setVisible(False)
            self.help_tor_button.setVisible(False)
            self.tor_status_label.setVisible(False)
            self.tor_progress_bar.setVisible(False)
            self.tor_output_label.setVisible(False)
            self.tor_output_text.setVisible(False)
        elif proxy_type == "tor":
            # Hide custom proxy widgets
            self.custom_proxy_label.setVisible(False)
            self.custom_proxy_input.setVisible(False)
            self.test_custom_proxy_button.setVisible(False)
            # Show Tor widgets
            self.tor_label.setVisible(enabled)
            self.tor_path_input.setVisible(enabled)
            self.browse_tor_button.setVisible(enabled)
            self.start_tor_button.setVisible(enabled)
            self.stop_tor_button.setVisible(enabled)
            self.download_tor_button.setVisible(enabled)
            self.test_tor_button.setVisible(enabled)
            self.help_tor_button.setVisible(enabled)
            self.tor_status_label.setVisible(enabled)
            self.tor_progress_bar.setVisible(
                enabled and self.tor_progress_bar.isVisible()
            )
            self.tor_output_label.setVisible(enabled)
            self.tor_output_text.setVisible(enabled)

        # Enable/disable individual controls
        self.custom_proxy_input.setEnabled(enabled and proxy_type == "custom")
        self.test_custom_proxy_button.setEnabled(enabled and proxy_type == "custom")
        self.tor_path_input.setEnabled(enabled and proxy_type == "tor")
        self.browse_tor_button.setEnabled(enabled and proxy_type == "tor")
        self.download_tor_button.setEnabled(enabled and proxy_type == "tor")
        self.test_tor_button.setEnabled(enabled and proxy_type == "tor")
        self.help_tor_button.setEnabled(enabled and proxy_type == "tor")
        self.tor_progress_bar.setVisible(
            enabled and proxy_type == "tor" and self.tor_progress_bar.isVisible()
        )
        self.tor_output_label.setVisible(enabled and proxy_type == "tor")
        self.tor_output_text.setVisible(enabled and proxy_type == "tor")
        self.tor_status_label.setVisible(enabled and proxy_type == "tor")

        # Only the chosen proxy type's panel takes up room.
        self.custom_proxy_panel.setVisible(proxy_type == "custom")
        self.tor_panel.setVisible(proxy_type == "tor")

        # Update Tor button states
        self.update_tor_button_states()

        # Auto-detect Tor if switching to Tor and no path is set
        if (
            auto_detect
            and enabled
            and proxy_type == "tor"
            and not self.temp_settings["tor_path"].strip()
        ):
            detected_path = self.auto_detect_tor()
            if detected_path:
                self.update_temp_setting("tor_path", detected_path)
                self.tor_path_input.setText(detected_path)
                QMessageBox.information(
                    self,
                    translate("info"),
                    translate("tor_auto_detected", detected_path),
                )
                # Update button states after auto-detection
                self.update_tor_button_states()

        # Update the UI
        self.layout().update()
        self.repaint()
        self.adjustSize()

    def test_custom_proxy(self):
        proxy_url = self.temp_settings["custom_proxy_url"].strip()
        if not proxy_url:
            QMessageBox.warning(
                self, translate("error"), translate("custom_proxy_url_empty")
            )
            return

        # Test the proxy by making a request
        try:
            import requests

            proxies = {"http": proxy_url, "https": proxy_url}
            response = requests.get(
                "http://httpbin.org/ip", proxies=proxies, timeout=10
            )
            if response.status_code == 200:
                QMessageBox.information(
                    self, translate("success"), translate("proxy_test_successful")
                )
            else:
                QMessageBox.warning(
                    self,
                    translate("error"),
                    translate("proxy_test_failed", response.status_code),
                )
        except Exception as e:
            QMessageBox.warning(
                self, translate("error"), translate("proxy_test_failed", str(e))
            )

    def test_tor(self):
        tor_path = self.temp_settings["tor_path"]
        if not tor_path or not os.path.exists(tor_path):
            QMessageBox.warning(
                self, translate("error"), translate("tor_not_configured")
            )
            return

        # Check if tor executable is valid
        try:
            import subprocess

            result = subprocess.run(
                [tor_path, "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0 or "Tor" not in result.stdout:
                QMessageBox.warning(
                    self, translate("error"), translate("tor_test_failed")
                )
                return
        except Exception as e:
            QMessageBox.warning(
                self, translate("error"), translate("tor_test_failed", str(e))
            )
            return

        # Check if Tor is running as SOCKS proxy
        try:
            import requests

            # Test SOCKS5 proxy connection
            proxies = {"http": TOR_SOCKS_PROXY, "https": TOR_SOCKS_PROXY}

            # Try to connect to a test service that works with Tor
            response = requests.get(
                "https://check.torproject.org/api/ip", proxies=proxies, timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("IsTor", False):
                    QMessageBox.information(
                        self, translate("success"), translate("tor_proxy_working")
                    )
                else:
                    QMessageBox.warning(
                        self,
                        translate("warning"),
                        translate("tor_executable_ok_but_proxy_not_running"),
                    )
            else:
                QMessageBox.warning(
                    self,
                    translate("warning"),
                    translate("tor_executable_ok_but_proxy_not_running"),
                )

        except ImportError:
            QMessageBox.information(
                self, translate("success"), translate("tor_test_successful")
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                translate("warning"),
                translate("tor_executable_ok_but_proxy_not_running", str(e)),
            )

    def start_tor(self):
        tor_path = self.temp_settings["tor_path"]
        if not tor_path or not os.path.exists(tor_path):
            QMessageBox.warning(
                self, translate("error"), translate("tor_not_configured")
            )
            return

        if (
            self.tor_process
            and self.tor_process.state() == QProcess.ProcessState.Running
        ):
            QMessageBox.information(
                self, translate("info"), translate("tor_already_running")
            )
            return

        # Create data directory if it doesn't exist
        if not self.tor_data_dir:
            import tempfile

            self.tor_data_dir = tempfile.mkdtemp(prefix="kemonodownloader_tor_")

        # Create a temporary torrc file to avoid using system config
        import tempfile

        self.tor_config_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".torrc", delete=False
        )
        self.tor_config_file.write(
            """SocksPort 9050
DataDirectory {data_dir}
Log notice stdout
ExitPolicy reject *:*
GeoIPExcludeUnknown 1
""".format(
                data_dir=self.tor_data_dir
            )
        )
        self.tor_config_file.close()

        # Clear previous output
        self.tor_output_text.clear()

        # Start Tor process
        self.tor_process = QProcess(self)
        self.tor_process.setProgram(tor_path)
        self.tor_process.setArguments(["--torrc-file", self.tor_config_file.name])

        self.tor_process.readyReadStandardOutput.connect(self.handle_tor_output)
        self.tor_process.readyReadStandardError.connect(self.handle_tor_error)
        self.tor_process.finished.connect(self.handle_tor_finished)

        self.tor_process.start()

        # Update UI
        self.start_tor_button.setEnabled(False)
        self.stop_tor_button.setEnabled(True)
        self.test_tor_button.setEnabled(True)
        self.tor_status_label.setText(translate("tor_status_starting"))
        set_tone(self.tor_status_label, "warning")

        # Disable proxy type selection while Tor is running
        self.proxy_type_combo.setEnabled(False)

        message = translate("tor_starting")
        if not self._uses_tor(self.settings):
            # Running Tor doesn't route anything by itself.
            message += "\n\n" + translate("tor_started_not_applied")
        QMessageBox.information(self, translate("info"), message)

    def stop_tor(self):
        if not self.tor_process:
            QMessageBox.warning(self, translate("error"), translate("tor_not_running"))
            return

        self.tor_process.terminate()
        if not self.tor_process.waitForFinished(5000):  # Wait up to 5 seconds
            self.tor_process.kill()
            self.tor_process.waitForFinished(2000)

        self.tor_process = None

        # Clean up temporary data directory
        if self.tor_data_dir and os.path.exists(self.tor_data_dir):
            try:
                import shutil

                shutil.rmtree(self.tor_data_dir)
                self.tor_data_dir = None
            except Exception as e:
                print(f"Failed to clean up Tor data directory: {e}")

        # Update UI
        self.start_tor_button.setEnabled(True)
        self.stop_tor_button.setEnabled(False)
        self.tor_status_label.setText(translate("tor_status_stopped"))
        set_tone(self.tor_status_label, "error")

        # Re-enable proxy type selection
        self.proxy_type_combo.setEnabled(True)

        message = translate("tor_stopped")
        if self._uses_tor(self.settings):
            # Downloads still go to Tor's port, and fail: never direct.
            message += "\n\n" + translate("tor_stopped_in_use")
        QMessageBox.information(self, translate("info"), message)

    def show_tor_help(self):
        """Show help modal with Tor setup instructions."""
        QMessageBox.information(
            self, translate("tor_help_title"), translate("tor_help_text")
        )

    def download_tor(self):
        try:
            # Pick the expert bundle for this OS and CPU
            bundle = tor_bundle_platform()
            if bundle is None:
                QMessageBox.warning(
                    self, translate("error"), translate("tor_unsupported_platform")
                )
                return
            tor_extract_dir = f"tor-expert-bundle-{bundle}-{TOR_BUNDLE_VERSION}"
            tor_url = f"{TOR_ARCHIVE_URL}/{TOR_BUNDLE_VERSION}/{tor_extract_dir}.tar.gz"
            expected_sha256 = TOR_BUNDLE_SHA256[bundle]

            # Create tor directory in app data
            tor_path = os.path.join(
                self.temp_settings["base_directory"],
                self.temp_settings["base_folder_name"],
                "Tor",
            )
            os.makedirs(tor_path, exist_ok=True)

            # Show progress bar and disable button
            self.tor_progress_bar.setVisible(True)
            self.tor_progress_bar.setValue(0)
            self.download_tor_button.setEnabled(False)
            self.download_tor_button.setText(translate("downloading"))

            # Download Tor with progress tracking
            QMessageBox.information(
                self, translate("info"), translate("downloading_tor")
            )

            # Start download thread
            self.download_thread = DownloadTorThread(
                tor_url, tor_extract_dir, tor_path, expected_sha256
            )
            self.download_thread.progress.connect(self.tor_progress_bar.setValue)
            self.download_thread.finished_success.connect(self.on_tor_download_success)
            self.download_thread.finished_error.connect(self.on_tor_download_error)

            # Disable buttons during download
            self.download_started.emit()
            self.test_tor_button.setEnabled(False)
            self.start_tor_button.setEnabled(False)
            self.stop_tor_button.setEnabled(False)
            # self.help_tor_button.setEnabled(False)  # Keep help always available

            self.download_thread.start()

        except Exception as e:
            # Hide progress bar and re-enable button on error
            self.tor_progress_bar.setVisible(False)
            self.download_tor_button.setEnabled(True)
            self.download_tor_button.setText(translate("download_tor"))
            self.download_finished.emit()
            QMessageBox.warning(
                self, translate("error"), translate("tor_download_failed", str(e))
            )

    def on_tor_download_success(self, tor_exe):
        self.download_finished.emit()
        # Hide progress bar and re-enable button
        self.tor_progress_bar.setVisible(False)
        self.download_tor_button.setEnabled(True)
        self.download_tor_button.setText(translate("download_tor"))

        self.update_temp_setting("tor_path", tor_exe)
        self.tor_path_input.setText(tor_exe)
        QMessageBox.information(
            self, translate("success"), translate("tor_download_successful")
        )
        self.update_tor_button_states()

    def on_tor_download_error(self, error_msg):
        self.download_finished.emit()
        # Hide progress bar and re-enable button on error
        self.tor_progress_bar.setVisible(False)
        self.download_tor_button.setEnabled(True)
        self.download_tor_button.setText(translate("download_tor"))
        if error_msg == "tor_exe_not_found":
            QMessageBox.warning(
                self, translate("error"), translate("tor_exe_not_found")
            )
        else:
            QMessageBox.warning(
                self, translate("error"), translate("tor_download_failed", error_msg)
            )

    def update_tor_button_states(self):
        tor_path = self.temp_settings["tor_path"]
        tor_exists = bool(tor_path and os.path.exists(tor_path))

        self.test_tor_button.setEnabled(bool(tor_exists))
        self.download_tor_button.setVisible(
            not tor_exists
        )  # Hide download button if Tor is already available

        if (
            self.tor_process
            and self.tor_process.state() == QProcess.ProcessState.Running
        ):
            self.start_tor_button.setEnabled(False)
            self.stop_tor_button.setEnabled(True)
        else:
            self.start_tor_button.setEnabled(bool(tor_exists))
            self.stop_tor_button.setEnabled(False)

    def handle_tor_output(self):
        if self.tor_process:
            output = (
                self.tor_process.readAllStandardOutput()
                .data()
                .decode("utf-8", errors="ignore")
            )
            if output.strip():
                # Append to text area
                self.tor_output_text.append(output.strip())
                # Auto-scroll to bottom
                scrollbar = self.tor_output_text.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())

                # Check for bootstrap completion
                if "Bootstrapped 100%" in output:
                    self.tor_status_label.setText(translate("tor_status_running"))
                    set_tone(self.tor_status_label, "success")
                    QMessageBox.information(
                        self, translate("success"), translate("tor_running")
                    )

    def handle_tor_error(self):
        if self.tor_process:
            error = (
                self.tor_process.readAllStandardError()
                .data()
                .decode("utf-8", errors="ignore")
            )
            if error.strip():
                # Append error to text area
                self.tor_output_text.append(f"[ERROR] {error.strip()}")
                # Auto-scroll to bottom
                scrollbar = self.tor_output_text.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())

    def handle_tor_finished(self, exit_code, exit_status):
        print(f"Tor finished with exit code: {exit_code}")
        self.tor_process = None

        # Clean up temporary data directory
        if self.tor_data_dir and os.path.exists(self.tor_data_dir):
            try:
                import shutil

                shutil.rmtree(self.tor_data_dir)
                self.tor_data_dir = None
            except Exception as e:
                print(f"Failed to clean up Tor data directory: {e}")

        # Clean up temporary config file
        if hasattr(self, "tor_config_file") and os.path.exists(
            self.tor_config_file.name
        ):
            try:
                os.unlink(self.tor_config_file.name)
            except Exception as e:
                print(f"Failed to clean up Tor config file: {e}")

        self.start_tor_button.setEnabled(True)
        self.stop_tor_button.setEnabled(False)
        self.tor_status_label.setText(translate("tor_status_stopped"))
        set_tone(self.tor_status_label, "error")

    def get_proxy_settings(self):
        """Proxies for requests, from the applied settings only.

        A proxy ticked but not yet applied isn't used: like every setting,
        it takes effect with Apply Changes.
        """
        return proxies_for(self.settings)


def proxies_for(values):
    """The ``requests`` proxies the settings *values* call for, or None."""
    if not values.get("use_proxy"):
        return None
    if values.get("proxy_type") == "custom":
        proxy_url = (values.get("custom_proxy_url") or "").strip()
        if proxy_url:
            return {"http": proxy_url, "https": proxy_url}
    elif values.get("proxy_type") == "tor":
        # Always route through Tor's SOCKS port, even when the Tor process
        # started from this tab isn't running. Falling back to a direct
        # connection would silently expose the user's IP address; without
        # a Tor listener the request fails instead. This also covers a Tor
        # service the user runs on the default port. socks5h resolves host
        # names through Tor as well. Without PySocks, requests refuses a
        # SOCKS proxy URL rather than connecting directly.
        return {"http": TOR_SOCKS_PROXY, "https": TOR_SOCKS_PROXY}
    return None


def tor_is_listening(timeout=0.3):
    """Whether something accepts connections on Tor's SOCKS port."""
    try:
        with socket.create_connection(TOR_SOCKS_ADDRESS, timeout=timeout):
            return True
    except OSError:
        return False


class DownloadTorThread(QThread):
    progress = pyqtSignal(int)
    finished_success = pyqtSignal(str)
    finished_error = pyqtSignal(str)

    def __init__(self, tor_url, tor_extract_dir, tor_path, expected_sha256=None):
        super().__init__()
        self.tor_url = tor_url
        self.tor_extract_dir = tor_extract_dir
        self.tor_path = tor_path
        # SHA-256 the archive must have; checked before anything is extracted.
        self.expected_sha256 = expected_sha256

    def run(self):
        import hashlib
        import tarfile
        import tempfile

        import requests

        tmp_archive = None
        try:
            # (connect, read) timeouts: without them a stalled connection
            # leaves this thread, and the settings UI, waiting forever.
            response = requests.get(self.tor_url, stream=True, timeout=(30, 60))
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0
            hasher = hashlib.sha256()

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".tar.gz"
            ) as tmp_file:
                tmp_archive = tmp_file.name
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                        hasher.update(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress.emit(progress)

            # Refuse a corrupted or tampered archive before extracting it.
            if (
                self.expected_sha256
                and hasher.hexdigest().lower() != self.expected_sha256.lower()
            ):
                raise ValueError(translate("tor_checksum_mismatch"))

            # Extract Tor
            self.progress.emit(100)

            with tarfile.open(tmp_archive, "r:gz") as tar_ref:
                # Safely extract files to avoid path traversal vulnerabilities.
                def _is_within_directory(directory, target):
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                    try:
                        return os.path.commonpath(
                            [abs_directory]
                        ) == os.path.commonpath([abs_directory, abs_target])
                    except Exception:
                        return False

                # The "data" filter (Python 3.12+, backported to 3.9.17,
                # 3.10.12 and 3.11.4) also rejects links that point outside
                # the target folder and special files, which the path check
                # below cannot see.
                extract_kwargs = (
                    {"filter": "data"} if hasattr(tarfile, "data_filter") else {}
                )
                for member in tar_ref.getmembers():
                    member_path = os.path.join(self.tor_path, member.name)
                    if not _is_within_directory(self.tor_path, member_path):
                        # Skip unsafe member
                        continue
                    tar_ref.extract(member, self.tor_path, **extract_kwargs)

            # Clean up
            os.unlink(tmp_archive)
            tmp_archive = None

            # Find the tor executable. The expert bundle keeps it in tor/; check
            # there first, then search the rest of the tree. The Linux bundle
            # also ships debug symbols as debug/tor, which cannot be run, so
            # that folder is skipped.
            tor_exe = None
            for name in ("tor.exe", "tor"):
                candidate = os.path.join(self.tor_path, "tor", name)
                if os.path.isfile(candidate):
                    tor_exe = candidate
                    break
            if tor_exe is None:
                for root, dirs, files in os.walk(self.tor_path):
                    dirs[:] = sorted(d for d in dirs if d.lower() != "debug")
                    for f in files:
                        if f.lower() in ("tor.exe", "tor"):
                            tor_exe = os.path.join(root, f)
                            break
                    if tor_exe:
                        break

            if tor_exe:
                self.finished_success.emit(tor_exe)
            else:
                self.finished_error.emit("tor_exe_not_found")

        except Exception as e:
            # Don't leave a partial download in the temp folder.
            if tmp_archive is not None:
                try:
                    os.unlink(tmp_archive)
                except OSError:
                    pass
            self.finished_error.emit(str(e))
