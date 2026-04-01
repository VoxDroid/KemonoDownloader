from types import SimpleNamespace

import requests

from kemonodownloader.creator_downloader import (
    CheckboxToggleThread,
    FilterThread,
    PostPopulationThread,
    ValidationThread,
    sanitize_filename,
)


def test_sanitize_filename_basic():
    assert sanitize_filename("") == "unnamed"
    s = sanitize_filename(' bad<>:"/\\|?*name.. ')
    # No invalid characters should remain
    for ch in '<>:"/\\|?*':
        assert ch not in s
    assert s == s.strip("_")


def test_post_population_thread_emits_map():
    detected = [("Title A", ("1", "u1")), ("Title B", ("2", "u2"))]
    thread = PostPopulationThread(detected)
    captured = []
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda m, lst: captured.append((m, lst)))
    thread.run()
    assert captured
    post_map, posts = captured[0]
    assert any("Title A (ID: 1)" in k for k in post_map.keys())


def test_filter_thread_filters_and_emits():
    all_detected = [("Title One", ("1", "u1")), ("Other", ("2", "u2"))]
    checked = {"1": True, "2": False}
    thread = FilterThread(all_detected, checked, search_text="Title")
    captured = []
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda items: captured.append(items))
    thread.run()
    assert captured
    filtered = captured[0]
    assert any(item[1] == "1" for item in filtered)


def test_validation_thread_success_and_failure(monkeypatch):
    # Success path: domain string present in response.text
    settings = SimpleNamespace(api_request_max_retries=1, settings_tab=None)
    t_success = ValidationThread("https://kemono.cr/service/user/1", settings)
    results = []
    t_success.log = SimpleNamespace(emit=lambda *a, **k: None)
    t_success.result = SimpleNamespace(emit=lambda v: results.append(v))

    class Resp:
        status_code = 200

        text = "Welcome to Kemono"

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session",
        lambda *a, **k: SimpleNamespace(get=lambda *a, **k: Resp()),
    )
    t_success.run()
    assert results and results[0] is True

    # Failure path: network error
    settings = SimpleNamespace(api_request_max_retries=1, settings_tab=None)
    t_fail = ValidationThread("https://kemono.cr/service/user/1", settings)
    results2 = []
    t_fail.log = SimpleNamespace(emit=lambda *a, **k: None)
    t_fail.result = SimpleNamespace(emit=lambda v: results2.append(v))

    class BadSession:
        def get(self, *a, **k):
            raise requests.RequestException("nope")

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.get_session", lambda *a, **k: BadSession()
    )
    t_fail.run()
    assert results2 and results2[0] is False


def test_checkbox_toggle_thread_updates_states():
    visible = [("Title", ("1", "u1"))]
    checked = {"1": False, "2": True}
    thread = CheckboxToggleThread(visible, checked, check_all_state=2)
    captured = []
    thread.log = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(
        emit=lambda new_checked, posts: captured.append((new_checked, posts))
    )
    thread.run()
    assert captured
    new_checked, posts = captured[0]
    assert new_checked["1"] is True
    assert set(posts) == {"1", "2"}
