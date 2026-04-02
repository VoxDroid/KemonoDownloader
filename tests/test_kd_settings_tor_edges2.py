import os
import shutil
from types import SimpleNamespace

import pytest

from kemonodownloader import kd_settings as ks
from kemonodownloader.kd_settings import SettingsTab


def make_tab(tmp_path):
    parent = SimpleNamespace()
    parent.base_folder = str(tmp_path / "base")
    parent.download_folder = str(tmp_path / "base" / "Downloads")
    parent.cache_folder = str(tmp_path / "base" / "Cache")
    parent.other_files_folder = str(tmp_path / "base" / "Other Files")
    parent.ensure_folders_exist = lambda: None
    parent.post_tab = SimpleNamespace()
    parent.creator_tab = SimpleNamespace()
    return SettingsTab(parent)


def test_open_app_directory_creation_failure_warns(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["base_directory"] = str(tmp_path)
    tab.temp_settings["base_folder_name"] = "AppFolder"
    target = os.path.join(str(tmp_path), "AppFolder")

    real_exists = os.path.exists
    monkeypatch.setattr(
        ks.os.path,
        "exists",
        lambda p: False if p == target else real_exists(p),
    )

    def fail_makedirs(*args, **kwargs):
        raise OSError("cannot create")

    monkeypatch.setattr(ks.os, "makedirs", fail_makedirs)

    warned = {}
    monkeypatch.setattr(
        ks.QMessageBox, "warning", lambda *a, **k: warned.setdefault("called", True)
    )

    tab.open_app_directory()
    assert warned.get("called") is True


def test_open_app_directory_open_failure_warns(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["base_directory"] = str(tmp_path)
    tab.temp_settings["base_folder_name"] = "AppFolder"

    app_dir = tmp_path / "AppFolder"
    app_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(ks.sys, "platform", "darwin")
    monkeypatch.setattr(
        ks.subprocess,
        "call",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("open failed")),
    )

    warned = {}
    monkeypatch.setattr(
        ks.QMessageBox, "warning", lambda *a, **k: warned.setdefault("called", True)
    )

    tab.open_app_directory()
    assert warned.get("called") is True


def test_browse_tor_executable_windows_updates_path(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["tor_path"] = ""

    monkeypatch.setattr(ks.sys, "platform", "win32")
    observed = {}

    def fake_open_file(*args, **kwargs):
        observed["initial_path"] = args[2]
        observed["file_filter"] = args[3]
        return ("C:\\Tor\\tor.exe", "")

    monkeypatch.setattr(ks.QFileDialog, "getOpenFileName", fake_open_file)

    tab.browse_tor_executable()

    assert observed["initial_path"] == "C:\\"
    assert "Executable files" in observed["file_filter"]
    assert tab.temp_settings["tor_path"] == "C:\\Tor\\tor.exe"
    assert tab.tor_path_input.text() == "C:\\Tor\\tor.exe"


def test_browse_tor_executable_non_windows_root_default(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["tor_path"] = ""

    monkeypatch.setattr(ks.sys, "platform", "darwin")
    observed = {}

    def fake_open_file(*args, **kwargs):
        observed["initial_path"] = args[2]
        observed["file_filter"] = args[3]
        return ("", "")

    monkeypatch.setattr(ks.QFileDialog, "getOpenFileName", fake_open_file)

    tab.browse_tor_executable()

    assert observed["initial_path"] == "/"
    assert observed["file_filter"] == "All files (*.*)"


def test_on_proxy_type_changed_auto_detects_tor_path(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["use_proxy"] = True
    tab.temp_settings["tor_path"] = "   "

    monkeypatch.setattr(tab, "auto_detect_tor", lambda: "/tmp/tor_auto")
    info = {}
    monkeypatch.setattr(
        ks.QMessageBox,
        "information",
        lambda *a, **k: info.setdefault("called", True),
    )

    state_calls = {"count": 0}

    def count_update_states():
        state_calls["count"] += 1

    monkeypatch.setattr(tab, "update_tor_button_states", count_update_states)

    tor_index = tab.proxy_type_combo.findData("tor")
    tab.on_proxy_type_changed(tor_index)

    assert tab.temp_settings["tor_path"] == "/tmp/tor_auto"
    assert tab.tor_path_input.text() == "/tmp/tor_auto"
    assert info.get("called") is True
    # Called once in the main path and once after auto-detect.
    assert state_calls["count"] >= 2


@pytest.mark.parametrize("is_tor,expected_info", [(True, True), (False, False)])
def test_test_tor_reports_proxy_state(
    tmp_path, monkeypatch, qapp, is_tor, expected_info
):
    tab = make_tab(tmp_path)
    tor_exe = tmp_path / "tor"
    tor_exe.write_text("tor")
    tab.temp_settings["tor_path"] = str(tor_exe)

    monkeypatch.setattr(ks.os.path, "exists", lambda p: True)
    monkeypatch.setattr(
        ks.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="Tor version 0.4"),
    )

    class Resp:
        status_code = 200

        def json(self):
            return {"IsTor": is_tor}

    monkeypatch.setattr("requests.get", lambda *a, **k: Resp())

    called = {"info": 0, "warn": 0}
    monkeypatch.setattr(
        ks.QMessageBox,
        "information",
        lambda *a, **k: called.__setitem__("info", called["info"] + 1),
    )
    monkeypatch.setattr(
        ks.QMessageBox,
        "warning",
        lambda *a, **k: called.__setitem__("warn", called["warn"] + 1),
    )

    tab.test_tor()

    if expected_info:
        assert called["info"] > 0
    else:
        assert called["warn"] > 0


def test_stop_tor_when_not_running_warns(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.tor_process = None

    warned = {}
    monkeypatch.setattr(
        ks.QMessageBox, "warning", lambda *a, **k: warned.setdefault("called", True)
    )

    tab.stop_tor()
    assert warned.get("called") is True


def test_start_tor_when_already_running_shows_info(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["tor_path"] = "/tmp/tor"
    monkeypatch.setattr(ks.os.path, "exists", lambda p: True)

    class RunningProc:
        def state(self):
            return ks.QProcess.ProcessState.Running

    tab.tor_process = RunningProc()

    info = {}
    monkeypatch.setattr(
        ks.QMessageBox,
        "information",
        lambda *a, **k: info.setdefault("called", True),
    )

    tab.start_tor()
    assert info.get("called") is True


def test_stop_tor_force_kill_path(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)

    class FakeProc:
        def __init__(self):
            self.terminated = False
            self.killed = False
            self.wait_calls = []

        def terminate(self):
            self.terminated = True

        def waitForFinished(self, timeout):
            self.wait_calls.append(timeout)
            return False

        def kill(self):
            self.killed = True

    tab.tor_process = FakeProc()

    info = {}
    monkeypatch.setattr(
        ks.QMessageBox,
        "information",
        lambda *a, **k: info.setdefault("called", True),
    )

    tab.stop_tor()

    assert info.get("called") is True
    assert tab.tor_process is None


def test_download_tor_exception_restores_ui(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["base_directory"] = str(tmp_path)
    tab.temp_settings["base_folder_name"] = "KDBase"

    monkeypatch.setattr(
        ks.os,
        "makedirs",
        lambda *a, **k: (_ for _ in ()).throw(OSError("boom")),
    )

    finished = []
    tab.download_finished = SimpleNamespace(emit=lambda: finished.append(True))

    warned = {}
    monkeypatch.setattr(
        ks.QMessageBox, "warning", lambda *a, **k: warned.setdefault("called", True)
    )

    tab.download_tor()

    assert warned.get("called") is True
    assert finished
    assert tab.download_tor_button.isEnabled() is True
    assert tab.tor_progress_bar.isVisible() is False


def test_handle_tor_finished_rmtree_error_keeps_data_dir(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)

    data_dir = tmp_path / "tor_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    config = tmp_path / "torrc.conf"
    config.write_text("SocksPort 9050")

    tab.tor_data_dir = str(data_dir)
    tab.tor_config_file = SimpleNamespace(name=str(config))

    real_exists = os.path.exists
    monkeypatch.setattr(
        ks.os.path,
        "exists",
        lambda p: True if p in {str(data_dir), str(config)} else real_exists(p),
    )

    monkeypatch.setattr(
        shutil,
        "rmtree",
        lambda p: (_ for _ in ()).throw(RuntimeError("cannot remove")),
    )

    unlinked = []
    monkeypatch.setattr(ks.os, "unlink", lambda p: unlinked.append(p))

    tab.handle_tor_finished(0, ks.QProcess.ExitStatus.NormalExit)

    assert tab.tor_data_dir == str(data_dir)
    assert str(config) in unlinked
