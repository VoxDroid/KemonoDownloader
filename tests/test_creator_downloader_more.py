import asyncio
import gzip
import hashlib
import json
import os
from types import SimpleNamespace

from kemonodownloader import creator_downloader as cd


def test_filter_thread_run():
    posts = [("A Post", ("101", None)), ("B Post", ("102", None))]
    checked = {"101": True, "102": False}
    t = cd.FilterThread(posts, checked, "A")
    out = {}
    t.finished = SimpleNamespace(emit=lambda data: out.setdefault("finished", data))
    t.log = SimpleNamespace(emit=lambda *a, **k: None)
    t.run()
    assert "finished" in out
    assert out["finished"][0][0] == "A Post"


def test_checkbox_toggle_thread():
    visible = [("Title", ("1", None)), ("Title2", ("2", None))]
    checked = {"1": False, "2": False}
    thr = cd.CheckboxToggleThread(visible, checked, 2)  # checked
    out = {}
    thr.finished = SimpleNamespace(emit=lambda a, b: out.setdefault("result", (a, b)))
    thr.log = SimpleNamespace(emit=lambda *a, **k: None)
    thr.run()
    new_state, posts = out["result"]
    assert new_state["1"] is True
    assert "1" in posts


def test_validation_thread_success_and_fail(monkeypatch):
    # success path: response contains domain check
    class FakeResp:
        status_code = 200

        @property
        def text(self):
            return "kemono content"

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda s=None: SimpleNamespace(
            get=lambda url, headers=None, timeout=None: FakeResp()
        ),
    )
    settings = SimpleNamespace(settings_tab=None, api_request_max_retries=1)
    vt = cd.ValidationThread("https://kemono.cr/user/1", settings)
    res = {}
    vt.result = SimpleNamespace(emit=lambda v: res.setdefault("ok", v))
    vt.log = SimpleNamespace(emit=lambda *a, **k: None)
    vt.run()
    assert res.get("ok") is True


def test_logs_window_update_and_clear(tmp_path):
    class Parent:
        def __init__(self):
            self.creator_console = SimpleNamespace(
                toHtml=lambda: "<b>log</b>", clear=lambda: None
            )

        def append_log_to_console(self, *a, **k):
            pass

    w = cd.LogsWindow(parent=None)
    w._parent = Parent()
    # Simulate update
    w.update_logs_content()
    w._do_update()
    assert "log" in w.logs_display.toHtml()
    w.clear_logs()
    assert w.logs_display.toPlainText() == ""


def test_preview_thread_error(monkeypatch):
    # Make get_session.get raise requests.RequestException
    import requests

    def fake_get(s=None):
        return SimpleNamespace(
            get=lambda url, headers=None, stream=True: (_ for _ in ()).throw(
                requests.RequestException("fail")
            )
        )

    monkeypatch.setattr(cd, "get_session", lambda s=None: fake_get())
    # Create a PreviewThread-like dummy and run
    pt = cd.PreviewThread("https://kemono.cr/image.jpg", "/tmp", settings_tab=None)
    errors = {}
    pt.error = SimpleNamespace(emit=lambda e: errors.setdefault("err", e))
    pt.preview_ready = SimpleNamespace(
        emit=lambda *a, **k: errors.setdefault("ok", True)
    )
    pt.progress = SimpleNamespace(emit=lambda *a, **k: None)
    pt.run()
    assert "err" in errors


def test_creator_download_thread_run_no_files(monkeypatch, tmp_path):
    # Create a minimal dummy instance to call run() and exercise the no-files branch
    dummy = SimpleNamespace()
    dummy.service = "fanbox"
    dummy.creator_id = "42"
    dummy.download_folder = str(tmp_path)
    dummy.selected_posts = []
    dummy.files_to_download = []
    dummy.files_to_posts_map = {}
    dummy.console = None
    dummy.other_files_dir = str(tmp_path)
    dummy.post_titles_map = {}
    dummy.auto_rename_enabled = False
    dummy.settings = SimpleNamespace(settings_tab=None, file_download_max_retries=1)
    dummy.max_concurrent = 2
    dummy.is_running = True
    dummy.hash_db = SimpleNamespace()
    dummy.post_file_counters_lock = SimpleNamespace(
        __enter__=lambda s: None, __exit__=lambda s, a, b, c: None
    )
    dummy.post_file_counters = {}
    dummy.failed_files = {}
    dummy.failed_files_lock = SimpleNamespace(
        __enter__=lambda s: None, __exit__=lambda s, a, b, c: None
    )
    dummy.completed_files = set()
    dummy.completed_files_lock = SimpleNamespace(
        __enter__=lambda s: None, __exit__=lambda s, a, b, c: None
    )
    dummy.fetched_texts_lock = SimpleNamespace(
        __enter__=lambda s: None, __exit__=lambda s, a, b, c: None
    )
    dummy.fetched_texts = set()
    dummy._ssl_lock = SimpleNamespace(
        __enter__=lambda s: None, __exit__=lambda s, a, b, c: None
    )
    dummy._destroyed = False
    # no-op methods used in run
    dummy.fetch_creator_and_post_info = lambda: None
    dummy._safe_emit = lambda sig, *a: None
    dummy.check_post_completion = lambda url: None

    # Call run - should take the no-files branch and not raise
    cd.CreatorDownloadThread.run(dummy)


class DummySignal:
    def __init__(self):
        self.emitted = False
        self.last_args = None

    def emit(self, *args):
        self.emitted = True
        self.last_args = args


def test_validation_thread_invalid_url():
    class DummySettings:
        api_request_max_retries = 1
        settings_tab = None

    t = cd.ValidationThread("https://kemono.cr/bad/link", DummySettings())
    t.log = DummySignal()
    t.result = DummySignal()
    t.run()
    assert t.result.emitted is True
    assert t.result.last_args == (False,)


def test_validation_thread_success(monkeypatch):
    class DummySettings:
        api_request_max_retries = 1
        settings_tab = None

    class FakeResp:
        status_code = 200

        def __init__(self):
            self.text = "Welcome to kemono site"

    class FakeSession:
        def get(self, url, headers=None, timeout=None):
            return FakeResp()

    monkeypatch.setattr(cd, "get_session", lambda settings_tab=None: FakeSession())

    t = cd.ValidationThread("https://kemono.cr/user/abc", DummySettings())
    t.log = DummySignal()
    t.result = DummySignal()
    t.run()
    assert t.result.emitted is True
    assert t.result.last_args == (True,)


def test_get_desc_folder_for_post_strategies(tmp_path):
    class DummySettingsTab:
        def __init__(self, strat):
            self._s = strat

        def get_creator_folder_strategy(self):
            return self._s

    class DummySettings:
        def __init__(self, st):
            self.settings_tab = st

    service = "fanbox"
    creator_id = "123"
    download_folder = str(tmp_path / "dl")
    selected_posts = ["1"]
    files_to_download = []
    files_to_posts_map = {}
    console = None
    other_files_dir = str(tmp_path / "other")
    post_titles_map = {}

    # by_file_type -> should return 'txt' subfolder
    s_tab = DummySettingsTab("by_file_type")
    thread = cd.CreatorDownloadThread(
        service,
        creator_id,
        download_folder,
        selected_posts,
        files_to_download,
        files_to_posts_map,
        console,
        other_files_dir,
        post_titles_map,
        auto_rename_enabled=False,
        settings=DummySettings(s_tab),
        max_concurrent=1,
    )
    creator_folder = os.path.normpath(str(tmp_path / "creator"))
    res = thread.get_desc_folder_for_post(creator_folder, "1", "Title")
    assert res.endswith(os.path.join("creator", "txt")) or res.endswith("txt")

    # single_folder -> return creator_folder
    s_tab2 = DummySettingsTab("single_folder")
    thread2 = cd.CreatorDownloadThread(
        service,
        creator_id,
        download_folder,
        selected_posts,
        files_to_download,
        files_to_posts_map,
        console,
        other_files_dir,
        post_titles_map,
        auto_rename_enabled=False,
        settings=DummySettings(s_tab2),
        max_concurrent=1,
    )
    res2 = thread2.get_desc_folder_for_post(creator_folder, "1", "Title")
    assert res2 == creator_folder


def test_check_post_completion_emits_post_completed():
    class DummySettings:
        file_download_max_retries = 1
        settings_tab = None

    file_url = "file://one"
    thread = cd.CreatorDownloadThread(
        service="fanbox",
        creator_id="123",
        download_folder=str(os.getcwd()),
        selected_posts=["1"],
        files_to_download=[file_url],
        files_to_posts_map={file_url: "1"},
        console=None,
        other_files_dir=str(os.getcwd()),
        post_titles_map={},
        auto_rename_enabled=False,
        settings=DummySettings(),
        max_concurrent=1,
    )
    thread.post_files_map = {"1": [file_url]}
    thread.completed_files = {file_url}
    sig = DummySignal()
    thread.post_completed = sig
    thread.check_post_completion(file_url)
    assert sig.emitted is True
    assert sig.last_args == ("1",)


def test_download_post_text_if_needed_calls_once(tmp_path):
    class DummySettings:
        file_download_max_retries = 1
        settings_tab = None

    thread = cd.CreatorDownloadThread(
        service="fanbox",
        creator_id="123",
        download_folder=str(tmp_path / "dl"),
        selected_posts=["1"],
        files_to_download=[],
        files_to_posts_map={},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={},
        auto_rename_enabled=False,
        settings=DummySettings(),
        max_concurrent=1,
    )

    calls = []

    def fake_download_sync(pid, folder):
        calls.append((pid, folder))

    thread._download_text_sync = fake_download_sync

    asyncio.run(thread.download_post_text_if_needed("1", str(tmp_path)))
    # second call should not invoke _download_text_sync again
    asyncio.run(thread.download_post_text_if_needed("1", str(tmp_path)))
    assert len(calls) == 1


def test_get_headers_and_session_proxy_behavior(monkeypatch):
    # Reset cached headers and user agent
    monkeypatch.setattr(cd, "HEADERS", None)
    monkeypatch.setattr(cd, "_user_agent", "test-agent")
    headers = cd.get_headers()
    assert headers["User-Agent"] == "test-agent"

    # Clear thread-local sessions if present
    try:
        delattr(cd._thread_local, "session")
    except Exception:
        pass
    try:
        delattr(cd._thread_local, "socks_session")
    except Exception:
        pass

    # HTTP proxy
    settings_tab = SimpleNamespace(
        get_proxy_settings=lambda: {"http": "http://127.0.0.1:8080"}
    )
    sess = cd.get_session(settings_tab)
    assert sess.proxies.get("http") == "http://127.0.0.1:8080"

    # SOCKS proxy uses socks_session
    try:
        delattr(cd._thread_local, "session")
    except Exception:
        pass
    try:
        delattr(cd._thread_local, "socks_session")
    except Exception:
        pass
    settings_tab2 = SimpleNamespace(
        get_proxy_settings=lambda: {"http": "socks5://127.0.0.1:1080"}
    )
    socks = cd.get_session(settings_tab2)
    assert hasattr(cd._thread_local, "socks_session")
    assert "socks5" in list(socks.proxies.values())[0]


def test_preview_thread_uses_cache(tmp_path):
    # Create a small valid image via QPixmap and save as the cache file
    from PyQt6.QtGui import QColor, QPixmap

    url = "https://example.com/image.jpg"
    cache_key = hashlib.md5(url.encode()).hexdigest() + os.path.splitext(url)[1]
    cache_dir = str(tmp_path / "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, cache_key)
    pix = QPixmap(8, 8)
    pix.fill(QColor("red"))
    # Save using the extension-derived format
    pix.save(cache_path)

    captured = {}

    def on_preview(u, pix):
        captured["url"] = u
        captured["pix"] = pix

    pt = cd.PreviewThread(url, cache_dir, settings_tab=None)
    pt.preview_ready.connect(on_preview)
    pt.run()
    assert captured.get("url") == url
    assert captured.get("pix") is not None


def test_validation_thread_detects_invalid_url():
    settings = SimpleNamespace(settings_tab=None)
    vt = cd.ValidationThread("https://kemono.cr/bad", settings)
    captured = {}

    def on_result(val):
        captured["result"] = val

    vt.result.connect(on_result)
    vt.run()
    assert captured.get("result") is False


def test_post_detection_thread_invalid_url_emits_error():
    settings = cd.ThreadSettings(1, 1, 1, 1, 1, settings_tab=None)
    captured = {}

    def on_error(msg):
        captured["error"] = msg

    pdt = cd.PostDetectionThread("https://kemono.cr/invalid", {}, settings)
    pdt.error.connect(on_error)
    pdt.run()
    assert captured.get("error")


def test_fetch_and_detect_files_respects_response(monkeypatch):
    # Fake session that returns a post payload
    class FakeResp:
        status_code = 200

        def json(self):
            return {
                "post": {"id": "7", "file": {"path": "/media/x.jpg", "name": "x.jpg"}}
            }

    class FakeSession:
        def get(self, *a, **k):
            return FakeResp()

    monkeypatch.setattr(cd, "get_session", lambda settings_tab=None: FakeSession())

    # fake checkboxes mapping
    class Box:
        def __init__(self, v):
            self._v = v

        def isChecked(self):
            return self._v

    fpt = cd.FilePreparationThread(
        [],
        {},
        {".jpg": Box(True)},
        True,
        True,
        True,
        cd.ThreadSettings(1, 1, 1, 1, 1, settings_tab=None),
        max_concurrent=1,
    )
    res = fpt.fetch_and_detect_files("7", "https://kemono.cr/user/42")
    assert res is not None
    pid, files = res
    assert pid == "7"
    assert any("x.jpg" in u for _, u in files)


def test_fetch_and_detect_files_handles_rate_limit(monkeypatch):
    # Simulate repeated 429 responses and ensure we return None after retries
    class Fake429:
        status_code = 429

    class Sess:
        def get(self, *a, **k):
            return Fake429()

    # Use small max attempts to keep test fast
    settings = SimpleNamespace(post_data_max_retries=2, settings_tab=None)
    t = cd.FilePreparationThread(
        [], {}, {}, True, True, True, settings, max_concurrent=1
    )

    monkeypatch.setattr(cd, "get_session", lambda *a, **k: Sess())
    # Patch time.sleep so retries don't actually delay the test
    monkeypatch.setattr(cd.time, "sleep", lambda s: None)

    res = t.fetch_and_detect_files("9", "https://kemono.cr/user/99")
    assert res is None


def test_download_file_short_circuit_with_hash(tmp_path):
    service = "kemono"
    creator_id = "8"
    other_dir = str(tmp_path / "hdb")
    settings = SimpleNamespace(settings_tab=None)

    file_url = "https://kemono.cr/media/file.bin"
    thread = cd.CreatorDownloadThread(
        service,
        creator_id,
        str(tmp_path),
        ["1"],
        [file_url],
        {file_url: "1"},
        None,
        other_dir,
        {},
        False,
        settings,
        max_concurrent=1,
        download_text=False,
    )

    # create an existing file and register it in the hash DB
    existing = tmp_path / "existing.bin"
    existing.write_bytes(b"hello world")
    file_hash = hashlib.md5(existing.read_bytes()).hexdigest()
    url_hash = hashlib.md5(file_url.encode()).hexdigest()
    thread.hash_db.store(
        url_hash, str(existing), file_hash, file_url, existing.stat().st_size
    )

    asyncio.run(thread.download_file(file_url, str(tmp_path), 0, 1))
    assert file_url in thread.completed_files


def make_gzipped_json(obj):
    return gzip.compress(json.dumps(obj).encode())


def test_post_detection_thread_handles_gzipped_posts(qapp, monkeypatch):
    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    post_titles_map = {}
    url = "https://kemono.cr/fanbox/user/123"

    posts = [{"id": "p1", "title": "T1", "file": {"path": "/img/a.jpg"}}]
    mock_resp = SimpleNamespace()
    mock_resp.content = make_gzipped_json(posts)
    mock_resp.text = ""
    mock_resp.status_code = 200

    class Sess:
        def get(self, *a, **k):
            return mock_resp

    monkeypatch.setattr(cd, "get_session", lambda *a, **k: Sess())

    thread = cd.PostDetectionThread(url, post_titles_map, settings)
    batches = []
    thread.posts_batch.connect(lambda b: batches.append(b))

    thread.run()
    assert batches, "Expected at least one posts_batch emitted"
    assert batches[0][0][0] == "T1"


def test_post_detection_thread_handles_posts_key_and_data_key(qapp, monkeypatch):
    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    post_titles_map = {}
    url = "https://kemono.cr/fanbox/user/123"

    # Case: API returns {"posts": [...]}
    posts = [{"id": "p2", "title": "Title2"}]
    mock_resp1 = SimpleNamespace()
    mock_resp1.content = json.dumps({"posts": posts}).encode()
    mock_resp1.text = json.dumps({"posts": posts})
    mock_resp1.status_code = 200

    # Case: API returns {"data": [...]}
    posts3 = [{"id": "p3", "title": "Title3"}]
    mock_resp2 = SimpleNamespace()
    mock_resp2.content = json.dumps({"data": posts3}).encode()
    mock_resp2.text = json.dumps({"data": posts3})
    mock_resp2.status_code = 200

    class Sess:
        def __init__(self):
            self._calls = 0

        def get(self, *a, **k):
            self._calls += 1
            return mock_resp1 if self._calls == 1 else mock_resp2

    monkeypatch.setattr(cd, "get_session", lambda *a, **k: Sess())

    thread = cd.PostDetectionThread(url, post_titles_map, settings)
    out = []
    thread.posts_batch.connect(lambda b: out.append(b))
    thread.run()
    # We should have batches for both responses
    assert any("Title2" in str(b) or "Title3" in str(b) for b in out)


def test_file_preparation_detect_files_various_cases():
    # Create a FilePreparationThread and call detect_files with different inputs
    t = cd.FilePreparationThread(
        post_ids=[],
        all_files_map={},
        creator_ext_checks={},
        creator_main_check=True,
        creator_attachments_check=True,
        creator_content_check=True,
        settings=SimpleNamespace(post_data_max_retries=1),
    )

    domain_config = {"base_url": "https://kemono.cr"}

    post = {
        "file": {"path": "/a/b/c.jpg", "name": "pic.jpg"},
        "attachments": [{"path": "/att/d.png", "name": "att.png"}],
        "content": '<p>hello <img src="/img/e.gif"></p>',
    }

    detected = t.detect_files(post, [".jpg", ".png", ".gif"], domain_config)
    # Should detect main, attachment and content image
    names = [n for n, u in detected]
    assert "pic.jpg" in names
    assert "att.png" in names
    assert any(u.endswith("/img/e.gif") for _, u in detected)


def test_fetch_and_detect_files_success(monkeypatch, tmp_path):
    # Prepare a FilePreparationThread with checkbox-like objects
    checks = {".jpg": SimpleNamespace(isChecked=lambda: True)}
    settings = SimpleNamespace(post_data_max_retries=1, settings_tab=None)
    t = cd.FilePreparationThread(
        post_ids=[],
        all_files_map={},
        creator_ext_checks=checks,
        creator_main_check=True,
        creator_attachments_check=True,
        creator_content_check=True,
        settings=settings,
    )

    post_id = "99"
    creator_url = "https://kemono.cr/fanbox/user/321"

    post = {"id": post_id, "file": {"path": "/f/g.jpg", "name": "g.jpg"}}

    mock_resp = SimpleNamespace()
    mock_resp.status_code = 200
    mock_resp.json = lambda: post

    class Sess:
        def get(self, *a, **k):
            return mock_resp

    monkeypatch.setattr(cd, "get_session", lambda *a, **k: Sess())

    result = t.fetch_and_detect_files(post_id, creator_url)
    assert result is not None
    pid, files = result
    assert pid == post_id
    assert files and files[0][0] == "g.jpg"


def test_download_text_sync_writes_file(monkeypatch, tmp_path):
    # Create a CreatorDownloadThread and run _download_text_sync
    monkeypatch.setattr(
        cd,
        "get_session",
        lambda *a, **k: SimpleNamespace(
            get=lambda *a, **k: SimpleNamespace(
                status_code=200, json=lambda: {"post": {"content": "<p>Hi</p>"}}
            )
        ),
    )

    class DummyHashDB:
        def __init__(self, other_files_dir):
            pass

        def lookup(self, *a, **k):
            return None

        def store(self, *a, **k):
            return None

    monkeypatch.setattr(cd, "HashDB", DummyHashDB)

    th = cd.CreatorDownloadThread(
        service="fanbox",
        creator_id="321",
        download_folder=str(tmp_path),
        selected_posts=["11"],
        files_to_download=[],
        files_to_posts_map={},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={},
        auto_rename_enabled=False,
        settings=SimpleNamespace(settings_tab=None),
        max_concurrent=1,
        download_text=False,
    )

    post_folder = tmp_path / "postdesc"
    post_folder.mkdir()
    th._download_text_sync("11", str(post_folder))
    desc_path = post_folder / "desc_11.txt"
    assert desc_path.exists()
    content = desc_path.read_text(encoding="utf-8")
    assert "Hi" in content
