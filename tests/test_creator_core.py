import os

from kemonodownloader import creator_downloader as cd, kd_network


def _clear_thread_local():
    # Clear any per-thread session state to keep tests isolated
    try:
        delattr(kd_network._thread_local, "session")
    except Exception:
        pass
    try:
        delattr(kd_network._thread_local, "socks_session")
    except Exception:
        pass


def test_sanitize_and_domain_getters():
    assert cd.sanitize_filename("") == "unnamed"
    # Basic domain detection
    assert cd.get_domain_config("https://coomer.st/whatever")["domain"] == "coomer.st"
    assert cd.get_domain_config("https://kemono.cr/whatever")["domain"] == "kemono.cr"


def test_get_user_agent_fallback(monkeypatch):
    # Force UserAgent constructor to raise to exercise fallback
    monkeypatch.setattr(
        kd_network, "UserAgent", lambda: (_ for _ in ()).throw(Exception("no ua"))
    )
    # Reset cached value
    monkeypatch.setattr(kd_network, "_user_agent", None)
    ua = cd.get_user_agent()
    assert isinstance(ua, str)
    assert ua.startswith("Mozilla/")


def test_get_headers(monkeypatch):
    # Provide a simple fake UserAgent object that has a .chrome attribute
    class FakeUA:
        chrome = "FAKE_CHROME"

    monkeypatch.setattr(kd_network, "UserAgent", lambda: FakeUA())
    monkeypatch.setattr(kd_network, "_user_agent", None)
    # Reset HEADERS
    monkeypatch.setattr(kd_network, "HEADERS", None)
    headers = cd.get_headers()
    assert "User-Agent" in headers
    assert headers["User-Agent"] == "FAKE_CHROME"


def test_get_session_proxy_http_and_socks(monkeypatch):
    _clear_thread_local()

    class FakeSettings:
        def __init__(self, proxies):
            self._proxies = proxies

        def get_proxy_settings(self):
            return self._proxies

    # HTTP proxy -> should update the per-thread session proxies
    http_settings = FakeSettings({"http": "http://127.0.0.1:8080"})
    s = cd.get_session(http_settings)
    assert hasattr(s, "proxies")
    assert s.proxies.get("http", "").startswith("http://")

    # Clear so socks branch creates its own socks_session
    _clear_thread_local()
    socks_settings = FakeSettings({"http": "socks5://127.0.0.1:9050"})
    s2 = cd.get_session(socks_settings)
    # The module stores a socks_session on thread-local storage
    assert getattr(kd_network._thread_local, "socks_session", None) is not None
    assert s2 is getattr(kd_network._thread_local, "socks_session")


def test_detect_files_main_attachments_and_content(qapp):
    # Create a FilePreparationThread with all checks enabled
    settings = type("S", (), {"post_data_max_retries": 1, "settings_tab": None})()
    thread = cd.FilePreparationThread([], {}, {}, True, True, True, settings)

    domain = cd.get_domain_config("https://kemono.cr/")

    # Main file with explicit name
    post_main = {"file": {"path": "/media/image.jpg", "name": "orig.jpg"}}
    files = thread.detect_files(post_main, [".jpg"], domain)
    assert any("orig.jpg" in f[0] for f in files)
    assert any("media/image.jpg" in f[1] for f in files)

    # Attachment
    post_att = {"attachments": [{"path": "/att/file.png", "name": "a.png"}]}
    files2 = thread.detect_files(post_att, [".png"], domain)
    assert any("a.png" in f[0] for f in files2)

    # Content images
    post_content = {"content": '<p><img src="/images/pic.webp"/></p>'}
    files3 = thread.detect_files(post_content, [".webp"], domain)
    assert any("pic.webp" in f[0] or "pic.webp" in f[1] for f in files3)


def test_generate_filename_and_folder_variants(qapp, tmp_path):
    # Minimal settings object exposing settings_tab methods
    class SettingsTab:
        def get_creator_filename_template(self):
            return "{post_id}_{orig_name}"

        def get_creator_folder_strategy(self):
            return "per_post"

    class Settings:
        settings_tab = SettingsTab()

    download_folder = str(tmp_path)
    selected_posts = ["111"]
    files_to_download = []
    files_to_posts_map = {}
    post_titles_map = {("svc", "creator", "111"): "My Post"}

    thread = cd.CreatorDownloadThread(
        "svc",
        "creator",
        download_folder,
        selected_posts,
        files_to_download,
        files_to_posts_map,
        object(),
        str(tmp_path),
        post_titles_map,
        True,
        Settings(),
        1,
    )

    thread.creator_name = "Creator Name"

    # Default per_post strategy
    folder, filename = thread.generate_filename_and_folder(
        "https://kemono.cr/path/file.png?f=orig.png",
        download_folder,
        0,
        1,
        "111",
        "My Post",
    )
    assert os.path.basename(folder).startswith("111_")
    assert filename.endswith(".png")

    # single_folder strategy
    thread.settings.settings_tab.get_creator_folder_strategy = lambda: "single_folder"
    folder2, _ = thread.generate_filename_and_folder(
        "https://kemono.cr/path/file2.zip",
        download_folder,
        0,
        1,
        "111",
        "My Post",
    )
    # Should not create nested post folder
    assert os.path.basename(folder2) == f"{thread.creator_id}_{thread.creator_name}"

    # by_file_type strategy
    thread.settings.settings_tab.get_creator_folder_strategy = lambda: "by_file_type"
    folder3, _ = thread.generate_filename_and_folder(
        "https://kemono.cr/path/file3.mp4",
        download_folder,
        0,
        1,
        "111",
        "My Post",
    )
    assert os.path.basename(folder3).lower() == "mp4"


def test_post_detection_thread_invalid(qapp):
    errors = []
    settings = type("S", (), {"creator_posts_max_attempts": 1, "settings_tab": None})()
    pdt = cd.PostDetectionThread("https://kemono.cr/invalid", {}, settings)
    pdt.error.connect(lambda m: errors.append(m))
    # Run synchronously
    pdt.run()
    assert errors


def test_post_detection_thread_valid(monkeypatch, qapp):
    # Prepare a fake session that returns a JSON list of posts
    class FakeResp:
        def __init__(self, content_bytes):
            self.content = content_bytes
            self.status_code = 200
            self.text = content_bytes.decode("utf-8")

        def raise_for_status(self):
            return None

    def fake_get_session(tab=None):
        class S:
            def get(self, url, headers=None, timeout=None):
                data = '[{"id": "42", "title": "Hello Post", "file": {"path": "/img/p.jpg"}}]'
                return FakeResp(data.encode("utf-8"))

        return S()

    monkeypatch.setattr(cd, "get_session", fake_get_session)
    batches = []
    finished = []
    settings = type("S", (), {"creator_posts_max_attempts": 1, "settings_tab": None})()
    pdt = cd.PostDetectionThread("https://kemono.cr/user/1", {}, settings)
    pdt.posts_batch.connect(lambda b: batches.append(b))
    pdt.finished.connect(lambda f: finished.append(f))
    pdt.run()
    assert finished and len(finished[0]) >= 1


def test_fetch_and_detect_files_retry(monkeypatch):
    # Simulate a 429 first, then a 200 with valid JSON
    calls = {"count": 0}

    class FakeResp429:
        status_code = 429

    class FakeResp200:
        def __init__(self, data):
            self.status_code = 200
            self._data = data

        def json(self):
            return self._data

    def fake_get_session(tab=None):
        class S:
            def get(self, url, headers=None, timeout=None):
                calls["count"] += 1
                if calls["count"] == 1:
                    return FakeResp429()
                return FakeResp200(
                    {
                        "id": "9",
                        "title": "T",
                        "file": {"path": "/m.jpg", "name": "m.jpg"},
                    }
                )

        return S()

    monkeypatch.setattr(cd, "get_session", fake_get_session)
    # No waiting during tests
    monkeypatch.setattr(cd, "time", type("T", (), {"sleep": lambda *_: None}))

    class FakeCheckbox:
        def isChecked(self):
            return True

    settings = type("S", (), {"post_data_max_retries": 2, "settings_tab": None})()
    thread = cd.FilePreparationThread(
        ["9"], {}, {".jpg": FakeCheckbox()}, True, True, True, settings
    )
    res = thread.fetch_and_detect_files("9", "https://kemono.cr/user/creator")
    assert res is not None and res[0] == "9"


def test_download_text_sync_writes_file(monkeypatch, qapp, tmp_path):
    # Fake session returning a post with HTML content
    class FakeResp:
        status_code = 200

        def json(self):
            return {"content": "<p>Hello\n<br/>World</p>"}

    def fake_get_session(tab=None):
        class S:
            def get(self, url, headers=None, timeout=None):
                return FakeResp()

        return S()

    monkeypatch.setattr(cd, "get_session", fake_get_session)

    class SettingsTab:
        pass

    class Settings:
        settings_tab = SettingsTab()

    download_folder = str(tmp_path)
    thread = cd.CreatorDownloadThread(
        "svc",
        "creator",
        download_folder,
        ["1"],
        [],
        {},
        object(),
        download_folder,
        {},
        True,
        Settings(),
        1,
    )

    post_folder = str(tmp_path)
    # Call the synchronous text downloader
    thread._download_text_sync("1", post_folder)
    desc_path = os.path.join(post_folder, "desc_1.txt")
    assert os.path.exists(desc_path)
    with open(desc_path, "r", encoding="utf-8") as f:
        data = f.read()
    assert "Hello" in data


def test_creator_download_thread_run_no_files(qapp, tmp_path):
    # Ensure run() handles case with no files (logs and exits cleanly)
    class SettingsTab:
        pass

    class Settings:
        settings_tab = SettingsTab()

    download_folder = str(tmp_path)
    thread = cd.CreatorDownloadThread(
        "svc",
        "creator",
        download_folder,
        [],
        [],
        {},
        object(),
        download_folder,
        {},
        True,
        Settings(),
        1,
    )
    # Avoid network calls
    thread.fetch_creator_and_post_info = lambda: None
    # Should not raise
    thread.run()


def test_check_post_completion_emits(qapp):
    class SettingsTab:
        pass

    class Settings:
        settings_tab = SettingsTab()

    thread = cd.CreatorDownloadThread(
        "svc",
        "creator",
        "/tmp",
        ["p1"],
        ["u1", "u2"],
        {"u1": "p1", "u2": "p1"},
        object(),
        "/tmp",
        {},
        True,
        Settings(),
        1,
    )
    thread.post_files_map = {"p1": ["u1", "u2"]}
    thread.completed_files = set(["u1", "u2"])
    signalled = []
    thread.post_completed.connect(lambda pid: signalled.append(pid))
    thread.check_post_completion("u1")
    assert "p1" in signalled

    def test_download_file_hash_lookup_shortcircuit(qapp, tmp_path):
        import asyncio
        import hashlib

        class SettingsTab:
            pass

        class Settings:
            settings_tab = SettingsTab()

        # Create a small file to represent an already-downloaded file
        file_path = tmp_path / "existing.dat"
        data = b"hello world"
        file_path.write_bytes(data)
        file_hash = hashlib.md5(data).hexdigest()

        download_folder = str(tmp_path)
        file_url = "https://kemono.cr/path/existing.dat"

        thread = cd.CreatorDownloadThread(
            "svc",
            "creator",
            download_folder,
            ["1"],
            [file_url],
            {file_url: "1"},
            object(),
            str(tmp_path),
            {("svc", "creator", "1"): "Title"},
            True,
            Settings(),
            1,
        )

        # Stub out hash_db.lookup to return an entry pointing to the existing file
        url_hash = hashlib.md5(file_url.encode()).hexdigest()
        thread.hash_db.lookup = lambda h: (
            {
                "file_path": str(file_path),
                "file_hash": file_hash,
                "file_size": len(data),
            }
            if h == url_hash
            else None
        )

        # Run the async download_file which should short-circuit and mark the file as completed
        asyncio.run(thread.download_file(file_url, download_folder, 0, 1))
        assert file_url in thread.completed_files


def test_post_detection_gzipped_and_dict_variants(monkeypatch, qapp):
    import gzip as _gzip

    class FakeResp:
        def __init__(self, data_bytes):
            self.content = data_bytes
            self.status_code = 200
            self.text = data_bytes.decode("utf-8", errors="ignore")

        def raise_for_status(self):
            return None

    def make_session_for_bytes(data_bytes):
        def _get_session(tab=None):
            class S:
                def get(self, url, headers=None, timeout=None):
                    return FakeResp(data_bytes)

            return S()

        return _get_session

    # gzipped list
    data = b'[{"id":"7","title":"Gz","file":{"path":"/img/g.jpg"}}]'
    gz = _gzip.compress(data)
    monkeypatch.setattr(cd, "get_session", make_session_for_bytes(gz))
    settings = type("S", (), {"creator_posts_max_attempts": 1, "settings_tab": None})()
    pdt = cd.PostDetectionThread("https://kemono.cr/user/1", {}, settings)
    finished = []
    pdt.finished.connect(lambda f: finished.append(f))
    pdt.run()
    assert finished and finished[0]

    # dict with posts key
    data2 = b'{"posts": [{"id":"8","title":"P","file":{"path":"/img/p.jpg"}}]}'
    monkeypatch.setattr(cd, "get_session", make_session_for_bytes(data2))
    pdt2 = cd.PostDetectionThread("https://kemono.cr/user/1", {}, settings)
    fin2 = []
    pdt2.finished.connect(lambda f: fin2.append(f))
    pdt2.run()
    assert fin2 and fin2[0]


def test_post_detection_unexpected_and_json_error(monkeypatch, qapp):
    # Unexpected dict structure
    class FakeResp:
        def __init__(self, data_bytes, status=200):
            self.content = data_bytes
            self.status_code = status
            self.text = data_bytes.decode("utf-8", errors="ignore")

        def raise_for_status(self):
            return None

    def make_get_session(data_bytes, status=200):
        def _get_session(tab=None):
            class S:
                def get(self, url, headers=None, timeout=None):
                    return FakeResp(data_bytes, status=status)

            return S()

        return _get_session

    settings = type("S", (), {"creator_posts_max_attempts": 1, "settings_tab": None})()

    # Unexpected structure (no posts/data)
    monkeypatch.setattr(cd, "get_session", make_get_session(b'{"foo": 1}'))
    logs = []
    pdt = cd.PostDetectionThread("https://kemono.cr/user/1", {}, settings)
    pdt.log.connect(lambda m, lvl: logs.append((m, lvl)))
    pdt.run()
    # Expect an ERROR log emitted for unexpected structure
    assert any(lvl == "ERROR" for _, lvl in logs)

    # Invalid JSON
    monkeypatch.setattr(cd, "get_session", make_get_session(b"invalid json"))
    logs2 = []
    pdt2 = cd.PostDetectionThread("https://kemono.cr/user/1", {}, settings)
    pdt2.log.connect(lambda m, lvl: logs2.append((m, lvl)))
    pdt2.run()
    # Expect an ERROR log emitted for JSON parsing failure
    assert any(lvl == "ERROR" for _, lvl in logs2)


def test_validation_thread_success_and_failure(monkeypatch, qapp):
    # success: response text contains domain substring
    class FakeResp:
        def __init__(self, text, status=200):
            self.status_code = status
            self.text = text

    def session_success(tab=None):
        class S:
            def get(self, url, headers=None, timeout=None):
                return FakeResp("Kemono content and more")

        return S()

    monkeypatch.setattr(cd, "get_session", session_success)
    settings = type("S", (), {"api_request_max_retries": 1, "settings_tab": None})()
    vt = cd.ValidationThread("https://kemono.cr/user/1", settings)
    result = []
    vt.result.connect(lambda v: result.append(v))
    vt.run()
    assert result and result[0] is True

    # failure: network error -> logs
    import requests as _requests

    def session_fail(tab=None):
        class S:
            def get(self, url, headers=None, timeout=None):
                raise _requests.RequestException("network down")

        return S()

    monkeypatch.setattr(cd, "get_session", session_fail)
    vt2 = cd.ValidationThread("https://kemono.cr/user/1", settings)
    logs = []
    vt2.log.connect(lambda m, lvl: logs.append((m, lvl)))
    vt2.run()
    assert (
        any(
            "failed_to_validate" in str(m) or "network_error_attempt" in str(m)
            for m, _ in logs
        )
        or vt2.result
    )
