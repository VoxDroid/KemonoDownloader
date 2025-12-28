import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QGroupBox, QGridLayout, QLabel, QSlider, QSpinBox, 
    QFileDialog, QMessageBox, QCheckBox, QComboBox, QProgressBar, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal, QProcess, QTimer, QThread
from kemonodownloader.kd_language import language_manager, translate

class SettingsTab(QWidget):
    settings_applied = pyqtSignal()
    language_changed = pyqtSignal()
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
            "language": "english",
            "creator_posts_max_attempts": 200,
            "post_data_max_retries": 7,
            "file_download_max_retries": 50,
            "api_request_max_retries": 3,
            "use_proxy": False,
            "proxy_type": "tor",  # "custom", "tor"
            "custom_proxy_url": "",
            "tor_path": ""
        }
        self.settings = self.load_settings()
        self.temp_settings = self.settings.copy()
        
        # Tor process management
        self.tor_process = None
        self.tor_data_dir = None
        
        language_manager.set_language(self.settings["language"])
        
        self.setup_ui()

    def get_default_base_directory(self):
        """Return a platform-appropriate default directory for app data."""
        if sys.platform == "win32":  # Windows
            return os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "Kemono Downloader")
        elif sys.platform == "darwin":  # macOS
            return os.path.expanduser("~/Library/Application Support/Kemono Downloader")
        else:  # Linux and others
            return os.path.join(os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), "Kemono Downloader")
        
    def load_settings(self):
        settings_dict = {}
        settings_dict["base_folder_name"] = self.qsettings.value("base_folder_name", self.default_settings["base_folder_name"], type=str)
        settings_dict["base_directory"] = self.qsettings.value("base_directory", self.default_settings["base_directory"], type=str)
        settings_dict["simultaneous_downloads"] = self.qsettings.value("simultaneous_downloads", self.default_settings["simultaneous_downloads"], type=int)
        settings_dict["auto_check_updates"] = self.qsettings.value("auto_check_updates", self.default_settings["auto_check_updates"], type=bool)
        settings_dict["language"] = self.qsettings.value("language", self.default_settings["language"], type=str)
        settings_dict["creator_posts_max_attempts"] = self.qsettings.value("creator_posts_max_attempts", self.default_settings["creator_posts_max_attempts"], type=int)
        settings_dict["post_data_max_retries"] = self.qsettings.value("post_data_max_retries", self.default_settings["post_data_max_retries"], type=int)
        settings_dict["file_download_max_retries"] = self.qsettings.value("file_download_max_retries", self.default_settings["file_download_max_retries"], type=int)
        settings_dict["api_request_max_retries"] = self.qsettings.value("api_request_max_retries", self.default_settings["api_request_max_retries"], type=int)
        settings_dict["use_proxy"] = False  # Always start with proxy disabled
        settings_dict["proxy_type"] = self.qsettings.value("proxy_type", self.default_settings["proxy_type"], type=str)
        # Convert old "none" proxy type to "tor" for backward compatibility
        if settings_dict["proxy_type"] == "none":
            settings_dict["proxy_type"] = "tor"
        settings_dict["custom_proxy_url"] = self.qsettings.value("custom_proxy_url", self.default_settings["custom_proxy_url"], type=str)
        settings_dict["tor_path"] = self.qsettings.value("tor_path", self.default_settings["tor_path"], type=str)
        return settings_dict

    def save_settings(self):
        self.qsettings.setValue("base_folder_name", self.settings["base_folder_name"])
        self.qsettings.setValue("base_directory", self.settings["base_directory"])
        self.qsettings.setValue("simultaneous_downloads", self.settings["simultaneous_downloads"])
        self.qsettings.setValue("auto_check_updates", self.settings["auto_check_updates"])
        self.qsettings.setValue("language", self.settings["language"])
        self.qsettings.setValue("creator_posts_max_attempts", self.settings["creator_posts_max_attempts"])
        self.qsettings.setValue("post_data_max_retries", self.settings["post_data_max_retries"])
        self.qsettings.setValue("file_download_max_retries", self.settings["file_download_max_retries"])
        self.qsettings.setValue("api_request_max_retries", self.settings["api_request_max_retries"])
        self.qsettings.setValue("proxy_type", self.settings["proxy_type"])
        self.qsettings.setValue("custom_proxy_url", self.settings["custom_proxy_url"])
        self.qsettings.setValue("tor_path", self.settings["tor_path"])
        self.qsettings.sync()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Folder Settings Group
        self.folder_group = QGroupBox()
        self.folder_group.setStyleSheet("QGroupBox { color: white; font-weight: bold; padding: 10px; }")
        folder_layout = QGridLayout()
        
        self.folder_name_label = QLabel()
        folder_layout.addWidget(self.folder_name_label, 0, 0)
        self.folder_name_input = QLineEdit(self.temp_settings["base_folder_name"])
        self.folder_name_input.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.folder_name_input.textChanged.connect(lambda: self.update_temp_setting("base_folder_name", self.folder_name_input.text()))
        folder_layout.addWidget(self.folder_name_input, 0, 1)
        
        self.directory_label = QLabel()
        folder_layout.addWidget(self.directory_label, 1, 0)
        self.directory_input = QLineEdit(self.temp_settings["base_directory"])
        self.directory_input.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.directory_input.textChanged.connect(lambda: self.update_temp_setting("base_directory", self.directory_input.text()))
        folder_layout.addWidget(self.directory_input, 1, 1)
        
        self.browse_button = QPushButton()
        self.browse_button.setStyleSheet("background: #4A5B7A; padding: 5px; border-radius: 5px;")
        self.browse_button.clicked.connect(self.browse_directory)
        folder_layout.addWidget(self.browse_button, 1, 2)
        
        self.open_directory_button = QPushButton()
        self.open_directory_button.setStyleSheet("background: #4A5B7A; padding: 5px; border-radius: 5px;")
        self.open_directory_button.clicked.connect(self.open_app_directory)
        folder_layout.addWidget(self.open_directory_button, 1, 3)
        
        self.folder_group.setLayout(folder_layout)
        layout.addWidget(self.folder_group)

        # Download Settings Group
        self.download_group = QGroupBox()
        self.download_group.setStyleSheet("QGroupBox { color: white; font-weight: bold; padding: 10px; }")
        download_layout = QGridLayout()
        
        self.simultaneous_downloads_label = QLabel()
        download_layout.addWidget(self.simultaneous_downloads_label, 0, 0)
        self.download_slider = QSlider(Qt.Orientation.Horizontal)
        self.download_slider.setRange(1, 20)
        self.download_slider.setValue(self.temp_settings["simultaneous_downloads"])
        self.download_slider.setStyleSheet("QSlider::groove:horizontal { border: 1px solid #4A5B7A; height: 8px; background: #2A3B5A; margin: 2px 0; }"
                                           "QSlider::handle:horizontal { background: #4A5B7A; width: 18px; margin: -2px 0; border-radius: 9px; }")
        self.download_slider.valueChanged.connect(self.update_simultaneous_downloads)
        download_layout.addWidget(self.download_slider, 0, 1)
        self.download_spinbox = QSpinBox()
        self.download_spinbox.setRange(1, 20)
        self.download_spinbox.setValue(self.temp_settings["simultaneous_downloads"])
        self.download_spinbox.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.download_spinbox.valueChanged.connect(self.update_simultaneous_downloads)
        download_layout.addWidget(self.download_spinbox, 0, 2)
        
        self.download_group.setLayout(download_layout)
        layout.addWidget(self.download_group)

        # Retry Settings Group
        self.retry_group = QGroupBox()
        self.retry_group.setStyleSheet("QGroupBox { color: white; font-weight: bold; padding: 10px; }")
        retry_layout = QGridLayout()

        self.creator_posts_max_attempts_label = QLabel()
        retry_layout.addWidget(self.creator_posts_max_attempts_label, 0, 0)
        self.creator_posts_max_attempts_spinbox = QSpinBox()
        self.creator_posts_max_attempts_spinbox.setRange(1, 1000)
        self.creator_posts_max_attempts_spinbox.setValue(self.temp_settings["creator_posts_max_attempts"])
        self.creator_posts_max_attempts_spinbox.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.creator_posts_max_attempts_spinbox.valueChanged.connect(lambda value: self.update_temp_setting("creator_posts_max_attempts", value))
        retry_layout.addWidget(self.creator_posts_max_attempts_spinbox, 0, 1)

        self.post_data_max_retries_label = QLabel()
        retry_layout.addWidget(self.post_data_max_retries_label, 1, 0)
        self.post_data_max_retries_spinbox = QSpinBox()
        self.post_data_max_retries_spinbox.setRange(1, 100)
        self.post_data_max_retries_spinbox.setValue(self.temp_settings["post_data_max_retries"])
        self.post_data_max_retries_spinbox.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.post_data_max_retries_spinbox.valueChanged.connect(lambda value: self.update_temp_setting("post_data_max_retries", value))
        retry_layout.addWidget(self.post_data_max_retries_spinbox, 1, 1)

        self.file_download_max_retries_label = QLabel()
        retry_layout.addWidget(self.file_download_max_retries_label, 2, 0)
        self.file_download_max_retries_spinbox = QSpinBox()
        self.file_download_max_retries_spinbox.setRange(1, 200)
        self.file_download_max_retries_spinbox.setValue(self.temp_settings["file_download_max_retries"])
        self.file_download_max_retries_spinbox.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.file_download_max_retries_spinbox.valueChanged.connect(lambda value: self.update_temp_setting("file_download_max_retries", value))
        retry_layout.addWidget(self.file_download_max_retries_spinbox, 2, 1)

        self.api_request_max_retries_label = QLabel()
        retry_layout.addWidget(self.api_request_max_retries_label, 3, 0)
        self.api_request_max_retries_spinbox = QSpinBox()
        self.api_request_max_retries_spinbox.setRange(1, 50)
        self.api_request_max_retries_spinbox.setValue(self.temp_settings["api_request_max_retries"])
        self.api_request_max_retries_spinbox.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.api_request_max_retries_spinbox.valueChanged.connect(lambda value: self.update_temp_setting("api_request_max_retries", value))
        retry_layout.addWidget(self.api_request_max_retries_spinbox, 3, 1)

        self.retry_group.setLayout(retry_layout)
        layout.addWidget(self.retry_group)

        # Update Settings Group
        self.update_group = QGroupBox()
        self.update_group.setStyleSheet("QGroupBox { color: white; font-weight: bold; padding: 10px; }")
        update_layout = QGridLayout()
        
        self.auto_update_label = QLabel()
        update_layout.addWidget(self.auto_update_label, 0, 0)
        self.auto_update_checkbox = QCheckBox()
        self.auto_update_checkbox.setChecked(self.temp_settings["auto_check_updates"])
        self.auto_update_checkbox.setStyleSheet("QCheckBox::indicator { width: 16px; height: 16px; }"
                                                "QCheckBox::indicator:unchecked { background: #2A3B5A; border: 1px solid #4A5B7A; }"
                                                "QCheckBox::indicator:checked { background: #4A6B9A; border: 1px solid #5A7BA9; }")
        self.auto_update_checkbox.stateChanged.connect(lambda state: self.update_temp_setting("auto_check_updates", state == Qt.CheckState.Checked.value))
        update_layout.addWidget(self.auto_update_checkbox, 0, 1)
        
        self.update_group.setLayout(update_layout)
        layout.addWidget(self.update_group)
        
        # Language Settings Group
        self.language_group = QGroupBox()
        self.language_group.setStyleSheet("QGroupBox { color: white; font-weight: bold; padding: 10px; }")
        language_layout = QGridLayout()
        
        self.language_label = QLabel()
        language_layout.addWidget(self.language_label, 0, 0)
        
        self.language_combo = QComboBox()
        self.update_language_combo()
        
        self.language_combo.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.language_combo.currentIndexChanged.connect(self.update_language)
        language_layout.addWidget(self.language_combo, 0, 1)
        
        self.language_group.setLayout(language_layout)
        layout.addWidget(self.language_group)

        # Enable proxy checkbox (outside the proxy group so it's always visible)
        self.use_proxy_checkbox = QCheckBox()
        self.use_proxy_checkbox.setStyleSheet("QCheckBox::indicator { width: 16px; height: 16px; }"
                                              "QCheckBox::indicator:unchecked { background: #2A3B5A; border: 1px solid #4A5B7A; }"
                                              "QCheckBox::indicator:checked { background: #4A6B9A; border: 1px solid #5A7BA9; }")
        self.use_proxy_checkbox.stateChanged.connect(self.on_use_proxy_changed)
        
        # Proxy Settings Group
        self.proxy_group = QGroupBox()
        self.proxy_group.setStyleSheet("QGroupBox { color: white; font-weight: bold; padding: 10px; }")
        self.proxy_group.setVisible(False)  # Start hidden, will be shown by on_use_proxy_changed
        proxy_layout = QVBoxLayout()
        
        # Proxy type selection
        proxy_type_layout = QHBoxLayout()
        self.proxy_type_label = QLabel()
        proxy_type_layout.addWidget(self.proxy_type_label)
        
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItem("Custom Proxy", "custom")
        self.proxy_type_combo.addItem("Tor", "tor")
        self.proxy_type_combo.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.proxy_type_combo.currentIndexChanged.connect(self.on_proxy_type_changed)
        
        # Block signals during initialization to prevent premature UI updates
        self.use_proxy_checkbox.blockSignals(True)
        self.proxy_type_combo.blockSignals(True)
        
        # Set initial values
        self.use_proxy_checkbox.setChecked(self.temp_settings["use_proxy"])
        self.proxy_type_combo.setCurrentIndex(self.get_proxy_type_index(self.temp_settings["proxy_type"]))
        
        # Unblock signals
        self.use_proxy_checkbox.blockSignals(False)
        self.proxy_type_combo.blockSignals(False)
        
        layout.addWidget(self.use_proxy_checkbox)
        
        proxy_type_layout.addWidget(self.proxy_type_combo)
        proxy_layout.addLayout(proxy_type_layout)
        
        # Custom proxy input
        self.custom_proxy_layout = QHBoxLayout()
        self.custom_proxy_label = QLabel()
        self.custom_proxy_layout.addWidget(self.custom_proxy_label)
        
        self.custom_proxy_input = QLineEdit(self.temp_settings["custom_proxy_url"])
        self.custom_proxy_input.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.custom_proxy_input.textChanged.connect(lambda: self.update_temp_setting("custom_proxy_url", self.custom_proxy_input.text()))
        self.custom_proxy_layout.addWidget(self.custom_proxy_input)
        
        self.test_custom_proxy_button = QPushButton()
        self.test_custom_proxy_button.setStyleSheet("background: #4A5B7A; padding: 5px; border-radius: 5px;")
        self.test_custom_proxy_button.clicked.connect(self.test_custom_proxy)
        self.custom_proxy_layout.addWidget(self.test_custom_proxy_button)
        
        proxy_layout.addLayout(self.custom_proxy_layout)
        
        # Tor settings
        self.tor_layout = QVBoxLayout()
        self.tor_label = QLabel()
        self.tor_layout.addWidget(self.tor_label)
        
        tor_path_layout = QHBoxLayout()
        self.tor_path_input = QLineEdit(self.temp_settings["tor_path"])
        self.tor_path_input.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.tor_path_input.setReadOnly(True)
        self.tor_path_input.textChanged.connect(self.update_tor_button_states)
        tor_path_layout.addWidget(self.tor_path_input)
        
        self.browse_tor_button = QPushButton()
        self.browse_tor_button.setStyleSheet("background: #4A5B7A; padding: 5px; border-radius: 5px;")
        self.browse_tor_button.clicked.connect(self.browse_tor_executable)
        tor_path_layout.addWidget(self.browse_tor_button)
        
        self.start_tor_button = QPushButton()
        self.start_tor_button.setStyleSheet("background: #4A5B7A; padding: 5px; border-radius: 5px;")
        self.start_tor_button.clicked.connect(self.start_tor)
        tor_path_layout.addWidget(self.start_tor_button)
        
        self.stop_tor_button = QPushButton()
        self.stop_tor_button.setStyleSheet("background: #7A4A4A; padding: 5px; border-radius: 5px;")
        self.stop_tor_button.clicked.connect(self.stop_tor)
        tor_path_layout.addWidget(self.stop_tor_button)
        
        # Tor status label
        self.tor_status_label = QLabel("Tor Status: Stopped")
        self.tor_status_label.setStyleSheet("color: #FF6B6B; font-weight: bold; margin-left: 10px;")
        self.tor_status_label.setVisible(False)
        tor_path_layout.addWidget(self.tor_status_label)
        tor_path_layout.addStretch()
        
        self.download_tor_button = QPushButton()
        self.download_tor_button.setStyleSheet("background: #4A5B7A; padding: 5px; border-radius: 5px;")
        self.download_tor_button.clicked.connect(self.download_tor)
        tor_path_layout.addWidget(self.download_tor_button)
        
        self.test_tor_button = QPushButton()
        self.test_tor_button.setStyleSheet("background: #4A5B7A; padding: 5px; border-radius: 5px;")
        self.test_tor_button.clicked.connect(self.test_tor)
        tor_path_layout.addWidget(self.test_tor_button)
        
        self.help_tor_button = QPushButton("Help")
        self.help_tor_button.setStyleSheet("background: #5A6B8A; padding: 5px; border-radius: 5px;")
        self.help_tor_button.clicked.connect(self.show_tor_help)
        tor_path_layout.addWidget(self.help_tor_button)
        
        self.tor_layout.addLayout(tor_path_layout)
        
        # Tor download progress bar
        self.tor_progress_bar = QProgressBar()
        self.tor_progress_bar.setStyleSheet("QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; } QProgressBar::chunk { background: #4A5B7A; }")
        self.tor_progress_bar.setVisible(False)
        self.tor_layout.addWidget(self.tor_progress_bar)
        
        # Tor output text area
        self.tor_output_label = QLabel("Tor Output:")
        self.tor_output_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.tor_output_label.setVisible(False)
        self.tor_layout.addWidget(self.tor_output_label)
        
        self.tor_output_text = QTextEdit()
        self.tor_output_text.setMaximumHeight(150)
        self.tor_output_text.setStyleSheet("QTextEdit { border: 1px solid #4A5B7A; border-radius: 5px; padding: 5px; background: #2A2A2A; color: #FFFFFF; font-family: monospace; font-size: 10px; }")
        self.tor_output_text.setReadOnly(True)
        self.tor_output_text.setVisible(False)
        self.tor_layout.addWidget(self.tor_output_text)
        
        proxy_layout.addLayout(self.tor_layout)
        
        self.proxy_group.setLayout(proxy_layout)
        layout.addWidget(self.proxy_group)

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

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        
        self.apply_button = QPushButton()
        self.apply_button.setStyleSheet("background: #4A5B7A; padding: 8px; border-radius: 5px;")
        self.apply_button.clicked.connect(self.confirm_and_apply_settings)
        buttons_layout.addWidget(self.apply_button)
        
        self.reset_button = QPushButton(translate("reset_to_defaults"))
        self.reset_button.setStyleSheet("background: #7A4A5B; padding: 8px; border-radius: 5px;")
        self.reset_button.clicked.connect(self.confirm_and_reset_settings)
        buttons_layout.addWidget(self.reset_button)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()

        # Make the settings page scrollable
        container = QWidget()
        container.setLayout(layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(container)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

        self.update_ui_text()
        
        # Initialize Tor button states
        self.update_tor_button_states()

    def update_language_combo(self):
        self.language_combo.blockSignals(True)
        current_language = self.temp_settings["language"]
        self.language_combo.clear()
        self.language_combo.addItem(translate("english"), "english")
        self.language_combo.addItem(translate("japanese"), "japanese")
        self.language_combo.addItem(translate("korean"), "korean")
        self.language_combo.addItem(translate("chinese-simplified"), "chinese-simplified")
        
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_language:
                self.language_combo.setCurrentIndex(i)
                break
        self.language_combo.blockSignals(False)

    def update_language(self, index):
        language = self.language_combo.itemData(index)
        self.update_temp_setting("language", language)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, translate("browse"), self.temp_settings["base_directory"])
        if directory:
            self.directory_input.setText(directory)
            self.update_temp_setting("base_directory", directory)

    def open_app_directory(self):
        """Open the current app directory in the system file explorer."""
        directory = os.path.join(self.temp_settings["base_directory"], self.temp_settings["base_folder_name"])
        
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError:
                QMessageBox.warning(self, translate("error"), f"Could not create directory: {directory}")
                return
        
        try:
            if sys.platform == "win32":  # Windows
                os.startfile(directory)
            elif sys.platform == "darwin":  # macOS
                subprocess.call(["open", directory])
            else:  # Linux and other Unix-like systems
                subprocess.call(["xdg-open", directory])
        except Exception as e:
            QMessageBox.warning(self, translate("error"), f"Could not open directory: {str(e)}")

    def browse_tor_executable(self):
        """Browse for Tor executable file."""
        if sys.platform == "win32":
            file_filter = "Executable files (*.exe);;All files (*.*)"
            initial_path = self.temp_settings["tor_path"] or "C:\\"
        else:
            file_filter = "All files (*.*)"
            initial_path = self.temp_settings["tor_path"] or "/"
        
        tor_exe_path, _ = QFileDialog.getOpenFileName(
            self, 
            translate("select_tor_executable"), 
            initial_path, 
            file_filter
        )
        
        if tor_exe_path:
            self.update_temp_setting("tor_path", tor_exe_path)
            self.tor_path_input.setText(tor_exe_path)

    def auto_detect_tor(self):
        """Try to auto-detect Tor executable in common locations."""
        common_paths = []
        
        if sys.platform == "win32":
            # Windows common paths
            common_paths.extend([
                r"C:\Users\Drei\Downloads\Kemono Downloader\Tor\tor\tor.exe",  # User's known location
                os.path.join(os.getenv("PROGRAMFILES", "C:\\Program Files"), "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
                os.path.join(os.getenv("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
                os.path.join(os.path.expanduser("~"), "Desktop", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
                os.path.join(os.path.expanduser("~"), "Downloads", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
            ])
        elif sys.platform == "darwin":
            # macOS common paths
            common_paths.extend([
                "/Applications/Tor Browser.app/Contents/MacOS/Tor/tor",
                os.path.join(os.path.expanduser("~"), "Applications", "Tor Browser.app", "Contents", "MacOS", "Tor", "tor"),
                os.path.join(os.path.expanduser("~"), "Desktop", "Tor Browser.app", "Contents", "MacOS", "Tor", "tor"),
                os.path.join(os.path.expanduser("~"), "Downloads", "Tor Browser.app", "Contents", "MacOS", "Tor", "tor"),
            ])
        else:
            # Linux common paths
            common_paths.extend([
                "/usr/bin/tor",
                "/usr/local/bin/tor",
                "/opt/tor-browser/Browser/TorBrowser/Tor/tor",
                os.path.join(os.path.expanduser("~"), "tor-browser", "Browser", "TorBrowser", "Tor", "tor"),
                os.path.join(os.path.expanduser("~"), "Desktop", "tor-browser", "Browser", "TorBrowser", "Tor", "tor"),
                os.path.join(os.path.expanduser("~"), "Downloads", "tor-browser", "Browser", "TorBrowser", "Tor", "tor"),
            ])
        
        for path in common_paths:
            if os.path.exists(path) and os.path.isfile(path):
                try:
                    # Quick test to see if it's actually Tor
                    import subprocess
                    result = subprocess.run([path, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and 'Tor' in result.stdout:
                        return path
                except:
                    continue
        
        return None

    def update_temp_setting(self, key, value):
        self.temp_settings[key] = value

    def update_simultaneous_downloads(self, value):
        self.temp_settings["simultaneous_downloads"] = value
        self.download_slider.blockSignals(True)
        self.download_spinbox.blockSignals(True)
        self.download_slider.setValue(value)
        self.download_spinbox.setValue(value)
        self.download_slider.blockSignals(False)
        self.download_spinbox.blockSignals(False)

    def confirm_and_apply_settings(self):
        auto_check_status = translate("enabled") if self.temp_settings["auto_check_updates"] else translate("disabled")
        language_name = language_manager.get_text(self.temp_settings["language"])
        proxy_status = translate("enabled") if self.temp_settings["use_proxy"] else translate("disabled")
        proxy_type_name = self.temp_settings["proxy_type"].capitalize()
        
        reply = QMessageBox.question(
            self,
            translate("confirm_settings_change"),
            translate("confirm_settings_message", 
                self.temp_settings['base_folder_name'],
                self.temp_settings['base_directory'],
                self.temp_settings['simultaneous_downloads'],
                auto_check_status,
                language_name,
                proxy_status,
                proxy_type_name
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        if not self.temp_settings["base_folder_name"].strip():
            QMessageBox.warning(self, translate("invalid_input"), translate("folder_name_empty"))
            self.folder_name_input.setText(self.settings["base_folder_name"])
            self.temp_settings["base_folder_name"] = self.settings["base_folder_name"]
            return

        # Create the base_directory if it doesn’t exist
        base_dir = self.temp_settings["base_directory"]
        if not os.path.isdir(base_dir):
            try:
                os.makedirs(base_dir, exist_ok=True)
            except OSError as e:
                QMessageBox.warning(self, translate("invalid_input"), 
                                    translate("directory_creation_failed", str(e)))
                self.directory_input.setText(self.settings["base_directory"])
                self.temp_settings["base_directory"] = self.settings["base_directory"]
                return

        language_changed = self.settings["language"] != self.temp_settings["language"]
        
        self.settings = self.temp_settings.copy()
        self.settings["use_proxy"] = False  # Always keep proxy disabled in saved settings
        self.save_settings()
        old_base_folder = self.parent.base_folder
        self.parent.base_folder = os.path.join(self.settings["base_directory"], self.settings["base_folder_name"])
        self.parent.download_folder = os.path.join(self.parent.base_folder, "Downloads")
        self.parent.cache_folder = os.path.join(self.parent.base_folder, "Cache")
        self.parent.other_files_folder = os.path.join(self.parent.base_folder, "Other Files")
        self.parent.ensure_folders_exist()

        if old_base_folder != self.parent.base_folder:
            self.parent.post_tab.cache_dir = self.parent.cache_folder
            self.parent.post_tab.other_files_dir = self.parent.other_files_folder
            self.parent.creator_tab.cache_dir = self.parent.cache_folder
            self.parent.creator_tab.other_files_dir = self.parent.other_files_folder

        if language_changed:
            language_manager.set_language(self.settings["language"])
            self.language_changed.emit()
            self.parent.log(translate("language_changed"))
            self.update_ui_text()

        self.settings_applied.emit()

        auto_check_status = translate("enabled") if self.settings["auto_check_updates"] else translate("disabled")
        language_name = language_manager.get_text(self.settings["language"])
        proxy_status = translate("enabled") if self.settings["use_proxy"] else translate("disabled")
        proxy_type_name = self.settings["proxy_type"].capitalize()
        
        QMessageBox.information(
            self,
            translate("settings_applied"),
            translate("settings_applied_message",
                self.settings['base_folder_name'],
                self.settings['base_directory'],
                self.settings['simultaneous_downloads'],
                auto_check_status,
                language_name,
                proxy_status,
                proxy_type_name
            )
        )

    def confirm_and_reset_settings(self):
        """Confirm and reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            translate("reset_to_defaults"),
            translate("confirm_reset_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.reset_to_defaults()

    def reset_to_defaults(self):
        """Reset temp_settings to default values and update UI."""
        self.temp_settings = self.default_settings.copy()

        # Update UI elements to reflect default values
        self.folder_name_input.setText(self.temp_settings["base_folder_name"])
        self.directory_input.setText(self.temp_settings["base_directory"])
        self.download_slider.setValue(self.temp_settings["simultaneous_downloads"])
        self.download_spinbox.setValue(self.temp_settings["simultaneous_downloads"])
        self.auto_update_checkbox.setChecked(self.temp_settings["auto_check_updates"])
        self.creator_posts_max_attempts_spinbox.setValue(self.temp_settings["creator_posts_max_attempts"])
        self.post_data_max_retries_spinbox.setValue(self.temp_settings["post_data_max_retries"])
        self.file_download_max_retries_spinbox.setValue(self.temp_settings["file_download_max_retries"])
        self.api_request_max_retries_spinbox.setValue(self.temp_settings["api_request_max_retries"])
        
        # Update proxy settings
        self.use_proxy_checkbox.blockSignals(True)
        self.proxy_type_combo.blockSignals(True)
        self.use_proxy_checkbox.setChecked(self.temp_settings["use_proxy"])
        self.proxy_type_combo.setCurrentIndex(self.get_proxy_type_index(self.temp_settings["proxy_type"]))
        self.use_proxy_checkbox.blockSignals(False)
        self.proxy_type_combo.blockSignals(False)
        self.custom_proxy_input.setText(self.temp_settings["custom_proxy_url"])
        self.tor_path_input.setText(self.temp_settings["tor_path"])
        self.on_use_proxy_changed(self.temp_settings["use_proxy"])

        # Update language combo box
        self.update_language_combo()
        
        QMessageBox.information(
            self,
            translate("reset_to_defaults"),
            translate("settings_reset_message")
        )

    def update_ui_text(self):
        self.folder_group.setTitle(translate("folder_settings"))
        self.folder_name_label.setText(translate("folder_name"))
        self.directory_label.setText(translate("save_directory"))
        self.browse_button.setText(translate("browse"))
        self.open_directory_button.setText(translate("open_directory"))  # Added text for open directory button

        self.download_group.setTitle(translate("download_settings"))
        self.simultaneous_downloads_label.setText(translate("simultaneous_downloads"))

        self.retry_group.setTitle(translate("retry_settings"))
        self.creator_posts_max_attempts_label.setText(translate("creator_posts_max_attempts"))
        self.post_data_max_retries_label.setText(translate("post_data_max_retries"))
        self.file_download_max_retries_label.setText(translate("file_download_max_retries"))
        self.api_request_max_retries_label.setText(translate("api_request_max_retries"))

        self.update_group.setTitle(translate("update_settings"))
        self.auto_update_label.setText(translate("auto_check_updates"))

        self.language_group.setTitle(translate("language_settings"))
        self.language_label.setText(translate("language"))
        self.update_language_combo()

        self.proxy_group.setTitle(translate("proxy_settings"))
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
        self.tor_output_label.setText(translate("tor_output"))
        self.tor_status_label.setText("Tor Status: Stopped")

        self.apply_button.setText(translate("apply_changes"))
        self.reset_button.setText(translate("reset_to_defaults"))

    def get_simultaneous_downloads(self):
        return self.settings["simultaneous_downloads"]

    def is_auto_check_updates_enabled(self):
        return self.settings["auto_check_updates"]

    def get_creator_posts_max_attempts(self):
        return self.settings["creator_posts_max_attempts"]

    def get_post_data_max_retries(self):
        return self.settings["post_data_max_retries"]

    def get_file_download_max_retries(self):
        return self.settings["file_download_max_retries"]

    def get_api_request_max_retries(self):
        return self.settings["api_request_max_retries"]

    def get_proxy_type_index(self, proxy_type):
        type_map = {"custom": 0, "tor": 1}
        return type_map.get(proxy_type, 1)  # Default to tor

    def is_tor_running(self):
        """Check if Tor process is currently running."""
        return self.tor_process is not None and self.tor_process.state() == QProcess.ProcessState.Running

    def on_use_proxy_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.update_temp_setting("use_proxy", enabled)
        
        # Show/hide the proxy settings group (checkbox stays visible)
        self.proxy_group.setVisible(enabled)
        
        if enabled:
            # When enabling proxy, default to Tor if not already set
            if self.temp_settings["proxy_type"] not in ["custom", "tor"]:
                self.update_temp_setting("proxy_type", "tor")
                self.proxy_type_combo.setCurrentIndex(1)  # Tor index
            
            # Update UI based on current proxy type
            self.on_proxy_type_changed(self.proxy_type_combo.currentIndex())
            
            # Save proxy settings immediately when enabled
            self.settings["use_proxy"] = enabled
            self.settings["proxy_type"] = self.temp_settings["proxy_type"]
            self.save_settings()
        else:
            # When disabling proxy, save immediately
            self.settings["use_proxy"] = enabled
            self.save_settings()
        
        # Update the UI
        self.layout().update()
        self.repaint()
        self.adjustSize()

    def on_proxy_type_changed(self, index):
        proxy_type = self.proxy_type_combo.itemData(index)
        self.update_temp_setting("proxy_type", proxy_type)
        enabled = self.temp_settings["use_proxy"]
        
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
            self.tor_progress_bar.setVisible(enabled and self.tor_progress_bar.isVisible())
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
        self.tor_progress_bar.setVisible(enabled and proxy_type == "tor" and self.tor_progress_bar.isVisible())
        self.tor_output_label.setVisible(enabled and proxy_type == "tor")
        self.tor_output_text.setVisible(enabled and proxy_type == "tor")
        self.tor_status_label.setVisible(enabled and proxy_type == "tor")
        
        # Update Tor button states
        self.update_tor_button_states()
        
        # Save proxy_type immediately when changed
        self.settings["proxy_type"] = proxy_type
        self.save_settings()
        
        # Auto-detect Tor if switching to Tor and no path is set
        if enabled and proxy_type == "tor" and not self.temp_settings["tor_path"].strip():
            detected_path = self.auto_detect_tor()
            if detected_path:
                self.update_temp_setting("tor_path", detected_path)
                self.tor_path_input.setText(detected_path)
                QMessageBox.information(self, translate("info"), 
                                      translate("tor_auto_detected", detected_path))
                # Update button states after auto-detection
                self.update_tor_button_states()
        
        # Update the UI
        self.layout().update()
        self.repaint()
        self.adjustSize()

    def test_custom_proxy(self):
        proxy_url = self.temp_settings["custom_proxy_url"].strip()
        if not proxy_url:
            QMessageBox.warning(self, translate("error"), translate("custom_proxy_url_empty"))
            return
        
        # Test the proxy by making a request
        try:
            import requests
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
            if response.status_code == 200:
                QMessageBox.information(self, translate("success"), translate("proxy_test_successful"))
            else:
                QMessageBox.warning(self, translate("error"), translate("proxy_test_failed", response.status_code))
        except Exception as e:
            QMessageBox.warning(self, translate("error"), translate("proxy_test_failed", str(e)))

    def test_tor(self):
        tor_path = self.temp_settings["tor_path"]
        if not tor_path or not os.path.exists(tor_path):
            QMessageBox.warning(self, translate("error"), translate("tor_not_configured"))
            return
        
        # Check if tor executable is valid
        try:
            import subprocess
            result = subprocess.run([tor_path, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0 or 'Tor' not in result.stdout:
                QMessageBox.warning(self, translate("error"), translate("tor_test_failed"))
                return
        except Exception as e:
            QMessageBox.warning(self, translate("error"), translate("tor_test_failed", str(e)))
            return
        
        # Check if Tor is running as SOCKS proxy
        try:
            import requests
            import socks
            
            # Test SOCKS5 proxy connection
            proxies = {
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            }
            
            # Try to connect to a test service that works with Tor
            response = requests.get('https://check.torproject.org/api/ip', proxies=proxies, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('IsTor', False):
                    QMessageBox.information(self, translate("success"), translate("tor_proxy_working"))
                else:
                    QMessageBox.warning(self, translate("warning"), translate("tor_executable_ok_but_proxy_not_running"))
            else:
                QMessageBox.warning(self, translate("warning"), translate("tor_executable_ok_but_proxy_not_running"))
                
        except ImportError:
            QMessageBox.information(self, translate("success"), translate("tor_test_successful"))
        except Exception as e:
            QMessageBox.warning(self, translate("warning"), translate("tor_executable_ok_but_proxy_not_running", str(e)))

    def start_tor(self):
        tor_path = self.temp_settings["tor_path"]
        if not tor_path or not os.path.exists(tor_path):
            QMessageBox.warning(self, translate("error"), translate("tor_not_configured"))
            return
        
        if self.tor_process and self.tor_process.state() == QProcess.ProcessState.Running:
            QMessageBox.information(self, translate("info"), translate("tor_already_running"))
            return
        
        # Create data directory if it doesn't exist
        if not self.tor_data_dir:
            import tempfile
            self.tor_data_dir = tempfile.mkdtemp(prefix="kemonodownloader_tor_")
        
        # Clear previous output
        self.tor_output_text.clear()
        
        # Start Tor process
        self.tor_process = QProcess(self)
        self.tor_process.setProgram(tor_path)
        self.tor_process.setArguments([
            "--SocksPort", "9050",
            "--DataDirectory", self.tor_data_dir,
            "--Log", "notice stdout",
            "--ExitPolicy", "reject *:*",  # Disable exit relay
            "--GeoIPExcludeUnknown", "1"
        ])
        
        self.tor_process.readyReadStandardOutput.connect(self.handle_tor_output)
        self.tor_process.readyReadStandardError.connect(self.handle_tor_error)
        self.tor_process.finished.connect(self.handle_tor_finished)
        
        self.tor_process.start()
        
        # Update UI
        self.start_tor_button.setEnabled(False)
        self.stop_tor_button.setEnabled(True)
        self.test_tor_button.setEnabled(True)
        self.tor_status_label.setText("Tor Status: Starting...")
        self.tor_status_label.setStyleSheet("color: #FFD93D; font-weight: bold; margin-left: 10px;")
        
        # Disable proxy type selection while Tor is running
        self.proxy_type_combo.setEnabled(False)
        
        QMessageBox.information(self, translate("info"), translate("tor_starting"))

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
        self.tor_status_label.setText("Tor Status: Stopped")
        self.tor_status_label.setStyleSheet("color: #FF6B6B; font-weight: bold; margin-left: 10px;")
        
        # Re-enable proxy type selection
        self.proxy_type_combo.setEnabled(True)
        
        QMessageBox.information(self, translate("info"), translate("tor_stopped"))

    def show_tor_help(self):
        """Show help modal with Tor setup instructions."""
        help_text = """<b>How to set up Tor for downloading:</b><br><br>
1. First Click <b>Download Tor</b> to download the Tor browser<br>
2. Wait for the download to complete<br>
3. Click <b>Start Tor</b> to start the Tor process<br>
4. Click <b>Test Tor</b> to verify Tor is working<br>
5. You can start downloading now with Tor proxy enabled<br><br>
<b>Note:</b> Tor provides anonymity but may be slower than direct connections."""
        
        QMessageBox.information(self, "Tor Setup Help", help_text)

    def download_tor(self):
        try:
            # Determine the Tor download URL based on platform
            if sys.platform == "win32":
                # Tor expert bundle for Windows
                tor_url = "https://archive.torproject.org/tor-package-archive/torbrowser/15.0.3/tor-expert-bundle-windows-x86_64-15.0.3.tar.gz"
                tor_extract_dir = "tor-expert-bundle-windows-x86_64-15.0.3"
            elif sys.platform == "darwin":
                # Check for Apple Silicon vs Intel
                import platform
                machine = platform.machine().lower()
                if machine == "arm64":
                    tor_url = "https://archive.torproject.org/tor-package-archive/torbrowser/15.0.3/tor-expert-bundle-macos-aarch64-15.0.3.tar.gz"
                    tor_extract_dir = "tor-expert-bundle-macos-aarch64-15.0.3"
                else:
                    tor_url = "https://archive.torproject.org/tor-package-archive/torbrowser/15.0.3/tor-expert-bundle-macos-x86_64-15.0.3.tar.gz"
                    tor_extract_dir = "tor-expert-bundle-macos-x86_64-15.0.3"
            else:  # Linux
                tor_url = "https://archive.torproject.org/tor-package-archive/torbrowser/15.0.3/tor-expert-bundle-linux-x86_64-15.0.3.tar.gz"
                tor_extract_dir = "tor-expert-bundle-linux-x86_64-15.0.3"
            
            # Create tor directory in app data
            tor_path = os.path.join(self.temp_settings["base_directory"], self.temp_settings["base_folder_name"], "Tor")
            os.makedirs(tor_path, exist_ok=True)
            
            # Show progress bar and disable button
            self.tor_progress_bar.setVisible(True)
            self.tor_progress_bar.setValue(0)
            self.download_tor_button.setEnabled(False)
            self.download_tor_button.setText(translate("downloading"))
            
            # Download Tor with progress tracking
            QMessageBox.information(self, translate("info"), translate("downloading_tor"))
            
            # Start download thread
            self.download_thread = DownloadTorThread(tor_url, tor_extract_dir, tor_path)
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
            QMessageBox.warning(self, translate("error"), translate("tor_download_failed", str(e)))

    def on_tor_download_success(self, tor_exe):
        self.download_finished.emit()
        # Hide progress bar and re-enable button
        self.tor_progress_bar.setVisible(False)
        self.download_tor_button.setEnabled(True)
        self.download_tor_button.setText(translate("download_tor"))
        
        self.update_temp_setting("tor_path", tor_exe)
        self.tor_path_input.setText(tor_exe)
        QMessageBox.information(self, translate("success"), translate("tor_download_successful"))
        self.update_tor_button_states()

    def on_tor_download_error(self, error_msg):
        self.download_finished.emit()
        # Hide progress bar and re-enable button on error
        self.tor_progress_bar.setVisible(False)
        self.download_tor_button.setEnabled(True)
        self.download_tor_button.setText(translate("download_tor"))
        if error_msg == "tor_exe_not_found":
            QMessageBox.warning(self, translate("error"), translate("tor_exe_not_found"))
        else:
            QMessageBox.warning(self, translate("error"), translate("tor_download_failed", error_msg))

    def update_tor_button_states(self):
        tor_path = self.temp_settings["tor_path"]
        tor_exists = tor_path and os.path.exists(tor_path)
        
        self.test_tor_button.setEnabled(tor_exists)
        self.download_tor_button.setVisible(not tor_exists)  # Hide download button if Tor is already available
        
        if self.tor_process and self.tor_process.state() == QProcess.ProcessState.Running:
            self.start_tor_button.setEnabled(False)
            self.stop_tor_button.setEnabled(True)
        else:
            self.start_tor_button.setEnabled(tor_exists)
            self.stop_tor_button.setEnabled(False)

    def handle_tor_output(self):
        if self.tor_process:
            output = self.tor_process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
            if output.strip():
                # Append to text area
                self.tor_output_text.append(output.strip())
                # Auto-scroll to bottom
                scrollbar = self.tor_output_text.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
                
                # Check for bootstrap completion
                if "Bootstrapped 100%" in output:
                    self.tor_status_label.setText("Tor Status: Running")
                    self.tor_status_label.setStyleSheet("color: #6BCF7F; font-weight: bold; margin-left: 10px;")
                    QMessageBox.information(self, translate("success"), translate("tor_running"))

    def handle_tor_error(self):
        if self.tor_process:
            error = self.tor_process.readAllStandardError().data().decode('utf-8', errors='ignore')
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
        
        self.start_tor_button.setEnabled(True)
        self.stop_tor_button.setEnabled(False)
        self.tor_status_label.setText("Tor Status: Stopped")
        self.tor_status_label.setStyleSheet("color: #FF6B6B; font-weight: bold; margin-left: 10px;")

    def get_proxy_settings(self):
        """Return proxy settings for use with requests"""
        # Check both saved settings and temp settings (in case settings haven't been applied yet)
        settings_to_check = self.settings if self.settings.get("use_proxy") else self.temp_settings
        
        if not settings_to_check["use_proxy"]:
            return None
        
        if settings_to_check["proxy_type"] == "custom":
            proxy_url = settings_to_check["custom_proxy_url"]
            if proxy_url:
                return {
                    'http': proxy_url,
                    'https': proxy_url
                }
        elif settings_to_check["proxy_type"] == "tor":
            # Check if Tor is actually running
            if not self.tor_process or self.tor_process.state() != QProcess.ProcessState.Running:
                print("Tor proxy requested but Tor is not running")
                return None
            
            # For Tor, we need to use SOCKS5h proxy (resolves DNS through Tor)
            # Note: This requires requests[socks] or PySocks to be installed
            try:
                import socks
                proxies = {
                    'http': 'socks5h://127.0.0.1:9050',
                    'https': 'socks5h://127.0.0.1:9050'
                }
                print(f"Returning Tor proxy settings: {proxies}")
                return proxies
            except ImportError:
                print("PySocks not available, falling back to HTTP proxy")
                # Fallback to HTTP proxy if socks not available
                return {
                    'http': 'http://127.0.0.1:8118',  # Privoxy default
                    'https': 'http://127.0.0.1:8118'
                }
        return None

class DownloadTorThread(QThread):
    progress = pyqtSignal(int)
    finished_success = pyqtSignal(str)
    finished_error = pyqtSignal(str)

    def __init__(self, tor_url, tor_extract_dir, tor_path):
        super().__init__()
        self.tor_url = tor_url
        self.tor_extract_dir = tor_extract_dir
        self.tor_path = tor_path

    def run(self):
        import requests
        import tarfile
        import tempfile

        try:
            response = requests.get(self.tor_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as tmp_file:
                tmp_archive = tmp_file.name
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress.emit(progress)

            # Extract Tor
            self.progress.emit(100)

            with tarfile.open(tmp_archive, 'r:gz') as tar_ref:
                tar_ref.extractall(self.tor_path)

            # Clean up
            os.unlink(tmp_archive)

            # Find tor executable - search entire extracted directory tree
            tor_exe = None
            for root, dirs, files in os.walk(self.tor_path):
                for f in files:
                    if f.lower() in ('tor.exe', 'tor'):
                        tor_exe = os.path.join(root, f)
                        break
                if tor_exe:
                    break

            if tor_exe:
                self.finished_success.emit(tor_exe)
            else:
                self.finished_error.emit("tor_exe_not_found")

        except Exception as e:
            self.finished_error.emit(str(e))
