"""History and favorites must survive a restart (issue #98).

They are lost when the library file moves out from under them: when the save
folder changes, when a temporarily locked file is mistaken for a damaged one,
and when a file that couldn't be opened at launch is never retried.
"""

import os
import sqlite3
import time
from types import SimpleNamespace

import pytest

from kemonodownloader import history_store as hs
from kemonodownloader.history_store import (
    KIND_CREATOR,
    KIND_POST,
    HistoryEntry,
    HistoryStore,
)

POST = "https://kemono.cr/patreon/user/123/post/456"
POST_2 = "https://kemono.cr/patreon/user/123/post/789"
CREATOR = "https://coomer.st/onlyfans/user/someone"


def entry(url=POST, finished_at=160.0, **overrides):
    return HistoryEntry(
        kind=KIND_POST, url=url, title="A post", finished_at=finished_at, **overrides
    )


def reopen(directory):
    """What the next launch sees."""
    store = HistoryStore(str(directory))
    try:
        return (
            [f.url for f in store.favorites()],
            [(e.url, e.finished_at) for e in store.history()],
            store.recording_enabled,
        )
    finally:
        store.close()


def wait_for(condition, timeout=5.0):
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() > deadline:
            return False
        time.sleep(0.02)
    return True


# --------------------------------------------------------- save folder moves


def test_relocate_brings_the_library_to_the_new_folder(tmp_path):
    old, new = tmp_path / "old" / "Other Files", tmp_path / "new" / "Other Files"
    store = HistoryStore(str(old))
    store.add_favorite(CREATOR, "Someone", "note")
    store.record(entry())
    assert store.relocate(str(new))
    assert store.path == os.path.join(str(new), HistoryStore.DB_FILENAME)
    # Saved after the move: lands in the new file, not the old one.
    store.add_favorite(POST_2)
    store.close()

    favorites, history, _ = reopen(new)
    assert sorted(favorites) == sorted([CREATOR, POST_2])
    assert history == [(POST, 160.0)]
    # The old file is left as it was, never deleted.
    old_favorites, old_history, _ = reopen(old)
    assert old_favorites == [CREATOR] and old_history == [(POST, 160.0)]


def test_relocate_keeps_titles_notes_and_the_recording_switch(tmp_path):
    store = HistoryStore(str(tmp_path / "a"))
    store.add_favorite(CREATOR, "Someone", "a note")
    store.recording_enabled = False
    store.relocate(str(tmp_path / "b"))
    store.close()
    moved = HistoryStore(str(tmp_path / "b"))
    try:
        favorite = moved.favorites()[0]
        assert (favorite.title, favorite.note) == ("Someone", "a note")
        assert moved.recording_enabled is False
    finally:
        moved.close()


def test_relocate_merges_with_a_library_already_there(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    earlier = HistoryStore(str(b))
    earlier.add_favorite(POST_2)
    earlier.record(entry(url=POST_2, finished_at=50.0))
    earlier.close()

    store = HistoryStore(str(a))
    store.add_favorite(CREATOR)
    store.record(entry())
    assert store.relocate(str(b))
    # Switching back and forth must not duplicate anything.
    assert store.relocate(str(a))
    assert store.relocate(str(b))
    store.close()

    favorites, history, _ = reopen(b)
    assert sorted(favorites) == sorted([CREATOR, POST_2])
    assert sorted(history) == sorted([(POST_2, 50.0), (POST, 160.0)])


def test_relocate_to_the_same_folder_changes_nothing(tmp_path):
    store = HistoryStore(str(tmp_path))
    store.add_favorite(CREATOR)
    revision = store.revision
    assert store.relocate(str(tmp_path) + os.sep)
    assert store.revision == revision
    assert [f.url for f in store.favorites()] == [CREATOR]
    store.close()


def test_relocate_failure_keeps_the_current_library(tmp_path):
    store = HistoryStore(str(tmp_path / "lib"))
    store.add_favorite(CREATOR)
    blocker = tmp_path / "file_in_the_way"
    blocker.write_text("x")
    assert not store.relocate(str(blocker))
    assert store.error
    assert store.is_persistent  # still saving to the old file
    store.add_favorite(POST_2)
    store.close()
    favorites, _, _ = reopen(tmp_path / "lib")
    assert sorted(favorites) == sorted([CREATOR, POST_2])


def test_closed_store_does_not_relocate(tmp_path):
    store = HistoryStore(str(tmp_path / "a"))
    store.close()
    assert not store.relocate(str(tmp_path / "b"))


def test_folder_sizes_follow_the_library(tmp_path):
    folder = tmp_path / "downloads" / "post"
    folder.mkdir(parents=True)
    (folder / "file.bin").write_bytes(b"12345")
    store = HistoryStore(str(tmp_path / "a"))
    store.record(entry(folder=str(folder)))
    assert wait_for(lambda: store.history()[0].size_bytes == 5)
    store.relocate(str(tmp_path / "b"))
    assert store.history()[0].size_bytes == 5
    store.close()


def test_unknown_sizes_are_measured_after_a_move(tmp_path):
    folder = tmp_path / "post"
    folder.mkdir()
    (folder / "f").write_bytes(b"1234567")
    # An entry whose size was never measured (the app closed first).
    earlier = HistoryStore(str(tmp_path / "b"))
    earlier._conn.execute(
        "INSERT INTO history (kind, url, folder, status, finished_at) "
        "VALUES (?, ?, ?, 'completed', 1)",
        (KIND_POST, POST_2, str(folder)),
    )
    earlier._conn.commit()
    earlier.close()
    store = HistoryStore(str(tmp_path / "a"))
    store.relocate(str(tmp_path / "b"))
    assert wait_for(lambda: store.history()[0].size_bytes == 7)
    store.close()


def test_a_size_measured_for_the_old_file_is_not_written_to_the_new_one(tmp_path):
    folder = tmp_path / "post"
    folder.mkdir()
    (folder / "f").write_bytes(b"123")
    store = HistoryStore(str(tmp_path / "a"))
    # Ids differ between the files: here the old row 1 becomes row 2.
    target = HistoryStore(str(tmp_path / "b"))
    target.record(entry(url=POST_2, finished_at=10.0))
    target.close()
    first = store.record(entry())
    stale_generation = store._generation
    store.relocate(str(tmp_path / "b"))
    store._measure_folder(first, str(folder), stale_generation)
    sizes = {e.url: e.size_bytes for e in store.history()}
    assert sizes == {POST_2: None, POST: None}
    store.close()


# ------------------------------------------------ locked or unreadable files


def test_a_locked_library_is_not_set_aside(tmp_path, monkeypatch):
    saved = HistoryStore(str(tmp_path))
    saved.add_favorite(CREATOR)
    saved.close()
    real_connect = HistoryStore._connect

    def locked(path):
        if path != ":memory:":
            raise sqlite3.OperationalError("database is locked")
        return real_connect(path)

    monkeypatch.setattr(HistoryStore, "_connect", staticmethod(locked))
    store = HistoryStore(str(tmp_path))
    assert not store.is_persistent
    assert "locked" in (store.error or "")
    store.close()
    monkeypatch.setattr(HistoryStore, "_connect", staticmethod(real_connect))
    assert not [n for n in os.listdir(tmp_path) if ".corrupt-" in n]
    favorites, _, _ = reopen(tmp_path)
    assert favorites == [CREATOR]


def test_a_damaged_library_is_still_set_aside(tmp_path):
    (tmp_path / HistoryStore.DB_FILENAME).write_bytes(b"not a database" * 100)
    store = HistoryStore(str(tmp_path))
    assert store.is_persistent
    assert [n for n in os.listdir(tmp_path) if ".corrupt-" in n]
    store.close()


def test_a_library_locked_at_launch_is_saved_once_it_opens(tmp_path, monkeypatch):
    real_connect = HistoryStore._connect
    locked = {"on": True}

    def connect(path):
        if path != ":memory:" and locked["on"]:
            raise sqlite3.OperationalError("database is locked")
        return real_connect(path)

    monkeypatch.setattr(HistoryStore, "_connect", staticmethod(connect))
    monkeypatch.setattr(HistoryStore, "REOPEN_INTERVAL", 0.0)
    store = HistoryStore(str(tmp_path))
    store.add_favorite(CREATOR)  # still locked: kept in memory
    assert not store.is_persistent
    locked["on"] = False
    store.record(entry())  # the next write reconnects and saves both
    assert store.is_persistent and store.error is None
    store.close()
    favorites, history, _ = reopen(tmp_path)
    assert favorites == [CREATOR]
    assert history == [(POST, 160.0)]


def test_reconnecting_is_not_retried_on_every_write(tmp_path, monkeypatch):
    real_connect = HistoryStore._connect
    attempts = []

    def connect(path):
        if path != ":memory:":
            attempts.append(path)
            raise sqlite3.OperationalError("database is locked")
        return real_connect(path)

    monkeypatch.setattr(HistoryStore, "_connect", staticmethod(connect))
    store = HistoryStore(str(tmp_path))
    for _ in range(20):
        store.add_favorite(CREATOR)
    store.close()
    assert len(attempts) == 1  # the launch only; retries wait REOPEN_INTERVAL


def test_copy_library_rolls_back_on_failure(tmp_path):
    source = HistoryStore._connect(":memory:")
    source.execute(
        "INSERT INTO favorites (url, kind, title, note, added_at) "
        "VALUES (?, ?, '', '', 1)",
        (CREATOR, KIND_CREATOR),
    )
    target = HistoryStore._connect(str(tmp_path / "t.db"))
    target.execute("DROP TABLE meta")  # make the last step fail
    with pytest.raises(sqlite3.Error):
        hs._copy_library(source, target)
    assert target.execute("SELECT COUNT(*) FROM favorites").fetchone()[0] == 0
    source.close()
    target.close()


# --------------------------------------------------------- the app around it


@pytest.fixture
def settings_tab(qapp):
    from kemonodownloader.kd_settings import SettingsTab

    tab = SettingsTab(SimpleNamespace(log=lambda m: None))
    yield tab
    tab.deleteLater()


def test_applying_a_new_save_folder_moves_the_library(settings_tab, tmp_path):
    store = HistoryStore(str(tmp_path / "old" / "Other Files"))
    store.add_favorite(CREATOR)
    tabs = {
        name: SimpleNamespace(cache_dir="old", other_files_dir="old")
        for name in ("post_tab", "creator_tab", "thumbnail_tab")
    }
    new = tmp_path / "new"
    settings_tab.parent = SimpleNamespace(
        history_store=store,
        cache_folder=str(new / "Cache"),
        other_files_folder=str(new / "Other Files"),
        **tabs,
    )
    settings_tab._move_to_new_folder()
    store.close()
    for tab in tabs.values():
        assert tab.cache_dir == str(new / "Cache")
        assert tab.other_files_dir == str(new / "Other Files")
    assert reopen(new / "Other Files")[0] == [CREATOR]


def test_a_failed_move_is_explained(settings_tab, tmp_path, monkeypatch):
    from kemonodownloader import kd_settings

    shown = []
    monkeypatch.setattr(
        kd_settings.QMessageBox, "warning", lambda *a, **k: shown.append(a)
    )
    store = HistoryStore(str(tmp_path / "lib"))
    blocker = tmp_path / "file_in_the_way"
    blocker.write_text("x")
    settings_tab.parent = SimpleNamespace(
        history_store=store,
        cache_folder=str(tmp_path / "Cache"),
        other_files_folder=str(blocker),
    )
    settings_tab._move_to_new_folder()
    store.close()
    assert len(shown) == 1
    assert str(blocker) in shown[0][2]


def test_bookmarks_survive_a_restart_after_changing_the_save_folder(
    qapp, tmp_path, monkeypatch
):
    """The whole #98 flow in the real window: bookmark, change folder, reopen."""
    from kemonodownloader import app as kd_app, kd_settings

    yes = kd_settings.QMessageBox.StandardButton.Yes
    monkeypatch.setattr(kd_settings.QMessageBox, "question", lambda *a, **k: yes)
    monkeypatch.setattr(kd_settings.QMessageBox, "information", lambda *a, **k: None)
    warnings = []
    monkeypatch.setattr(
        kd_settings.QMessageBox, "warning", lambda *a, **k: warnings.append(a)
    )
    monkeypatch.setattr(kd_app.KemonoDownloader, "check_for_updates", lambda s: None)

    first = kd_app.KemonoDownloader()
    try:
        first.setup_main_ui()
        settings = first.settings_tab
        first.post_tab.post_url_input.setText(POST)
        first.post_tab.bookmark_current_link()
        settings.update_temp_setting("base_directory", str(tmp_path / "elsewhere"))
        settings.confirm_and_apply_settings()
        first.post_tab.post_url_input.setText(POST_2)
        first.post_tab.bookmark_current_link()
        first.history_store.close()  # what main() does on exit
    finally:
        first.deleteLater()

    second = kd_app.KemonoDownloader()
    try:
        assert second.settings_tab.settings["base_directory"] == str(
            tmp_path / "elsewhere"
        )
        assert sorted(f.url for f in second.history_store.favorites()) == sorted(
            [POST, POST_2]
        )
        assert not warnings
    finally:
        second.history_store.close()
        second.settings_tab.qsettings.remove("base_directory")
        second.settings_tab.qsettings.sync()
        second.deleteLater()


def test_history_tab_warning_clears_once_the_file_opens(qapp, tmp_path, monkeypatch):
    from kemonodownloader.kd_history import HistoryTab

    blocker = tmp_path / "lib"
    blocker.write_text("a file where the folder should be")
    monkeypatch.setattr(HistoryStore, "REOPEN_INTERVAL", 0.0)
    store = HistoryStore(str(blocker))
    tab = HistoryTab(SimpleNamespace(history_store=store))
    try:
        assert not tab.storage_warning.isHidden()
        blocker.unlink()
        store.add_favorite(CREATOR)
        assert store.is_persistent
        tab._refresh_if_changed()
        assert tab.storage_warning.isHidden()
    finally:
        tab.deleteLater()
        store.close()
