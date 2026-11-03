from types import SimpleNamespace

import kemonodownloader.creator_downloader as cd


def _mk_checkbox(checked=True):
    return SimpleNamespace(isChecked=lambda: checked)


def test_detect_files_main_attachment_content(qapp):
    thread = cd.FilePreparationThread(
        post_ids=[],
        all_files_map={},
        creator_ext_checks={},
        creator_main_check=True,
        creator_attachments_check=True,
        creator_content_check=True,
        settings=SimpleNamespace(post_data_max_retries=1, settings_tab=None),
    )

    post = {
        "id": "p1",
        "title": "Title",
        "file": {"path": "/media/1.png", "name": "img1.png"},
        "attachments": [{"path": "/att/2.zip", "name": "file2.zip"}],
        "content": "<p><img src='/content/3.jpg'/></p>",
    }
    domain_config = {
        "base_url": "https://kemono.cr",
        "referer": "https://kemono.cr/",
        "api_base": "https://kemono.cr/api/v1",
        "domain": "kemono.cr",
    }

    allowed = [".png", ".jpg", ".zip"]
    files = thread.detect_files(post, allowed, domain_config)

    assert ("img1.png", "https://kemono.cr/media/1.png?f=img1.png") in files
    assert ("file2.zip", "https://kemono.cr/att/2.zip?f=file2.zip") in files
    assert ("3.jpg", "https://kemono.cr/content/3.jpg") in files


def test_fetch_and_detect_files_success(monkeypatch, qapp):
    # Create a FilePreparationThread with a single extension enabled
    creator_ext_checks = {".png": _mk_checkbox(True)}
    thread = cd.FilePreparationThread(
        post_ids=[],
        all_files_map={},
        creator_ext_checks=creator_ext_checks,
        creator_main_check=True,
        creator_attachments_check=True,
        creator_content_check=True,
        settings=SimpleNamespace(post_data_max_retries=1, settings_tab=None),
    )

    # Mock session responses
    class Resp:
        status_code = 200

        def json(self):
            return {
                "id": "p1",
                "title": "T",
                "file": {"path": "/media/1.png", "name": "img1.png"},
            }

    class S:
        def get(self, url, headers=None, timeout=None):
            return Resp()

    monkeypatch.setattr(cd, "get_session", lambda st: S())

    result = thread.fetch_and_detect_files("p1", "https://kemono.cr/artist/user/10")
    assert result is not None
    pid, files = result
    assert pid == "p1"
    assert any("img1.png" in fn for fn, _ in files)


def test_fetch_and_detect_files_429_retry(monkeypatch, qapp):
    # Ensure we don't actually sleep during retries
    monkeypatch.setattr(cd, "time", SimpleNamespace(sleep=lambda *_: None))

    creator_ext_checks = {".png": _mk_checkbox(True)}
    thread = cd.FilePreparationThread(
        post_ids=[],
        all_files_map={},
        creator_ext_checks=creator_ext_checks,
        creator_main_check=True,
        creator_attachments_check=True,
        creator_content_check=True,
        settings=SimpleNamespace(post_data_max_retries=2, settings_tab=None),
    )

    # First response 429, then 200
    class Resp429:
        status_code = 429

    class Resp200:
        status_code = 200

        def json(self):
            return {"id": "p1", "file": {"path": "/media/1.png", "name": "img1.png"}}

    calls = {"i": 0}

    class S:
        def get(self, url, headers=None, timeout=None):
            calls["i"] += 1
            return Resp429() if calls["i"] == 1 else Resp200()

    monkeypatch.setattr(cd, "get_session", lambda st: S())

    res = thread.fetch_and_detect_files("p1", "https://kemono.cr/artist/user/10")
    assert res is not None and res[0] == "p1"
