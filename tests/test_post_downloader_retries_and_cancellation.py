import os
from types import SimpleNamespace

from kemonodownloader.post_downloader import DownloadThread, ThreadSettings


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


def make_settings(tmp_path):
    settings_tab = SimpleNamespace(settings_tab=None)
    return ThreadSettings(
        creator_posts_max_attempts=1,
        post_data_max_retries=1,
        file_download_max_retries=1,
        api_request_max_retries=1,
        simultaneous_downloads=1,
        settings_tab=settings_tab,
    )


def test_post_size_mismatch_deletes_incomplete(monkeypatch, tmp_path):
    download_folder = str(tmp_path / "pd_mismatch")
    other_files_dir = str(tmp_path / "other_pd")
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(other_files_dir, exist_ok=True)

    file_url = "https://kemono.cr/files/partial_post.png"
    selected_files = [file_url]
    files_to_posts_map = {file_url: "1"}

    chunks = [b"abc"]
    header_size = 10

    monkeypatch.setattr(
        "kemonodownloader.post_downloader.get_session",
        lambda settings_tab=None: FakeSessionMismatch(chunks, header_size),
    )

    settings = make_settings(tmp_path)
    thread = DownloadThread(
        url="https://kemono.cr/service/user/creator/post/1",
        download_folder=download_folder,
        selected_files=selected_files,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir=other_files_dir,
        post_id="1",
        settings=settings,
        max_concurrent=1,
        auto_rename=False,
        download_text=False,
    )

    # Call download_file synchronously
    thread.download_file(file_url, download_folder, 0, total_files=1)

    assert file_url not in thread.completed_files
    # Ensure no file artifacts remain
    found = []
    for root, dirs, files in os.walk(download_folder):
        for f in files:
            found.append(os.path.join(root, f))
    assert len(found) == 0


def test_post_cancellation_deletes_incomplete(monkeypatch, tmp_path):
    download_folder = str(tmp_path / "pd_cancel")
    other_files_dir = str(tmp_path / "other_pd2")
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(other_files_dir, exist_ok=True)

    file_url = "https://kemono.cr/files/cancel_post.png"
    selected_files = [file_url]
    files_to_posts_map = {file_url: "1"}

    chunks = [b"first", b"second"]

    settings = make_settings(tmp_path)
    thread = DownloadThread(
        url="https://kemono.cr/service/user/creator/post/1",
        download_folder=download_folder,
        selected_files=selected_files,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir=other_files_dir,
        post_id="1",
        settings=settings,
        max_concurrent=1,
        auto_rename=False,
        download_text=False,
    )

    monkeypatch.setattr(
        "kemonodownloader.post_downloader.get_session",
        lambda settings_tab=None: FakeSessionCancel(chunks, thread),
    )

    thread.download_file(file_url, download_folder, 0, total_files=1)

    assert file_url not in thread.completed_files
    found = []
    for root, dirs, files in os.walk(download_folder):
        for f in files:
            found.append(os.path.join(root, f))
    assert len(found) == 0


def test_post_cancellation_remove_failure_is_ignored(monkeypatch, tmp_path):
    download_folder = str(tmp_path / "pd_cancel_remove_fail")
    other_files_dir = str(tmp_path / "other_pd_cancel_remove_fail")
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(other_files_dir, exist_ok=True)

    file_url = "https://kemono.cr/files/cancel_post_remove_fail.png"
    selected_files = [file_url]
    files_to_posts_map = {file_url: "1"}

    chunks = [b"first", b"second"]

    settings = make_settings(tmp_path)
    thread = DownloadThread(
        url="https://kemono.cr/service/user/creator/post/1",
        download_folder=download_folder,
        selected_files=selected_files,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir=other_files_dir,
        post_id="1",
        settings=settings,
        max_concurrent=1,
        auto_rename=False,
        download_text=False,
    )

    monkeypatch.setattr(
        "kemonodownloader.post_downloader.get_session",
        lambda settings_tab=None: FakeSessionCancel(chunks, thread),
    )
    monkeypatch.setattr(
        "kemonodownloader.post_downloader.os.remove",
        lambda _p: (_ for _ in ()).throw(OSError("cannot remove")),
    )

    thread.download_file(file_url, download_folder, 0, total_files=1)

    assert file_url not in thread.completed_files
