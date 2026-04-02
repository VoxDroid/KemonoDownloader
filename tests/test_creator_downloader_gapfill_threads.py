import asyncio
import gzip
import json
import os
import runpy
from types import SimpleNamespace

from PyQt6.QtWidgets import QWidget

from kemonodownloader import creator_downloader as cd


class Recorder:
    def __init__(self):
        self.calls = []

    def emit(self, *args):
        self.calls.append(args)


def _clear_thread_local_sessions():
    for name in ("session", "socks_session"):
        try:
            delattr(cd._thread_local, name)
        except Exception:
            pass


def test_get_session_clears_proxies_when_proxy_disabled():
    _clear_thread_local_sessions()

    with_proxy = SimpleNamespace(
        get_proxy_settings=lambda: {"http": "http://127.0.0.1:8080"}
    )
    sess = cd.get_session(with_proxy)
    assert sess.proxies.get("http") == "http://127.0.0.1:8080"

    disabled_proxy = SimpleNamespace(get_proxy_settings=lambda: None)
    sess2 = cd.get_session(disabled_proxy)
    assert sess2 is sess
    assert sess2.proxies == {}


def test_preview_thread_bad_content_length_emits_zero_progress(monkeypatch, tmp_path):
    class Resp:
        headers = {"content-length": "not-an-int"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            yield b"abc"

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )
    monkeypatch.setattr(cd.QPixmap, "loadFromData", lambda self, b: False)

    progress = []
    errors = []
    pt = cd.PreviewThread("https://kemono.cr/x.jpg", str(tmp_path), settings_tab=None)
    pt.progress = SimpleNamespace(emit=lambda v: progress.append(v))
    pt.preview_ready = SimpleNamespace(emit=lambda *a, **k: None)
    pt.error = SimpleNamespace(emit=lambda msg: errors.append(msg))

    pt.run()

    assert progress == [0]
    assert errors


def test_preview_thread_unexpected_exception_path(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(
            get=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        ),
    )

    errors = []
    pt = cd.PreviewThread("https://kemono.cr/x.jpg", str(tmp_path), settings_tab=None)
    pt.progress = SimpleNamespace(emit=lambda *a, **k: None)
    pt.preview_ready = SimpleNamespace(emit=lambda *a, **k: None)
    pt.error = SimpleNamespace(emit=lambda msg: errors.append(msg))

    pt.run()

    assert errors


def test_post_detection_stop_and_early_run_return():
    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)

    thread.stop()
    thread.run()

    assert thread.is_running is False


def test_post_detection_top_level_exception_emits_error(monkeypatch):
    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)
    logs = []
    errors = []
    thread.log = SimpleNamespace(emit=lambda msg, level: logs.append((msg, level)))
    thread.error = SimpleNamespace(emit=lambda msg: errors.append(msg))

    monkeypatch.setattr(
        cd, "urlparse", lambda *_a, **_k: (_ for _ in ()).throw(ValueError("bad"))
    )

    thread.run()

    assert logs
    assert errors


def test_post_detection_invalid_offset_logs_warning(monkeypatch):
    class Resp:
        status_code = 500
        text = ""
        content = b""

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread(
        "https://kemono.cr/fanbox/user/1?o=abc", {}, settings
    )
    logs = []
    thread.log = SimpleNamespace(emit=lambda msg, level: logs.append((msg, level)))
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert any(level == "WARNING" for _, level in logs)


def test_post_detection_likely_end_branch_after_first_page(monkeypatch):
    posts = [{"id": str(i), "title": f"T{i}"} for i in range(50)]
    ok_payload = json.dumps(posts)

    class Resp200:
        status_code = 200
        text = ok_payload
        content = ok_payload.encode("utf-8")

    class Resp500:
        status_code = 500
        text = ""
        content = b""

    class Sess:
        def __init__(self):
            self.calls = 0

        def get(self, *a, **k):
            self.calls += 1
            if self.calls == 1:
                return Resp200()
            if self.calls == 3:
                raise cd.requests.RequestException("net")
            return Resp500()

    sess = Sess()
    monkeypatch.setattr(cd, "get_session", lambda *a, **k: sess)
    monkeypatch.setattr(cd.time, "sleep", lambda _s: None)

    settings = SimpleNamespace(creator_posts_max_attempts=2, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)
    out = []
    thread.finished = SimpleNamespace(emit=lambda posts: out.append(posts))
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert out
    assert len(out[0]) == 50


def test_post_detection_returns_if_stopped_after_success(monkeypatch):
    payload = json.dumps([{"id": "1", "title": "A"}])

    class Resp200:
        status_code = 200
        text = payload
        content = payload.encode("utf-8")

    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)

    def fake_get(*a, **k):
        thread.is_running = False
        return Resp200()

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=fake_get),
    )

    finished = []
    thread.finished = SimpleNamespace(emit=lambda *a, **k: finished.append(True))
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert finished == []


def test_post_detection_empty_response_breaks(monkeypatch):
    class Resp:
        status_code = 200
        text = "   "
        content = b"   "

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)
    finished = []
    thread.finished = SimpleNamespace(emit=lambda posts: finished.append(posts))
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert finished == [[]]


def test_post_detection_stops_before_json_parse(monkeypatch):
    payload = gzip.compress(json.dumps([{"id": "1", "title": "A"}]).encode("utf-8"))

    class Resp:
        status_code = 200
        text = ""
        content = payload

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )
    monkeypatch.setattr(
        cd,
        "translate",
        lambda key, *args: f"{key}:{'|'.join(str(a) for a in args)}",
    )

    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)

    def log_emit(msg, level):
        if "successfully_decompressed_gzipped_response" in str(msg):
            thread.is_running = False

    thread.log = SimpleNamespace(emit=log_emit)
    finished = []
    thread.finished = SimpleNamespace(emit=lambda *a, **k: finished.append(True))
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert finished == []


def test_post_detection_data_key_branch(monkeypatch):
    payload = {"data": [{"id": "11", "title": "DataTitle"}]}

    class Resp:
        status_code = 200
        text = json.dumps(payload)
        content = text.encode("utf-8")

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    post_titles_map = {}
    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread(
        "https://kemono.cr/fanbox/user/1", post_titles_map, settings
    )
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert any(k[2] == "11" for k in post_titles_map)


def test_post_detection_invalid_posts_data_type(monkeypatch):
    class Resp:
        status_code = 200
        text = json.dumps(42)
        content = text.encode("utf-8")

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()


def test_post_detection_skips_invalid_posts_and_sets_file_thumbnail(monkeypatch):
    posts = [
        123,
        {"title": "NoId"},
        {"id": "p1", "title": "T1", "file": {"path": "/files/raw.bin"}},
    ]

    class Resp:
        status_code = 200
        text = json.dumps(posts)
        content = text.encode("utf-8")

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )
    monkeypatch.setattr(
        cd,
        "translate",
        lambda key, *args: f"{key}:{'|'.join(str(a) for a in args)}",
    )

    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)
    batches = []
    finished = []
    thread.posts_batch = SimpleNamespace(emit=lambda b: batches.append(b))
    thread.finished = SimpleNamespace(emit=lambda posts: finished.append(posts))

    def log_emit(msg, level):
        # Stop before final detected_posts loop, where non-dict entries are not handled.
        if "last_page_reached_with_counts" in str(msg):
            thread.is_running = False

    thread.log = SimpleNamespace(emit=log_emit)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert batches
    assert batches[0][0][1][1].endswith("/files/raw.bin")
    assert finished == []


def test_post_detection_single_page_target(monkeypatch):
    posts = [{"id": "p1", "title": "Title"}]

    class Resp:
        status_code = 200
        text = json.dumps(posts)
        content = text.encode("utf-8")

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    settings = SimpleNamespace(creator_posts_max_attempts=2, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1?o=0", {}, settings)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()


def test_post_detection_offset_increment_path(monkeypatch):
    posts = [{"id": str(i), "title": f"T{i}"} for i in range(50)]

    class Resp:
        status_code = 200
        text = json.dumps(posts)
        content = text.encode("utf-8")

    sleeps = []
    monkeypatch.setattr(cd.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert 0.5 in sleeps


def test_post_population_stop_then_run_returns_early():
    t = cd.PostPopulationThread([("A", ("1", None))])
    t.stop()
    t.run()
    assert t.is_running is False


def test_file_prep_fetch_detect_cleans_query_parts(monkeypatch):
    called = {}

    class Resp:
        status_code = 500

    class Sess:
        def get(self, url, headers=None):
            called["url"] = url
            return Resp()

    monkeypatch.setattr(cd, "get_session", lambda *a, **k: Sess())

    settings = SimpleNamespace(post_data_max_retries=1, settings_tab=None)
    t = cd.FilePreparationThread([], {}, {}, True, True, True, settings)
    t.log = SimpleNamespace(emit=lambda *a, **k: None)

    res = t.fetch_and_detect_files("77", "https://kemono.cr/fanbox?x=1/user/42?z=9")

    assert res is None
    assert "/fanbox/user/42/post/77" in called["url"]


def test_file_prep_fetch_detect_unknown_service_fallback(monkeypatch):
    called = {}

    class Resp:
        status_code = 500

    class Sess:
        def get(self, url, headers=None):
            called["url"] = url
            return Resp()

    monkeypatch.setattr(cd, "get_session", lambda *a, **k: Sess())

    settings = SimpleNamespace(post_data_max_retries=1, settings_tab=None)
    t = cd.FilePreparationThread([], {}, {}, True, True, True, settings)
    t.log = SimpleNamespace(emit=lambda *a, **k: None)

    res = t.fetch_and_detect_files("77", "broken")

    assert res is None
    assert "/unknown_service/user/unknown_creator/post/77" in called["url"]


def test_file_prep_fetch_detect_exception_retries(monkeypatch):
    monkeypatch.setattr(
        cd,
        "get_session",
        lambda *a, **k: SimpleNamespace(
            get=lambda *aa, **kk: (_ for _ in ()).throw(RuntimeError("net"))
        ),
    )
    monkeypatch.setattr(cd.time, "sleep", lambda _s: None)

    settings = SimpleNamespace(post_data_max_retries=2, settings_tab=None)
    t = cd.FilePreparationThread([], {}, {}, True, True, True, settings)
    t.log = SimpleNamespace(emit=lambda *a, **k: None)

    assert t.fetch_and_detect_files("1", "https://kemono.cr/fanbox/user/1") is None


def test_file_prep_run_no_matching_creator_urls_emits_empty_result():
    settings = SimpleNamespace(post_data_max_retries=1, settings_tab=None)
    t = cd.FilePreparationThread(
        ["1"],
        {"https://kemono.cr/fanbox/user/1": [("Title", ("2", None))]},
        {},
        True,
        True,
        True,
        settings,
    )
    t.log = SimpleNamespace(emit=lambda *a, **k: None)
    emitted = []
    t.finished = SimpleNamespace(
        emit=lambda files, mapping: emitted.append((files, mapping))
    )

    t.run()

    assert emitted == [([], {})]


def test_file_prep_run_stop_before_loop_breaks_wait(monkeypatch):
    settings = SimpleNamespace(post_data_max_retries=1, settings_tab=None)
    checks = {".jpg": SimpleNamespace(isChecked=lambda: True)}
    all_files_map = {"https://kemono.cr/fanbox/user/1": [("Title", ("1", None))]}
    t = cd.FilePreparationThread(
        ["1"],
        all_files_map,
        checks,
        True,
        True,
        True,
        settings,
        max_concurrent=0,
    )
    t.log = SimpleNamespace(emit=lambda *a, **k: None)
    t.finished = SimpleNamespace(emit=lambda *a, **k: None)
    t.fetch_and_detect_files = lambda *_a, **_k: ("1", [])

    def sleepy(_s):
        t.is_running = False

    monkeypatch.setattr(cd.time, "sleep", sleepy)

    t.run()

    assert t.is_running is False


def test_file_prep_run_progress_emit_runtimeerror(monkeypatch):
    settings = SimpleNamespace(post_data_max_retries=1, settings_tab=None)
    checks = {".jpg": SimpleNamespace(isChecked=lambda: True)}
    all_files_map = {"https://kemono.cr/fanbox/user/1": [("Title", ("1", None))]}
    t = cd.FilePreparationThread(
        ["1"],
        all_files_map,
        checks,
        True,
        True,
        True,
        settings,
        max_concurrent=1,
    )
    t.log = SimpleNamespace(emit=lambda *a, **k: None)
    t.finished = SimpleNamespace(emit=lambda *a, **k: None)
    t.fetch_and_detect_files = lambda *_a, **_k: ("1", [("f.jpg", "u")])
    t.progress = SimpleNamespace(
        emit=lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("dead"))
    )

    t.run()


def test_safe_emit_runtimeerror_is_ignored():
    dummy = SimpleNamespace(_destroyed=False)
    signal = SimpleNamespace(
        emit=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("deleted"))
    )

    cd.CreatorDownloadThread._safe_emit(dummy, signal, "x")


def test_get_desc_folder_strategy_exception_falls_back_per_post(tmp_path):
    bad_settings = SimpleNamespace(
        settings_tab=SimpleNamespace(
            get_creator_folder_strategy=lambda: (_ for _ in ()).throw(
                RuntimeError("bad")
            )
        )
    )
    dummy = SimpleNamespace(settings=bad_settings)

    desc = cd.CreatorDownloadThread.get_desc_folder_for_post(
        dummy, str(tmp_path), "11", "My Post"
    )

    assert desc.endswith("11_My_Post")


def test_download_text_sync_returns_when_description_exists(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cd,
        "get_session",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("must-not-call")),
    )

    thread = cd.CreatorDownloadThread(
        service="fanbox",
        creator_id="1",
        download_folder=str(tmp_path),
        selected_posts=["1"],
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

    post_folder = tmp_path / "post"
    post_folder.mkdir(parents=True, exist_ok=True)
    (post_folder / "desc_1.txt").write_text("already")

    thread._download_text_sync("1", str(post_folder))


def test_download_text_sync_exception_logs_warning(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cd,
        "get_session",
        lambda *a, **k: SimpleNamespace(
            get=lambda *aa, **kk: (_ for _ in ()).throw(RuntimeError("net"))
        ),
    )

    thread = cd.CreatorDownloadThread(
        service="fanbox",
        creator_id="1",
        download_folder=str(tmp_path),
        selected_posts=["1"],
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

    logs = []
    thread._safe_emit = lambda signal, *args: logs.append(args)

    thread._download_text_sync("1", str(tmp_path / "post"))

    assert logs


def test_download_worker_handles_cancellederror_from_download_file():
    dummy = SimpleNamespace(is_running=True)

    async def fail_download(*_a, **_k):
        raise asyncio.CancelledError()

    dummy.download_file = fail_download
    dummy._safe_emit = lambda *a, **k: None
    dummy.log = SimpleNamespace(emit=lambda *a, **k: None)

    async def main():
        q = asyncio.Queue()
        await q.put((0, "u1"))
        await cd.CreatorDownloadThread.download_worker(dummy, q, "/tmp", 1)

    asyncio.run(main())


def test_validation_thread_stop_and_early_run_return():
    settings = SimpleNamespace(api_request_max_retries=1, settings_tab=None)
    t = cd.ValidationThread("https://kemono.cr/fanbox/user/1", settings)
    t.stop()
    t.run()
    assert t.is_running is False


def test_validation_thread_non_200_retry_branch(monkeypatch):
    class Resp:
        status_code = 500
        text = ""

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda *a, **k: SimpleNamespace(get=lambda *aa, **kk: Resp()),
    )
    monkeypatch.setattr(cd.time, "sleep", lambda _s: None)

    settings = SimpleNamespace(api_request_max_retries=2, settings_tab=None)
    t = cd.ValidationThread("https://kemono.cr/fanbox/user/1", settings)
    t.log = SimpleNamespace(emit=lambda *a, **k: None)
    out = []
    t.result = SimpleNamespace(emit=lambda ok: out.append(ok))

    t.run()

    assert out == [False]


def test_validation_thread_request_exception_retry_branch(monkeypatch):
    monkeypatch.setattr(
        cd,
        "get_session",
        lambda *a, **k: SimpleNamespace(
            get=lambda *aa, **kk: (_ for _ in ()).throw(
                cd.requests.RequestException("net")
            )
        ),
    )
    monkeypatch.setattr(cd.time, "sleep", lambda _s: None)

    settings = SimpleNamespace(api_request_max_retries=2, settings_tab=None)
    t = cd.ValidationThread("https://kemono.cr/fanbox/user/1", settings)
    t.log = SimpleNamespace(emit=lambda *a, **k: None)
    out = []
    t.result = SimpleNamespace(emit=lambda ok: out.append(ok))

    t.run()

    assert out == [False]


def test_checkbox_toggle_thread_stop_and_early_return():
    t = cd.CheckboxToggleThread([], {}, 2)
    t.stop()
    t.run()
    assert t.is_running is False


def test_creator_logs_window_download_empty_and_write_error(monkeypatch, tmp_path):
    parent_logs = []
    parent = QWidget()
    parent.creator_console = SimpleNamespace(
        toHtml=lambda: "<b>x</b>", clear=lambda: None
    )
    parent.append_log_to_console = lambda msg, level: parent_logs.append((msg, level))
    window = cd.LogsWindow(parent)

    # Empty logs branch should return early.
    window.logs_display.setPlainText("   ")
    window.download_logs()

    # Write-error branch.
    window.logs_display.setPlainText("text")
    target = tmp_path / "out.txt"
    monkeypatch.setattr(
        cd.QFileDialog, "getSaveFileName", lambda *a, **k: (str(target), "Text")
    )
    monkeypatch.setattr(
        "builtins.open",
        lambda *a, **k: (_ for _ in ()).throw(OSError("cannot write")),
    )

    window.download_logs()

    assert any(level == "ERROR" for _, level in parent_logs)


def test_creator_module_import_executes_locale_and_windows_branches(monkeypatch):
    import ctypes
    import locale

    call_count = {"n": 0}
    real_locale_error = locale.Error

    def fake_setlocale(_cat, _value=None):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise real_locale_error("bad locale")
        return "C"

    monkeypatch.setattr(locale, "setlocale", fake_setlocale)
    monkeypatch.setattr(
        ctypes,
        "windll",
        SimpleNamespace(kernel32=SimpleNamespace(GetUserDefaultLCID=lambda: 1033)),
        raising=False,
    )
    monkeypatch.setattr(locale, "windows_locale", {1033: "en_US"}, raising=False)

    runpy.run_path(cd.__file__, run_name="creator_cov_import")

    assert call_count["n"] >= 2


def test_post_detection_nested_emit_failures_are_ignored(monkeypatch):
    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)
    monkeypatch.setattr(
        cd, "urlparse", lambda *_a, **_k: (_ for _ in ()).throw(ValueError("bad"))
    )

    thread.log = SimpleNamespace(
        emit=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("gone-log"))
    )
    thread.error = SimpleNamespace(
        emit=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("gone-error"))
    )

    thread.run()


def test_post_detection_fallback_creator_id_query_split(monkeypatch):
    class Resp:
        status_code = 500
        text = ""
        content = b""

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/user/1?foo=bar", {}, settings)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()


def test_post_detection_returns_when_stopped_inside_alt_url_loop(monkeypatch):
    class Resp:
        status_code = 500
        text = ""
        content = b""

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)

    def log_emit(_msg, level):
        if level == "DEBUG":
            thread.is_running = False

    thread.log = SimpleNamespace(emit=log_emit)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()


def test_post_detection_final_fallback_thumbnail_path(monkeypatch):
    posts = [{"id": "id1", "title": "T", "file": {"path": "/files/raw.bin"}}]

    class Resp:
        status_code = 200
        text = json.dumps(posts)
        content = text.encode("utf-8")

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    settings = SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None)
    thread = cd.PostDetectionThread("https://kemono.cr/fanbox/user/1", {}, settings)
    out = []
    thread.finished = SimpleNamespace(emit=lambda posts_out: out.append(posts_out))
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert out
    assert out[0][0][1][1].endswith("/files/raw.bin")


def test_file_prep_stop_and_run_early_return():
    t = cd.FilePreparationThread([], {}, {}, True, True, True, SimpleNamespace())
    t.stop()
    t.run()
    assert t.is_running is False


def test_file_prep_worker_returns_when_stopped_before_fetch(monkeypatch):
    checks = {".jpg": SimpleNamespace(isChecked=lambda: True)}
    all_files_map = {"https://kemono.cr/fanbox/user/1": [("Title", ("1", None))]}
    t = cd.FilePreparationThread(
        ["1"],
        all_files_map,
        checks,
        True,
        True,
        True,
        SimpleNamespace(post_data_max_retries=1, settings_tab=None),
        max_concurrent=1,
    )
    t.log = SimpleNamespace(emit=lambda *a, **k: None)
    t.progress = SimpleNamespace(emit=lambda *a, **k: None)
    t.finished = SimpleNamespace(emit=lambda *a, **k: None)
    called = {"fetch": 0}
    t.fetch_and_detect_files = lambda *_a, **_k: called.__setitem__("fetch", 1)

    class ImmediateThread:
        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args

        def start(self):
            t.is_running = False
            self.target(*self.args)

        def is_alive(self):
            return False

    monkeypatch.setattr(cd.threading, "Thread", ImmediateThread)

    t.run()

    assert called["fetch"] == 0


def test_file_prep_worker_runtimeerror_from_log_emit_is_ignored(monkeypatch):
    checks = {".jpg": SimpleNamespace(isChecked=lambda: True)}
    all_files_map = {"https://kemono.cr/fanbox/user/1": [("Title", ("1", None))]}
    t = cd.FilePreparationThread(
        ["1"],
        all_files_map,
        checks,
        True,
        True,
        True,
        SimpleNamespace(post_data_max_retries=1, settings_tab=None),
        max_concurrent=1,
    )
    monkeypatch.setattr(
        cd,
        "translate",
        lambda key, *args: f"{key}:{'|'.join(str(a) for a in args)}",
    )

    def log_emit(msg, _level):
        if "detected_file" in str(msg):
            raise RuntimeError("log deleted")

    t.log = SimpleNamespace(emit=log_emit)
    t.progress = SimpleNamespace(emit=lambda *a, **k: None)
    t.finished = SimpleNamespace(emit=lambda *a, **k: None)
    t.fetch_and_detect_files = lambda *_a, **_k: ("1", [("f.jpg", "u")])

    class ImmediateThread:
        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args

        def start(self):
            self.target(*self.args)

        def is_alive(self):
            return False

    monkeypatch.setattr(cd.threading, "Thread", ImmediateThread)

    t.run()


def test_file_prep_worker_exception_is_ignored(monkeypatch):
    checks = {".jpg": SimpleNamespace(isChecked=lambda: True)}
    all_files_map = {"https://kemono.cr/fanbox/user/1": [("Title", ("1", None))]}
    t = cd.FilePreparationThread(
        ["1"],
        all_files_map,
        checks,
        True,
        True,
        True,
        SimpleNamespace(post_data_max_retries=1, settings_tab=None),
        max_concurrent=1,
    )
    t.log = SimpleNamespace(emit=lambda *a, **k: None)
    t.progress = SimpleNamespace(emit=lambda *a, **k: None)
    t.finished = SimpleNamespace(emit=lambda *a, **k: None)
    t.fetch_and_detect_files = lambda *_a, **_k: (_ for _ in ()).throw(ValueError("x"))

    class ImmediateThread:
        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args

        def start(self):
            self.target(*self.args)

        def is_alive(self):
            return False

    monkeypatch.setattr(cd.threading, "Thread", ImmediateThread)

    t.run()


def test_file_prep_wait_polling_sleep_path(monkeypatch):
    checks = {".jpg": SimpleNamespace(isChecked=lambda: True)}
    all_files_map = {"https://kemono.cr/fanbox/user/1": [("Title", ("1", None))]}
    t = cd.FilePreparationThread(
        ["1"],
        all_files_map,
        checks,
        True,
        True,
        True,
        SimpleNamespace(post_data_max_retries=1, settings_tab=None),
        max_concurrent=1,
    )
    t.log = SimpleNamespace(emit=lambda *a, **k: None)
    t.progress = SimpleNamespace(emit=lambda *a, **k: None)
    t.finished = SimpleNamespace(emit=lambda *a, **k: None)
    t.fetch_and_detect_files = lambda *_a, **_k: ("1", [])

    class PollingThread:
        def __init__(self, target, args=(), daemon=False):
            self.calls = 0

        def start(self):
            return None

        def is_alive(self):
            self.calls += 1
            return self.calls == 1

    sleeps = []
    monkeypatch.setattr(cd.threading, "Thread", PollingThread)
    monkeypatch.setattr(cd.time, "sleep", lambda s: sleeps.append(s))

    t.run()

    assert 0.05 in sleeps


def test_file_prep_run_breaks_at_loop_start_when_stopped(monkeypatch):
    checks = {".jpg": SimpleNamespace(isChecked=lambda: True)}
    all_files_map = {
        "https://kemono.cr/fanbox/user/1": [
            ("T1", ("1", None)),
            ("T2", ("2", None)),
        ]
    }
    t = cd.FilePreparationThread(
        ["1", "2"],
        all_files_map,
        checks,
        True,
        True,
        True,
        SimpleNamespace(post_data_max_retries=1, settings_tab=None),
        max_concurrent=1,
    )
    t.log = SimpleNamespace(emit=lambda *a, **k: None)
    t.progress = SimpleNamespace(emit=lambda *a, **k: None)
    t.finished = SimpleNamespace(emit=lambda *a, **k: None)
    t.fetch_and_detect_files = lambda *_a, **_k: ("1", [])

    class ImmediateThread:
        calls = 0

        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args

        def start(self):
            ImmediateThread.calls += 1
            self.target(*self.args)
            if ImmediateThread.calls == 1:
                t.is_running = False

        def is_alive(self):
            return False

    monkeypatch.setattr(cd.threading, "Thread", ImmediateThread)

    t.run()

    assert t.is_running is False


def _make_creator_thread(tmp_path, file_url, download_text=False):
    return cd.CreatorDownloadThread(
        service="fanbox",
        creator_id="1",
        download_folder=str(tmp_path / "dl"),
        selected_posts=["p1"],
        files_to_download=[file_url],
        files_to_posts_map={file_url: "p1"},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={("fanbox", "1", "p1"): "Title"},
        auto_rename_enabled=False,
        settings=SimpleNamespace(file_download_max_retries=1, settings_tab=None),
        max_concurrent=1,
        download_text=download_text,
    )


def test_download_file_desc_folder_makedirs_failure_is_ignored(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/raw.bin"
    thread = _make_creator_thread(tmp_path, file_url, download_text=True)

    desc_folder = str(tmp_path / "desc_folder")
    thread.get_desc_folder_for_post = lambda *a, **k: desc_folder
    text_calls = []

    async def fake_download_text(*_a, **_k):
        text_calls.append(True)

    thread.download_post_text_if_needed = fake_download_text

    existing = tmp_path / "existing.bin"
    existing.write_bytes(b"abc")
    file_hash = cd.hashlib.md5(existing.read_bytes()).hexdigest()
    thread.hash_db.lookup = lambda _h: {
        "file_path": str(existing),
        "file_hash": file_hash,
        "file_size": existing.stat().st_size,
    }

    real_makedirs = os.makedirs

    def fake_makedirs(path, exist_ok=True):
        if os.path.normpath(path) == os.path.normpath(desc_folder):
            raise OSError("no desc dir")
        return real_makedirs(path, exist_ok=exist_ok)

    monkeypatch.setattr(cd.os, "makedirs", fake_makedirs)

    asyncio.run(thread.download_file(file_url, str(tmp_path), 0, 1))

    assert text_calls == [True]


def test_download_file_cancellation_before_connection(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/stop.bin"
    thread = _make_creator_thread(tmp_path, file_url, download_text=False)

    class CancelOnEnterLock:
        def __enter__(self):
            thread.is_running = False

        def __exit__(self, exc_type, exc, tb):
            return False

    thread._ssl_lock = CancelOnEnterLock()
    monkeypatch.setattr(
        cd,
        "get_session",
        lambda *a, **k: SimpleNamespace(get=lambda *aa, **kk: None),
    )

    asyncio.run(thread.download_file(file_url, str(tmp_path), 0, 1))

    assert file_url in thread.failed_files


def test_download_file_bad_content_length_header(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/contentlen.bin"
    thread = _make_creator_thread(tmp_path, file_url, download_text=False)

    class Resp:
        def raise_for_status(self):
            return None

        @property
        def headers(self):
            return {"content-length": "NaN"}

        def iter_content(self, chunk_size=8192):
            yield b"abc"

        def close(self):
            return None

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda *a, **k: SimpleNamespace(get=lambda *aa, **kk: Resp()),
    )

    asyncio.run(thread.download_file(file_url, str(tmp_path), 0, 1))

    assert file_url in thread.completed_files


def test_download_file_deletion_outer_exception_is_ignored(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/faildelete.bin"
    thread = _make_creator_thread(tmp_path, file_url, download_text=False)

    class Resp:
        def raise_for_status(self):
            raise RuntimeError("download boom")

        @property
        def headers(self):
            return {}

        def close(self):
            return None

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda *a, **k: SimpleNamespace(get=lambda *aa, **kk: Resp()),
    )

    thread.generate_filename_and_folder = (
        lambda file_url, folder, file_index, total_files, post_id, post_title: (
            str(tmp_path),
            "known.bin",
        )
    )
    full_path = os.path.join(str(tmp_path), "known.bin")
    real_exists = os.path.exists

    def flaky_exists(path):
        if os.path.normpath(path) == os.path.normpath(full_path):
            raise RuntimeError("exists check failed")
        return real_exists(path)

    monkeypatch.setattr(cd.os.path, "exists", flaky_exists)

    asyncio.run(thread.download_file(file_url, str(tmp_path), 0, 1))

    assert file_url in thread.failed_files
