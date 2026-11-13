"""Extras around preview-only and missing files: filters, direct servers,
saving previews, the missing-files window and History counts."""

import asyncio
import csv
import hashlib
import io
import os
import sqlite3
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import requests
from PyQt6.QtWidgets import QCheckBox

import kemonodownloader.creator_downloader as cd
import kemonodownloader.post_downloader as pd
from kemonodownloader import download_utils as du
from kemonodownloader.domain_config import get_domain_config
from kemonodownloader.history_store import (
    KIND_POST,
    SCHEMA_VERSION,
    HistoryEntry,
    HistoryStore,
)
from kemonodownloader.kd_preview_notice import MissingFilesNotice, PreviewOnlyNotice

PAW = get_domain_config("https://pawchive.pw/patreon/user/1/post/2")
ZIP_PATH = (
    "/118/1d/181dd6c41d920a2066e9cd56a6c6a03b4023f7c46bdf8bc77ddd60955ec0b44f.zip"
)


def entry(**kw):
    base = dict(
        kind="attachment",
        name="frankie.zip",
        url=f"https://file.pawchive.pw/data{ZIP_PATH}?f=frankie.zip",
        extension=".zip",
        preview_only=False,
        path=ZIP_PATH,
        server="https://n3.pawchive.pw",
    )
    base.update(kw)
    return du.PostFile(**base)


def response(url, status=200, body=b""):
    r = requests.models.Response()
    r.status_code = status
    r.url = url
    r.reason = "OK" if status == 200 else "Not Found"
    r.headers["content-length"] = str(len(body))
    r.raw = io.BytesIO(body)
    return r


# --- 1: type filters ------------------------------------------------------


def test_checked_extensions_reads_checkboxes_and_booleans(qapp):
    on, off = QCheckBox(), QCheckBox()
    on.setChecked(True)
    assert du.checked_extensions({".JPG": on, ".png": off}) == [".jpg"]
    assert du.checked_extensions({".zip": True, ".mp4": False}) == [".zip"]


def test_post_preparation_honours_unticked_types(qapp):
    zip_box, png_box = QCheckBox(), QCheckBox()
    zip_box.setChecked(True)  # PNG left unticked
    thread = pd.FilePreparationThread(
        [], {}, {".zip": zip_box, ".png": png_box}, {}, PAW["base_url"], MagicMock()
    )
    # It used to test the checkbox object itself, which is always true.
    assert thread.allowed_extensions == [".zip"]


# --- 5: direct media servers ----------------------------------------------


def test_direct_download_url_uses_the_named_server():
    assert du.direct_download_url(entry(), PAW) == (
        f"https://n3.pawchive.pw/data{ZIP_PATH}?f=frankie.zip"
    )


@pytest.mark.parametrize(
    "server",
    [
        "",
        "http://n3.pawchive.pw",  # not https
        "https://n3.example.com",  # another site
        "https://pawchive.pw.evil.com",
        "https://n3.pawchive.pw:8443",  # unexpected port
        "https://n3.pawchive.pw/other",  # unexpected path
    ],
)
def test_direct_download_url_rejects_untrusted_servers(server):
    assert du.direct_download_url(entry(server=server), PAW) is None


def test_direct_url_registry():
    du.remember_direct_url("u", "d")
    assert du.direct_url_for("u") == "d"
    du.forget_direct_url("u")
    assert du.direct_url_for("u") is None


def test_preparation_remembers_direct_urls():
    post = {
        "id": "1",
        "title": "T",
        "attachments": [
            {
                "name": "frankie.zip",
                "path": ZIP_PATH,
                "server": "https://n3.pawchive.pw",
            }
        ],
    }
    thread = pd.FilePreparationThread([], {}, {}, {}, PAW["base_url"], MagicMock())
    [(name, url)] = thread.detect_files(post, [".zip"])
    assert du.direct_url_for(url).startswith("https://n3.pawchive.pw/data/")
    du.forget_direct_url(url)


class Session:
    def __init__(self, handler):
        self.handler = handler
        self.urls = []

    def get(self, url, **kwargs):
        self.urls.append(url)
        return self.handler(url)


def post_thread(tmp_path, file_url, retries):
    thread = pd.DownloadThread(
        url="https://pawchive.pw/patreon/user/1/post/2",
        download_folder=str(tmp_path / "dl"),
        selected_files=[file_url],
        files_to_posts_map={file_url: "2"},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_id="2",
        settings=SimpleNamespace(file_download_max_retries=retries, settings_tab=None),
        max_concurrent=1,
        auto_rename=False,
        download_text=False,
    )
    for name in ("file_progress", "file_completed", "log"):
        setattr(thread, name, SimpleNamespace(calls=[], emit=None))
        signal = getattr(thread, name)
        signal.emit = lambda *a, s=signal: s.calls.append(a)
    return thread


def test_post_download_requests_the_direct_server(tmp_path, monkeypatch):
    canonical = f"https://file.pawchive.pw/data{ZIP_PATH}?f=frankie.zip"
    direct = f"https://n3.pawchive.pw/data{ZIP_PATH}?f=frankie.zip"
    du.remember_direct_url(canonical, direct)
    session = Session(lambda url: response(url, 200, b"zipdata"))
    monkeypatch.setattr(pd, "get_session", lambda settings_tab=None: session)
    thread = post_thread(tmp_path, canonical, retries=3)

    thread.download_file(canonical, str(tmp_path / "dl"), 0, 1)

    assert session.urls == [direct]
    assert thread.completed_files == {canonical}
    # Duplicate detection still keys on the usual URL.
    url_hash = hashlib.md5(canonical.encode()).hexdigest()
    assert thread.hash_db.lookup(url_hash) is not None
    du.forget_direct_url(canonical)


@pytest.mark.parametrize(
    "direct_failure",
    [
        lambda url: (_ for _ in ()).throw(requests.ConnectionError("node down")),
        lambda url: response(url, 404),
    ],
    ids=["connection-error", "404-on-node"],
)
def test_post_download_falls_back_without_using_a_retry(
    tmp_path, monkeypatch, direct_failure
):
    canonical = f"https://file.pawchive.pw/data{ZIP_PATH}?f=frankie.zip"
    direct = f"https://n3.pawchive.pw/data{ZIP_PATH}?f=frankie.zip"
    du.remember_direct_url(canonical, direct)
    session = Session(
        lambda url: direct_failure(url) if url == direct else response(url, 200, b"z")
    )
    monkeypatch.setattr(pd, "get_session", lambda settings_tab=None: session)
    # Only one attempt allowed: the fallback must not use it up.
    thread = post_thread(tmp_path, canonical, retries=1)

    thread.download_file(canonical, str(tmp_path / "dl"), 0, 1)

    assert session.urls == [direct, canonical]
    assert thread.completed_files == {canonical}
    assert thread.unavailable_files == set()
    assert du.direct_url_for(canonical) is None  # not tried again


def test_creator_download_falls_back_from_a_failing_direct_server(
    tmp_path, monkeypatch
):
    canonical = f"https://file.pawchive.pw/data{ZIP_PATH}?f=frankie.zip"
    direct = f"https://n3.pawchive.pw/data{ZIP_PATH}?f=frankie.zip"
    du.remember_direct_url(canonical, direct)
    session = Session(
        lambda url: response(url, 404) if url == direct else response(url, 200, b"z")
    )
    monkeypatch.setattr(cd, "get_session", lambda st=None: session)
    os.makedirs(tmp_path / "other", exist_ok=True)
    thread = cd.CreatorDownloadThread(
        service="patreon",
        creator_id="1",
        download_folder=str(tmp_path / "dl"),
        selected_posts=["2"],
        files_to_download=[canonical],
        files_to_posts_map={canonical: "2"},
        console=SimpleNamespace(),
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={},
        auto_rename_enabled=False,
        settings=SimpleNamespace(settings_tab=None, file_download_max_retries=1),
        max_concurrent=1,
        download_text=False,
    )
    for name in ("file_progress", "file_completed", "post_completed", "log"):
        setattr(thread, name, SimpleNamespace(emit=lambda *a: None))
    target = str(tmp_path / "dl")
    os.makedirs(target, exist_ok=True)
    thread.generate_filename_and_folder = lambda *a, **k: (target, "frankie.zip")

    asyncio.run(thread.download_file(canonical, target, 0, total_files=1))

    assert session.urls == [direct, canonical]
    assert canonical in thread.completed_files
    assert thread.unavailable_files == set()


# --- 3: save preview images -----------------------------------------------


def preview_post():
    return {
        "id": "164102776",
        "title": "Frankie",
        "attachments": [
            {"name": "00501.png", "path": "/f8/98/f898.png", "preview_only": True},
            {"name": "pack.zip", "path": "/aa/bb/aabb.zip", "preview_only": True},
        ],
    }


def test_preview_image_url():
    e = entry(name="00501.png", extension=".png", path="/f8/98/f898.png", server="")
    assert du.preview_image_url(e, PAW) == (
        "https://img.pawchive.pw/thumbnail/data/f8/98/f898.png?f=00501_preview.png"
    )
    # No preview exists for non-image files.
    assert du.preview_image_url(entry(preview_only=True), PAW) is None


@pytest.mark.parametrize("enabled", [True, False])
def test_preparation_saves_previews_only_when_enabled(enabled):
    settings = du.ThreadSettings(1, 1, 1, 1, 1, save_preview_images=enabled)
    thread = cd.FilePreparationThread([], {}, {}, True, True, True, settings)
    files = thread.detect_files(preview_post(), [".png", ".zip"], PAW)

    names = [name for name, _ in files]
    assert names == (["00501_preview.png"] if enabled else [])
    saved = {f.name: f.preview_saved for f in thread.preview_only_files}
    assert saved == {"00501.png": enabled, "pack.zip": False}


def test_setting_reader_is_safe():
    assert du.save_preview_images_enabled(None) is False
    assert du.save_preview_images_enabled(MagicMock()) is False  # not literally True
    tab = SimpleNamespace(is_save_preview_images_enabled=lambda: True)
    assert du.save_preview_images_enabled(tab) is True
    assert du.ThreadSettings(1, 1, 1, 1, 1).save_preview_images is False


def test_setting_round_trips(qapp, tmp_path):
    from PyQt6.QtCore import QSettings

    from kemonodownloader.kd_settings import SettingsTab

    tab = SettingsTab(SimpleNamespace())
    try:
        # A throwaway settings file, so the real app settings are untouched.
        tab.qsettings = QSettings(
            str(tmp_path / "settings.ini"), QSettings.Format.IniFormat
        )
        assert tab.load_settings()["save_preview_images"] is False  # default
        tab.save_previews_checkbox.setChecked(True)
        assert tab.temp_settings["save_preview_images"] is True
        tab.settings = tab.temp_settings.copy()
        tab.save_settings()
        assert tab.load_settings()["save_preview_images"] is True
        assert tab.is_save_preview_images_enabled() is True
    finally:
        tab.deleteLater()


def test_notice_wording_when_previews_are_saved(qapp):
    from kemonodownloader.kd_language import translate

    notice = PreviewOnlyNotice()
    notice.add([du.PreviewOnlyFile("1", "T", "a.png", "https://x/a", True)])
    assert notice._box.informativeText() == translate("preview_only_info_saved")
    notice.reset()


# --- 2: missing-files window ----------------------------------------------


def test_missing_files_notice(qapp):
    notice = MissingFilesNotice()
    notice.show([])
    assert notice._box is None  # nothing to say

    notice.show(["https://k/data/a.png?f=a.png", "https://k/data/b.png?f=b.png"])
    box = notice._box
    assert box.isVisible() and not box.isModal()
    assert "2" in box.text()
    assert "a.png  (https://k/data/a.png?f=a.png)" in box.detailedText()
    notice.close()


def test_post_finish_shows_missing_files(qapp, monkeypatch, tmp_path):
    from PyQt6.QtGui import QIcon

    monkeypatch.setattr("qtawesome.icon", lambda *a, **k: QIcon())
    parent = MagicMock()
    parent.cache_folder = str(tmp_path / "c")
    parent.other_files_folder = str(tmp_path / "o")
    tab = pd.PostDownloaderTab(parent)
    try:
        shown = []
        monkeypatch.setattr(tab.missing_files_notice, "show", shown.append)
        tab.failed_files = {"m", "f"}
        tab.unavailable_files = {"m"}
        tab.post_download_finished()
        assert shown == [{"m"}]
    finally:
        tab.deleteLater()


# --- 4: History counts ----------------------------------------------------

V1_SCHEMA = """
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, url TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '', service TEXT NOT NULL DEFAULT '',
    creator TEXT NOT NULL DEFAULT '', folder TEXT NOT NULL DEFAULT '',
    files_total INTEGER NOT NULL DEFAULT 0, files_done INTEGER NOT NULL DEFAULT 0,
    files_failed INTEGER NOT NULL DEFAULT 0, posts_total INTEGER NOT NULL DEFAULT 0,
    posts_done INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL, started_at REAL,
    finished_at REAL NOT NULL, size_bytes INTEGER,
    extra_urls TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL, title TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '', added_at REAL NOT NULL
);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
PRAGMA user_version = 1;
"""
POST = "https://kemono.cr/patreon/user/1/post/2"


def test_history_upgrades_a_version_1_database(tmp_path):
    path = tmp_path / HistoryStore.DB_FILENAME
    conn = sqlite3.connect(path)
    conn.executescript(V1_SCHEMA)
    conn.execute(
        "INSERT INTO history (kind, url, title, files_total, files_done, status, "
        "finished_at) VALUES ('post', ?, 'Old', 3, 3, 'completed', 1.0)",
        (POST,),
    )
    conn.commit()
    conn.close()

    store = HistoryStore(str(tmp_path))
    try:
        old = store.history()[0]
        assert (old.title, old.files_preview_only, old.files_missing) == ("Old", 0, 0)

        store.record(
            HistoryEntry(
                kind=KIND_POST,
                url=POST,
                title="New",
                files_total=5,
                files_done=4,
                files_failed=1,
                files_preview_only=10,
                files_missing=1,
            )
        )
        new = next(e for e in store.history() if e.title == "New")
        assert (new.files_preview_only, new.files_missing) == (10, 1)
    finally:
        store.close()

    conn = sqlite3.connect(path)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    # Opening again doesn't try to add the columns twice.
    conn.close()
    HistoryStore(str(tmp_path)).close()


def test_history_tooltip_and_csv(qapp, tmp_path, monkeypatch):
    from PyQt6.QtCore import Qt

    from kemonodownloader import kd_history

    store = HistoryStore(str(tmp_path))
    try:
        store.record(
            HistoryEntry(
                kind=KIND_POST,
                url=POST,
                title="T",
                files_total=4,
                files_done=3,
                files_failed=1,
                files_preview_only=6,
                files_missing=1,
            )
        )
        window = SimpleNamespace(
            history_store=store,
            post_tab=None,
            creator_tab=None,
            thumbnail_tab=None,
            tabs=None,
        )
        tab = kd_history.HistoryTab(window)
        tab.refresh()
        model = tab.history_model
        index = model.index(0, model.FILES)
        tip = model.data(index, Qt.ItemDataRole.ToolTipRole)
        assert "6" in tip and "3" in tip and "4" in tip

        out = tmp_path / "h.csv"
        monkeypatch.setattr(
            kd_history.QFileDialog, "getSaveFileName", lambda *a: (str(out), "")
        )
        tab.export_history()
        with open(out, encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        header = rows[0]
        row = dict(zip(header, rows[1]))
        assert (row["files_preview_only"], row["files_missing"]) == ("6", "1")
        assert header[-1] == "links"
        tab.deleteLater()
    finally:
        store.close()
