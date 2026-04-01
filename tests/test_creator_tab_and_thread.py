import os
from types import SimpleNamespace

from PyQt6.QtWidgets import QMessageBox, QTextEdit

from kemonodownloader.creator_downloader import (
    CancellationThread,
    CreatorDownloaderTab,
    CreatorDownloadThread,
    ThreadSettings,
)


class _FakeParent:
    def __init__(self, base_path):
        self.cache_folder = os.path.join(base_path, "cache")
        self.other_files_folder = os.path.join(base_path, "other")
        self.download_folder = os.path.join(base_path, "download")


def test_create_thread_settings_defaults(tmp_path):
    parent = _FakeParent(str(tmp_path))
    tab = CreatorDownloaderTab(parent)
    ts = tab._create_thread_settings()
    assert ts.creator_posts_max_attempts == 1
    assert ts.post_data_max_retries == 1
    assert ts.file_download_max_retries == 1
    assert ts.api_request_max_retries == 1
    assert ts.simultaneous_downloads == 1
    assert ts.settings_tab is None


def test_toggle_fast_mode_updates_ui_and_logs(tmp_path):
    parent = _FakeParent(str(tmp_path))
    tab = CreatorDownloaderTab(parent)

    # Enable fast mode (Qt.Checked == 2)
    tab.toggle_fast_mode(2)
    assert tab.fast_mode is True
    # Controls that should be disabled when fast mode is on
    assert not tab.creator_main_check.isEnabled()
    assert not tab.creator_attachments_check.isEnabled()
    assert not tab.creator_content_check.isEnabled()

    # Console should contain the fast mode enabled info
    assert "Fast Mode enabled" in tab.creator_console.toPlainText()


def test_add_multiple_creators_to_queue_and_duplicates_and_invalid(tmp_path):
    parent = _FakeParent(str(tmp_path))
    tab = CreatorDownloaderTab(parent)

    # Prepare multi-line input with: valid, invalid, duplicate
    tab.creator_multi_url_input.setPlainText(
        "https://kemono.cr/a/user/1\nhttps://example.com/bad\nhttps://kemono.cr/a/user/1"
    )
    tab.add_multiple_creators_to_queue()

    # One valid entry should be added, duplicates skipped, invalid counted
    assert len(tab.creator_queue) == 1
    # Input should be cleared after successful add
    assert tab.creator_multi_url_input.toPlainText() == ""
    # Summary message should be logged
    assert "Added 1 link(s) to queue" in tab.creator_console.toPlainText()


def test_create_remove_handler_prompts_and_removes(monkeypatch, tmp_path):
    parent = _FakeParent(str(tmp_path))
    tab = CreatorDownloaderTab(parent)
    tab.creator_queue = [("u1", False), ("u2", False)]
    tab.update_creator_queue_list()

    # Simulate user confirming the removal
    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.QMessageBox.question",
        lambda *a, **k: QMessageBox.StandardButton.Yes,
    )

    handler = tab.create_remove_handler("u1")
    handler()
    assert all(u != "u1" for u, _ in tab.creator_queue)


def test_add_creators_from_file_reads_and_adds(monkeypatch, tmp_path):
    parent = _FakeParent(str(tmp_path))
    tab = CreatorDownloaderTab(parent)

    # Create a temporary file with one valid and one invalid link (and a duplicate)
    file_path = tmp_path / "links.txt"
    file_path.write_text(
        "https://kemono.cr/x/user/42\nnot-a-url\nhttps://kemono.cr/x/user/42\n"
    )

    # Mock the file dialog to return our test file
    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.QFileDialog.getOpenFileName",
        lambda *a, **k: (str(file_path), "Text Files (*.txt);;All Files (*)"),
    )
    # Prevent actual message box from showing
    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.QMessageBox.information",
        lambda *a, **k: None,
    )

    tab.add_creators_from_file()
    assert any("kemono.cr" in u for u, _ in tab.creator_queue)


def test_creator_download_thread_generate_filename_and_folder_and_counters(tmp_path):
    # Setup a simple CreatorDownloadThread and test filename generation
    file_url = "https://kemono.cr/files/123?f=my image.jpg"
    post_id = "1"
    service = "svc"
    creator_id = "42"

    settings = ThreadSettings(1, 1, 1, 1, 1, settings_tab=None)
    console = QTextEdit()
    post_titles_map = {
        (
            service,
            creator_id,
            post_id,
        ): "My Post Title"
    }

    thread = CreatorDownloadThread(
        service,
        creator_id,
        str(tmp_path / "dl"),
        [post_id],
        [file_url],
        {file_url: post_id},
        console,
        str(tmp_path / "other"),
        post_titles_map,
        False,
        settings,
        settings.simultaneous_downloads,
    )

    # Without auto-rename prefix
    target_folder, filename = thread.generate_filename_and_folder(
        file_url,
        str(tmp_path),
        0,
        1,
        post_id,
        post_titles_map[(service, creator_id, post_id)],
    )
    assert filename.endswith(".jpg")
    assert creator_id in target_folder

    # With auto-rename enabled, counters increment
    thread.auto_rename_enabled = True
    target_folder2, filename2 = thread.generate_filename_and_folder(
        file_url,
        str(tmp_path),
        0,
        1,
        post_id,
        post_titles_map[(service, creator_id, post_id)],
    )
    assert filename2.startswith("1_")
    # Second call increments to 2_
    _, filename3 = thread.generate_filename_and_folder(
        file_url,
        str(tmp_path),
        0,
        1,
        post_id,
        post_titles_map[(service, creator_id, post_id)],
    )
    assert filename3.startswith("2_")


def test_get_desc_folder_for_post_respects_strategy(tmp_path):
    file_url = "https://kemono.cr/files/1.jpg"
    settings = ThreadSettings(1, 1, 1, 1, 1, settings_tab=None)
    console = QTextEdit()
    thread = CreatorDownloadThread(
        "svc",
        "42",
        str(tmp_path / "dl"),
        ["1"],
        [file_url],
        {file_url: "1"},
        console,
        str(tmp_path / "other"),
        {},
        False,
        settings,
        settings.simultaneous_downloads,
    )

    # Default (per_post)
    out = thread.get_desc_folder_for_post(str(tmp_path / "creator"), "1", "My Title")
    assert "1_" in out

    # Force single_folder strategy
    fake_settings_tab = SimpleNamespace(
        get_creator_folder_strategy=lambda: "single_folder"
    )
    thread.settings.settings_tab = fake_settings_tab
    out2 = thread.get_desc_folder_for_post(str(tmp_path / "creator"), "1", "My Title")
    assert out2 == os.path.normpath(str(tmp_path / "creator"))

    # Force by_file_type strategy
    fake_settings_tab = SimpleNamespace(
        get_creator_folder_strategy=lambda: "by_file_type"
    )
    thread.settings.settings_tab = fake_settings_tab
    out3 = thread.get_desc_folder_for_post(str(tmp_path / "creator"), "1", "My Title")
    assert out3.endswith(os.path.join("creator", "txt")) or out3.endswith(
        os.path.join("creator", "txt")
    )


def test__download_text_sync_writes_description(monkeypatch, tmp_path):
    # Prepare a fake session/response to avoid network
    class FakeResp:
        status_code = 200

        def json(self):
            return {"content": "<p>Hello world</p>"}

    class FakeSession:
        def get(self, *a, **k):
            return FakeResp()

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session", lambda *a, **k: FakeSession()
    )

    file_url = "https://kemono.cr/files/1.jpg"
    settings = ThreadSettings(1, 1, 1, 1, 1, settings_tab=None)
    console = QTextEdit()
    thread = CreatorDownloadThread(
        "svc",
        "42",
        str(tmp_path / "dl"),
        ["1"],
        [file_url],
        {file_url: "1"},
        console,
        str(tmp_path / "other"),
        {},
        False,
        settings,
        settings.simultaneous_downloads,
    )

    # Run the sync downloader which should write a desc_1.txt file
    post_folder = str(tmp_path / "desc")
    os.makedirs(post_folder, exist_ok=True)
    thread._download_text_sync("1", post_folder)
    desc_path = os.path.join(post_folder, "desc_1.txt")
    assert os.path.exists(desc_path)
    assert "Hello world" in open(desc_path, encoding="utf-8").read()


def test_cancellation_thread_signals_stop_and_emits_logs():
    class Dummy:
        def __init__(self):
            self.stopped = False

        def stop(self):
            self.stopped = True

        def isRunning(self):
            return False

    d1 = Dummy()
    d2 = Dummy()
    ct = CancellationThread([d1, d2])
    logs = []
    ct.log.connect(lambda msg, level: logs.append((msg, level)))
    # Call run() directly (no thread start) to synchronously execute
    ct.run()
    assert d1.stopped and d2.stopped
    assert any("Starting cancellation" in m for m, _ in logs)
