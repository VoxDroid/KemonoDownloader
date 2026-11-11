import importlib
import os
from types import SimpleNamespace

from kemonodownloader import kd_settings as ks
from kemonodownloader.kd_settings import SettingsTab


def test_auto_detect_tor_prefers_app_local(tmp_path, monkeypatch, qapp):
    parent = SimpleNamespace(download_folder=str(tmp_path / "downloads"))
    st = SettingsTab(parent)

    # Use the temp base directory so candidate_roots includes it
    st.temp_settings["base_directory"] = str(tmp_path)
    st.temp_settings["base_folder_name"] = "AppBase"

    # Create a fake tor executable under the base dir
    tor_dir = tmp_path / "Tor" / "TorBrowser" / "Tor"
    os.makedirs(tor_dir, exist_ok=True)
    tor_path = tor_dir / "tor"
    tor_path.write_text("#!/bin/sh\necho Tor")
    os.chmod(tor_path, 0o755)

    # Monkeypatch subprocess.run to claim the binary is Tor
    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="Tor version XYZ"),
    )

    found = st.auto_detect_tor()
    assert found is not None
    assert os.path.basename(found) == "tor"


def test_show_template_help_and_browse_directory(monkeypatch, tmp_path, qapp):
    st = SettingsTab(SimpleNamespace())

    called = {}

    # Monkeypatch QMessageBox.information
    monkeypatch.setattr(
        "kemonodownloader.kd_settings.QMessageBox.information",
        lambda *a, **k: called.setdefault("info", True),
    )

    st.show_template_help()
    assert called.get("info")

    # Monkeypatch QFileDialog.getExistingDirectory
    monkeypatch.setattr(
        "kemonodownloader.kd_settings.QFileDialog.getExistingDirectory",
        lambda *a, **k: str(tmp_path / "chosen"),
    )

    st.browse_directory()
    assert st.temp_settings["base_directory"].endswith("chosen")


def make_tab(tmp_path):
    parent = SimpleNamespace()
    parent.base_folder = str(tmp_path / "base")
    parent.download_folder = str(tmp_path / "base" / "Downloads")
    parent.cache_folder = str(tmp_path / "base" / "Cache")
    parent.other_files_folder = str(tmp_path / "base" / "Other Files")
    parent.ensure_folders_exist = lambda: None
    parent.post_tab = SimpleNamespace()
    parent.creator_tab = SimpleNamespace()
    return ks.SettingsTab(parent)


def test_get_proxy_settings_tor_fallback(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    tab.temp_settings["use_proxy"] = True
    tab.temp_settings["proxy_type"] = "tor"

    class FakeProc:
        def state(self):
            from PyQt6.QtCore import QProcess

            return QProcess.ProcessState.Running

    tab.tor_process = FakeProc()

    # Missing socks package: no HTTP fallback, still Tor's SOCKS URL
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)

    proxies = tab.get_proxy_settings()
    assert proxies is not None
    assert proxies.get("http").startswith("socks5h://")


def test_auto_detect_tor_returns_none_when_not_found(tmp_path):
    tab = make_tab(tmp_path)
    # Ensure temp_settings points to a tmp base directory that does not contain tor
    tab.temp_settings["base_directory"] = str(tmp_path / "no_tor")
    res = tab.auto_detect_tor()
    assert res is None
