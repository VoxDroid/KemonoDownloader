import asyncio
import os
from types import SimpleNamespace

from kemonodownloader.creator_downloader import CreatorDownloadThread, ThreadSettings


class FakeResponseMismatch:
    def __init__(self, chunks, header_size):
        self._chunks = chunks
        self.status_code = 200
        self.headers = {"content-length": str(header_size)}

    def iter_content(self, chunk_size=8192):
        for c in self._chunks:
            yield c

    def raise_for_status(self):
        return None

    def close(self):
        return None


class FakeSessionMismatch:
    def __init__(self, chunks, header_size):
        self._chunks = chunks
        self._header_size = header_size

    def get(self, *args, **kwargs):
        return FakeResponseMismatch(self._chunks, self._header_size)


class FakeResponseCancel:
    def __init__(self, chunks, thread_ref):
        self._chunks = chunks
        self.status_code = 200
        self.headers = {"content-length": str(sum(len(c) for c in chunks))}
        self._thread_ref = thread_ref

    def iter_content(self, chunk_size=8192):
        first = True
        for c in self._chunks:
            if first:
                first = False
                yield c
            else:
                # Simulate user cancellation just before next chunk is processed
                try:
                    self._thread_ref.stop()
                except Exception:
                    pass
                yield c

    def raise_for_status(self):
        return None

    def close(self):
        return None


class FakeSessionCancel:
    def __init__(self, chunks, thread_ref):
        self._chunks = chunks
        self._thread_ref = thread_ref

    def get(self, *args, **kwargs):
        return FakeResponseCancel(self._chunks, self._thread_ref)


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


def test_size_mismatch_deletes_incomplete_and_records_failure(monkeypatch, tmp_path):
    download_folder = str(tmp_path / "d_mismatch")
    other_files_dir = str(tmp_path / "other_mismatch")
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(other_files_dir, exist_ok=True)

    file_url = "https://kemono.cr/files/partial.png"
    files_to_download = [file_url]
    files_to_posts_map = {file_url: "1"}

    # Chunks smaller than header indicates → triggers size-mismatch path
    chunks = [b"abc"]
    header_size = 10

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session",
        lambda settings_tab=None: FakeSessionMismatch(chunks, header_size),
    )

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

    asyncio.run(thread.download_file(file_url, download_folder, 0, total_files=1))

    assert file_url not in thread.completed_files
    assert file_url in thread.failed_files
    msg = thread.failed_files[file_url]
    assert "Size mismatch" in msg or "size mismatch" in msg.lower()

    # Ensure no file artifacts remain under download_folder
    found_files = []
    for root, dirs, files in os.walk(download_folder):
        for f in files:
            found_files.append(os.path.join(root, f))
    assert len(found_files) == 0


def test_cancellation_during_streaming_deletes_incomplete_and_records_failure(
    monkeypatch, tmp_path
):
    download_folder = str(tmp_path / "d_cancel")
    other_files_dir = str(tmp_path / "other_cancel")
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(other_files_dir, exist_ok=True)

    file_url = "https://kemono.cr/files/cancel.png"
    files_to_download = [file_url]
    files_to_posts_map = {file_url: "1"}

    chunks = [b"first", b"second"]

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

    # Monkeypatch get_session AFTER thread is created so the FakeSessionCancel
    # can call thread.stop() during iteration.
    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session",
        lambda settings_tab=None: FakeSessionCancel(chunks, thread),
    )

    asyncio.run(thread.download_file(file_url, download_folder, 0, total_files=1))

    # Cancellation should result in a failure and no completed file
    assert file_url not in thread.completed_files
    assert file_url in thread.failed_files

    # Ensure no file artifacts remain under download_folder
    found_files = []
    for root, dirs, files in os.walk(download_folder):
        for f in files:
            found_files.append(os.path.join(root, f))
    assert len(found_files) == 0
