"""Preview-only files (listed by the site, full file gone) and missing files."""

import asyncio
import io
import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import requests

import kemonodownloader.creator_downloader as cd
import kemonodownloader.post_downloader as pd
from kemonodownloader import kd_preview_notice
from kemonodownloader.domain_config import get_domain_config
from kemonodownloader.download_utils import (
    PreviewOnlyFile,
    is_missing_file_error,
    is_preview_only,
    iter_post_file_entries,
    iter_post_files,
)
from kemonodownloader.kd_preview_notice import PreviewOnlyNotice

POST_URL = "https://pawchive.pw/patreon/user/103321013/post/164102776"
ZIP_PATH = (
    "/118/1d/181dd6c41d920a2066e9cd56a6c6a03b4023f7c46bdf8bc77ddd60955ec0b44f.zip"
)
PNG_PATH = "/f8/98/f8983eb853c2df17c2ca7ed5141977827892742d32316bec7194aea769e64ccc.png"


def pawchive_post():
    """Shape of the real Pawchive API response for a partly preview-only post."""
    preview = {"name": "00501.png", "path": PNG_PATH, "preview_only": True}
    return {
        "id": "164102776",
        "title": "Frankie",
        "file": dict(preview),
        "attachments": [
            {
                "name": "frankie.zip",
                "path": ZIP_PATH,
                "server": "https://n3.pawchive.pw",
            },
            dict(preview),
            {"name": "00502.png", "path": "/aa/bb/aabb.png", "preview_only": True},
        ],
        "content": "",
    }


def missing_response(url, status=404):
    response = requests.models.Response()
    response.status_code = status
    response.url = url
    response.reason = "Not Found"
    response.raw = io.BytesIO(b"")  # real responses always have a body stream
    return response


# --- shared helpers -------------------------------------------------------


def test_is_preview_only_needs_the_flag_to_be_true():
    assert is_preview_only({"preview_only": True})
    assert not is_preview_only({"preview_only": False})
    assert not is_preview_only({"server": "https://n3.pawchive.pw"})
    assert not is_preview_only(None)


def test_iter_post_file_entries_flags_preview_only_files():
    entries = list(iter_post_file_entries(pawchive_post(), get_domain_config(POST_URL)))
    flags = {(e.kind, e.name): e.preview_only for e in entries}
    assert flags[("attachment", "frankie.zip")] is False
    assert flags[("main", "00501.png")] is True
    assert flags[("attachment", "00502.png")] is True


def test_iter_post_files_keeps_its_four_value_shape():
    files = list(iter_post_files(pawchive_post(), get_domain_config(POST_URL)))
    assert all(len(f) == 4 for f in files)
    assert ("attachment", "frankie.zip") == files[1][:2]


@pytest.mark.parametrize(
    "error, missing",
    [
        (requests.HTTPError(response=missing_response("u", 404)), True),
        (requests.HTTPError(response=missing_response("u", 410)), True),
        (requests.HTTPError(response=missing_response("u", 500)), False),
        (requests.HTTPError(response=missing_response("u", 403)), False),
        (requests.ConnectionError("down"), False),
        (ValueError("other"), False),
    ],
)
def test_is_missing_file_error(error, missing):
    assert is_missing_file_error(error) is missing


# --- file preparation -----------------------------------------------------


def test_post_preparation_skips_and_records_preview_only():
    thread = pd.FilePreparationThread([], {}, {}, {}, POST_URL, MagicMock())
    files = thread.detect_files(pawchive_post(), [".zip", ".png"])

    assert [name for name, _ in files] == ["frankie.zip"]
    # 00501.png is both the main file and an attachment: reported once.
    assert sorted(f.name for f in thread.preview_only_files) == [
        "00501.png",
        "00502.png",
    ]
    assert all(f.post_title == "Frankie" for f in thread.preview_only_files)


def test_post_preparation_ignores_preview_only_of_filtered_types():
    thread = pd.FilePreparationThread([], {}, {}, {}, POST_URL, MagicMock())
    thread.detect_files(pawchive_post(), [".zip"])
    # The user didn't ask for PNGs, so they aren't "skipped" either.
    assert thread.preview_only_files == []


def test_creator_preparation_skips_and_records_preview_only():
    thread = cd.FilePreparationThread([], {}, {}, True, True, True, MagicMock())
    files = thread.detect_files(
        pawchive_post(), [".zip", ".png"], get_domain_config(POST_URL)
    )
    assert [name for name, _ in files] == ["frankie.zip"]
    assert len(thread.preview_only_files) == 2


def test_check_all_detection_leaves_preview_only_out():
    thread = pd.PostDetectionThread(POST_URL, MagicMock())
    assert [name for name, _ in thread.detect_files(pawchive_post())] == ["frankie.zip"]


# --- downloads: a missing file is not retried -----------------------------


class Recorder:
    def __init__(self):
        self.calls = []

    def emit(self, *args):
        self.calls.append(args)


class CountingSession:
    def __init__(self, response):
        self.response = response
        self.gets = 0

    def get(self, url, **kwargs):
        self.gets += 1
        return self.response


def make_post_thread(tmp_path, file_url, retries):
    thread = pd.DownloadThread(
        url="https://kemono.cr/fanbox/user/123/post/1",
        download_folder=str(tmp_path / "downloads"),
        selected_files=[file_url],
        files_to_posts_map={file_url: "1"},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_id="1",
        settings=SimpleNamespace(file_download_max_retries=retries, settings_tab=None),
        max_concurrent=1,
        auto_rename=False,
        download_text=False,
    )
    thread.file_progress = Recorder()
    thread.file_completed = Recorder()
    thread.log = Recorder()
    return thread


@pytest.mark.parametrize("status", [404, 410])
def test_post_download_does_not_retry_a_missing_file(tmp_path, monkeypatch, status):
    file_url = "https://kemono.cr/data/aa/bb/aabb.png?f=x.png"
    session = CountingSession(missing_response(file_url, status))
    monkeypatch.setattr(pd, "get_session", lambda settings_tab=None: session)
    thread = make_post_thread(tmp_path, file_url, retries=50)

    thread.download_file(file_url, str(tmp_path / "downloads"), 0, 1)

    assert session.gets == 1
    assert thread.unavailable_files == {file_url}
    assert thread.file_completed.calls == [(0, file_url, False)]
    logged = " ".join(str(c[0]) for c in thread.log.calls)
    assert "Not available on the server" in logged
    assert f"HTTP {status}" in logged


def test_post_download_still_retries_server_errors(tmp_path, monkeypatch):
    file_url = "https://kemono.cr/data/aa/bb/aabb.png?f=x.png"
    session = CountingSession(missing_response(file_url, 503))
    monkeypatch.setattr(pd, "get_session", lambda settings_tab=None: session)
    monkeypatch.setattr(pd.time, "sleep", lambda s: None)
    thread = make_post_thread(tmp_path, file_url, retries=3)

    thread.download_file(file_url, str(tmp_path / "downloads"), 0, 1)

    assert session.gets == 3
    assert thread.unavailable_files == set()


def test_creator_download_does_not_retry_a_missing_file(tmp_path, monkeypatch):
    file_url = "https://kemono.cr/data/aa/bb/aabb.png?f=x.png"
    session = CountingSession(missing_response(file_url))
    monkeypatch.setattr(cd, "get_session", lambda st=None: session)
    os.makedirs(tmp_path / "other", exist_ok=True)
    thread = cd.CreatorDownloadThread(
        service="patreon",
        creator_id="1",
        download_folder=str(tmp_path / "dl"),
        selected_posts=["1"],
        files_to_download=[file_url],
        files_to_posts_map={file_url: "1"},
        console=SimpleNamespace(),
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={},
        auto_rename_enabled=False,
        settings=SimpleNamespace(settings_tab=None, file_download_max_retries=50),
        max_concurrent=1,
        download_text=False,
    )
    thread.file_progress = Recorder()
    thread.file_completed = Recorder()
    thread.post_completed = Recorder()
    thread.log = Recorder()
    target = str(tmp_path / "dl")
    os.makedirs(target, exist_ok=True)
    thread.generate_filename_and_folder = lambda *a, **k: (target, "x.png")

    asyncio.run(thread.download_file(file_url, target, 0, total_files=1))

    assert session.gets == 1
    assert thread.unavailable_files == {file_url}
    # Still counted as failed, so "all files attempted" detection still works.
    assert file_url in thread.failed_files
    assert thread.file_completed.calls == [(0, file_url, False)]


# --- warning window -------------------------------------------------------


def files(*names):
    return [PreviewOnlyFile("1", "Post", n, f"https://x/{n}") for n in names]


def test_notice_opens_non_modal_and_updates_in_place(qapp):
    notice = PreviewOnlyNotice()
    assert notice.add(files("a.png", "b.png")) == 2
    box = notice._box
    assert box is not None and box.isVisible()
    assert not box.isModal()
    assert "2" in box.text()

    assert notice.add(files("b.png", "c.png")) == 1  # b.png already counted
    assert notice._box is box  # one window, updated
    assert "3" in box.text()
    assert "Post — c.png" in box.detailedText()
    notice.reset()


def test_notice_stays_closed_for_the_rest_of_the_run(qapp):
    notice = PreviewOnlyNotice()
    notice.add(files("a.png"))
    notice._box.done(0)  # the user closes it
    notice.add(files("b.png"))
    assert not notice._box.isVisible()
    assert notice.count == 2  # still counted for the summary

    notice.reset()  # next download run
    assert notice.count == 0
    notice.add(files("c.png"))
    assert notice._box.isVisible()
    notice.reset()


def test_notice_details_are_capped(qapp, monkeypatch):
    monkeypatch.setattr(kd_preview_notice, "DETAIL_LIMIT", 2)
    notice = PreviewOnlyNotice()
    notice.add(files("a", "b", "c", "d"))
    lines = notice._box.detailedText().splitlines()
    assert len(lines) == 3 and "2" in lines[-1]
    notice.reset()


# --- Post tab -------------------------------------------------------------


@pytest.fixture
def post_tab(qapp, monkeypatch, tmp_path):
    from PyQt6.QtGui import QIcon

    monkeypatch.setattr("qtawesome.icon", lambda *a, **k: QIcon())
    parent = MagicMock()
    parent.cache_folder = str(tmp_path / "cache")
    parent.other_files_folder = str(tmp_path / "other")
    parent.download_folder = str(tmp_path / "downloads")
    tab = pd.PostDownloaderTab(parent)
    yield tab
    tab.preview_only_notice.reset()
    tab.deleteLater()


def test_post_list_shows_preview_only_files_unselectable(post_tab):
    post_tab.current_post_url = POST_URL
    detected = post_tab.detect_files(pawchive_post(), [".zip", ".png"])
    post_tab.all_detected_files = detected
    for name, url in detected:
        post_tab.checked_urls[url] = not post_tab._is_preview_only(url)
        post_tab.add_list_item(name, url)

    rows = {}
    for i in range(post_tab.post_file_list.count()):
        item = post_tab.post_file_list.item(i)
        rows[item.data(pd.Qt.UserRole)] = post_tab.post_file_list.itemWidget(item)
    zip_row = next(w for u, w in rows.items() if "frankie.zip" in u)
    png_row = next(w for u, w in rows.items() if "00502.png" in u)
    assert zip_row.check_box.isEnabled() and zip_row.check_box.isChecked()
    assert not png_row.check_box.isEnabled() and not png_row.check_box.isChecked()
    assert "preview only" in png_row.label.text()

    post_tab.toggle_check_all(2)  # "check all" must not pick preview-only files
    assert all(
        not post_tab.checked_urls[u] for u in rows if post_tab._is_preview_only(u)
    )


def test_post_report_adjusts_total_and_opens_warning(post_tab):
    skipped = files("a.png", "b.png")
    post_tab.checked_urls = {skipped[0].url: True, "https://x/keep.zip": True}
    post_tab.total_files_to_download = 2

    post_tab._report_preview_only(skipped)

    assert post_tab.total_files_to_download == 1  # only a.png had been counted
    assert post_tab.checked_urls[skipped[0].url] is False
    assert post_tab.preview_only_notice.count == 2
    assert post_tab.preview_only_notice._box.isVisible()


def test_post_summary_separates_missing_from_failed(post_tab, monkeypatch):
    logs = []
    monkeypatch.setattr(
        post_tab, "append_log_to_console", lambda m, lvl: logs.append(m)
    )
    post_tab.completed_files = {"d1", "d2"}
    post_tab.failed_files = {"m1", "f1"}
    post_tab.unavailable_files = {"m1"}
    post_tab.preview_only_notice.add(files("p.png"))

    post_tab._log_download_summary()

    assert any(
        "2 downloaded, 1 only available as previews (skipped), "
        "1 not found on the server, 1 failed" in m
        for m in logs
    )


def test_post_completion_marks_missing_files(post_tab):
    post_tab.thread = SimpleNamespace(unavailable_files={"u1"})
    post_tab.total_files_to_download = 2
    post_tab.update_file_completion(0, "u1", False)
    post_tab.update_file_completion(1, "u2", False)
    assert post_tab.unavailable_files == {"u1"}
    assert post_tab.failed_files == {"u1", "u2"}


# --- Creator tab ----------------------------------------------------------


@pytest.fixture
def creator_tab(qapp, tmp_path):
    parent = MagicMock()
    parent.cache_folder = str(tmp_path / "cache")
    parent.other_files_folder = str(tmp_path / "other")
    parent.download_folder = str(tmp_path / "downloads")
    tab = cd.CreatorDownloaderTab(parent)
    yield tab
    tab.preview_only_notice.reset()
    tab.deleteLater()


def test_creator_run_totals_and_summary(creator_tab, monkeypatch):
    logs = []
    monkeypatch.setattr(
        creator_tab, "append_log_to_console", lambda m, lvl: logs.append((lvl, m))
    )
    creator_tab._report_preview_only(files("p1.png", "p2.png"))
    # Two creators finish; completed_files is per creator, so the run total
    # is added up from each thread.
    for done, missing in (({"a", "b"}, {"m1"}), ({"c"}, set())):
        thread = SimpleNamespace(completed_files=done, unavailable_files=missing)
        creator_tab._run_downloaded += len(thread.completed_files)
        creator_tab.unavailable_files.update(thread.unavailable_files)
    creator_tab.failed_files = {"m1": "404 Client Error", "f1": "timeout"}

    creator_tab._log_download_summary()

    assert creator_tab.preview_only_notice.count == 2
    assert any(
        "3 downloaded, 2 only available as previews (skipped), "
        "1 not found on the server, 1 failed" in m
        for _, m in logs
    )


def test_creator_finish_lists_only_real_failures(creator_tab, monkeypatch):
    logs = []
    monkeypatch.setattr(
        creator_tab, "append_log_to_console", lambda m, lvl: logs.append((lvl, m))
    )
    creator_tab.failed_files = {"m1": "404 Client Error", "f1": "timeout"}
    creator_tab.unavailable_files = {"m1"}

    creator_tab.creator_download_finished()

    errors = [m for lvl, m in logs if lvl == "ERROR"]
    assert any("f1" in m for m in errors)
    assert not any("m1" in m for m in errors)  # reported as "not on the server"
    assert creator_tab.unavailable_files == set()
