import asyncio
import hashlib
import os
from types import SimpleNamespace

import requests

from kemonodownloader.creator_downloader import CreatorDownloadThread, ThreadSettings


def make_settings():
    settings_tab = SimpleNamespace(
        get_creator_filename_template=lambda: None,
        get_creator_folder_strategy=lambda: "per_post",
        get_proxy_settings=lambda: None,
    )
    return ThreadSettings(
        creator_posts_max_attempts=1,
        post_data_max_retries=1,
        file_download_max_retries=1,
        api_request_max_retries=1,
        simultaneous_downloads=1,
        settings_tab=settings_tab,
    )


def test_fetch_creator_and_post_info_populates(monkeypatch):
    settings = make_settings()
    file_url = "https://kemono.cr/files/x.png"
    files_to_download = [file_url]
    files_to_posts_map = {file_url: "1"}

    thread = CreatorDownloadThread(
        service="svc",
        creator_id="creator123",
        download_folder="/tmp",
        selected_posts=["1"],
        files_to_download=files_to_download,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir="/tmp/other",
        post_titles_map={},
        auto_rename_enabled=False,
        settings=settings,
        download_text=False,
    )

    # Fake session implementation returning profile and post JSON
    def fake_get_session(settings_tab=None):
        def get(url, *a, **k):
            if url.endswith("/profile"):
                return SimpleNamespace(
                    status_code=200, json=lambda: {"name": "X Alice"}
                )
            if "/post/" in url:
                pid = url.rstrip("/").split("/")[-1]
                return SimpleNamespace(
                    status_code=200, json=lambda: {"title": f"Title{pid}"}
                )
            return SimpleNamespace(status_code=404, json=lambda: {})

        return SimpleNamespace(get=get)

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session", fake_get_session
    )

    # Replace signal emitters to avoid PyQt interactions
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)

    thread.fetch_creator_and_post_info()

    assert thread.creator_name is not None
    key = ("svc", "creator123", "1")
    assert key in thread.post_titles_map


def test_fetch_creator_and_post_info_handles_errors(monkeypatch):
    settings = make_settings()
    file_url = "https://kemono.cr/files/x.png"
    files_to_download = [file_url]
    files_to_posts_map = {file_url: "1"}

    thread = CreatorDownloadThread(
        service="svc",
        creator_id="creator123",
        download_folder="/tmp",
        selected_posts=["1"],
        files_to_download=files_to_download,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir="/tmp/other",
        post_titles_map={},
        auto_rename_enabled=False,
        settings=settings,
        download_text=False,
    )

    class BadSession:
        def get(self, *a, **k):
            raise requests.RequestException("network")

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session", lambda *a, **k: BadSession()
    )

    thread.log = SimpleNamespace(emit=lambda *a, **k: None)

    thread.fetch_creator_and_post_info()

    assert thread.creator_name == "Unknown_Creator"
    key = ("svc", "creator123", "1")
    assert key in thread.post_titles_map


def test_download_file_size_mismatch_triggers_redownload(monkeypatch, tmp_path):
    download_folder = str(tmp_path / "dl")
    other_files_dir = str(tmp_path / "other")
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(other_files_dir, exist_ok=True)

    file_url = "https://kemono.cr/files/z.png"
    files_to_download = [file_url]
    files_to_posts_map = {file_url: "1"}

    settings = make_settings()
    thread = CreatorDownloadThread(
        service="svc",
        creator_id="creator123",
        download_folder=download_folder,
        selected_posts=["1"],
        files_to_download=files_to_download,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir=other_files_dir,
        post_titles_map={("svc", "creator123", "1"): "MyPost"},
        auto_rename_enabled=False,
        settings=settings,
        download_text=False,
    )

    # Create existing file with different size/hash than recorded in DB
    existing_path = os.path.join(other_files_dir, "z.png")
    with open(existing_path, "wb") as f:
        f.write(b"olddata")
    actual_size = os.path.getsize(existing_path)

    class FakeHashDB:
        def __init__(self):
            self.store_calls = {}

        def lookup(self, url_hash):
            # Return an entry that claims a different expected size/hash
            return {
                "file_path": existing_path,
                "file_hash": "differenthash",
                "file_size": actual_size + 10,
            }

        def store(self, url_hash, path, file_hash, file_url, file_size):
            self.store_calls[url_hash] = {
                "file_path": path,
                "file_hash": file_hash,
                "file_size": file_size,
            }

    fake_db = FakeHashDB()
    thread.hash_db = fake_db

    # Fake download response with different content
    class FakeResp:
        def __init__(self, chunks):
            self._chunks = chunks
            self.status_code = 200
            self.headers = {"content-length": str(sum(len(c) for c in chunks))}

        def iter_content(self, chunk_size=8192):
            for c in self._chunks:
                yield c

        def raise_for_status(self):
            return None

        def close(self):
            return None

    class FakeSession:
        def __init__(self, chunks):
            self._chunks = chunks

        def get(self, *a, **k):
            return FakeResp(self._chunks)

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session",
        lambda settings_tab=None: FakeSession([b"newcontent"]),
    )

    # Run the download
    asyncio.run(thread.download_file(file_url, download_folder, 0, total_files=1))

    # Should have stored a new hash entry and marked completed
    url_hash = hashlib.md5(file_url.encode()).hexdigest()
    assert file_url in thread.completed_files
    assert url_hash in fake_db.store_calls


def test_download_file_makedirs_failure_records_error(monkeypatch, tmp_path):
    download_folder = str(tmp_path / "dl2")
    other_files_dir = str(tmp_path / "other2")
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(other_files_dir, exist_ok=True)

    file_url = "https://kemono.cr/files/y.png"
    files_to_download = [file_url]
    files_to_posts_map = {file_url: "1"}

    settings = make_settings()
    thread = CreatorDownloadThread(
        service="svc",
        creator_id="creator123",
        download_folder=download_folder,
        selected_posts=["1"],
        files_to_download=files_to_download,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir=other_files_dir,
        post_titles_map={("svc", "creator123", "1"): "MyPost"},
        auto_rename_enabled=False,
        settings=settings,
        download_text=False,
    )

    # Replace log/progress/completed signals to no-ops
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(emit=lambda *a, **k: None)

    real_makedirs = os.makedirs

    def bad_makedirs(path, exist_ok=False):
        if str(path).startswith(download_folder):
            raise OSError("permission denied")
        return real_makedirs(path, exist_ok=exist_ok)

    monkeypatch.setattr(os, "makedirs", bad_makedirs)

    # Running should record a failure for this file_url
    asyncio.run(thread.download_file(file_url, download_folder, 0, total_files=1))
    assert file_url in thread.failed_files


def test_download_file_request_exception_records_failure(monkeypatch, tmp_path):
    download_folder = str(tmp_path / "dl3")
    other_files_dir = str(tmp_path / "other3")
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(other_files_dir, exist_ok=True)

    file_url = "https://kemono.cr/files/bad.png"
    files_to_download = [file_url]
    files_to_posts_map = {file_url: "1"}

    settings = make_settings()
    thread = CreatorDownloadThread(
        service="svc",
        creator_id="creator123",
        download_folder=download_folder,
        selected_posts=["1"],
        files_to_download=files_to_download,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir=other_files_dir,
        post_titles_map={("svc", "creator123", "1"): "MyPost"},
        auto_rename_enabled=False,
        settings=settings,
        download_text=False,
    )

    # No-op signals
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(emit=lambda *a, **k: None)

    class BadSession:
        def get(self, *a, **k):
            raise requests.RequestException("net")

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session", lambda *a, **k: BadSession()
    )

    asyncio.run(thread.download_file(file_url, download_folder, 0, total_files=1))
    assert file_url in thread.failed_files
