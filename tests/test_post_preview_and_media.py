import os
from types import SimpleNamespace

from kemonodownloader import post_downloader as pd


class SimpleSignal:
    def __init__(self):
        self._cb = None

    def connect(self, cb):
        self._cb = cb

    def emit(self, *args):
        if self._cb:
            self._cb(*args)


def test_preview_thread_network_success_post(tmp_path, monkeypatch):
    # Generate valid PNG bytes via QPixmap->QBuffer
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

    monkeypatch.setattr(pd, "get_session", lambda settings_tab=None: FakeSession())

    url = "https://kemono.cr/uploads/1.png"
    cache_dir = str(tmp_path / "cache")
    thread = pd.PreviewThread(url, cache_dir)
    sig = SimpleSignal()
    thread.preview_ready = sig
    thread.run()

    cache_key = pd.hashlib.md5(url.encode()).hexdigest() + os.path.splitext(url)[1]
    assert os.path.exists(os.path.join(cache_dir, cache_key))


def test_media_preview_modal_display_and_error(monkeypatch, tmp_path):
    # Replace PreviewThread with a fake that does not start network activity
    class FakePreviewThread:
        def __init__(self, url, cache_dir, settings_tab):
            self.preview_ready = SimpleSignal()
            self.progress = SimpleSignal()
            self.error = SimpleSignal()

        def start(self):
            return

    monkeypatch.setattr(pd, "PreviewThread", FakePreviewThread)

    # Build a fake tab_parent with parent.settings_tab and append_log_to_console
    from PyQt6.QtWidgets import QWidget

    tab_parent = QWidget()
    tab_parent.parent = SimpleNamespace(settings_tab=None)
    tab_parent.append_log_to_console = lambda *a, **k: None

    # Create a small PNG file to act as media
    from PyQt6.QtGui import QPixmap

    media_path = str(tmp_path / "img.png")
    p = QPixmap(1, 1)
    p.fill()
    assert p.save(media_path)

    modal = pd.MediaPreviewModal.__new__(pd.MediaPreviewModal)
    # Construct via __init__ path but avoid double-start: call real __init__ with fake PreviewThread
    modal.__init__(media_path, str(tmp_path / "cache"), tab_parent)

    # Test update_progress creates a loading label
    modal.update_progress(30)
    assert modal.progress_bar.value() == 30

    # Test display_image with a PNG path
    modal.display_image(media_path, media_path)
    assert hasattr(modal, "content_label")

    # Test display_error uses QMessageBox.critical (monkeypatch to avoid dialog)
    called = {}

    def fake_critical(*a, **k):
        called["ok"] = True

    monkeypatch.setattr(pd, "QMessageBox", SimpleNamespace(critical=fake_critical))
    modal.display_error("err")
    assert called.get("ok") is True
