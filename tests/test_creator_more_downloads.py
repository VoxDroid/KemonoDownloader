import asyncio
import gzip
import hashlib
import os
from types import SimpleNamespace

from kemonodownloader.creator_downloader import (
    CreatorDownloadThread,
    PostDetectionThread,
    ThreadSettings,
)


def make_settings():
    return ThreadSettings(
        creator_posts_max_attempts=1,
        post_data_max_retries=1,
        file_download_max_retries=1,
        api_request_max_retries=1,
        simultaneous_downloads=1,
        settings_tab=None,
    )


def test_post_detection_handles_gzipped_response(monkeypatch):
    post_titles_map = {}
    settings = make_settings()
    url = "https://kemono.cr/service/user/123"

    thread = PostDetectionThread(url, post_titles_map, settings)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    data = [{"id": "1", "title": "Gzip Post"}]
    compressed = gzip.compress(bytes(__import__("json").dumps(data), "utf-8"))

    def fake_get_session(settings_tab=None):
        def get(u, *a, **k):
            return SimpleNamespace(status_code=200, content=compressed, text="")

        return SimpleNamespace(get=get)

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session", fake_get_session
    )

    thread.run()
    assert ("service", "123", "1") in post_titles_map


def test_generate_filename_by_file_type_and_creator_folder(tmp_path):
    file_url = "https://kemono.cr/files/photo.png"
    settings_tab = SimpleNamespace(
        get_creator_filename_template=lambda: None,
        get_creator_folder_strategy=lambda: "by_file_type",
    )
    settings = ThreadSettings(
        creator_posts_max_attempts=1,
        post_data_max_retries=1,
        file_download_max_retries=1,
        api_request_max_retries=1,
        simultaneous_downloads=1,
        settings_tab=settings_tab,
    )
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
    # Ensure a readable creator name so creator folder becomes creator123_Alice
    thread.creator_name = "Alice"
    # Pass folder that already ends with creator folder name
    creator_folder = os.path.join(str(tmp_path), "creator123_Alice")
    target_folder, filename = thread.generate_filename_and_folder(
        file_url, creator_folder, 0, 1, "1", "MyPost"
    )
    # Expect subfolder by file type
    assert target_folder.endswith(os.path.join("creator123_Alice", "png"))
    assert filename.endswith(".png")


def test_download_file_skips_when_hash_matches(tmp_path):
    file_url = "https://kemono.cr/files/existing.png"
    download_folder = str(tmp_path / "dl")
    other_files_dir = str(tmp_path / "other")
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(other_files_dir, exist_ok=True)

    # Create existing file in other_files_dir
    existing_path = os.path.join(other_files_dir, "existing.png")
    with open(existing_path, "wb") as f:
        f.write(b"contents")
    file_hash = hashlib.md5(open(existing_path, "rb").read()).hexdigest()
    file_size = os.path.getsize(existing_path)

    settings = make_settings()
    thread = CreatorDownloadThread(
        service="svc",
        creator_id="creator123",
        download_folder=download_folder,
        selected_posts=["1"],
        files_to_download=[file_url],
        files_to_posts_map={file_url: "1"},
        console=None,
        other_files_dir=other_files_dir,
        post_titles_map={("svc", "creator123", "1"): "MyPost"},
        auto_rename_enabled=False,
        settings=settings,
        download_text=False,
    )

    class FakeHashDB:
        def lookup(self, url_hash):
            return {
                "file_path": existing_path,
                "file_hash": file_hash,
                "file_size": file_size,
            }

    thread.hash_db = FakeHashDB()
    called = []
    thread.file_completed = SimpleNamespace(emit=lambda *a, **k: called.append(True))

    asyncio.run(thread.download_file(file_url, download_folder, 0, total_files=1))
    assert file_url in thread.completed_files
    assert called
