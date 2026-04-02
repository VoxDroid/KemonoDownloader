import asyncio
import gzip
import hashlib
import json
import os
from types import SimpleNamespace

from kemonodownloader import creator_downloader as cd


def test_sanitize_filename_and_domain():
    assert cd.sanitize_filename("Hello World.jpg") == "Hello_World.jpg"
    assert cd.sanitize_filename("") == "unnamed"
    cfg = cd.get_domain_config("https://coomer.st/user/1")
    assert cfg["domain"] == "coomer.st"


def make_settings(filename_template=None, strategy="per_post"):
    settings_tab = SimpleNamespace()
    settings_tab.get_creator_filename_template = lambda: filename_template
    settings_tab.get_creator_folder_strategy = lambda: strategy
    return SimpleNamespace(settings_tab=settings_tab)


def test_generate_filename_and_folder_variants(tmp_path):
    # Create a dummy instance (not a real QThread) with required attributes
    dummy = SimpleNamespace()
    dummy.service = "fanbox"
    dummy.creator_id = "42"
    dummy.post_titles_map = {("fanbox", "42", "101"): "My Post"}
    dummy.creator_name = "Creator"
    dummy.auto_rename_enabled = True
    dummy.post_file_counters = {}
    import threading

    dummy.post_file_counters_lock = threading.Lock()
    # Default settings (no template)
    dummy.settings = make_settings(None, "per_post")

    target_folder, filename = cd.CreatorDownloadThread.generate_filename_and_folder(
        dummy,
        "https://kemono.cr/files/img.png?f=orig.png",
        str(tmp_path),
        0,
        1,
        "101",
        "My Post",
    )
    assert "42_Creator" in target_folder
    assert filename.endswith(".png")

    # by_file_type strategy
    dummy.settings = make_settings("{post_id}_{orig_name}", "by_file_type")
    tf, fn = cd.CreatorDownloadThread.generate_filename_and_folder(
        dummy,
        "https://kemono.cr/files/doc.pdf",
        str(tmp_path),
        0,
        1,
        "101",
        "My Post",
    )
    assert os.path.basename(tf) == "pdf"


def test_get_desc_folder_for_post(tmp_path):
    dummy = SimpleNamespace()
    dummy.settings = make_settings(None, "single_folder")
    folder = cd.CreatorDownloadThread.get_desc_folder_for_post(
        dummy, str(tmp_path), "101", "Title"
    )
    assert folder == str(tmp_path)
    dummy.settings = make_settings(None, "by_file_type")
    folder2 = cd.CreatorDownloadThread.get_desc_folder_for_post(
        dummy, str(tmp_path), "101", "Title"
    )
    assert folder2.endswith("txt")


def test_file_preparation_detect_files():
    # Test the detect_files helper with main file, attachments and content images

    settings = SimpleNamespace()
    # enable all detection checks
    fpt = cd.FilePreparationThread([], {}, {}, True, True, True, settings)
    post = {
        "id": "101",
        "file": {"path": "/media/img1.jpg", "name": "img1.jpg"},
        "attachments": [{"path": "/media/att.zip", "name": "att.zip"}],
        "content": '<p>Some text <img src="/media/inline.png"/></p>',
    }
    domain = {"base_url": "https://kemono.cr"}
    files = fpt.detect_files(post, [".jpg", ".zip", ".png"], domain)
    # Should include main file, attachment and content image
    names = [n for n, u in files]
    assert any("img1" in n for n in names)
    assert any("att" in n for n in names)
    assert any("inline" in n for n in names)


def _make_fake_response(content_bytes, status=200, headers=None):
    class FakeResp:
        def __init__(self, content, status, headers):
            self.content = content
            self.status_code = status
            self._headers = headers or {}

        @property
        def text(self):
            try:
                return self.content.decode("utf-8")
            except Exception:
                return ""

        def json(self):
            return json.loads(self.text)

        def raise_for_status(self):
            if not (200 <= self.status_code < 300):
                raise Exception("status")

        def close(self):
            pass

        def iter_content(self, chunk_size=8192):
            # yield the entire content as single chunk
            yield self.content

        @property
        def headers(self):
            return self._headers

    return FakeResp(content_bytes, status, headers)


def test_post_detection_thread_plain_and_gzipped(monkeypatch):
    # Prepare gzipped JSON list response
    posts = [{"id": "101", "title": "Hello"}]
    gz = gzip.compress(json.dumps(posts).encode())

    def fake_get(session_tab=None):
        return SimpleNamespace(
            get=lambda url, headers=None, timeout=None: _make_fake_response(gz)
        )

    monkeypatch.setattr(cd, "get_session", lambda s=None: fake_get())

    post_titles_map = {}
    settings = SimpleNamespace(settings_tab=None, creator_posts_max_attempts=1)
    thread = cd.PostDetectionThread(
        "https://kemono.cr/user/42", post_titles_map, settings
    )

    collected = {}

    # Replace signals with simple emit capture
    thread.posts_batch = SimpleNamespace(
        emit=lambda data: collected.setdefault("batch", data)
    )
    thread.finished = SimpleNamespace(
        emit=lambda data: collected.setdefault("finished", data)
    )
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda e: collected.setdefault("error", e))

    thread.run()
    assert "finished" in collected
    assert (
        collected["finished"][0][0].startswith("Hello")
        or collected["finished"][0][0] == "Hello"
    )


def test_download_file_skips_when_hash_matches(tmp_path, monkeypatch):
    # Prepare dummy instance attributes
    dummy = SimpleNamespace()
    dummy.service = "fanbox"
    dummy.creator_id = "42"
    dummy.post_titles_map = {("fanbox", "42", "101"): "Title"}
    dummy.creator_name = "Creator"
    dummy.auto_rename_enabled = False
    dummy.post_file_counters_lock = None
    dummy.post_file_counters = {}
    dummy.settings = SimpleNamespace(settings_tab=None, file_download_max_retries=1)
    dummy.files_to_download = ["http://example.com/file.jpg"]
    dummy.files_to_posts_map = {"http://example.com/file.jpg": "101"}
    dummy.is_running = True
    dummy.hash_db = SimpleNamespace()

    # Create an existing file with known contents
    existing = tmp_path / "existing.jpg"
    existing.write_bytes(b"hello")
    existing_hash = hashlib.md5(b"hello").hexdigest()
    dummy.hash_db.lookup = lambda h: {
        "file_path": str(existing),
        "file_hash": existing_hash,
        "file_size": 5,
    }
    dummy.hash_db.store = lambda *a, **k: None

    # Capture emits
    emitted = {"progress": [], "completed": []}
    dummy.file_progress = SimpleNamespace(
        emit=lambda i, p: emitted["progress"].append((i, p))
    )
    dummy.file_completed = SimpleNamespace(
        emit=lambda idx, url, ok: emitted["completed"].append((idx, url, ok))
    )
    dummy.log = SimpleNamespace(emit=lambda *a, **k: None)
    import contextlib

    dummy.completed_files_lock = contextlib.nullcontext()
    dummy.completed_files = set()
    dummy.completed_files = set()
    dummy.check_post_completion = lambda url: None

    dummy.download_text = False
    # provide _safe_emit helper used by the method
    dummy._safe_emit = lambda signal, *args: signal.emit(*args)

    # Monkeypatch generate_filename_and_folder to avoid filesystem complexity
    dummy.generate_filename_and_folder = (
        lambda file_url, folder, file_index, total_files, post_id, post_title: (
            str(tmp_path),
            "existing.jpg",
        )
    )

    # Run the async download_file
    asyncio.run(
        cd.CreatorDownloadThread.download_file(
            dummy, "http://example.com/file.jpg", str(tmp_path), 0, 1
        )
    )

    # Should have recorded a completed emit with success True
    assert any(c for c in emitted["completed"] if c[2] is True)


def test_sanitize_filename_various():
    assert cd.sanitize_filename("") == "unnamed"
    assert cd.sanitize_filename("simple name") == "simple_name"
    assert cd.sanitize_filename("..weird<>name..") == "weird_name"
    long_name = "a" * 200
    truncated = cd.sanitize_filename(long_name, max_length=50)
    assert len(truncated) <= 50


def test_get_domain_config():
    coomer = cd.get_domain_config("https://coomer.st/user/1")
    assert coomer["domain"] == "coomer.st"
    default_ = cd.get_domain_config("https://kemono.cr/user/1")
    assert default_["domain"] == "kemono.cr"


def test_get_user_agent_fallback(monkeypatch):
    # Force a UserAgent error to exercise fallback
    monkeypatch.setattr(cd, "_user_agent", None)

    class BrokenUA:
        def __init__(self):
            raise RuntimeError("nope")

    monkeypatch.setattr(cd, "UserAgent", BrokenUA)
    ua = cd.get_user_agent()
    assert ua.startswith("Mozilla/")


def test_detect_files_main_attachments_content():
    fpt = cd.FilePreparationThread(
        post_ids=[],
        all_files_map={},
        creator_ext_checks={},
        creator_main_check=True,
        creator_attachments_check=True,
        creator_content_check=True,
        settings=SimpleNamespace(settings_tab=None),
        max_concurrent=1,
    )

    post = {
        "id": "1",
        "file": {"path": "/media/img1.jpg", "name": "photo.jpg"},
        "attachments": [
            {"path": "/media/att.zip", "name": "archive.zip"},
            {"path": "/media/att2.png", "name": "att2.png"},
        ],
        "content": '<p>Hello<img src="/media/inside.png"></p>',
    }

    allowed = [".jpg", ".png", ".zip"]
    domain = cd.get_domain_config("https://kemono.cr")
    files = fpt.detect_files(post, allowed, domain)
    urls = [u for _, u in files]
    assert any("img1.jpg" in u for u in urls)
    assert any("att2.png" in u for u in urls)
    assert any("inside.png" in u for u in urls)


def test_filter_and_checkbox_toggle_and_population_threads():
    # FilterThread
    captured = {}

    def on_filtered(items):
        captured["filtered"] = items

    all_detected = [("Alpha Post", ("1", "urlA")), ("Beta Post", ("2", "urlB"))]
    ft = cd.FilterThread(all_detected, {"1": True}, "Alpha")
    ft.finished.connect(on_filtered)
    ft.run()
    assert "filtered" in captured
    assert any(item[0] == "Alpha Post" for item in captured["filtered"])

    # CheckboxToggleThread
    cb_captured = {}

    def on_cb(checked_urls, posts_to_download):
        cb_captured["checked"] = checked_urls
        cb_captured["posts"] = posts_to_download

    visible = [("Alpha Post", ("1", "urlA"))]
    cbt = cd.CheckboxToggleThread(visible, {}, 2)  # Checked
    cbt.finished.connect(on_cb)
    cbt.run()
    assert cb_captured["checked"].get("1") is True
    assert "1" in cb_captured["posts"]

    # PostPopulationThread
    pop_captured = {}

    def on_pop(mp, lst):
        pop_captured["map"] = mp
        pop_captured["list"] = lst

    ppt = cd.PostPopulationThread([("T", ("9", "thumb"))])
    ppt.finished.connect(on_pop)
    ppt.run()
    assert isinstance(pop_captured.get("map"), dict)
    assert pop_captured["list"][0][0] == "T"


def test_creator_generate_filename_and_desc_folder(tmp_path, monkeypatch):
    service = "kemono"
    creator_id = "42"
    other_dir = str(tmp_path / "other")
    # Minimal settings object exposing expected interface
    settings = SimpleNamespace(
        settings_tab=SimpleNamespace(
            get_creator_filename_template=lambda: "{post_id}_{orig_name}",
            get_creator_folder_strategy=lambda: "per_post",
        )
    )

    post_titles = {(service, creator_id, "1"): "Cool Post"}

    thread = cd.CreatorDownloadThread(
        service,
        creator_id,
        str(tmp_path),
        ["1"],
        ["https://kemono.cr/media/pic.png?f=pic.png"],
        {"https://kemono.cr/media/pic.png?f=pic.png": "1"},
        None,
        other_dir,
        post_titles,
        True,
        settings,
        max_concurrent=1,
        download_text=False,
    )

    # First call should apply auto-rename prefix when enabled
    folder, filename = thread.generate_filename_and_folder(
        "https://kemono.cr/media/pic.png?f=pic.png",
        str(tmp_path),
        0,
        1,
        "1",
        "Cool Post",
    )
    assert "pic" in filename
    # Folder should be <download_root>/<creator_folder>/<post_folder>
    assert os.path.basename(folder) == "1_Cool_Post"
    creator_folder = os.path.basename(os.path.dirname(folder))
    assert creator_folder.startswith("42_") or creator_folder == "42_Unknown_Creator"

    # Desc folder for per_post
    desc = thread.get_desc_folder_for_post(str(tmp_path), "1", "Cool Post")
    assert "1_" in desc


def test_download_text_sync_writes_file(tmp_path, monkeypatch):
    # Prepare a fake session that returns JSON with content
    class FakeResp:
        status_code = 200

        def json(self):
            return {"content": "<p>Hello world</p>"}

    class FakeSession:
        def get(self, *a, **k):
            return FakeResp()

    monkeypatch.setattr(cd, "get_session", lambda settings_tab=None: FakeSession())

    service = "kemono"
    creator_id = "99"
    other_dir = str(tmp_path / "other2")
    settings = SimpleNamespace(settings_tab=None)
    thread = cd.CreatorDownloadThread(
        service,
        creator_id,
        str(tmp_path),
        ["1"],
        [],
        {},
        None,
        other_dir,
        {},
        False,
        settings,
        max_concurrent=1,
        download_text=False,
    )

    post_folder = str(tmp_path / "postfolder")
    os.makedirs(post_folder, exist_ok=True)
    thread._download_text_sync("1", post_folder)
    assert os.path.exists(os.path.join(post_folder, "desc_1.txt"))


def test_generate_filename_strategies_and_download_text_dup(tmp_path, monkeypatch):
    service = "kemono"
    creator_id = "42"
    other_dir = str(tmp_path / "otherb")
    # settings with different folder strategies
    settings_single = SimpleNamespace(
        settings_tab=SimpleNamespace(
            get_creator_filename_template=lambda: "{post_id}_{orig_name}",
            get_creator_folder_strategy=lambda: "single_folder",
        )
    )

    settings_bytype = SimpleNamespace(
        settings_tab=SimpleNamespace(
            get_creator_filename_template=lambda: "{post_id}_{orig_name}",
            get_creator_folder_strategy=lambda: "by_file_type",
        )
    )

    post_titles = {(service, creator_id, "1"): "Cool Post"}

    t1 = cd.CreatorDownloadThread(
        service,
        creator_id,
        str(tmp_path),
        ["1"],
        ["https://kemono.cr/media/pic.png?f=pic.png"],
        {"https://kemono.cr/media/pic.png?f=pic.png": "1"},
        None,
        other_dir,
        post_titles,
        False,
        settings_single,
        max_concurrent=1,
        download_text=False,
    )
    folder_single, _ = t1.generate_filename_and_folder(
        "https://kemono.cr/media/pic.png?f=pic.png",
        str(tmp_path),
        0,
        1,
        "1",
        "Cool Post",
    )
    assert os.path.basename(folder_single).startswith("42_")

    t2 = cd.CreatorDownloadThread(
        service,
        creator_id,
        str(tmp_path),
        ["1"],
        ["https://kemono.cr/media/pic.png?f=pic.png"],
        {"https://kemono.cr/media/pic.png?f=pic.png": "1"},
        None,
        other_dir,
        post_titles,
        False,
        settings_bytype,
        max_concurrent=1,
        download_text=False,
    )
    folder_bytype, _ = t2.generate_filename_and_folder(
        "https://kemono.cr/media/pic.png?f=pic.png",
        str(tmp_path),
        0,
        1,
        "1",
        "Cool Post",
    )
    assert (
        os.path.basename(folder_bytype).lower() in ("png", "other")
        or "42_" in folder_bytype
    )

    # download_text dedup: monkeypatch _download_text_sync and verify called once
    called = {"count": 0}

    def fake_download_sync(pid, pfolder):
        called["count"] += 1

    t3 = cd.CreatorDownloadThread(
        service,
        creator_id,
        str(tmp_path),
        ["1"],
        [],
        {},
        None,
        other_dir,
        post_titles,
        False,
        settings_single,
        max_concurrent=1,
        download_text=True,
    )
    monkeypatch.setattr(t3, "_download_text_sync", fake_download_sync)
    asyncio.run(t3.download_post_text_if_needed("1", str(tmp_path)))
    asyncio.run(t3.download_post_text_if_needed("1", str(tmp_path)))
    assert called["count"] == 1


def test_fetch_creator_and_post_info_populates_titles(tmp_path, monkeypatch):
    service = "kemono"
    creator_id = "77"
    other_dir = str(tmp_path / "otherc")
    settings = SimpleNamespace(settings_tab=None)

    # Fake responses for profile and post
    class ProfileResp:
        status_code = 200

        def json(self):
            return {"name": "Creator Name"}

    class PostResp:
        status_code = 200

        def json(self):
            return {"title": "A Title"}

    class FakeSession:
        def get(self, url, *a, **k):
            if url.endswith("/profile"):
                return ProfileResp()
            return PostResp()

    monkeypatch.setattr(cd, "get_session", lambda settings_tab=None: FakeSession())

    t = cd.CreatorDownloadThread(
        service,
        creator_id,
        str(tmp_path),
        ["5"],
        ["https://kemono.cr/media/x.png"],
        {"https://kemono.cr/media/x.png": "5"},
        None,
        other_dir,
        {},
        False,
        settings,
        max_concurrent=1,
        download_text=False,
    )
    t.fetch_creator_and_post_info()
    assert t.creator_name is not None
    assert (service, creator_id, "5") in t.post_titles_map


def teardown_module(module):
    # Clean any thread-local or cached state that could leak between tests
    try:
        cd._user_agent = None
    except Exception:
        pass
    try:
        cd.HEADERS = None
    except Exception:
        pass
    try:
        cd._thread_local.__dict__.clear()
    except Exception:
        pass


def test_get_headers_caching():
    cd.HEADERS = None
    h1 = cd.get_headers()
    assert isinstance(h1, dict)
    h2 = cd.get_headers()
    assert h1 is h2
    # cleanup
    cd.HEADERS = None


def test_get_session_thread_local_and_socks(monkeypatch):
    # Reset thread local storage
    cd._thread_local.__dict__.clear()

    s1 = cd.get_session(None)
    s2 = cd.get_session(None)
    assert s1 is s2

    class S:
        def get_proxy_settings(self):
            return {"http": "socks5://127.0.0.1:9050"}

    socks_session = cd.get_session(S())
    # socks_session should be stored on thread local
    assert getattr(cd._thread_local, "socks_session", None) is not None
    assert getattr(cd._thread_local, "socks_session") is socks_session

    # calling again returns same socks session instance
    socks_session2 = cd.get_session(S())
    assert socks_session is socks_session2
    # cleanup
    cd._thread_local.__dict__.clear()


# duplicate sanitize_filename test removed to avoid redefinition


def test_generate_filename_and_folder_and_auto_rename(tmp_path, qapp, monkeypatch):
    # Monkeypatch HashDB to avoid filesystem DB interactions
    class DummyHashDB:
        def __init__(self, other_files_dir):
            pass

        def lookup(self, *a, **k):
            return None

        def store(self, *a, **k):
            return None

    monkeypatch.setattr(cd, "HashDB", DummyHashDB)

    file_url = "https://kemono.cr/some/path/orig.jpg?f=orig.jpg"
    files_to_download = [file_url]
    files_to_posts_map = {file_url: "42"}

    th = cd.CreatorDownloadThread(
        service="fanbox",
        creator_id="123",
        download_folder=str(tmp_path),
        selected_posts=["42"],
        files_to_download=files_to_download,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={},
        auto_rename_enabled=True,
        settings=None,
        max_concurrent=1,
        download_text=False,
    )

    target_folder, filename = th.generate_filename_and_folder(
        file_url, str(tmp_path), 0, 1, "42", "My Title"
    )

    # Filename should include auto-rename prefix and post id/orig name
    assert filename.endswith(".jpg")
    assert filename.startswith("1_")

    # Target folder should contain creator folder and per-post folder
    expected_creator = os.path.join(str(tmp_path), "123_123")
    assert expected_creator in target_folder
    # When no title exists in post_titles_map the implementation falls back
    # to a Post_{post_id} title — assert that fallback is used.
    assert os.path.join("42_Post_42") in target_folder

    # second call increments auto-rename counter
    target2, filename2 = th.generate_filename_and_folder(
        file_url, str(tmp_path), 1, 1, "42", "My Title"
    )
    assert filename2.startswith("2_")


def test_get_desc_folder_for_post_respects_strategy(tmp_path, qapp, monkeypatch):
    class DummyHashDB:
        def __init__(self, other_files_dir):
            pass

        def lookup(self, *a, **k):
            return None

        def store(self, *a, **k):
            return None

    monkeypatch.setattr(cd, "HashDB", DummyHashDB)

    class Settings:
        def __init__(self, strat):
            self.settings_tab = SimpleNamespace(
                get_creator_folder_strategy=lambda: strat
            )

    th = cd.CreatorDownloadThread(
        service="fanbox",
        creator_id="123",
        download_folder=str(tmp_path),
        selected_posts=["42"],
        files_to_download=[],
        files_to_posts_map={},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={},
        auto_rename_enabled=False,
        settings=Settings("per_post"),
        max_concurrent=1,
        download_text=False,
    )

    creator_folder = os.path.join(str(tmp_path), "123_123")
    desc = th.get_desc_folder_for_post(creator_folder, "42", "My Title")
    assert desc.endswith(os.path.join("42_My_Title"))

    th2 = cd.CreatorDownloadThread(
        service="fanbox",
        creator_id="123",
        download_folder=str(tmp_path),
        selected_posts=["42"],
        files_to_download=[],
        files_to_posts_map={},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={},
        auto_rename_enabled=False,
        settings=Settings("by_file_type"),
        max_concurrent=1,
        download_text=False,
    )
    desc2 = th2.get_desc_folder_for_post(creator_folder, "42", "My Title")
    assert desc2.endswith(os.path.join("txt"))

    th3 = cd.CreatorDownloadThread(
        service="fanbox",
        creator_id="123",
        download_folder=str(tmp_path),
        selected_posts=["42"],
        files_to_download=[],
        files_to_posts_map={},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={},
        auto_rename_enabled=False,
        settings=Settings("single_folder"),
        max_concurrent=1,
        download_text=False,
    )
    desc3 = th3.get_desc_folder_for_post(creator_folder, "42", "My Title")
    assert desc3 == os.path.normpath(creator_folder)
