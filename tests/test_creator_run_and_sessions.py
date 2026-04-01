from types import SimpleNamespace

from kemonodownloader.creator_downloader import (
    CreatorDownloadThread,
    _thread_local,
    get_session,
)


def test_check_post_completion_emits(tmp_path):
    file_url1 = "https://kemono.cr/files/a.png"
    file_url2 = "https://kemono.cr/files/b.png"
    settings = SimpleNamespace(settings_tab=None)
    thread = CreatorDownloadThread(
        service="svc",
        creator_id="creator123",
        download_folder=str(tmp_path),
        selected_posts=["1"],
        files_to_download=[file_url1, file_url2],
        files_to_posts_map={file_url1: "1", file_url2: "1"},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={("svc", "creator123", "1"): "MyPost"},
        auto_rename_enabled=False,
        settings=settings,
        download_text=False,
    )
    captured = []
    thread.post_completed = SimpleNamespace(emit=lambda pid: captured.append(pid))
    # simulate post_files_map and completed files
    thread.post_files_map = {"1": [file_url1, file_url2]}
    thread.completed_files = set([file_url1])

    # first completion should not emit
    thread.check_post_completion(file_url1)
    assert not captured

    # mark second as completed -> should emit
    thread.completed_files.add(file_url2)
    thread.check_post_completion(file_url2)
    assert captured == ["1"]


def test_creator_run_executes_download_loop(tmp_path):
    file_url = "https://kemono.cr/files/x.png"
    settings = SimpleNamespace(settings_tab=None, file_download_max_retries=1)
    thread = CreatorDownloadThread(
        service="svc",
        creator_id="creator123",
        download_folder=str(tmp_path),
        selected_posts=["1"],
        files_to_download=[file_url],
        files_to_posts_map={file_url: "1"},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map={("svc", "creator123", "1"): "MyPost"},
        auto_rename_enabled=False,
        settings=settings,
        download_text=False,
    )
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    finished = []
    thread.finished = SimpleNamespace(emit=lambda: finished.append(True))

    # Avoid network when fetching creator info
    thread.fetch_creator_and_post_info = lambda: None

    async def fake_download(file_url, folder, file_index, total_files):
        # simulate work
        thread.completed_files.add(file_url)

    thread.download_file = fake_download

    # Running run() should process queue and finish
    thread.run()
    assert finished
    assert file_url in thread.completed_files


def test_get_session_socks_proxy_is_used(monkeypatch):
    # Ensure thread-local session state is clean
    try:
        delattr(_thread_local, "session")
    except Exception:
        pass
    try:
        delattr(_thread_local, "socks_session")
    except Exception:
        pass

    class ST:
        def get_proxy_settings(self):
            return {"http": "socks5://127.0.0.1:1080"}

    session = get_session(ST())
    assert session.proxies.get("http") == "socks5://127.0.0.1:1080"
