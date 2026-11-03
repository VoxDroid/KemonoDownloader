"""Tests for the History tab and the download-recording hooks."""

import csv
import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox
from tests.test_app import mock_app_dependencies  # noqa: F401  (fixture)

from kemonodownloader import kd_history
from kemonodownloader.history_store import (
    KIND_CREATOR,
    KIND_POST,
    KIND_THUMBNAIL,
    QUEUE_ADDED,
    QUEUE_BUSY,
    QUEUE_DUPLICATE,
    QUEUE_INVALID,
    QUEUE_MODE_MISMATCH,
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_PARTIAL,
    HistoryEntry,
    HistoryStore,
)
from kemonodownloader.kd_history import (
    FavoritesModel,
    HistoryModel,
    HistoryTab,
    format_duration,
    format_size,
    nearest_existing_folder,
)
from kemonodownloader.kd_language import language_manager

POST = "https://kemono.cr/patreon/user/123/post/456"
POST2 = "https://kemono.cr/patreon/user/123/post/789"
CREATOR = "https://kemono.cr/fanbox/user/999"


class QueueTab:
    def __init__(self, result=QUEUE_ADDED):
        self.result = result
        self.received = []

    def enqueue_from_library(self, url):
        self.received.append(url)
        return self.result


@pytest.fixture
def store(tmp_path):
    s = HistoryStore(str(tmp_path / "lib"))
    yield s
    s.close()


@pytest.fixture
def tab(qapp, store):
    window = SimpleNamespace(
        history_store=store,
        post_tab=QueueTab(),
        creator_tab=QueueTab(),
        thumbnail_tab=QueueTab(),
        tabs=None,
    )
    widget = HistoryTab(window)
    yield widget
    widget.deleteLater()


def select_all(table):
    table.selectAll()


def test_formatting_helpers(tmp_path):
    assert format_size(None) == "—"
    assert format_size(512) == "512 B"
    assert format_size(1536) == "1.5 KB"
    assert format_size(5 * 1024**3) == "5.0 GB"
    assert format_duration(None) == "—"
    assert format_duration(42) == "42s"
    assert format_duration(125) == "2m 05s"
    assert format_duration(3 * 3600 + 60) == "3h 01m"
    deep = tmp_path / "a" / "b" / "c"
    assert nearest_existing_folder(str(deep)) == str(tmp_path)


def test_tables_are_destroyed_before_their_models(tab):
    # Regression: Qt destroys children in the order they were added. Models
    # destroyed before their tables made the tables call into half-destroyed
    # Python objects, which crashed the test suite natively.
    children = tab.children()
    views_at = children.index(tab.views)
    for model in (
        tab.history_model,
        tab.history_proxy,
        tab.favorites_model,
        tab.favorites_proxy,
    ):
        assert model.parent() is tab
        assert children.index(model) > views_at


def test_lists_entries_with_summary_and_empty_state(tab, store, tmp_path):
    assert tab.history_stack.currentWidget() is tab.history_empty
    folder = tmp_path / "done"
    folder.mkdir()
    store.record(
        HistoryEntry(
            kind=KIND_POST,
            url=POST,
            title="First",
            folder=str(folder),
            files_total=2,
            files_done=2,
            posts_total=1,
            posts_done=1,
            status=STATUS_COMPLETED,
            size_bytes=2048,
        )
    )
    store.record(
        HistoryEntry(
            kind=KIND_CREATOR,
            url=CREATOR,
            title="Artist",
            folder=str(tmp_path / "x"),
            files_total=10,
            files_done=7,
            files_failed=3,
            posts_total=4,
            posts_done=2,
            status=STATUS_PARTIAL,
            size_bytes=1024,
        )
    )
    tab.refresh()
    assert tab.history_stack.currentWidget() is tab.history_table
    assert tab.history_model.rowCount() == 2
    summary = tab.summary_label.text()
    for part in ("2", "9", "3", "3.0 KB"):
        assert part in summary

    model = tab.history_model
    rows = {e.title: i for i, e in enumerate(model.entries)}
    artist = model.index(rows["Artist"], HistoryModel.FOLDER)
    first = model.index(rows["First"], HistoryModel.FOLDER)
    assert model.data(artist) == language_manager.get_text("history_folder_missing")
    assert model.data(first) == language_manager.get_text("history_folder_ok")
    assert model.data(model.index(rows["Artist"], HistoryModel.FILES)) == "7/10 (−3)"


def test_filters_by_kind_and_text(tab, store):
    store.record(HistoryEntry(kind=KIND_POST, url=POST, title="Sunset"))
    store.record(
        HistoryEntry(kind=KIND_CREATOR, url=CREATOR, title="Artist", creator="Mika")
    )
    store.record(HistoryEntry(kind=KIND_THUMBNAIL, url=POST2, title="Thumbs"))
    tab.refresh()
    tab.kind_filter.setCurrentIndex(tab.kind_filter.findData(KIND_CREATOR))
    assert tab.history_proxy.rowCount() == 1
    tab.kind_filter.setCurrentIndex(0)
    tab.history_search.setText("mika")
    assert tab.history_proxy.rowCount() == 1
    tab.history_search.setText("")
    assert tab.history_proxy.rowCount() == 3


def test_open_existing_and_missing_folder(tab, store, tmp_path, monkeypatch):
    opened = []
    monkeypatch.setattr(
        kd_history.QDesktopServices,
        "openUrl",
        lambda url: opened.append(url.toLocalFile()),
    )
    folder = tmp_path / "here"
    folder.mkdir()
    entry = HistoryEntry(kind=KIND_POST, url=POST, folder=str(folder))
    tab.open_folder(entry)
    assert os.path.normpath(opened[-1]) == os.path.normpath(str(folder))

    infos = []
    monkeypatch.setattr(
        kd_history.QMessageBox, "information", lambda *a: infos.append(a)
    )
    tab.open_folder(HistoryEntry(kind=KIND_POST, url=POST, folder=""))
    assert infos


def click_button(label):
    def exec_(box):
        for button in box.buttons():
            if button.text() == label:
                button.click()
                return 0
        raise AssertionError(f"no button {label!r}")

    return exec_


def test_missing_folder_locate_parent_and_redownload(tab, store, tmp_path, monkeypatch):
    gone = tmp_path / "creator" / "post_folder"
    (tmp_path / "creator").mkdir()
    entry_id = store.record(HistoryEntry(kind=KIND_POST, url=POST, folder=str(gone)))
    tab.refresh()
    entry = tab.history_model.entries[0]

    new_home = tmp_path / "moved"
    new_home.mkdir()
    monkeypatch.setattr(
        QMessageBox,
        "exec",
        click_button(language_manager.get_text("history_locate_folder")),
    )
    monkeypatch.setattr(
        kd_history.QFileDialog, "getExistingDirectory", lambda *a: str(new_home)
    )
    tab.open_folder(entry)
    assert store.history()[0].folder == str(new_home)
    assert store.history()[0].id == entry_id

    opened = []
    monkeypatch.setattr(
        kd_history.QDesktopServices,
        "openUrl",
        lambda url: opened.append(url.toLocalFile()),
    )
    monkeypatch.setattr(
        QMessageBox,
        "exec",
        click_button(language_manager.get_text("history_open_parent")),
    )
    tab.open_folder(entry)
    assert os.path.normpath(opened[-1]) == os.path.normpath(str(tmp_path / "creator"))

    monkeypatch.setattr(
        QMessageBox,
        "exec",
        click_button(language_manager.get_text("history_redownload")),
    )
    tab.open_folder(entry)
    assert tab.window_ref.post_tab.received == [POST]


def test_copy_queue_and_favorite_from_history(tab, store):
    store.record(HistoryEntry(kind=KIND_POST, url=POST, title="Post"))
    store.record(
        HistoryEntry(
            kind=KIND_THUMBNAIL, url=CREATOR, extra_urls=[POST2], title="Thumbs"
        )
    )
    tab.refresh()
    select_all(tab.history_table)

    tab.copy_history_links()
    assert set(QApplication.clipboard().text().splitlines()) == {POST, CREATOR, POST2}

    tab.queue_history_links()
    window = tab.window_ref
    assert window.post_tab.received == [POST]
    assert window.thumbnail_tab.received == [CREATOR, POST2]  # whole batch
    assert window.creator_tab.received == []
    assert "3" in tab.status_label.text()

    tab.favorite_history_links()
    assert {f.url for f in store.favorites()} == {POST, CREATOR, POST2}
    assert tab.favorites_model.rowCount() == 3


def test_queue_problems_are_reported(tab, store):
    window = tab.window_ref
    window.post_tab.result = QUEUE_BUSY
    window.creator_tab.result = QUEUE_DUPLICATE
    window.thumbnail_tab.result = QUEUE_MODE_MISMATCH
    tab._queue(
        [(POST, False), (CREATOR, False), (POST2, True), ("https://x.y/z", False)]
    )
    text = tab.status_label.text()
    assert language_manager.get_text("history_queue_busy") in text
    assert CREATOR in text
    assert language_manager.get_text("history_queue_mode_mismatch") in text
    assert "https://x.y/z" in text


def test_queue_switches_to_target_tab(tab):
    tabs = MagicMock()
    tabs.indexOf.return_value = 2
    tabs.isTabEnabled.return_value = True
    tab.window_ref.tabs = tabs
    tab._queue([(POST, False)])
    tabs.setCurrentIndex.assert_called_once_with(2)


def test_remove_clear_and_toggle(tab, store, monkeypatch):
    for i in range(3):
        store.record(HistoryEntry(kind=KIND_POST, url=f"{POST}{i}", title=str(i)))
    tab.refresh()
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a: QMessageBox.StandardButton.No
    )
    select_all(tab.history_table)
    tab.remove_history()
    assert len(store.history()) == 3

    monkeypatch.setattr(
        QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Yes
    )
    tab.history_table.selectRow(0)
    tab.remove_history()
    assert len(store.history()) == 2
    tab.clear_history()
    assert store.history() == []
    assert tab.history_stack.currentWidget() is tab.history_empty

    tab.record_check.setChecked(False)
    assert store.recording_enabled is False


def test_export_history_csv(tab, store, tmp_path, monkeypatch):
    store.record(
        HistoryEntry(
            kind=KIND_POST,
            url=POST,
            title="Ünïcode, title",
            files_total=2,
            files_done=2,
        )
    )
    tab.refresh()
    target = tmp_path / "out.csv"
    monkeypatch.setattr(
        kd_history.QFileDialog, "getSaveFileName", lambda *a: (str(target), "")
    )
    tab.export_history()
    with open(target, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[0][0] == "finished_at"
    assert rows[1][2] == "Ünïcode, title" and rows[1][-1] == POST


def test_export_failure_is_shown(tab, store, monkeypatch, tmp_path):
    store.record(HistoryEntry(kind=KIND_POST, url=POST))
    tab.refresh()
    monkeypatch.setattr(
        kd_history.QFileDialog,
        "getSaveFileName",
        lambda *a: (str(tmp_path / "no" / "such" / "dir" / "x.csv"), ""),
    )
    errors = []
    monkeypatch.setattr(kd_history.QMessageBox, "critical", lambda *a: errors.append(a))
    tab.export_history()
    assert errors


def test_favorites_add_edit_queue_and_remove(tab, store, monkeypatch):
    tab.favorite_input.setText("not a link")
    tab.add_favorite_from_input()
    assert store.favorites() == []

    tab.favorite_input.setText(CREATOR + "/")
    tab.add_favorite_from_input()
    assert [f.url for f in store.favorites()] == [CREATOR]
    assert tab.favorite_input.text() == ""

    tab.favorite_input.setText(CREATOR)
    tab.add_favorite_from_input()
    assert tab.favorite_input.text() == CREATOR  # kept: already saved

    model = tab.favorites_model
    title = model.index(0, FavoritesModel.TITLE)
    assert model.flags(title) & kd_history.Qt.ItemFlag.ItemIsEditable
    assert model.setData(title, "  Renamed ")
    assert not model.setData(model.index(0, FavoritesModel.LINK), "x")
    assert store.favorites()[0].title == "Renamed"

    tab.favorites_table.selectRow(0)
    tab.queue_favorite_links()
    assert tab.window_ref.creator_tab.received == [CREATOR]

    monkeypatch.setattr(
        QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Yes
    )
    tab.remove_favorites()
    assert store.favorites() == []


def test_favorites_import_export(tab, store, tmp_path, monkeypatch):
    source = tmp_path / "links.txt"
    source.write_text(f"{POST}\n\nnot a link\n{CREATOR}/\n{POST}\n", encoding="utf-8")
    monkeypatch.setattr(
        kd_history.QFileDialog, "getOpenFileName", lambda *a: (str(source), "")
    )
    tab.import_favorites()
    assert {f.url for f in store.favorites()} == {POST, CREATOR}
    assert (
        language_manager.get_text("favorites_imported", None, 2, 2)
        in tab.status_label.text()
    )

    target = tmp_path / "out.txt"
    monkeypatch.setattr(
        kd_history.QFileDialog, "getSaveFileName", lambda *a: (str(target), "")
    )
    tab.export_favorites()
    assert set(target.read_text(encoding="utf-8").split()) == {POST, CREATOR}


def test_last_downloaded_column(tab, store):
    store.add_favorite(POST)
    store.record(HistoryEntry(kind=KIND_POST, url=POST, finished_at=1_700_000_000))
    tab.refresh()
    cell = tab.favorites_model.index(0, FavoritesModel.LAST)
    assert tab.favorites_model.data(cell) == kd_history.format_time(1_700_000_000)


def test_picks_up_background_changes(tab, store):
    store.record(HistoryEntry(kind=KIND_POST, url=POST))
    assert tab.history_model.rowCount() == 0
    tab._refresh_if_changed()
    assert tab.history_model.rowCount() == 1


def test_storage_warning_and_translation(qapp, tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x")
    store = HistoryStore(str(blocker))
    window = SimpleNamespace(history_store=store)
    widget = HistoryTab(window)
    try:
        assert not widget.storage_warning.isHidden()
        original = language_manager.get_language()
        language_manager.set_language("japanese")
        try:
            widget.update_ui_text()
            header = widget.history_model.headerData(
                HistoryModel.STATUS, kd_history.Qt.Orientation.Horizontal
            )
            assert header == "状態"
        finally:
            language_manager.set_language(original)
            widget.update_ui_text()
    finally:
        widget.deleteLater()
        store.close()


# ----------------------------------------------------------------------------
# Hooks in the downloader tabs
# ----------------------------------------------------------------------------


def test_post_tab_records_download(store, tmp_path):
    from kemonodownloader.post_downloader import PostDownloaderTab

    owner = SimpleNamespace(
        parent=SimpleNamespace(history_store=store), failed_files={"u3"}
    )
    thread = SimpleNamespace(
        selected_files=["u1", "u2", "u3"],
        completed_files={"u1", "u2"},
        url=POST,
        download_folder=str(tmp_path),
        service="patreon",
        post_id="456",
        post_title="Nice_Post",
        started_at=1.0,
    )
    PostDownloaderTab._record_download(owner, thread)
    PostDownloaderTab._record_download(owner, thread)  # recorded once only
    [saved] = store.history()
    assert saved.kind == KIND_POST and saved.status == STATUS_PARTIAL
    assert (saved.files_done, saved.files_total, saved.files_failed) == (2, 3, 1)
    assert saved.folder == os.path.join(str(tmp_path), "patreon", "456_Nice_Post")
    assert saved.creator == "123"

    cancelled = SimpleNamespace(**{**vars(thread), "_history_recorded": False})
    PostDownloaderTab._record_download(owner, cancelled, cancelled=True)
    assert store.history()[0].status == STATUS_CANCELLED

    # Mock windows (as in many tests) are ignored.
    PostDownloaderTab._record_download(
        SimpleNamespace(parent=MagicMock()), SimpleNamespace()
    )


def test_post_tab_cleanup_records_real_thread(qapp, store, tmp_path):
    from kemonodownloader.post_downloader import DownloadThread, PostDownloaderTab

    parent = MagicMock()
    parent.history_store = store
    tab = PostDownloaderTab(parent)
    try:
        settings = SimpleNamespace(api_request_max_retries=1, settings_tab=None)
        thread = DownloadThread(
            POST,
            str(tmp_path),
            ["f1"],
            {"f1": "456"},
            None,
            str(tmp_path / "o"),
            "456",
            settings,
        )
        thread.post_title = "T"
        thread.completed_files.add("f1")
        tab.cleanup_thread(thread, [])
        assert store.history()[0].status == STATUS_COMPLETED
    finally:
        tab.deleteLater()


def fake_queue_owner(**extra):
    owner = SimpleNamespace(
        downloading=False,
        post_queue=[],
        creator_queue=[],
        update_post_queue_list=MagicMock(),
        update_creator_queue_list=MagicMock(),
        append_log_to_console=MagicMock(),
        download_all_links=MagicMock(isChecked=lambda: False),
        check_all_posts=MagicMock(),
        post_detection_thread=None,
    )
    for key, value in extra.items():
        setattr(owner, key, value)
    return owner


def test_post_tab_enqueue_from_library():
    from kemonodownloader.post_downloader import PostDownloaderTab

    owner = fake_queue_owner()
    assert PostDownloaderTab.enqueue_from_library(owner, POST + "/") == QUEUE_ADDED
    assert owner.post_queue == [(POST, False)]
    assert PostDownloaderTab.enqueue_from_library(owner, POST) == QUEUE_DUPLICATE
    assert PostDownloaderTab.enqueue_from_library(owner, CREATOR) == QUEUE_INVALID
    owner.downloading = True
    assert PostDownloaderTab.enqueue_from_library(owner, POST2) == QUEUE_BUSY


def test_creator_tab_records_and_enqueues(store, tmp_path):
    from kemonodownloader.creator_downloader import CreatorDownloaderTab

    owner = fake_queue_owner(_parent=SimpleNamespace(history_store=store))
    owner._is_fetching = lambda: CreatorDownloaderTab._is_fetching(owner)
    thread = SimpleNamespace(
        files_to_download=["a", "b", "c"],
        completed_files={"a", "b", "c"},
        failed_files={},
        post_files_map={"1": ["a", "b"], "2": ["c"], "3": []},
        selected_posts=["1", "2", "3"],
        creator_name="Artist",
        creator_id="999",
        service="fanbox",
        download_folder=str(tmp_path),
        is_running=True,
        domain_config={"base_url": "https://kemono.cr"},
        source_url=CREATOR,
    )
    CreatorDownloaderTab._record_download(owner, thread)
    [saved] = store.history()
    assert saved.status == STATUS_COMPLETED and saved.posts_done == 2
    assert saved.folder == os.path.join(str(tmp_path), "999_Artist")

    early = SimpleNamespace(
        **{
            **vars(thread),
            "creator_name": None,
            "is_running": False,
            "_history_recorded": False,
        }
    )
    del early.source_url
    CreatorDownloaderTab._record_download(owner, early)
    latest = store.history()[0]
    assert latest.status == STATUS_CANCELLED and latest.folder == ""
    assert latest.url == CREATOR

    assert CreatorDownloaderTab.enqueue_from_library(owner, CREATOR) == QUEUE_ADDED
    assert (
        CreatorDownloaderTab.enqueue_from_library(owner, CREATOR + "/")
        == QUEUE_DUPLICATE
    )
    assert CreatorDownloaderTab.enqueue_from_library(owner, POST) == QUEUE_INVALID
    owner.post_detection_thread = MagicMock(isRunning=lambda: True)
    assert CreatorDownloaderTab.enqueue_from_library(owner, CREATOR + "x") == QUEUE_BUSY


def test_thumbnail_tab_records_and_enqueues(qapp, store, tmp_path):
    from kemonodownloader.kd_thumbnaildl import ThumbnailDownloaderTab

    parent = MagicMock()
    parent.history_store = store
    tab = ThumbnailDownloaderTab(parent)
    try:
        tab.download_thread = SimpleNamespace(
            download_items=[
                ("t", "1", ["u"], "fanbox", "999", "Artist", "kemono.cr"),
                ("t2", "2", ["v"], "fanbox", "999", "Artist", "kemono.cr"),
            ],
            save_dir=str(tmp_path / "Thumbnails"),
            is_cancelled=False,
            isRunning=lambda: False,
        )
        tab._history_sources = [CREATOR, POST]
        tab._record_download(3, 4)
        [saved] = store.history()
        assert saved.kind == KIND_THUMBNAIL and saved.status == STATUS_PARTIAL
        assert saved.links == [CREATOR, POST]
        assert saved.posts_total == 2
        assert saved.folder == os.path.join(str(tmp_path / "Thumbnails"), "999_Artist")

        tab.download_thread = None
        assert tab.enqueue_from_library(CREATOR) == QUEUE_ADDED
        assert tab.get_current_mode() == "creator"  # switched: queue was empty
        assert tab.enqueue_from_library(CREATOR + "/") == QUEUE_DUPLICATE
        assert tab.enqueue_from_library(POST) == QUEUE_MODE_MISMATCH
        assert tab.enqueue_from_library("https://example.com") == QUEUE_INVALID
    finally:
        tab.deleteLater()


def test_bookmark_buttons(store):
    from kemonodownloader.creator_downloader import CreatorDownloaderTab
    from kemonodownloader.post_downloader import PostDownloaderTab

    logs = []
    post_owner = SimpleNamespace(
        parent=SimpleNamespace(history_store=store),
        post_url_input=MagicMock(text=lambda: ""),
        current_post_url=None,
        append_log_to_console=lambda msg, level: logs.append(level),
    )
    PostDownloaderTab.bookmark_current_link(post_owner)
    assert logs[-1] == "WARNING" and store.favorites() == []

    post_owner.current_post_url = POST
    PostDownloaderTab.bookmark_current_link(post_owner)
    assert store.is_favorite(POST) and logs[-1] == "INFO"
    PostDownloaderTab.bookmark_current_link(post_owner)
    assert logs[-1] == "WARNING"  # already saved

    post_owner.post_url_input = MagicMock(text=lambda: "https://example.com/x")
    PostDownloaderTab.bookmark_current_link(post_owner)
    assert logs[-1] == "ERROR"

    creator_owner = SimpleNamespace(
        _parent=SimpleNamespace(history_store=store),
        creator_url_input=MagicMock(text=lambda: CREATOR),
        current_creator_url=None,
        append_log_to_console=lambda msg, level: logs.append(level),
    )
    CreatorDownloaderTab.bookmark_current_link(creator_owner)
    assert store.is_favorite(CREATOR)


def test_app_has_history_tab_and_labels_by_widget(
    qapp, mock_app_dependencies, monkeypatch  # noqa: F811
):
    # The fixture must be a parameter: importing it inside the test does not
    # apply it, and the window would read real settings and check for updates.
    from kemonodownloader.app import KemonoDownloader

    monkeypatch.setattr(os, "makedirs", MagicMock())
    window = KemonoDownloader()
    try:
        assert isinstance(window.history_store, HistoryStore)
        window.transition_to_main()
        index = window.tabs.indexOf(window.history_tab)
        assert index == 3
        window.tabs.setTabText(index, "stale")
        window.update_all_ui()
        # The fixture stubs translate() to return the key.
        assert window.tabs.tabText(index) == "history_tab"
    finally:
        window.deleteLater()
