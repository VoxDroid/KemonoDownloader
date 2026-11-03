"""Tests for the persistent history and favorites store."""

import os
import sqlite3
import time

import pytest

from kemonodownloader.history_store import (
    KIND_CREATOR,
    KIND_POST,
    KIND_THUMBNAIL,
    SCHEMA_VERSION,
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PARTIAL,
    HistoryEntry,
    HistoryStore,
    download_status,
    link_kind,
    normalize_link,
)

POST = "https://kemono.cr/patreon/user/123/post/456"
CREATOR = "https://coomer.st/onlyfans/user/someone"


@pytest.fixture
def store(tmp_path):
    s = HistoryStore(str(tmp_path / "lib"))
    yield s
    s.close()


def entry(**overrides):
    values = dict(
        kind=KIND_POST,
        url=POST + "/",
        title="A post",
        files_total=4,
        files_done=3,
        files_failed=1,
        posts_total=1,
        status=STATUS_PARTIAL,
        started_at=100.0,
        finished_at=160.0,
    )
    values.update(overrides)
    return HistoryEntry(**values)


def test_link_helpers():
    assert normalize_link("  " + POST + "/ ") == POST
    assert link_kind(POST) == KIND_POST
    assert link_kind(CREATOR + "/") == KIND_CREATOR
    assert link_kind(CREATOR + "?o=50") == KIND_CREATOR
    assert link_kind("https://example.com/whatever") is None
    assert link_kind("not a link") is None


def test_download_status():
    assert download_status(3, 3, False) == STATUS_COMPLETED
    assert download_status(3, 1, False) == STATUS_PARTIAL
    assert download_status(3, 0, False) == STATUS_FAILED
    assert download_status(0, 0, False) == STATUS_FAILED
    assert download_status(3, 3, True) == STATUS_CANCELLED


def test_record_round_trip(store):
    entry_id = store.record(entry(extra_urls=[CREATOR + "/"]))
    assert entry_id is not None
    [saved] = store.history()
    assert saved.id == entry_id
    assert saved.url == POST  # normalised
    assert saved.links == [POST, CREATOR]
    assert saved.duration == 60.0
    assert (saved.files_done, saved.files_total, saved.files_failed) == (3, 4, 1)
    assert store.path and os.path.exists(store.path)
    assert store.is_persistent and store.error is None


def test_history_is_newest_first_and_survives_reopen(tmp_path):
    first = HistoryStore(str(tmp_path))
    first.record(entry(title="old", finished_at=10.0))
    first.record(entry(title="new", finished_at=20.0))
    first.close()
    second = HistoryStore(str(tmp_path))
    assert [e.title for e in second.history()] == ["new", "old"]
    assert second._conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    second.close()


def test_recording_can_be_paused_and_is_remembered(tmp_path):
    store = HistoryStore(str(tmp_path))
    assert store.recording_enabled
    store.recording_enabled = False
    assert store.record(entry()) is None
    assert store.history() == []
    store.close()
    reopened = HistoryStore(str(tmp_path))
    assert reopened.recording_enabled is False
    reopened.recording_enabled = True
    assert reopened.record(entry()) is not None
    reopened.close()


def test_delete_and_clear(store):
    ids = [store.record(entry(title=str(i))) for i in range(3)]
    store.delete_history(ids[:2])
    assert [e.title for e in store.history()] == ["2"]
    store.delete_history([])
    store.clear_history()
    assert store.history() == []


def test_revision_changes_on_writes_only(store):
    start = store.revision
    store.history()
    store.favorites()
    assert store.revision == start
    store.record(entry())
    assert store.revision > start


def test_folder_size_is_measured_in_background(store, tmp_path):
    folder = tmp_path / "files"
    (folder / "sub").mkdir(parents=True)
    (folder / "a.bin").write_bytes(b"x" * 1000)
    (folder / "sub" / "b.bin").write_bytes(b"y" * 24)
    store.record(entry(folder=str(folder)))
    deadline = time.monotonic() + 5
    while store.history()[0].size_bytes is None and time.monotonic() < deadline:
        time.sleep(0.02)
    assert store.history()[0].size_bytes == 1024


def test_missing_folder_is_not_measured(store, tmp_path):
    store.record(entry(folder=str(tmp_path / "gone")))
    time.sleep(0.1)
    assert store.history()[0].size_bytes is None


def test_update_folder_remeasures(store, tmp_path):
    entry_id = store.record(entry(folder=str(tmp_path / "gone")))
    moved = tmp_path / "moved"
    moved.mkdir()
    (moved / "f").write_bytes(b"12345")
    store.update_folder(entry_id, str(moved))
    deadline = time.monotonic() + 5
    while store.history()[0].size_bytes is None and time.monotonic() < deadline:
        time.sleep(0.02)
    saved = store.history()[0]
    assert saved.folder == str(moved) and saved.size_bytes == 5


def test_corrupt_database_is_set_aside(tmp_path):
    path = tmp_path / HistoryStore.DB_FILENAME
    path.write_bytes(b"this is not a sqlite database" * 100)
    store = HistoryStore(str(tmp_path))
    assert store.is_persistent and store.error is None
    assert store.record(entry()) is not None
    assert any(name.startswith("library.db.corrupt-") for name in os.listdir(tmp_path))
    store.close()


def test_unwritable_location_falls_back_to_memory(tmp_path):
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("file in the way")
    store = HistoryStore(str(blocker))
    assert not store.is_persistent
    assert store.error
    assert store.record(entry()) is not None
    assert len(store.history()) == 1
    store.close()


def test_closed_store_is_inert(tmp_path):
    store = HistoryStore(str(tmp_path))
    store.close()
    store.close()  # twice is fine
    assert store.record(entry()) is None
    assert store.history() == []
    assert store.favorites() == []


def test_favorites_lifecycle(store):
    assert store.add_favorite(POST + "/", title=" My post ")
    assert not store.add_favorite(POST)  # same link, other spelling
    assert not store.add_favorite("https://example.com/nope")
    assert store.add_favorite(CREATOR)
    assert store.is_favorite(POST + "/")
    favorites = {f.url: f for f in store.favorites()}
    assert favorites[POST].kind == KIND_POST and favorites[POST].title == "My post"
    assert favorites[CREATOR].kind == KIND_CREATOR

    store.update_favorite(favorites[CREATOR].id, title="Them", note="weekly")
    updated = {f.url: f for f in store.favorites()}[CREATOR]
    assert (updated.title, updated.note) == ("Them", "weekly")

    store.remove_favorites([favorites[POST].id])
    store.remove_favorites([])
    assert [f.url for f in store.favorites()] == [CREATOR]


def test_last_downloaded(store):
    store.record(entry(finished_at=50.0))
    store.record(entry(finished_at=90.0))
    store.record(entry(kind=KIND_THUMBNAIL, url=CREATOR, finished_at=70.0))
    assert store.last_downloaded() == {POST: 90.0, CREATOR: 70.0}


def test_sql_errors_are_reported_not_raised(store, monkeypatch):
    class Broken:
        def execute(self, *a, **k):
            raise sqlite3.OperationalError("disk I/O error")

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(store, "_conn", Broken())
    assert store.history() == []
    assert store.record(entry()) is None
    assert "disk I/O error" in store.error
