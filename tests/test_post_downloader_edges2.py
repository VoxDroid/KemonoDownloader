import os
from types import SimpleNamespace

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QMovie

from kemonodownloader import post_downloader as pd


class BadStr:
    def __str__(self):
        raise RuntimeError("cannot stringify")


def make_file_prep_thread(max_retries=2):
    settings = SimpleNamespace(api_request_max_retries=max_retries, settings_tab=None)
    return pd.FilePreparationThread(
        post_ids=[],
        all_files_map={},
        post_ext_checks={},
        file_url_map={},
        url="https://kemono.cr/fanbox/user/123/post/1",
        settings=settings,
        max_concurrent=1,
    )


def make_download_thread(
    tmp_path, selected_files, files_to_posts_map, max_retries=2, download_text=False
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
    return pd.DownloadThread(
        url="https://kemono.cr/fanbox/user/123/post/1",
        download_folder=download_folder,
        selected_files=selected_files,
        files_to_posts_map=files_to_posts_map,
        console=None,
        other_files_dir=other_dir,
        post_id="1",
        settings=settings,
        max_concurrent=1,
        auto_rename=False,
        download_text=download_text,
    )


def test_translate_args_stringify_failure(monkeypatch):
    import kemonodownloader.kd_language as lang

    monkeypatch.setattr(lang, "translate", lambda key, *a, **k: "base")

    out = pd.translate("k", BadStr())
    assert out == "base"


def test_media_preview_apply_display_mode_fit_starts_invalid_movie():
    class FakeMovie:
        def __init__(self):
            self.scaled = []
            self.started = 0

        def setScaledSize(self, size):
            self.scaled.append(size)

        def isValid(self):
            return False

        def state(self):
            return QMovie.MovieState.NotRunning

        def start(self):
            self.started += 1

    movie = FakeMovie()
    dummy = SimpleNamespace(
        display_mode="Fit",
        content_label=object(),
        original_size=QSize(640, 480),
        content_widget=SimpleNamespace(size=lambda: QSize(300, 200)),
        movie=movie,
    )

    pd.MediaPreviewModal.apply_display_mode(dummy)

    assert movie.scaled
    assert movie.started == 1


def test_media_preview_apply_display_mode_stretch_starts_invalid_movie():
    class FakeMovie:
        def __init__(self):
            self.scaled = []
            self.started = 0

        def setScaledSize(self, size):
            self.scaled.append(size)

        def isValid(self):
            return False

        def state(self):
            return QMovie.MovieState.NotRunning

        def start(self):
            self.started += 1

    movie = FakeMovie()
    dummy = SimpleNamespace(
        display_mode="Stretch",
        content_label=object(),
        original_size=QSize(640, 480),
        content_widget=SimpleNamespace(size=lambda: QSize(320, 240)),
        movie=movie,
    )

    pd.MediaPreviewModal.apply_display_mode(dummy)

    assert movie.scaled
    assert movie.started == 1


def test_file_prep_make_robust_request_403_fallback(monkeypatch):
    thread = make_file_prep_thread(max_retries=1)

    calls = []

    class Resp403:
        status_code = 403

    class Resp200:
        status_code = 200

    responses = [Resp403(), Resp200()]

    def fake_get(url, headers=None, timeout=10):
        calls.append(headers.get("Accept"))
        return responses.pop(0)

    monkeypatch.setattr(
        pd, "get_session", lambda settings_tab=None: SimpleNamespace(get=fake_get)
    )

    response = thread.make_robust_request("https://example.com", max_retries=1)

    assert response.status_code == 200
    assert calls[1] == "text/css"


def test_file_prep_make_robust_request_default_success(monkeypatch):
    thread = make_file_prep_thread(max_retries=3)
    ok = SimpleNamespace(status_code=200)

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: ok),
    )

    response = thread.make_robust_request("https://example.com")
    assert response is ok


def test_file_prep_make_robust_request_exception_retry(monkeypatch):
    thread = make_file_prep_thread(max_retries=2)

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(
            get=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("net"))
        ),
    )

    sleeps = []
    monkeypatch.setattr(pd.time, "sleep", lambda s: sleeps.append(s))

    response = thread.make_robust_request("https://example.com", max_retries=2)

    assert response is None
    assert sleeps == [1]


def test_file_prep_parse_response_content_invalid_gzip():
    thread = make_file_prep_thread(max_retries=1)
    response = SimpleNamespace(content=b"\x1f\x8b_not_gzip_data")

    parsed = thread.parse_response_content(response)
    assert parsed is None


def test_download_thread_make_robust_request_403_fallback(monkeypatch, tmp_path):
    thread = make_download_thread(tmp_path, [], {}, max_retries=1)

    class Resp403:
        status_code = 403

    class Resp200:
        status_code = 200

    responses = [Resp403(), Resp200()]

    def fake_get(url, headers=None, timeout=10):
        return responses.pop(0)

    monkeypatch.setattr(
        pd, "get_session", lambda settings_tab=None: SimpleNamespace(get=fake_get)
    )

    response = thread.make_robust_request("https://example.com", max_retries=1)
    assert response.status_code == 200


def test_download_thread_make_robust_request_exception_retry(monkeypatch, tmp_path):
    thread = make_download_thread(tmp_path, [], {}, max_retries=2)

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(
            get=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("down"))
        ),
    )

    sleeps = []
    monkeypatch.setattr(pd.time, "sleep", lambda s: sleeps.append(s))

    response = thread.make_robust_request("https://example.com", max_retries=2)

    assert response is None
    assert sleeps == [1]


def test_download_thread_extract_service_unknown_url(tmp_path):
    thread = make_download_thread(tmp_path, [], {}, max_retries=1)
    service = thread.extract_service_from_url("https://example.com/not/a/post/url")
    assert service == "unknown_service"


def test_download_thread_build_post_files_map_filters_posts(tmp_path):
    selected = ["u1", "u2", "u3"]
    mapping = {"u1": "1", "u2": "2", "u3": "1"}
    thread = make_download_thread(tmp_path, selected, mapping, max_retries=1)

    post_files = thread.build_post_files_map()
    assert post_files == {"1": ["u1", "u3"]}


def test_download_thread_stop_sets_destroyed_and_logs(tmp_path):
    thread = make_download_thread(tmp_path, [], {}, max_retries=1)
    logs = []
    thread.log = SimpleNamespace(
        emit=lambda message, level: logs.append((message, level))
    )

    thread.stop()

    assert thread.is_running is False
    assert thread._destroyed is True
    assert logs


def test_download_file_retry_cancelled_during_countdown(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/file.bin"
    thread = make_download_thread(
        tmp_path,
        [file_url],
        {file_url: "1"},
        max_retries=2,
        download_text=False,
    )
    thread.post_title = "Post"

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(
            get=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fail"))
        ),
    )
    monkeypatch.setattr(
        pd,
        "translate",
        lambda key, *args, **kwargs: f"{key} {' '.join(str(a) for a in args)}".strip(),
    )
    monkeypatch.setattr(pd.time, "sleep", lambda s: None)

    logs = []

    def log_emit(message, level):
        logs.append((message, level))
        if "retry_countdown" in str(message):
            thread.is_running = False

    thread.log = SimpleNamespace(emit=log_emit)
    thread.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(emit=lambda *a, **k: None)

    thread.download_file(file_url, thread.download_folder, 0, 1)

    assert thread.is_running is False
    assert len(logs) >= 2


def test_download_file_retry_exhaustion_after_countdown(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/file2.bin"
    thread = make_download_thread(
        tmp_path,
        [file_url],
        {file_url: "1"},
        max_retries=2,
        download_text=False,
    )
    thread.post_title = "Post"

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(
            get=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fail"))
        ),
    )
    monkeypatch.setattr(pd.time, "sleep", lambda s: None)

    completed = []
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(
        emit=lambda idx, url, ok: completed.append((idx, url, ok))
    )

    thread.download_file(file_url, thread.download_folder, 0, 1)

    assert completed
    assert completed[-1][2] is False


def test_download_file_close_error_is_ignored(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/file3.bin"
    thread = make_download_thread(
        tmp_path,
        [file_url],
        {file_url: "1"},
        max_retries=1,
        download_text=False,
    )
    thread.post_title = "Post"

    class BadResp:
        status_code = 500

        def raise_for_status(self):
            raise RuntimeError("http error")

        @property
        def headers(self):
            return {}

        def close(self):
            raise RuntimeError("close failed")

    monkeypatch.setattr(
        pd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: BadResp()),
    )

    completed = []
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_progress = SimpleNamespace(emit=lambda *a, **k: None)
    thread.file_completed = SimpleNamespace(
        emit=lambda idx, url, ok: completed.append((idx, url, ok))
    )

    thread.download_file(file_url, thread.download_folder, 0, 1)

    assert completed
    assert completed[-1][2] is False


def test_download_thread_run_writes_desc_file(monkeypatch, tmp_path):
    thread = make_download_thread(tmp_path, [], {}, max_retries=1, download_text=True)
    thread.post_title = "My_Post"
    thread.post_content = "<p>Hello post text</p>"

    thread.fetch_post_info = lambda: None
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    desc_path = (
        tmp_path
        / "download"
        / thread.service
        / f"{thread.post_id}_{thread.post_title}"
        / "desc.txt"
    )
    assert desc_path.exists()
    assert "Hello post text" in desc_path.read_text(encoding="utf-8")


def test_download_thread_run_desc_write_exception_logs_warning(monkeypatch, tmp_path):
    thread = make_download_thread(tmp_path, [], {}, max_retries=1, download_text=True)
    thread.post_title = "My_Post"
    thread.post_content = "<p>Hello post text</p>"

    thread.fetch_post_info = lambda: None

    logs = []
    thread.log = SimpleNamespace(
        emit=lambda message, level: logs.append((message, level))
    )
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    monkeypatch.setattr(
        "builtins.open",
        lambda *a, **k: (_ for _ in ()).throw(OSError("cannot write")),
    )

    thread.run()

    warning_count = sum(1 for _, level in logs if level == "WARNING")
    assert warning_count >= 2


def test_download_thread_run_no_files_logs_warning(monkeypatch, tmp_path):
    thread = make_download_thread(tmp_path, [], {}, max_retries=1, download_text=False)
    thread.post_title = "Title"
    thread.fetch_post_info = lambda: None

    logs = []
    thread.log = SimpleNamespace(
        emit=lambda message, level: logs.append((message, level))
    )
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    thread.run()

    assert any(
        "No files selected for download for this post." in str(msg) for msg, _ in logs
    )


def test_download_thread_run_worker_exception_logs(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/files/a.bin"
    thread = make_download_thread(
        tmp_path,
        [file_url],
        {file_url: "1"},
        max_retries=1,
        download_text=False,
    )
    thread.post_title = "Title"
    thread.post_content = ""

    thread.fetch_post_info = lambda: None
    thread.download_file = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))

    logs = []
    thread.log = SimpleNamespace(
        emit=lambda message, level: logs.append((message, level))
    )
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)

    monkeypatch.setattr(pd.time, "sleep", lambda s: None)

    thread.run()

    assert any("Error in download" in str(msg) for msg, _ in logs)
