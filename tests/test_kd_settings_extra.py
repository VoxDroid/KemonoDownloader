import importlib
import os
import subprocess
from types import SimpleNamespace

from PyQt6.QtCore import QByteArray, QProcess, QSettings
from PyQt6.QtWidgets import QMessageBox


def make_parent():
    class MockParent:
        def __init__(self):
            self.base_folder = "base"
            self.download_folder = os.path.join("base", "Downloads")
            self.cache_folder = os.path.join("base", "Cache")
            self.other_files_folder = os.path.join("base", "Other Files")

        def log(self, msg):
            pass

        def ensure_folders_exist(self):
            pass

    return MockParent()


def test_confirm_and_apply_no_response(qapp, monkeypatch):
    from kemonodownloader.kd_settings import SettingsTab

    QSettings("VoxDroid", "KemonoDownloader").clear()
    parent = make_parent()

    # Simulate user clicking 'No' on confirmation
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.No
    )

    st = SettingsTab(parent)
    orig = st.settings["base_folder_name"]
    st.temp_settings["base_folder_name"] = "changed"

    st.confirm_and_apply_settings()
    assert st.settings["base_folder_name"] == orig


def test_confirm_and_apply_empty_folder_name_shows_warning(qapp, monkeypatch):
    from kemonodownloader.kd_settings import SettingsTab

    QSettings("VoxDroid", "KemonoDownloader").clear()
    parent = make_parent()

    # Accept the confirmation
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes
    )
    called = {}
    monkeypatch.setattr(
        QMessageBox, "warning", lambda *a, **k: called.setdefault("warn", True)
    )

    st = SettingsTab(parent)
    # Set empty folder name
    st.temp_settings["base_folder_name"] = ""
    st.confirm_and_apply_settings()

    # Should have triggered a warning and restored the folder name
    assert called.get("warn") is True
    assert st.temp_settings["base_folder_name"] == st.settings["base_folder_name"]


def test_confirm_and_apply_directory_creation_failure(qapp, monkeypatch):
    from kemonodownloader.kd_settings import SettingsTab

    QSettings("VoxDroid", "KemonoDownloader").clear()
    parent = make_parent()

    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes
    )
    warned = {}
    monkeypatch.setattr(
        QMessageBox, "warning", lambda *a, **k: warned.setdefault("w", True)
    )

    # Force directory creation to fail
    monkeypatch.setattr(os.path, "isdir", lambda p: False)

    def fail_makedirs(p, exist_ok=True):
        raise OSError("fail")

    monkeypatch.setattr(os, "makedirs", fail_makedirs)

    st = SettingsTab(parent)
    # Ensure we attempt to create a non-existent directory
    st.temp_settings["base_directory"] = "/nonexistent/path"
    st.confirm_and_apply_settings()

    assert warned.get("w") is True
    # Reset should keep settings' base_directory
    assert st.temp_settings["base_directory"] == st.settings["base_directory"]


def test_auto_detect_tor_finds_executable(qapp, monkeypatch):
    from kemonodownloader.kd_settings import SettingsTab

    QSettings("VoxDroid", "KemonoDownloader").clear()
    parent = make_parent()

    st = SettingsTab(parent)

    # Make tor paths present and return a successful --version
    monkeypatch.setattr(os.path, "exists", lambda p: "tor" in str(p).lower())
    monkeypatch.setattr(os.path, "isfile", lambda p: "tor" in str(p).lower())

    def fake_run(args, capture_output=True, text=True, timeout=5):
        return SimpleNamespace(returncode=0, stdout="Tor v")

    monkeypatch.setattr(subprocess, "run", fake_run)

    found = st.auto_detect_tor()
    assert found is not None and "tor" in found.lower()


def test_get_proxy_settings_custom_and_tor(qapp, monkeypatch):
    from kemonodownloader.kd_settings import SettingsTab

    QSettings("VoxDroid", "KemonoDownloader").clear()
    parent = make_parent()
    st = SettingsTab(parent)

    # Custom proxy
    st.settings["use_proxy"] = True
    st.settings["proxy_type"] = "custom"
    st.settings["custom_proxy_url"] = "127.0.0.1:8080"
    assert st.get_proxy_settings() == {
        "http": "127.0.0.1:8080",
        "https": "127.0.0.1:8080",
    }

    # Tor proxy when Tor not running -> still Tor's port (fails closed)
    st.settings["proxy_type"] = "tor"
    st.tor_process = None
    assert st.get_proxy_settings()["http"].startswith("socks5h://")

    # Tor running and socks available
    class FakeProcess:
        def state(self):
            return QProcess.ProcessState.Running

    st.tor_process = FakeProcess()
    monkeypatch.setattr(
        importlib.util, "find_spec", lambda name: object() if name == "socks" else None
    )
    proxies = st.get_proxy_settings()
    assert proxies["http"].startswith("socks5h://")


def test_handle_tor_output_and_error(qapp, monkeypatch):
    from kemonodownloader.kd_settings import SettingsTab

    QSettings("VoxDroid", "KemonoDownloader").clear()
    parent = make_parent()
    st = SettingsTab(parent)

    # Prepare fake process that returns Bootstrapped output
    class FakeProcOut:
        def readAllStandardOutput(self):
            return QByteArray(b"Bootstrapped 100%\n")

        def readAllStandardError(self):
            return QByteArray(b"")

    st.tor_process = FakeProcOut()
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    st.handle_tor_output()
    assert "running" in st.tor_status_label.text().lower() or st.tor_status_label.text()

    # Now test error handling
    class FakeProcErr:
        def readAllStandardOutput(self):
            return QByteArray(b"")

        def readAllStandardError(self):
            return QByteArray(b"Some error\n")

    st.tor_process = FakeProcErr()
    st.handle_tor_error()
    assert (
        "error" in st.tor_output_text.toPlainText().lower()
        or "some error" in st.tor_output_text.toPlainText().lower()
    )


def test_on_tor_download_handlers(qapp, monkeypatch):
    from kemonodownloader.kd_settings import SettingsTab

    QSettings("VoxDroid", "KemonoDownloader").clear()
    parent = make_parent()
    st = SettingsTab(parent)

    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)

    # Success path
    st.on_tor_download_success("/tmp/tor_exe")
    assert st.tor_path_input.text() == "/tmp/tor_exe"

    # Error paths
    st.on_tor_download_error("tor_exe_not_found")
    st.on_tor_download_error("other error")
