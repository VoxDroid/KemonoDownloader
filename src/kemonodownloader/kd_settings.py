import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QGroupBox, QGridLayout, QLabel, QSlider, QSpinBox, 
    QFileDialog, QMessageBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from kemonodownloader.kd_language import language_manager, translate

class SettingsTab(QWidget):
    settings_applied = pyqtSignal()
    language_changed = pyqtSignal()

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
            "api_request_max_retries": 3
        }
        self.settings = self.load_settings()
        self.temp_settings = self.settings.copy()
        
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

        self.update_ui_text()

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
        
        reply = QMessageBox.question(
            self,
            translate("confirm_settings_change"),
            translate("confirm_settings_message", 
                self.temp_settings['base_folder_name'],
                self.temp_settings['base_directory'],
                self.temp_settings['simultaneous_downloads'],
                auto_check_status,
                language_name
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
        
        QMessageBox.information(
            self,
            translate("settings_applied"),
            translate("settings_applied_message",
                self.settings['base_folder_name'],
                self.settings['base_directory'],
                self.settings['simultaneous_downloads'],
                auto_check_status,
                language_name
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
