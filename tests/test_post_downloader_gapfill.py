import os
import runpy
from types import SimpleNamespace

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QMovie

from kemonodownloader import post_downloader as pd


def make_file_prep_thread(max_retries=2, max_concurrent=1):
    settings = SimpleNamespace(
        post_data_max_retries=max_retries,
        api_request_max_retries=max_retries,
        settings_tab=None,
    )
    return pd.FilePreparationThread(
        post_ids=["1"],
        all_files_map={"https://kemono.cr/fanbox/user/123/post/1": [("T", "1")]},
        post_ext_checks={},
        file_url_map={},
        url="https://kemono.cr/fanbox/user/123/post/1",
        settings=settings,
        max_concurrent=max_concurrent,
    )


def make_download_thread(
    tmp_path,
    selected_files,
    files_to_posts_map,
    max_retries=2,
    max_concurrent=1,
    auto_rename=False,
):
    settings = SimpleNamespace(
        api_request_max_retries=max_retries,
        file_download_max_retries=max_retries,
        settings_tab=None,
    )
    download_folder = str(tmp_path / "download")
    other_dir = str(tmp_path / "other")
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(other_dir, exist_ok=True)
    thread = pd.DownloadThread(
        url="https://kemono.cr/fanbox/user/123/post/1",
        download_folder=download_folder,
        selected_files=selected_files,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir=other_dir,
        post_id="1",
        settings=settings,
        max_concurrent=max_concurrent,
        auto_rename=auto_rename,
        download_text=False,
    )
    thread.post_title = "Title"
    return thread


def test_post_module_import_executes_locale_windows_branches(monkeypatch):
    import ctypes
    import locale

    calls = {"n": 0}
    real_locale_error = locale.Error

    def fake_setlocale(_category, _value=None):
        calls["n"] += 1
        if calls["n"] == 1:
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

    runpy.run_path(pd.__file__, run_name="post_cov_import")

    assert calls["n"] >= 2


def test_preview_thread_invalid_content_length_progress_zero(monkeypatch, tmp_path):
    class Resp:
        headers = {"content-length": "bad-int"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            yield b"abc"

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )
    monkeypatch.setattr(pd.QPixmap, "loadFromData", lambda self, _data: False)

    progress_values = []
    errors = []
    thread = pd.PreviewThread(
        "https://kemono.cr/f.jpg", str(tmp_path), settings_tab=None
    )
    thread.progress = SimpleNamespace(emit=lambda value: progress_values.append(value))
    thread.error = SimpleNamespace(emit=lambda msg: errors.append(msg))
    thread.preview_ready = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert progress_values == [0]
    assert errors


def test_preview_thread_unexpected_exception_branch(monkeypatch, tmp_path):
    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(
            get=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        ),
    )

    errors = []
    thread = pd.PreviewThread(
        "https://kemono.cr/f.jpg", str(tmp_path), settings_tab=None
    )
    thread.error = SimpleNamespace(emit=lambda msg: errors.append(msg))
    thread.preview_ready = SimpleNamespace(emit=lambda *a, **k: None)
    thread.progress = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert errors


def test_media_preview_play_media_clears_widgets(tmp_path):
    deleted = {"count": 0}

    class Widget:
        def deleteLater(self):
            deleted["count"] += 1

    class Item:
        def widget(self):
            return Widget()

    class Layout:
        def __init__(self):
            self.items = [Item()]

        def count(self):
            return len(self.items)

        def takeAt(self, _index):
            return self.items.pop(0)

        def addWidget(self, _widget):
            return None

    dummy = SimpleNamespace(
        content_layout=Layout(),
        media_url="https://kemono.cr/file.jpg",
        cache_dir=str(tmp_path),
        progress_bar=SimpleNamespace(hide=lambda: None),
        player=SimpleNamespace(setSource=lambda _source: None),
        controls_widget=SimpleNamespace(setVisible=lambda _v: None),
        display_options_widget=SimpleNamespace(setVisible=lambda _v: None),
    )

    pd.MediaPreviewModal.play_media(dummy, "https://kemono.cr/file.jpg", None)

    assert deleted["count"] == 1


def test_media_preview_get_video_size_uses_default_when_invalid():
    dummy = SimpleNamespace(
        video_widget=SimpleNamespace(sizeHint=lambda: QSize()),
        apply_display_mode=lambda: None,
        adjust_dialog_size=lambda: None,
    )

    pd.MediaPreviewModal.get_video_size(dummy)

    assert dummy.original_size == QSize(640, 480)


def test_media_preview_apply_display_mode_video_widget_branches():
    class FakeVideo:
        def __init__(self):
            self.min_size = None
            self.max_size = None

        def setMinimumSize(self, w, h=None):
            self.min_size = (w, h) if h is not None else w

        def setMaximumSize(self, size):
            self.max_size = size

    fit_video = FakeVideo()
    fit_dummy = SimpleNamespace(
        display_mode="Fit",
        content_widget=SimpleNamespace(size=lambda: QSize(300, 200)),
        video_widget=fit_video,
    )
    pd.MediaPreviewModal.apply_display_mode(fit_dummy)

    stretch_video = FakeVideo()
    stretch_dummy = SimpleNamespace(
        display_mode="Stretch",
        content_widget=SimpleNamespace(size=lambda: QSize(320, 210)),
        video_widget=stretch_video,
    )
    pd.MediaPreviewModal.apply_display_mode(stretch_dummy)

    original_video = FakeVideo()
    original_dummy = SimpleNamespace(
        display_mode="Original",
        original_size=QSize(640, 480),
        video_widget=original_video,
    )
    pd.MediaPreviewModal.apply_display_mode(original_dummy)

    assert fit_video.min_size == (0, 0)
    assert stretch_video.min_size == QSize(320, 210)
    assert original_video.max_size == QSize(640, 480)


def test_media_preview_apply_display_mode_original_movie_branch():
    class FakeMovie:
        def __init__(self):
            self.started = 0
            self.scaled = None

        def setScaledSize(self, size):
            self.scaled = size

        def isValid(self):
            return False

        def state(self):
            return QMovie.MovieState.NotRunning

        def start(self):
            self.started += 1

    movie = FakeMovie()
    dummy = SimpleNamespace(
        display_mode="Original",
        content_label=object(),
        original_size=QSize(400, 300),
        movie=movie,
    )

    pd.MediaPreviewModal.apply_display_mode(dummy)

    assert movie.scaled == QSize(400, 300)
    assert movie.started == 1


def test_media_preview_apply_display_mode_fullscreen_branches(monkeypatch):
    monkeypatch.setattr(
        pd.QApplication,
        "primaryScreen",
        lambda: SimpleNamespace(availableSize=lambda: QSize(1200, 300)),
    )

    class FakeMovie:
        def __init__(self):
            self.started = 0

        def setScaledSize(self, _size):
            return None

        def isValid(self):
            return False

        def state(self):
            return QMovie.MovieState.NotRunning

        def start(self):
            self.started += 1

    resized = []
    movie = FakeMovie()
    with_movie = SimpleNamespace(
        display_mode="Full Screen (Modal)",
        content_label=object(),
        original_size=QSize(0, 0),
        content_widget=SimpleNamespace(size=lambda: QSize(600, 400)),
        movie=movie,
        resize=lambda w, h: resized.append((w, h)),
    )
    pd.MediaPreviewModal.apply_display_mode(with_movie)

    resized_else = []
    with_else = SimpleNamespace(
        display_mode="Full Screen (Modal)",
        content_label=object(),
        original_size=QSize(1000, 1000),
        content_widget=SimpleNamespace(size=lambda: QSize(600, 400)),
        movie=None,
        resize=lambda w, h: resized_else.append((w, h)),
    )
    pd.MediaPreviewModal.apply_display_mode(with_else)

    video_widget = SimpleNamespace(
        min_size=None,
        max_size=None,
        setMinimumSize=lambda size: setattr(video_widget, "min_size", size),
        setMaximumSize=lambda size: setattr(video_widget, "max_size", size),
    )
    with_video = SimpleNamespace(
        display_mode="Full Screen (Modal)",
        content_widget=SimpleNamespace(size=lambda: QSize(640, 360)),
        video_widget=video_widget,
    )
    pd.MediaPreviewModal.apply_display_mode(with_video)

    assert with_movie.original_size == QSize(400, 300)
    assert movie.started == 1
    assert resized
    assert resized_else and resized_else[0][0] == 190
    assert video_widget.max_size == QSize(640, 360)


def test_post_detection_make_robust_request_returns_none(monkeypatch):
    settings = SimpleNamespace(api_request_max_retries=1, settings_tab=None)
    thread = pd.PostDetectionThread("https://kemono.cr/fanbox/user/1/post/2", settings)

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(
            get=lambda *a, **k: SimpleNamespace(status_code=500)
        ),
    )

    assert thread.make_robust_request("https://example.com", max_retries=1) is None


def test_file_preparation_stop_logs_message():
    thread = make_file_prep_thread(max_retries=1)
    logs = []
    thread.log = SimpleNamespace(emit=lambda msg, level: logs.append((msg, level)))

    thread.stop()

    assert thread.is_running is False
    assert logs


def test_file_preparation_detect_files_main_file_non_jpg_branch():
    thread = make_file_prep_thread(max_retries=1)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)

    post = {"file": {"path": "/docs/file.pdf", "name": "file.pdf"}}
    files = thread.detect_files(post, [".pdf"])

    assert files and files[0][0] == "file.pdf"


def test_file_preparation_fetch_post_data_none_response_retry_logs(monkeypatch):
    thread = make_file_prep_thread(max_retries=2)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.make_robust_request = lambda *_a, **_k: None

    sleeps = []
    monkeypatch.setattr(pd.time, "sleep", lambda s: sleeps.append(s))

    result = thread.fetch_post_data("1", max_retries=2, retry_delay_seconds=2)

    assert result is None
    assert sleeps.count(1) >= 2


def test_file_preparation_fetch_post_data_exception_retry_countdown(monkeypatch):
    thread = make_file_prep_thread(max_retries=2)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.make_robust_request = lambda *_a, **_k: SimpleNamespace(content=b"{}")
    thread.parse_response_content = lambda *_a, **_k: (_ for _ in ()).throw(
        RuntimeError("parse")
    )

    sleeps = []
    monkeypatch.setattr(pd.time, "sleep", lambda s: sleeps.append(s))

    result = thread.fetch_post_data("1", max_retries=2, retry_delay_seconds=2)

    assert result is None
    assert sleeps.count(1) >= 2


def test_file_preparation_make_request_none_and_parse_json_success(monkeypatch):
    thread = make_file_prep_thread(max_retries=1)

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(
            get=lambda *a, **k: SimpleNamespace(status_code=500)
        ),
    )

    assert thread.make_robust_request("https://example.com", max_retries=1) is None
    assert thread.parse_response_content(SimpleNamespace(content=b'{"ok": 1}')) == {
        "ok": 1
    }


def test_file_preparation_run_worker_returns_when_stopped(monkeypatch):
    thread = make_file_prep_thread(max_retries=1)
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    class ImmediateThread:
        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args

        def start(self):
            thread.is_running = False
            self.target(*self.args)

        def is_alive(self):
            return False

    monkeypatch.setattr(pd.threading, "Thread", ImmediateThread)

    thread.run()


def test_file_preparation_run_worker_runtimeerror_paths(monkeypatch):
    thread = make_file_prep_thread(max_retries=1)
    thread.fetch_post_data = lambda *_a, **_k: ("1", [("name", "url")])

    def log_emit(message, _level):
        if "Detected file:" in str(message):
            raise RuntimeError("gone")

    thread.log = SimpleNamespace(emit=log_emit)
    thread.progress = SimpleNamespace(
        emit=lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("gone"))
    )
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    class ImmediateThread:
        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args

        def start(self):
            self.target(*self.args)

        def is_alive(self):
            return False

    monkeypatch.setattr(pd.threading, "Thread", ImmediateThread)

    thread.run()


def test_file_preparation_run_worker_fetch_exception_is_swallowed(monkeypatch):
    thread = make_file_prep_thread(max_retries=1)
    thread.fetch_post_data = lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("x"))
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    class ImmediateThread:
        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args

        def start(self):
            self.target(*self.args)

        def is_alive(self):
            return False

    monkeypatch.setattr(pd.threading, "Thread", ImmediateThread)

    thread.run()


def test_file_preparation_run_wait_loop_sleeps_for_alive_workers(monkeypatch):
    thread = make_file_prep_thread(max_retries=1)
    thread.fetch_post_data = lambda *_a, **_k: ("1", [])
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    class AliveOnceThread:
        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args
            self.calls = 0

        def start(self):
            self.target(*self.args)

        def is_alive(self):
            self.calls += 1
            return self.calls == 1

    sleeps = []
    monkeypatch.setattr(pd.threading, "Thread", AliveOnceThread)
    monkeypatch.setattr(pd.time, "sleep", lambda s: sleeps.append(s))

    thread.run()

    assert 0.05 in sleeps


def test_download_thread_make_request_none_and_parse_invalid_gzip(
    monkeypatch, tmp_path
):
    thread = make_download_thread(tmp_path, [], {}, max_retries=1)

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(
            get=lambda *a, **k: SimpleNamespace(status_code=500)
        ),
    )

    assert thread.make_robust_request("https://example.com", max_retries=1) is None
    assert (
        thread.parse_response_content(SimpleNamespace(content=b"\x1f\x8b_not_gzip"))
        is None
    )


def test_download_file_skip_runtimeerror_from_log_emit_is_ignored(tmp_path):
    file_url = "https://kemono.cr/files/a.bin"
    thread = make_download_thread(tmp_path, [file_url], {file_url: "1"}, max_retries=1)
    thread.is_running = False
    thread._destroyed = False
    thread.log = SimpleNamespace(
        emit=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("gone"))
    )

    thread.download_file(file_url, thread.download_folder, 0, 1)


def test_download_file_auto_rename_branch(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/file.jpg?f=orig.jpg"
    thread = make_download_thread(
        tmp_path,
        [file_url],
        {file_url: "1"},
        max_retries=1,
        auto_rename=True,
    )

    class Resp:
        status_code = 200
        headers = {"content-length": "3"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            yield b"abc"

        def close(self):
            return None

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(emit=lambda *a, **k: None)

    thread.download_file(file_url, thread.download_folder, 0, 1)

    expected = tmp_path / "download" / "fanbox" / "1_Title" / "1_orig.jpg"
    assert expected.exists()


def test_download_file_existing_hash_size_mismatch_branch(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/mismatch.bin"
    thread = make_download_thread(tmp_path, [file_url], {file_url: "1"}, max_retries=1)

    existing = tmp_path / "existing.bin"
    existing.write_bytes(b"abc")
    thread.hash_db.lookup = lambda _h: {
        "file_path": str(existing),
        "file_hash": "dummy",
        "file_size": 10,
    }

    class Resp:
        status_code = 200
        headers = {"content-length": "3"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            yield b"abc"

        def close(self):
            return None

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    logs = []
    thread.log = SimpleNamespace(emit=lambda msg, level: logs.append((msg, level)))
    thread.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(emit=lambda *a, **k: None)

    thread.download_file(file_url, thread.download_folder, 0, 1)

    assert any(level == "WARNING" for _, level in logs)


def test_download_file_returns_when_stopped_before_retry_loop(tmp_path):
    file_url = "https://kemono.cr/files/early-return.bin"
    thread = make_download_thread(tmp_path, [file_url], {file_url: "1"}, max_retries=1)

    def lookup(_h):
        thread.is_running = False
        return None

    thread.hash_db.lookup = lookup
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(emit=lambda *a, **k: None)

    thread.download_file(file_url, thread.download_folder, 0, 1)


def test_download_file_returns_when_stopped_inside_ssl_lock(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/inside-lock.bin"
    thread = make_download_thread(tmp_path, [file_url], {file_url: "1"}, max_retries=1)

    class ToggleLock:
        def __enter__(self):
            thread.is_running = False

        def __exit__(self, exc_type, exc, tb):
            return False

    thread._ssl_lock = ToggleLock()
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(emit=lambda *a, **k: None)

    thread.download_file(file_url, thread.download_folder, 0, 1)


def test_download_file_invalid_header_progress_zero(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/bad-header.bin"
    thread = make_download_thread(tmp_path, [file_url], {file_url: "1"}, max_retries=1)

    class Resp:
        status_code = 200
        headers = {"content-length": "not-int"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            yield b"abc"

        def close(self):
            return None

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    progresses = []
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_progress = SimpleNamespace(emit=lambda _idx, p: progresses.append(p))
    thread.file_completed = SimpleNamespace(emit=lambda *a, **k: None)

    thread.download_file(file_url, thread.download_folder, 0, 1)

    assert progresses and progresses[0] == 0


def test_download_file_delete_incomplete_oserror_branch(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/mismatch-delete.bin"
    thread = make_download_thread(tmp_path, [file_url], {file_url: "1"}, max_retries=1)

    class Resp:
        status_code = 200
        headers = {"content-length": "10"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            yield b"abc"

        def close(self):
            return None

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )
    monkeypatch.setattr(
        os,
        "remove",
        lambda _path: (_ for _ in ()).throw(OSError("cannot delete")),
    )

    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(emit=lambda *a, **k: None)

    thread.download_file(file_url, thread.download_folder, 0, 1)


def test_download_file_fallback_emit_exception_swallowed(tmp_path):
    file_url = "https://kemono.cr/files/fallback.bin"
    thread = make_download_thread(tmp_path, [file_url], {file_url: "1"}, max_retries=0)

    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(
        emit=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("gone"))
    )

    thread.download_file(file_url, thread.download_folder, 0, 1)


def test_download_thread_run_worker_returns_when_stopped(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/r1.bin"
    thread = make_download_thread(tmp_path, [file_url], {file_url: "1"}, max_retries=1)
    thread.fetch_post_info = lambda: None
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    class ImmediateThread:
        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args

        def start(self):
            thread.is_running = False
            self.target(*self.args)

        def is_alive(self):
            return False

    monkeypatch.setattr(pd.threading, "Thread", ImmediateThread)

    thread.run()


def test_download_thread_run_worker_runtimeerror_log_emit_swallowed(
    monkeypatch, tmp_path
):
    file_url = "https://kemono.cr/files/r2.bin"
    thread = make_download_thread(tmp_path, [file_url], {file_url: "1"}, max_retries=1)
    thread.fetch_post_info = lambda: None
    thread.download_file = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))

    def log_emit(message, _level):
        if "Error in download" in str(message):
            raise RuntimeError("gone")

    thread.log = SimpleNamespace(emit=log_emit)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    class ImmediateThread:
        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args

        def start(self):
            self.target(*self.args)

        def is_alive(self):
            return False

    monkeypatch.setattr(pd.threading, "Thread", ImmediateThread)

    thread.run()


def test_download_thread_run_wait_slot_breaks_when_stopped(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/r3.bin"
    thread = make_download_thread(
        tmp_path,
        [file_url],
        {file_url: "1"},
        max_retries=1,
        max_concurrent=0,
    )
    thread.fetch_post_info = lambda: None
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    def fake_sleep(_seconds):
        thread.is_running = False

    monkeypatch.setattr(pd.time, "sleep", fake_sleep)

    thread.run()


def test_download_thread_run_join_loop_sleeps(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/r4.bin"
    thread = make_download_thread(tmp_path, [file_url], {file_url: "1"}, max_retries=1)
    thread.fetch_post_info = lambda: None
    thread.download_file = lambda *a, **k: None
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    class AliveOnceThread:
        def __init__(self, target, args=(), daemon=False):
            self.target = target
            self.args = args
            self.calls = 0

        def start(self):
            self.target(*self.args)

        def is_alive(self):
            self.calls += 1
            return self.calls == 1

    sleeps = []
    monkeypatch.setattr(pd.threading, "Thread", AliveOnceThread)
    monkeypatch.setattr(pd.time, "sleep", lambda s: sleeps.append(s))

    thread.run()

    assert 0.05 in sleeps


def test_logs_window_update_close_download_error_and_window_title(
    monkeypatch, tmp_path, qapp
):
    parent_console = SimpleNamespace(toHtml=lambda: "<b>hello</b>", clear=lambda: None)
    window = pd.LogsWindow(parent_console)

    class FakeTimer:
        def __init__(self):
            self.active = False
            self.started = 0
            self.stopped = 0

        def isActive(self):
            return self.active

        def start(self):
            self.active = True
            self.started += 1

        def stop(self):
            self.active = False
            self.stopped += 1

    timer = FakeTimer()
    window.update_timer = timer

    window.update_logs()
    window._do_update()

    accepted = {"v": False}
    event = SimpleNamespace(accept=lambda: accepted.__setitem__("v", True))
    window.closeEvent(event)

    window.logs_display.setPlainText("some logs")
    target = tmp_path / "logs.txt"
    monkeypatch.setattr(
        pd.QFileDialog, "getSaveFileName", lambda *a, **k: (str(target), "Text")
    )
    monkeypatch.setattr(
        "builtins.open",
        lambda *a, **k: (_ for _ in ()).throw(OSError("no write")),
    )
    critical_calls = []
    monkeypatch.setattr(
        pd.QMessageBox,
        "critical",
        lambda *a, **k: critical_calls.append((a, k)),
    )
    monkeypatch.setattr(pd, "translate", lambda key, *args: key)

    window.download_logs()
    title = pd.LogsWindow.windowTitle(window)

    assert timer.started == 1
    assert accepted["v"] is True
    assert critical_calls
    assert title == "full_logs"


def test_on_files_detected_label_appends_count_when_translation_lacks_number(
    monkeypatch,
):
    label_texts = []
    dummy = SimpleNamespace(
        detected_files_during_check_all=[],
        checked_urls={},
        file_url_map={},
        post_file_count_label=SimpleNamespace(setText=lambda t: label_texts.append(t)),
        append_log_to_console=lambda *a, **k: None,
    )

    monkeypatch.setattr(pd, "translate", lambda key, *args: key)

    pd.PostDownloaderTab.on_files_detected_during_check_all(dummy, [("f", "u")])

    assert label_texts
    assert label_texts[0].endswith(" 1")
