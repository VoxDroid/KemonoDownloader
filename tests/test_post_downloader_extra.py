import hashlib
import os

from kemonodownloader import kd_network


def test_get_user_agent_fallback(monkeypatch):
    import kemonodownloader.post_downloader as pd

    # Force UserAgent() to raise so fallback is used
    class BadUA:
        def __init__(self):
            raise Exception("no ua")

    monkeypatch.setattr(kd_network, "UserAgent", BadUA)
    # Reset cached value
    monkeypatch.setattr(kd_network, "_user_agent", None)
    ua = pd.get_user_agent()
    assert "Mozilla/5.0" in ua


def test_get_domain_config():
    import kemonodownloader.post_downloader as pd

    cfg = pd.get_domain_config("https://coomer.st/post/1")
    assert cfg["domain"] == "coomer.st"
    cfg2 = pd.get_domain_config("https://kemono.cr/post/1")
    assert cfg2["domain"] == "kemono.cr"


def test_get_headers_cached(monkeypatch):
    import kemonodownloader.post_downloader as pd

    # Reset HEADERS
    monkeypatch.setattr(kd_network, "HEADERS", None)
    h1 = pd.get_headers()
    h2 = pd.get_headers()
    assert h1 is h2


def test_preview_thread_cached_jpg(monkeypatch, tmp_path):
    import kemonodownloader.post_downloader as pd

    url = "http://example.com/img.jpg"
    cache_dir = str(tmp_path)
    ext = ".jpg"
    cache_key = hashlib.md5(url.encode()).hexdigest() + ext
    cache_path = os.path.join(cache_dir, cache_key)

    # Create a dummy cache file
    with open(cache_path, "wb") as f:
        f.write(b"data")

    # Ensure QPixmap.load returns True
    monkeypatch.setattr(pd.QPixmap, "load", lambda self, p: True)

    results = []

    thread = pd.PreviewThread(url, cache_dir)
    thread.preview_ready.connect(lambda u, o: results.append((u, o)))
    thread.run()

    assert results and results[0][0] == url


def test_preview_thread_download_invalid_image(monkeypatch, tmp_path):
    import kemonodownloader.post_downloader as pd

    url = "http://example.com/img.jpg"
    cache_dir = str(tmp_path)

    # Mock session.get to return a response with content that is not an image
    class MockResp:
        def __init__(self):
            self.headers = {"content-length": "4"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            yield b"abcd"

    class MockSession:
        def get(self, url, headers=None, stream=False):
            return MockResp()

    monkeypatch.setattr(pd, "get_session", lambda s: MockSession())
    monkeypatch.setattr(pd, "get_headers", lambda: {})

    # Make loadFromData fail to exercise error path
    monkeypatch.setattr(pd.QPixmap, "loadFromData", lambda self, b: False)

    errors = []
    thread = pd.PreviewThread(url, cache_dir)
    thread.error.connect(lambda e: errors.append(e))
    thread.run()

    assert errors
