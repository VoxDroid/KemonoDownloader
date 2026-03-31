import hashlib
import os

from kemonodownloader import post_downloader as pd


def test_filepreparation_detect_files():
    class DummySettings:
        post_data_max_retries = 1
        settings_tab = None

    post_ext_checks = {".png": True, ".jpg": True, ".gif": True}
    fthread = pd.FilePreparationThread(
        post_ids=[],
        all_files_map={},
        post_ext_checks=post_ext_checks,
        file_url_map={},
        url="https://kemono.cr/",
        settings=DummySettings(),
        max_concurrent=1,
    )

    post = {
        "file": {"path": "/uploads/image.jpg", "name": "image.jpg"},
        "attachments": [{"path": "/uploads/attach.png", "name": "attach.png"}],
        "content": '<p>Hi<img src="/uploads/content.gif"/></p>',
    }

    allowed = [".jpg", ".png", ".gif"]
    files = fthread.detect_files(post, allowed)
    names = [n for n, _ in files]
    assert "image.jpg" in names
    assert "attach.png" in names
    assert "content.gif" in names


def test_preview_thread_cache_hit(tmp_path):
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPixmap

    url = "https://kemono.cr/uploads/preview.jpg"
    cache_dir = str(tmp_path / "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_key = hashlib.md5(url.encode()).hexdigest() + os.path.splitext(url)[1]
    cache_path = os.path.join(cache_dir, cache_key)

    pix = QPixmap(10, 10)
    pix.fill(Qt.GlobalColor.white)
    assert pix.save(cache_path)

    thread = pd.PreviewThread(url, cache_dir)
    results = {}

    def on_preview(u, p):
        results["url"] = u
        results["pix"] = p

    thread.preview_ready.connect(on_preview)
    thread.run()
    assert results.get("url") == url
    assert isinstance(results.get("pix"), QPixmap)


def test_download_thread_uses_hash_db_entry(tmp_path):
    # Prepare a fake existing file and hash DB lookup
    file_content = b"hello world"
    existing = tmp_path / "existing.dat"
    existing.write_bytes(file_content)
    import hashlib as _hash

    file_hash = _hash.md5(file_content).hexdigest()
    file_url = "https://kemono.cr/files/orig.jpg"

    class DummySettings:
        file_download_max_retries = 1
        settings_tab = None

    download_folder = str(tmp_path / "downloads")
    os.makedirs(download_folder, exist_ok=True)
    thread = pd.DownloadThread(
        url="https://kemono.cr/fanbox/user/123/post/1",
        download_folder=download_folder,
        selected_files=[file_url],
        files_to_posts_map={file_url: "1"},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_id="1",
        settings=DummySettings(),
        max_concurrent=1,
        auto_rename=False,
        download_text=False,
    )

    # Monkeypatch hash_db.lookup to return our existing file entry
    url_hash = _hash.md5(file_url.encode()).hexdigest()
    thread.hash_db.lookup = lambda h: (
        {
            "file_path": str(existing),
            "file_hash": file_hash,
            "file_size": len(file_content),
        }
        if h == url_hash
        else None
    )

    # Capture signal emissions by replacing pyqt signals with dummies
    class DummySignal:
        def __init__(self):
            self.calls = []

        def emit(self, *args):
            self.calls.append(args)

    thread.file_progress = DummySignal()
    thread.file_completed = DummySignal()

    thread.download_file(file_url, download_folder, 0, 1)

    # Expect a file_progress of 100 and a successful file_completed
    assert any(call[1] == 100 for call in thread.file_progress.calls)
    assert any(call[2] is True for call in thread.file_completed.calls)
