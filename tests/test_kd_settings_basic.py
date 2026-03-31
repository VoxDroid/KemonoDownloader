import subprocess
import sys
from types import SimpleNamespace

from PyQt6.QtCore import QSettings

from kemonodownloader import kd_settings as ks
from kemonodownloader.kd_settings import SettingsTab


def test_get_default_base_directory_platforms(monkeypatch, tmp_path):
    # Windows
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path / "AppData"))
    path = SettingsTab.get_default_base_directory(None)
    assert "Kemono Downloader" in path

    # macOS
    monkeypatch.setattr(sys, "platform", "darwin")
    path = SettingsTab.get_default_base_directory(None)
    assert "Library/Application Support" in path

    # Linux/other
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    path = SettingsTab.get_default_base_directory(None)
    assert "Kemono Downloader" in path


def test_save_and_load_settings_roundtrip(tmp_path):
    ini_path = str(tmp_path / "test_settings.ini")
    qs = QSettings(ini_path, QSettings.Format.IniFormat)

    # Build a fake SettingsTab-like object for save_settings
    s = SettingsTab.__new__(SettingsTab)
    s.qsettings = qs
    s.settings = {
        "base_folder_name": "My Folder",
        "base_directory": str(tmp_path / "base"),
        "simultaneous_downloads": 3,
        "auto_check_updates": False,
        "language": "english",
        "creator_posts_max_attempts": 10,
        "post_data_max_retries": 2,
        "file_download_max_retries": 5,
        "api_request_max_retries": 1,
        "proxy_type": "custom",
        "custom_proxy_url": "http://127.0.0.1:8080",
        "tor_path": "",
        "creator_filename_template": "{post_id}_{orig_name}",
        "creator_folder_strategy": "per_post",
        "font": "JetBrains Mono",
    }

    # Call save_settings which should write to the INI
    SettingsTab.save_settings(s)

    # Now load settings using a fresh object
    s2 = SettingsTab.__new__(SettingsTab)
    s2.qsettings = QSettings(ini_path, QSettings.Format.IniFormat)
    # Provide default_settings minimal shape referenced by load_settings
    s2.default_settings = s.settings.copy()
    loaded = SettingsTab.load_settings(s2)

    assert loaded["base_folder_name"] == s.settings["base_folder_name"]
    assert int(loaded["simultaneous_downloads"]) == s.settings["simultaneous_downloads"]
    assert loaded["proxy_type"] == s.settings["proxy_type"]


def make_tab(tmp_path):
    parent = SimpleNamespace()
    # Ensure parent has methods used when applying settings
    parent.base_folder = str(tmp_path / "base")
    parent.download_folder = str(tmp_path / "base" / "Downloads")
    parent.cache_folder = str(tmp_path / "base" / "Cache")
    parent.other_files_folder = str(tmp_path / "base" / "Other Files")
    parent.ensure_folders_exist = lambda: None
    parent.post_tab = SimpleNamespace()
    parent.creator_tab = SimpleNamespace()
    return ks.SettingsTab(parent)


def test_getters_and_temp_update(tmp_path):
    tab = make_tab(tmp_path)
    # initial getters
    assert isinstance(tab.get_creator_folder_strategy(), str)
    tab.update_temp_setting("simultaneous_downloads", 7)
    tab.update_simultaneous_downloads(7)
    assert tab.temp_settings["simultaneous_downloads"] == 7
    assert tab.download_slider.value() == 7
    assert tab.download_spinbox.value() == 7


def test_proxy_type_and_get_proxy_settings(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    # custom proxy
    tab.temp_settings["use_proxy"] = True
    tab.temp_settings["proxy_type"] = "custom"
    tab.temp_settings["custom_proxy_url"] = "http://127.0.0.1:8080"
    proxies = tab.get_proxy_settings()
    assert proxies["http"].startswith("http")

    # tor proxy when tor not running -> returns None
    tab.temp_settings["proxy_type"] = "tor"
    tab.tor_process = None
    assert tab.get_proxy_settings() is None

    # simulate tor process running but no socks package -> fallback to http
    class FakeProc:
        def state(self):
            return ks.QProcess.ProcessState.Running

    tab.tor_process = FakeProc()
    monkeypatch.setattr("importlib.util.find_spec", lambda name: None)
    proxies = tab.get_proxy_settings()
    assert "http" in proxies


def test_browse_and_open_directory(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    # browse_directory
    monkeypatch.setattr(
        "kemonodownloader.kd_settings.QFileDialog.getExistingDirectory",
        lambda *a, **k: str(tmp_path),
    )
    tab.browse_directory()
    assert tab.directory_input.text() == str(tmp_path)

    # open_app_directory should call subprocess; monkeypatch to avoid side-effects
    tab.temp_settings["base_directory"] = str(tmp_path)
    tab.temp_settings["base_folder_name"] = "MyApp"
    monkeypatch.setattr(subprocess, "call", lambda *a, **k: 0)
    tab.open_app_directory()


def test_reset_to_defaults_and_template_help(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    # change some fields
    tab.folder_name_input.setText("X")
    tab.directory_input.setText(str(tmp_path))
    # Reset should restore defaults
    monkeypatch.setattr(
        "kemonodownloader.kd_settings.QMessageBox.information", lambda *a, **k: None
    )
    tab.reset_to_defaults()
    assert tab.folder_name_input.text() == tab.default_settings["base_folder_name"]
