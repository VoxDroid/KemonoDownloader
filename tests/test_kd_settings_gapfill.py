import builtins
import os
from types import SimpleNamespace

from kemonodownloader import kd_settings as ks
from kemonodownloader.kd_settings import DownloadTorThread, SettingsTab


def make_tab(tmp_path):
    parent = SimpleNamespace()
    parent.base_folder = str(tmp_path / "base")
    parent.download_folder = str(tmp_path / "base" / "Downloads")
    parent.cache_folder = str(tmp_path / "base" / "Cache")
    parent.other_files_folder = str(tmp_path / "base" / "Other Files")
    parent.ensure_folders_exist = lambda: None
    parent.post_tab = SimpleNamespace()
    parent.creator_tab = SimpleNamespace()
    parent.log = lambda *_a, **_k: None
    return SettingsTab(parent)


def test_auto_detect_tor_platform_windows_branch(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    monkeypatch.setattr(ks.sys, "platform", "win32")
    monkeypatch.setattr(ks.os.path, "exists", lambda _p: False)

    assert tab.auto_detect_tor() is None


def test_auto_detect_tor_platform_linux_branch(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    monkeypatch.setattr(ks.sys, "platform", "linux")
    monkeypatch.setattr(ks.os.path, "exists", lambda _p: False)

    assert tab.auto_detect_tor() is None


def test_auto_detect_tor_temp_settings_get_exception(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)

    class BadTemp:
        def get(self, _k):
            raise RuntimeError("bad get")

    tab.temp_settings = BadTemp()
    monkeypatch.setattr(ks.os.path, "exists", lambda _p: False)

    assert tab.auto_detect_tor() is None


def test_auto_detect_tor_subprocess_exception_for_direct_file(
    tmp_path, monkeypatch, qapp
):
    tab = make_tab(tmp_path)
    candidate = str(tmp_path / "tor")
    tab.temp_settings["base_directory"] = candidate
    tab.temp_settings["base_folder_name"] = ""

    monkeypatch.setattr(ks.os.path, "exists", lambda p: p == candidate)
    monkeypatch.setattr(ks.os.path, "isfile", lambda p: p == candidate)
    monkeypatch.setattr(ks.os.path, "isdir", lambda _p: False)
    monkeypatch.setattr(
        ks.subprocess,
        "run",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    assert tab.auto_detect_tor() is None


def test_auto_detect_tor_directory_candidate_subprocess_exception(
    tmp_path, monkeypatch, qapp
):
    tab = make_tab(tmp_path)
    base_dir = str(tmp_path / "search")
    tab.temp_settings["base_directory"] = base_dir
    tab.temp_settings["base_folder_name"] = ""

    monkeypatch.setattr(ks.os.path, "exists", lambda p: p == base_dir)
    monkeypatch.setattr(ks.os.path, "isfile", lambda _p: False)
    monkeypatch.setattr(ks.os.path, "isdir", lambda p: p == base_dir)
    monkeypatch.setattr(ks.os, "walk", lambda _p: [(base_dir, [], ["tor"])])
    monkeypatch.setattr(
        ks.subprocess,
        "run",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("bad tor")),
    )

    assert tab.auto_detect_tor() is None


def test_auto_detect_tor_directory_walk_exception(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    base_dir = str(tmp_path / "walk_err")
    tab.temp_settings["base_directory"] = base_dir
    tab.temp_settings["base_folder_name"] = ""

    monkeypatch.setattr(ks.os.path, "exists", lambda p: p == base_dir)
    monkeypatch.setattr(ks.os.path, "isfile", lambda _p: False)
    monkeypatch.setattr(ks.os.path, "isdir", lambda p: p == base_dir)
    monkeypatch.setattr(
        ks.os,
        "walk",
        lambda _p: (_ for _ in ()).throw(RuntimeError("walk fail")),
    )

    assert tab.auto_detect_tor() is None


def test_confirm_and_apply_settings_language_changed(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.settings["language"] = "en_US"
    tab.temp_settings["language"] = "ja_JP"
    tab.temp_settings["base_directory"] = str(tmp_path)
    tab.temp_settings["base_folder_name"] = "KD"

    monkeypatch.setattr(
        ks.QMessageBox,
        "question",
        lambda *a, **k: ks.QMessageBox.StandardButton.Yes,
    )
    monkeypatch.setattr(ks.QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(ks.os.path, "isdir", lambda _p: True)
    monkeypatch.setattr(tab, "save_settings", lambda: None)

    called = {"lang": 0, "emit": 0, "log": 0, "ui": 0}
    monkeypatch.setattr(
        ks.language_manager, "set_language", lambda _v: called.__setitem__("lang", 1)
    )
    tab.language_changed = SimpleNamespace(emit=lambda: called.__setitem__("emit", 1))
    tab.parent.log = lambda *_a, **_k: called.__setitem__("log", 1)
    monkeypatch.setattr(tab, "update_ui_text", lambda: called.__setitem__("ui", 1))

    tab.confirm_and_apply_settings()

    assert called == {"lang": 1, "emit": 1, "log": 1, "ui": 1}


def test_update_ui_text_template_else_branch(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["creator_filename_template"] = "__my_custom_template__"
    monkeypatch.setattr(tab, "update_temp_setting", lambda *_a, **_k: None)

    tab.update_ui_text()

    assert (
        tab.creator_filename_combo.currentIndex()
        == tab.creator_filename_combo.count() - 1
    )


def test_update_ui_text_template_exception_is_ignored(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)

    class BadCombo:
        def blockSignals(self, *_a, **_k):
            raise RuntimeError("combo gone")

    tab.creator_filename_combo = BadCombo()

    tab.update_ui_text()


def test_update_ui_text_folder_strategy_exception_is_ignored(tmp_path, qapp):
    tab = make_tab(tmp_path)

    class BadCombo:
        def currentIndex(self):
            raise RuntimeError("combo gone")

    tab.creator_folder_strategy_combo = BadCombo()

    tab.update_ui_text()


def test_settings_getters_and_is_tor_running(tmp_path, qapp):
    tab = make_tab(tmp_path)

    assert isinstance(tab.get_simultaneous_downloads(), int)
    assert isinstance(tab.is_auto_check_updates_enabled(), bool)
    assert isinstance(tab.get_creator_posts_max_attempts(), int)
    assert isinstance(tab.get_post_data_max_retries(), int)
    assert isinstance(tab.get_file_download_max_retries(), int)
    assert isinstance(tab.get_api_request_max_retries(), int)

    tab.tor_process = SimpleNamespace(state=lambda: ks.QProcess.ProcessState.Running)
    assert tab.is_tor_running() is True


def test_on_use_proxy_changed_sets_tor_default(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["proxy_type"] = "invalid"
    monkeypatch.setattr(tab, "on_proxy_type_changed", lambda *_a, **_k: None)
    monkeypatch.setattr(tab, "save_settings", lambda: None)

    tab.on_use_proxy_changed(ks.Qt.CheckState.Checked.value)

    assert tab.temp_settings["proxy_type"] == "tor"
    assert tab.proxy_type_combo.currentIndex() == 1


def test_test_custom_proxy_non_200_path(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["custom_proxy_url"] = "http://127.0.0.1:9999"

    class Resp:
        status_code = 503

    monkeypatch.setattr("requests.get", lambda *a, **k: Resp())

    warned = {}
    monkeypatch.setattr(
        ks.QMessageBox, "warning", lambda *a, **k: warned.setdefault("ok", True)
    )

    tab.test_custom_proxy()

    assert warned.get("ok") is True


def test_test_custom_proxy_200_path_shows_info(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["custom_proxy_url"] = "http://127.0.0.1:9999"

    class Resp:
        status_code = 200

    monkeypatch.setattr("requests.get", lambda *a, **k: Resp())

    informed = {}
    monkeypatch.setattr(
        ks.QMessageBox,
        "information",
        lambda *a, **k: informed.setdefault("ok", True),
    )

    tab.test_custom_proxy()

    assert informed.get("ok") is True


def test_test_tor_status_non_200_warns(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tor_exe = tmp_path / "tor"
    tor_exe.write_text("tor")
    tab.temp_settings["tor_path"] = str(tor_exe)

    monkeypatch.setattr(ks.os.path, "exists", lambda _p: True)
    monkeypatch.setattr(
        ks.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="Tor 0.4"),
    )

    class Resp:
        status_code = 500

        def json(self):
            return {}

    monkeypatch.setattr("requests.get", lambda *a, **k: Resp())

    warned = {}
    monkeypatch.setattr(
        ks.QMessageBox, "warning", lambda *a, **k: warned.setdefault("ok", True)
    )

    tab.test_tor()

    assert warned.get("ok") is True


def test_test_tor_importerror_branch_info(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tor_exe = tmp_path / "tor"
    tor_exe.write_text("tor")
    tab.temp_settings["tor_path"] = str(tor_exe)

    monkeypatch.setattr(ks.os.path, "exists", lambda _p: True)
    monkeypatch.setattr(
        ks.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="Tor 0.4"),
    )

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "requests":
            raise ImportError("no requests")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    informed = {}
    monkeypatch.setattr(
        ks.QMessageBox,
        "information",
        lambda *a, **k: informed.setdefault("ok", True),
    )

    tab.test_tor()

    assert informed.get("ok") is True


def test_start_tor_not_configured_branch(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["tor_path"] = ""

    warned = {}
    monkeypatch.setattr(
        ks.QMessageBox, "warning", lambda *a, **k: warned.setdefault("ok", True)
    )

    tab.start_tor()

    assert warned.get("ok") is True


def test_stop_tor_rmtree_exception_prints(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)

    class Proc:
        def terminate(self):
            return None

        def waitForFinished(self, _timeout):
            return True

    data_dir = tmp_path / "tor_data"
    data_dir.mkdir(parents=True, exist_ok=True)

    tab.tor_process = Proc()
    tab.tor_data_dir = str(data_dir)

    monkeypatch.setattr(ks.os.path, "exists", lambda _p: True)
    monkeypatch.setattr(
        "shutil.rmtree",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("cannot remove")),
    )

    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **k: printed.append(a))
    monkeypatch.setattr(ks.QMessageBox, "information", lambda *a, **k: None)

    tab.stop_tor()

    assert printed


def test_download_tor_windows_and_macos_intel_branches(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["base_directory"] = str(tmp_path)
    tab.temp_settings["base_folder_name"] = "KD"
    monkeypatch.setattr(ks.QMessageBox, "warning", lambda *a, **k: None)
    monkeypatch.setattr(ks.QMessageBox, "information", lambda *a, **k: None)

    monkeypatch.setattr(
        ks.os,
        "makedirs",
        lambda *_a, **_k: (_ for _ in ()).throw(OSError("stop early")),
    )

    # Windows branch
    monkeypatch.setattr(ks.sys, "platform", "win32")
    tab.download_tor()

    # macOS Intel branch
    monkeypatch.setattr(ks.sys, "platform", "darwin")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")
    tab.download_tor()

    # Linux branch
    monkeypatch.setattr(ks.sys, "platform", "linux")
    tab.download_tor()


def test_update_tor_button_states_running_branch(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    tab.temp_settings["tor_path"] = str(tmp_path / "tor")
    tab.tor_process = SimpleNamespace(state=lambda: ks.QProcess.ProcessState.Running)

    monkeypatch.setattr(ks.os.path, "exists", lambda _p: True)

    tab.update_tor_button_states()

    assert tab.start_tor_button.isEnabled() is False
    assert tab.stop_tor_button.isEnabled() is True


def test_handle_tor_finished_sets_data_dir_none(tmp_path, monkeypatch, qapp):
    tab = make_tab(tmp_path)
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    tab.tor_data_dir = str(data_dir)
    tab.tor_process = object()
    tab.tor_config_file = SimpleNamespace(name=str(tmp_path / "torrc.conf"))

    monkeypatch.setattr(ks.os.path, "exists", lambda _p: True)
    monkeypatch.setattr("shutil.rmtree", lambda *_a, **_k: None)
    monkeypatch.setattr(ks.os, "unlink", lambda *_a, **_k: None)

    tab.handle_tor_finished(0, ks.QProcess.ExitStatus.NormalExit)

    assert tab.tor_data_dir is None


def test_get_proxy_settings_custom_empty_returns_none(tmp_path, qapp):
    tab = make_tab(tmp_path)
    tab.settings["use_proxy"] = True
    tab.settings["proxy_type"] = "custom"
    tab.settings["custom_proxy_url"] = ""

    assert tab.get_proxy_settings() is None


def test_download_tor_thread_commonpath_exception_and_tor_exe_found(
    monkeypatch, tmp_path
):
    # Fake download response
    class Resp:
        status_code = 200
        headers = {"content-length": "4"}

        def iter_content(self, chunk_size=8192):
            yield b"data"

        def raise_for_status(self):
            return None

    monkeypatch.setattr("requests.get", lambda *a, **k: Resp())

    class Member:
        def __init__(self, name):
            self.name = name

    class FakeTar:
        def getmembers(self):
            return [Member("tor/bin/tor")]

        def extract(self, member, path):
            return None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("tarfile.open", lambda *a, **k: FakeTar())

    # Force _is_within_directory exception path.
    monkeypatch.setattr(
        ks.os.path,
        "commonpath",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("bad commonpath")),
    )

    monkeypatch.setattr(ks.os, "unlink", lambda *_a, **_k: None)

    tor_root = str(tmp_path / "tor")
    os.makedirs(tor_root, exist_ok=True)

    # Ensure walk finds tor executable (covers 2068-2075).
    monkeypatch.setattr(ks.os, "walk", lambda _p: [(tor_root, [], ["tor"])])

    t = DownloadTorThread("https://example.com/tor.tar.gz", str(tmp_path), tor_root)
    success = []
    t.finished_success = SimpleNamespace(emit=lambda p: success.append(p))
    t.finished_error = SimpleNamespace(emit=lambda *_a, **_k: None)
    t.progress = SimpleNamespace(emit=lambda *_a, **_k: None)

    t.run()

    assert success
