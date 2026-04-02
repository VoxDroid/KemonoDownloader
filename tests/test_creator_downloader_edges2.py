import asyncio
import contextlib
import hashlib
import os
import threading
from types import SimpleNamespace

from kemonodownloader import creator_downloader as cd


def test_generate_filename_template_error_fallback():
    dummy = SimpleNamespace()
    dummy.service = "fanbox"
    dummy.creator_id = "42"
    dummy.post_titles_map = {("fanbox", "42", "101"): "My Post"}
    dummy.creator_name = "Creator"
    dummy.auto_rename_enabled = False
    dummy.post_file_counters = {}
    dummy.post_file_counters_lock = threading.Lock()
    # Provide a template that references a missing key to force formatting error
    st = SimpleNamespace()
    st.get_creator_filename_template = lambda: "{does_not_exist}"
    st.get_creator_folder_strategy = lambda: "per_post"
    dummy.settings = SimpleNamespace(settings_tab=st)
    dummy._safe_emit = lambda *a, **k: None

    target, filename = cd.CreatorDownloadThread.generate_filename_and_folder(
        dummy,
        "https://kemono.cr/files/img.png?f=orig.png",
        "/tmp",
        0,
        1,
        "101",
        "My Post",
    )

    assert filename.endswith(".png")
    assert filename.startswith("101_")


def test_auto_rename_counter_per_post():
    dummy = SimpleNamespace()
    dummy.service = "fanbox"
    dummy.creator_id = "42"
    dummy.post_titles_map = {("fanbox", "42", "101"): "My Post"}
    dummy.creator_name = "Creator"
    dummy.auto_rename_enabled = True
    dummy.post_file_counters = {}
    dummy.post_file_counters_lock = threading.Lock()
    dummy.settings = SimpleNamespace(
        settings_tab=SimpleNamespace(
            get_creator_filename_template=lambda: None,
            get_creator_folder_strategy=lambda: "per_post",
        )
    )
    dummy._safe_emit = lambda *a, **k: None

    _, f1 = cd.CreatorDownloadThread.generate_filename_and_folder(
        dummy,
        "https://kemono.cr/files/a.jpg",
        "/tmp",
        0,
        2,
        "101",
        "Title",
    )
    _, f2 = cd.CreatorDownloadThread.generate_filename_and_folder(
        dummy,
        "https://kemono.cr/files/b.jpg",
        "/tmp",
        1,
        2,
        "101",
        "Title",
    )

    assert f1.startswith("1_")
    assert f2.startswith("2_")


def test_download_file_deletion_failure(monkeypatch, tmp_path):
    file_url = "http://example.com/out.bin"

    dummy = SimpleNamespace()
    dummy.service = "fanbox"
    dummy.creator_id = "42"
    dummy.post_titles_map = {("fanbox", "42", "101"): "Title"}
    dummy.creator_name = "Creator"
    dummy.auto_rename_enabled = False
    dummy.post_file_counters = {}
    dummy.post_file_counters_lock = threading.Lock()
    dummy.settings = SimpleNamespace(settings_tab=None, file_download_max_retries=1)
    dummy.files_to_download = [file_url]
    dummy.files_to_posts_map = {file_url: "101"}
    dummy.domain_config = {"referer": "https://kemono.cr/"}
    dummy.is_running = True
    dummy.hash_db = SimpleNamespace(lookup=lambda h: None, store=lambda *a, **k: None)
    dummy.failed_files = {}
    dummy.failed_files_lock = contextlib.nullcontext()
    dummy.completed_files = set()
    dummy.completed_files_lock = contextlib.nullcontext()
    dummy._ssl_lock = contextlib.nullcontext()
    dummy._safe_emit = lambda signal, *args: signal.emit(*args)
    dummy.log = SimpleNamespace(emit=lambda *a, **k: None)
    dummy.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    completed = []
    dummy.file_completed = SimpleNamespace(
        emit=lambda idx, url, ok: completed.append((idx, url, ok))
    )
    dummy.check_post_completion = lambda url: None
    dummy.download_text = False

    # generate filename
    dummy.generate_filename_and_folder = (
        lambda file_url, folder, file_index, total_files, post_id, post_title: (
            str(tmp_path),
            "out.bin",
        )
    )

    class FakeResp:
        def __init__(self):
            self.status_code = 200
            self._headers = {"content-length": "10"}

        def raise_for_status(self):
            return None

        @property
        def headers(self):
            return self._headers

        def iter_content(self, chunk_size=8192):
            yield b"abc"

        def close(self):
            pass

    class FakeSession:
        def get(self, *a, **k):
            return FakeResp()

    monkeypatch.setattr(cd, "get_session", lambda s=None: FakeSession())
    # make os.remove raise OSError to exercise deletion-failure branch
    monkeypatch.setattr(
        os, "remove", lambda p: (_ for _ in ()).throw(OSError("cant delete"))
    )

    asyncio.run(
        cd.CreatorDownloadThread.download_file(dummy, file_url, str(tmp_path), 0, 1)
    )

    assert file_url in dummy.failed_files


def test_preview_thread_cached_jpg(tmp_path):
    # Use a real small JPG saved via QPixmap so load(cache_path) succeeds
    from PyQt6.QtGui import QColor, QPixmap

    url = "https://example.com/img.jpg"
    cache_dir = str(tmp_path / "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_key = hashlib.md5(url.encode()).hexdigest() + os.path.splitext(url)[1]
    cache_path = os.path.join(cache_dir, cache_key)
    pix = QPixmap(8, 8)
    pix.fill(QColor("blue"))
    pix.save(cache_path)

    pt = cd.PreviewThread(url, cache_dir, settings_tab=None)
    captured = {}
    pt.preview_ready = SimpleNamespace(
        emit=lambda u, p: captured.update({"url": u, "val": p})
    )
    pt.progress = SimpleNamespace(emit=lambda *a, **k: None)
    pt.error = SimpleNamespace(emit=lambda *a, **k: None)
    pt.run()

    assert captured.get("url") == url
    assert captured.get("val") is not None


def test_download_file_success(monkeypatch, tmp_path):
    file_url = "http://example.com/success.bin"

    dummy = SimpleNamespace()
    dummy.service = "fanbox"
    dummy.creator_id = "42"
    dummy.post_titles_map = {("fanbox", "42", "101"): "Title"}
    dummy.creator_name = "Creator"
    dummy.auto_rename_enabled = False
    dummy.post_file_counters = {}
    dummy.post_file_counters_lock = threading.Lock()
    dummy.settings = SimpleNamespace(settings_tab=None, file_download_max_retries=1)
    dummy.files_to_download = [file_url]
    dummy.files_to_posts_map = {file_url: "101"}
    dummy.domain_config = {"referer": "https://kemono.cr/"}
    dummy.is_running = True
    stored = []
    dummy.hash_db = SimpleNamespace(
        lookup=lambda h: None, store=lambda *a, **k: stored.append(a)
    )
    dummy.failed_files = {}
    dummy.failed_files_lock = contextlib.nullcontext()
    dummy.completed_files = set()
    dummy.completed_files_lock = contextlib.nullcontext()
    dummy._ssl_lock = contextlib.nullcontext()
    dummy._safe_emit = lambda signal, *args: signal.emit(*args)
    dummy.log = SimpleNamespace(emit=lambda *a, **k: None)
    dummy.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    completed = []
    dummy.file_completed = SimpleNamespace(
        emit=lambda idx, url, ok: completed.append((idx, url, ok))
    )
    dummy.check_post_completion = lambda url: None
    dummy.download_text = False
    dummy.generate_filename_and_folder = (
        lambda file_url, folder, file_index, total_files, post_id, post_title: (
            str(tmp_path),
            "success.bin",
        )
    )

    class FakeResp:
        def __init__(self):
            self.status_code = 200
            self._headers = {"content-length": "5"}

        def raise_for_status(self):
            return None

        @property
        def headers(self):
            return self._headers

        def iter_content(self, chunk_size=8192):
            yield b"hello"

        def close(self):
            pass

    class FakeSession:
        def get(self, *a, **k):
            return FakeResp()

    monkeypatch.setattr(cd, "get_session", lambda s=None: FakeSession())

    asyncio.run(
        cd.CreatorDownloadThread.download_file(dummy, file_url, str(tmp_path), 0, 1)
    )
    assert not dummy.failed_files, dummy.failed_files
    full_path = os.path.join(str(tmp_path), "success.bin")
    assert os.path.exists(full_path), "Downloaded file should exist"
    with open(full_path, "rb") as f:
        assert f.read() == b"hello"
    assert stored
    assert any(c for c in completed if c[1] == file_url and c[2] is True)


def test_download_file_retry_exhaustion(monkeypatch, tmp_path):
    import requests

    file_url = "http://example.com/fail.bin"
    dummy = SimpleNamespace()
    dummy.service = "fanbox"
    dummy.creator_id = "42"
    dummy.post_titles_map = {("fanbox", "42", "101"): "Title"}
    dummy.creator_name = "Creator"
    dummy.auto_rename_enabled = False
    dummy.post_file_counters = {}
    dummy.post_file_counters_lock = threading.Lock()
    dummy.settings = SimpleNamespace(settings_tab=None, file_download_max_retries=1)
    dummy.files_to_download = [file_url]
    dummy.files_to_posts_map = {file_url: "101"}
    dummy.domain_config = {"referer": "https://kemono.cr/"}
    dummy.is_running = True
    dummy.hash_db = SimpleNamespace(lookup=lambda h: None, store=lambda *a, **k: None)
    dummy.failed_files = {}
    dummy.failed_files_lock = contextlib.nullcontext()
    dummy.completed_files = set()
    dummy.completed_files_lock = contextlib.nullcontext()
    dummy._ssl_lock = contextlib.nullcontext()
    dummy._safe_emit = lambda signal, *args: signal.emit(*args)
    dummy.log = SimpleNamespace(emit=lambda *a, **k: None)
    dummy.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    dummy.file_completed = SimpleNamespace(emit=lambda *a, **k: None)
    dummy.check_post_completion = lambda url: None
    dummy.download_text = False
    dummy.generate_filename_and_folder = (
        lambda file_url, folder, file_index, total_files, post_id, post_title: (
            str(tmp_path),
            "fail.bin",
        )
    )

    def raise_req(*a, **k):
        raise requests.RequestException("down")

    class Sess:
        def get(self, *a, **k):
            return (_ for _ in ()).throw(requests.RequestException("down"))

    monkeypatch.setattr(cd, "get_session", lambda s=None: Sess())
    # run
    asyncio.run(
        cd.CreatorDownloadThread.download_file(dummy, file_url, str(tmp_path), 0, 1)
    )
    assert file_url in dummy.failed_files


def test_download_worker_consumes_queue():
    dummy = SimpleNamespace()
    dummy.is_running = True

    calls = []

    async def fake_download(file_url, folder, file_index, total_files):
        calls.append((file_index, file_url))
        await asyncio.sleep(0)

    dummy.download_file = fake_download

    async def main():
        q = asyncio.Queue()
        await q.put((0, "u1"))
        t = asyncio.create_task(
            cd.CreatorDownloadThread.download_worker(dummy, q, "/tmp", 1)
        )
        await q.join()
        dummy.is_running = False
        t.cancel()
        await asyncio.gather(t, return_exceptions=True)

    asyncio.run(main())
    assert calls == [(0, "u1")]
