import hashlib
import os

from kemonodownloader import creator_downloader as cd


class DummySignal:
    def __init__(self):
        self.emitted = False
        self.last_args = None

    def emit(self, *args):
        self.emitted = True
        self.last_args = args


def test_preview_thread_network_success(tmp_path, monkeypatch):
    # Create a valid PNG by using QPixmap -> QBuffer to ensure valid image bytes
    from PyQt6.QtCore import QBuffer, QIODevice
    from PyQt6.QtGui import QPixmap

    pix = QPixmap(1, 1)
    pix.fill()
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.ReadWrite)
    pix.save(buf, "PNG")
    png_bytes = bytes(buf.data())

    class FakeResp:
        def __init__(self):
            self.status_code = 200
            self.headers = {"content-length": str(len(png_bytes))}

        def raise_for_status(self):
            return

        def iter_content(self, chunk_size=8192):
            yield png_bytes

        def close(self):
            return

    class FakeSession:
        def get(self, url, headers=None, stream=None, timeout=None):
            return FakeResp()

    monkeypatch.setattr(cd, "get_session", lambda settings_tab=None: FakeSession())

    url = "https://kemono.cr/uploads/1.png"
    cache_dir = str(tmp_path / "cache")
    thread = cd.PreviewThread(url, cache_dir)
    sig = DummySignal()
    thread.preview_ready = sig
    thread.run()

    # Ensure preview_ready emitted and cache file exists
    assert sig.emitted is True
    cache_key = hashlib.md5(url.encode()).hexdigest() + os.path.splitext(url)[1]
    assert os.path.exists(os.path.join(cache_dir, cache_key))


def test_post_detection_thread_invalid_url_emits_error():
    class DummySettings:
        creator_posts_max_attempts = 1
        settings_tab = None

    # URL missing /user/ should trigger invalid_url_format
    t = cd.PostDetectionThread("https://kemono.cr/bad/path", {}, DummySettings())
    err = DummySignal()
    t.error = err
    t.run()
    assert err.emitted is True
