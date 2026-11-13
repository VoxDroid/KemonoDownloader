"""A download that ends early (fewer bytes than announced) is retried."""

import asyncio
import io
import os
from types import SimpleNamespace

import requests

import kemonodownloader.creator_downloader as cd
from kemonodownloader.download_utils import IncompleteDownloadError

URL = "https://kemono.cr/data/aa/bb/archive.zip?f=archive.zip"
FULL = b"0123456789"


def response(body):
    r = requests.models.Response()
    r.status_code = 200
    r.url = URL
    r.headers["content-length"] = str(len(FULL))  # always announces the full size
    r.raw = io.BytesIO(body)
    return r


def run_creator_download(tmp_path, monkeypatch, bodies, retries):
    gets = []

    def get(url, **kwargs):
        gets.append(url)
        return response(bodies[min(len(gets), len(bodies)) - 1])

    async def no_sleep(_seconds):
        return None

    monkeypatch.setattr(cd, "get_session", lambda st=None: SimpleNamespace(get=get))
    monkeypatch.setattr(cd.asyncio, "sleep", no_sleep)
    os.makedirs(tmp_path / "other", exist_ok=True)
    target = str(tmp_path / "dl")
    os.makedirs(target, exist_ok=True)
    thread = cd.CreatorDownloadThread(
        service="patreon",
        creator_id="1",
        download_folder=target,
        selected_posts=["1"],
        files_to_download=[URL],
        files_to_posts_map={URL: "1"},
        console=SimpleNamespace(),
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={},
        auto_rename_enabled=False,
        settings=SimpleNamespace(settings_tab=None, file_download_max_retries=retries),
        max_concurrent=1,
        download_text=False,
    )
    for name in ("file_progress", "file_completed", "post_completed", "log"):
        setattr(thread, name, SimpleNamespace(emit=lambda *a: None))
    thread.generate_filename_and_folder = lambda *a, **k: (target, "archive.zip")
    asyncio.run(thread.download_file(URL, target, 0, total_files=1))
    return thread, gets, os.path.join(target, "archive.zip")


def test_incomplete_download_is_a_network_error():
    assert issubclass(IncompleteDownloadError, requests.RequestException)


def test_creator_retries_a_truncated_download(tmp_path, monkeypatch):
    # Two short bodies (a dropped connection), then the whole file.
    thread, gets, path = run_creator_download(
        tmp_path, monkeypatch, [b"01234", b"0123", FULL], retries=5
    )
    assert len(gets) == 3
    assert URL in thread.completed_files
    assert URL not in thread.failed_files
    with open(path, "rb") as fh:
        assert fh.read() == FULL


def test_creator_gives_up_after_all_retries(tmp_path, monkeypatch):
    thread, gets, path = run_creator_download(
        tmp_path, monkeypatch, [b"01234"], retries=3
    )
    assert len(gets) == 3
    assert "Size mismatch" in thread.failed_files[URL]
    assert URL not in thread.unavailable_files  # not "missing on the server"
    assert not os.path.exists(path)  # no partial file left behind
