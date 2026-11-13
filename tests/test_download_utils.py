"""Regression tests for the shared download helpers and the fixes built on them."""

import gzip
import hashlib
import json
import os
import threading
import time
from types import SimpleNamespace

import pytest
from PyQt6.QtWidgets import QTextEdit

from kemonodownloader import domain_config, download_utils
from kemonodownloader.download_utils import (
    ProgressTracker,
    extension_allowed,
    filename_from_url,
    iter_post_files,
    md5_file,
    parse_response_content,
    response_content_length,
    safe_local_filename,
    wait_for_workers,
)
from kemonodownloader.kd_logs import format_log_line


class FakeWorker:
    def __init__(self, alive_checks):
        self.alive_checks = alive_checks

    def is_alive(self):
        self.alive_checks -= 1
        return self.alive_checks > 0


class FakeClock:
    """Each sleep moves time a full minute forward."""

    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, _seconds):
        self.now += 60.0


def test_wait_for_workers_outlasts_any_deadline_while_running(monkeypatch):
    # A large file can download for longer than any fixed deadline; returning
    # early made the GUI report completion and delete the running thread.
    clock = FakeClock()
    monkeypatch.setattr(download_utils, "time", clock)
    worker = FakeWorker(alive_checks=200)

    wait_for_workers([worker], lambda: True)

    assert worker.alive_checks == 0
    assert clock.now >= 199 * 60.0


def test_wait_for_workers_gives_up_after_grace_when_cancelled(monkeypatch):
    clock = FakeClock()
    monkeypatch.setattr(download_utils, "time", clock)
    worker = FakeWorker(alive_checks=10_000)

    wait_for_workers([worker], lambda: False, grace_seconds=120.0)

    assert worker.alive_checks > 9_000


def test_progress_tracker_reports_each_percent_once():
    tracker = ProgressTracker(total_size=1_000_000)
    reported = [tracker.advance(1_000) for _ in range(1_000)]
    updates = [p for p in reported if p is not None]
    assert updates == list(range(0, 101))


def test_progress_tracker_unknown_size_reports_zero_once():
    tracker = ProgressTracker(total_size=0)
    updates = [tracker.advance(10) for _ in range(50)]
    assert [p for p in updates if p is not None] == [0]


def test_content_length_ignored_for_compressed_bodies():
    plain = SimpleNamespace(headers={"content-length": "42"})
    gz = SimpleNamespace(headers={"content-length": "42", "content-encoding": "gzip"})
    bad = SimpleNamespace(headers={"content-length": "abc"})
    assert response_content_length(plain) == 42
    assert response_content_length(gz) == 0
    assert response_content_length(bad) == 0
    assert response_content_length(SimpleNamespace(headers={})) == 0


@pytest.mark.parametrize(
    "name",
    ["..\\..\\evil.exe", "../../evil.exe", "a:b?.png", "con\x00trol.jpg"],
)
def test_safe_local_filename_cannot_escape_folder(name, tmp_path):
    folder = tmp_path / "post"
    safe = safe_local_filename(name)
    target = os.path.normpath(os.path.join(folder, safe))
    assert os.path.dirname(target) == os.path.normpath(folder)
    assert not any(ch in safe for ch in '<>:"/\\|?*\x00')


def test_safe_local_filename_keeps_normal_names():
    assert safe_local_filename("My File (1).png") == "My File (1).png"
    assert safe_local_filename("...") == "unnamed"


def test_filename_from_url():
    assert filename_from_url("https://x/data/ab.png?f=Nice name.png") == "Nice name.png"
    assert filename_from_url("https://x/data/ab.png?token=1") == "ab.png"


def test_md5_file_streams_large_files(tmp_path):
    data = os.urandom(3 * download_utils.HASH_CHUNK_SIZE + 17)
    path = tmp_path / "big.bin"
    path.write_bytes(data)
    assert md5_file(str(path)) == hashlib.md5(data).hexdigest()


def test_parse_response_content_handles_gzip():
    payload = {"post": {"id": "1"}}
    raw = SimpleNamespace(content=json.dumps(payload).encode())
    zipped = SimpleNamespace(content=gzip.compress(json.dumps(payload).encode()))
    assert parse_response_content(raw) == payload
    assert parse_response_content(zipped) == payload


def test_iter_post_files_and_filtering():
    config = domain_config._build_config("kemono.cr")
    post = {
        "file": {"path": "/data/a/main.jpeg", "name": "main.jpeg"},
        "attachments": [{"path": "/data/b/att.zip", "name": "att.zip"}, "junk"],
        "content": '<p><img src="/data/c/inline.png"></p>',
    }
    found = list(iter_post_files(post, config))
    assert [kind for kind, *_ in found] == ["main", "attachment", "content"]
    assert found[0][2] == "https://kemono.cr/data/a/main.jpeg?f=main.jpeg"
    assert list(iter_post_files(post, config, main=False, content=False)) == [found[1]]
    assert extension_allowed(".jpeg", [".jpg"])
    assert not extension_allowed(".png", [".jpg"])


def test_get_domains_never_waits_for_network(monkeypatch):
    release = threading.Event()

    def slow_fetch():
        release.wait(5)
        return None

    monkeypatch.setattr(domain_config, "_domains_cache", None)
    monkeypatch.setattr(domain_config, "_fetch_remote_domains", slow_fetch)
    start = time.monotonic()
    domains = domain_config.get_domains()
    elapsed = time.monotonic() - start
    release.set()

    assert elapsed < 1.0
    assert domains and all("." in d for d in domains)


def test_domain_refresh_rejects_malformed_lists(monkeypatch):
    monkeypatch.setattr(domain_config, "_domains_cache", ["kemono.cr"])
    monkeypatch.setattr(
        domain_config, "_fetch_remote_domains", lambda: ["<html>", "oops"]
    )
    domain_config._refresh_domains()
    assert domain_config._domains_cache == ["kemono.cr"]

    monkeypatch.setattr(
        domain_config, "_fetch_remote_domains", lambda: ["kemono.cr", "new.example"]
    )
    domain_config._refresh_domains()
    assert domain_config._domains_cache == ["kemono.cr", "new.example"]


def test_log_lines_escape_server_text():
    line = format_log_line("Title <b>bold</b> & co", "ERROR")
    assert "color:#FF7A7A" in line
    assert "<b>" not in line
    assert "&lt;b&gt;" in line and "&amp;" in line


def test_logs_window_mirrors_console_without_sharing_its_document(qapp):
    from kemonodownloader.post_downloader import LogsWindow

    console = QTextEdit()
    console.append("first line")
    window = LogsWindow(console)
    try:
        # A shared document is laid out at both widgets' widths in turn,
        # which moved the text under a reader scrolling the window.
        assert window.logs_display.document() is not console.document()
        console.append("second line")
        window.refresh_now()
        assert window.logs_display.toPlainText().splitlines() == [
            "first line",
            "second line",
        ]
    finally:
        window.deleteLater()


def test_post_translate_does_not_repeat_formatted_args():
    from kemonodownloader import post_downloader as pd
    from kemonodownloader.kd_language import language_manager

    text = pd.translate("overall_progress", 0, 5, 0, 1)
    assert text == language_manager.get_text("overall_progress", None, 0, 5, 0, 1)
    assert pd.translate("no_such_key", 7) == "no_such_key: 7"


def test_logs_window_copies_html_from_non_widget_consoles(qapp):
    from kemonodownloader.post_downloader import LogsWindow

    window = LogsWindow(SimpleNamespace(toHtml=lambda: "<b>copied</b>"))
    try:
        assert window.logs_display.toPlainText() == "copied"
    finally:
        window.deleteLater()


def test_creator_filter_reruns_for_text_typed_meanwhile(qapp, monkeypatch):
    from kemonodownloader.creator_downloader import CreatorDownloaderTab

    started = []

    class BusyThread:
        def isRunning(self):
            return True

        def deleteLater(self):
            pass

    tab = SimpleNamespace(
        filter_thread=BusyThread(),
        active_threads=[],
        append_log_to_console=lambda *a, **k: None,
    )
    tab.filter_items = lambda: started.append("rerun")

    CreatorDownloaderTab.filter_items(tab)
    assert tab._filter_rerun_requested is True
    assert started == []

    CreatorDownloaderTab.cleanup_filter_thread(tab)
    assert started == ["rerun"]
    assert tab._filter_rerun_requested is False


def test_creator_list_item_built_once(qapp, monkeypatch):
    from PyQt6.QtWidgets import QCheckBox

    from kemonodownloader import creator_downloader as cd

    made = []
    original_init = QCheckBox.__init__

    def counting_init(self, *args, **kwargs):
        made.append(self)
        original_init(self, *args, **kwargs)

    tab = SimpleNamespace(
        post_url_map={"Post (ID: 1)": ("1", None)},
        creator_post_list=cd.QListWidget(),
        post_widget_cache={},
        toggle_checkbox_state=lambda *_: None,
    )
    monkeypatch.setattr(QCheckBox, "__init__", counting_init)
    cd.CreatorDownloaderTab.add_list_item(tab, "Post (ID: 1)", None, True)

    assert len(made) == 1
    assert tab.post_widget_cache["Post (ID: 1)"][1].check_box is made[0]
