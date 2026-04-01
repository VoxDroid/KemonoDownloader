import importlib.util
import os
import subprocess
from types import SimpleNamespace

from PyQt6.QtCore import QProcess

from kemonodownloader.kd_settings import SettingsTab


def _make_parent(tmp_path):
    parent = SimpleNamespace()
    parent.base_folder = str(tmp_path / "base")
    parent.download_folder = str(tmp_path / "downloads")
    parent.cache_folder = str(tmp_path / "cache")
    parent.other_files_folder = str(tmp_path / "other")
    parent.ensure_folders_exist = lambda: None
    parent.post_tab = SimpleNamespace()
    parent.creator_tab = SimpleNamespace()
    return parent


def test_auto_detect_tor_finds_executable(tmp_path, qtbot, monkeypatch):
    parent = _make_parent(tmp_path)
    st = SettingsTab(parent)

    # Set base directory to tmp_path so candidate_roots include it
    st.temp_settings["base_directory"] = str(tmp_path)
    st.temp_settings["base_folder_name"] = "KDTest"

    # Create a fake tor executable inside the base directory
    tor_file = tmp_path / "tor"
    tor_file.write_text("#!/bin/sh\necho Tor")
    os.chmod(tor_file, 0o755)

    class FakeResult:
        def __init__(self):
            self.returncode = 0
            self.stdout = "Tor 0.4"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeResult())

    detected = st.auto_detect_tor()
    assert detected is not None
    assert str(tor_file) in detected


def test_get_proxy_settings_tor_with_socks(monkeypatch, qtbot, tmp_path):
    parent = _make_parent(tmp_path)
    st = SettingsTab(parent)
    st.temp_settings["use_proxy"] = True
    st.temp_settings["proxy_type"] = "tor"

    class FakeProc:
        def state(self):
            return QProcess.ProcessState.Running

    st.tor_process = FakeProc()

    # Simulate PySocks present
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())

    proxies = st.get_proxy_settings()
    assert proxies is not None
    assert proxies["http"].startswith("socks5h://")


def test_get_proxy_settings_tor_without_socks(monkeypatch, qtbot, tmp_path):
    parent = _make_parent(tmp_path)
    st = SettingsTab(parent)
    st.temp_settings["use_proxy"] = True
    st.temp_settings["proxy_type"] = "tor"

    class FakeProc:
        def state(self):
            return QProcess.ProcessState.Running

    st.tor_process = FakeProc()

    # Simulate PySocks not present
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)

    proxies = st.get_proxy_settings()
    assert proxies is not None
    assert proxies["http"].startswith("http://127.0.0.1")


def test_test_tor_not_configured(monkeypatch, qtbot, tmp_path):
    parent = _make_parent(tmp_path)
    st = SettingsTab(parent)
    st.temp_settings["tor_path"] = ""

    recorded = {}

    def fake_warning(*a, **k):
        recorded["called"] = True

    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.warning", fake_warning)
    st.test_tor()
    assert recorded.get("called") is True


def test_test_custom_proxy_empty(monkeypatch, qtbot, tmp_path):
    parent = _make_parent(tmp_path)
    st = SettingsTab(parent)
    st.temp_settings["custom_proxy_url"] = ""

    recorded = {}

    def fake_warning(*a, **k):
        recorded["called"] = True

    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.warning", fake_warning)
    st.test_custom_proxy()
    assert recorded.get("called") is True


def test_test_custom_proxy_requests_exception(monkeypatch, qtbot, tmp_path):
    parent = _make_parent(tmp_path)
    st = SettingsTab(parent)
    st.temp_settings["custom_proxy_url"] = "http://127.0.0.1:9999"

    def fake_get(*a, **k):
        raise Exception("conn fail")

    monkeypatch.setattr("requests.get", fake_get)

    recorded = {}

    def fake_warning(*a, **k):
        recorded["called"] = True

    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.warning", fake_warning)
    st.test_custom_proxy()
    assert recorded.get("called") is True
