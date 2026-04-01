import asyncio
import json
import os
from types import SimpleNamespace

from kemonodownloader.creator_downloader import (
    CreatorDownloadThread,
    FilePreparationThread,
    PostDetectionThread,
)


def make_settings_creator(attempts=1):
    return SimpleNamespace(creator_posts_max_attempts=attempts, settings_tab=None)


def test_post_detection_populates_titles(monkeypatch):
    post_titles_map = {}
    settings = make_settings_creator()
    url = "https://kemono.cr/service/user/123"

    thread = PostDetectionThread(url, post_titles_map, settings)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    # Fake session returning a simple posts list
    def fake_get_session(settings_tab=None):
        def get(u, *a, **k):
            data = [
                {"id": "1", "title": "Hello World", "file": {"path": "/files/main.png"}}
            ]
            return SimpleNamespace(
                status_code=200,
                text=json.dumps(data),
                content=json.dumps(data).encode(),
            )

        return SimpleNamespace(get=get)

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session", fake_get_session
    )

    thread.run()

    key = ("service", "123", "1")
    assert key in post_titles_map


def test_post_detection_invalid_url_emits_error():
    errors = []
    settings = make_settings_creator()
    thread = PostDetectionThread("https://kemono.cr/invalid/123", {}, settings)
    thread.error = SimpleNamespace(emit=lambda msg: errors.append(msg))
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()
    assert errors


def test_detect_files_collects_main_attachments_content():
    # Create checkboxes that report enabled
    class CB:
        def __init__(self, v=True):
            self._v = v

        def isChecked(self):
            return self._v

    creator_ext_checks = {".png": CB(True), ".jpg": CB(True), ".gif": CB(True)}
    settings = SimpleNamespace(settings_tab=None)

    thread = FilePreparationThread(
        post_ids=["1"],
        all_files_map={},
        creator_ext_checks=creator_ext_checks,
        creator_main_check=True,
        creator_attachments_check=True,
        creator_content_check=True,
        settings=settings,
        max_concurrent=1,
    )
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)

    post = {
        "file": {"path": "/files/main.png", "name": "main.png"},
        "attachments": [{"path": "/files/att.jpg", "name": "att.jpg"}],
        "content": "<p><img src='/files/incontent.gif'></p>",
    }

    domain_config = {"base_url": "https://kemono.cr"}
    files = thread.detect_files(post, [".png", ".jpg", ".gif"], domain_config)
    # Some URLs may include a `?f=` query with the original filename; compare base paths
    base_urls = [u.split("?")[0] for _, u in files]
    assert "https://kemono.cr/files/main.png" in base_urls
    assert "https://kemono.cr/files/att.jpg" in base_urls
    assert "https://kemono.cr/files/incontent.gif" in base_urls


def test_download_worker_processes_one(tmp_path):
    file_url = "https://kemono.cr/files/x.png"
    settings = SimpleNamespace(settings_tab=None, file_download_max_retries=1)
    thread = CreatorDownloadThread(
        service="svc",
        creator_id="creator123",
        download_folder=str(tmp_path),
        selected_posts=["1"],
        files_to_download=[file_url],
        files_to_posts_map={file_url: "1"},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={("svc", "creator123", "1"): "MyPost"},
        auto_rename_enabled=False,
        settings=settings,
        download_text=False,
    )
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)

    called = {"ok": False}

    async def fake_download(f_url, folder, file_index, total_files):
        called["ok"] = True
        # stop the worker loop after handling one item
        thread.is_running = False

    thread.download_file = fake_download

    async def run_worker():
        queue = asyncio.Queue()
        queue.put_nowait((0, file_url))
        await thread.download_worker(queue, str(tmp_path), total_files=1)

    asyncio.run(run_worker())
    assert called["ok"]


def test_download_text_sync_writes_file(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/x.png"
    settings = SimpleNamespace(settings_tab=None)
    thread = CreatorDownloadThread(
        service="svc",
        creator_id="creator123",
        download_folder=str(tmp_path),
        selected_posts=["1"],
        files_to_download=[file_url],
        files_to_posts_map={file_url: "1"},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={("svc", "creator123", "1"): "MyPost"},
        auto_rename_enabled=False,
        settings=settings,
        download_text=False,
    )
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)

    class FakeResp:
        status_code = 200

        def json(self):
            return {"content": "<p>This is <b>text</b></p>"}

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session",
        lambda *a, **k: SimpleNamespace(get=lambda *a, **k: FakeResp()),
    )

    post_folder = tmp_path / "post1"
    os.makedirs(post_folder, exist_ok=True)
    thread._download_text_sync("1", str(post_folder))
    desc_path = os.path.join(str(post_folder), "desc_1.txt")
    assert os.path.exists(desc_path)
    with open(desc_path, "r", encoding="utf-8") as f:
        contents = f.read()
    assert "This is" in contents
