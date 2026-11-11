"""Pawchive request policy: host matching, headers, previews and URL checks."""

from types import SimpleNamespace

import pytest

from kemonodownloader import creator_downloader as cd, post_downloader as pd
from kemonodownloader.download_policy import (
    IDENTIFIABLE_USER_AGENT,
    get_request_headers,
    is_pawchive_url,
)

BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"


@pytest.mark.parametrize(
    "url",
    [
        "https://pawchive.pw/patreon/user/1/post/2",
        "https://file.pawchive.pw/data/12/34/abc.png",
        "https://img.pawchive.pw/thumbnail/data/12/34/abc.png",
        # The site has moved between suffixes before (see domain_config).
        "https://pawchive.st/patreon/user/1",
        "https://file.pawchive.st/data/12/34/abc.zip",
        "https://PAWCHIVE.PW./patreon/user/1",
    ],
)
def test_is_pawchive_url_matches_every_pawchive_host(url):
    assert is_pawchive_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://kemono.cr/patreon/user/1/post/2",
        "https://n1.kemono.cr/data/12/34/abc.png",
        "https://coomer.st/onlyfans/user/x",
        "https://notpawchive.pw/x",
        "https://pawchive.pw.example.com/x",
        "https://pawchive/x",
        "not a url",
        "",
    ],
)
def test_is_pawchive_url_rejects_other_hosts(url):
    assert not is_pawchive_url(url)


def test_get_request_headers_identifies_only_to_pawchive():
    headers = {"User-Agent": BROWSER_UA, "Referer": "https://pawchive.pw/"}

    pawchive = get_request_headers(headers, "https://file.pawchive.pw/data/a.png")
    kemono = get_request_headers(headers, "https://kemono.cr/data/a.png")

    assert pawchive["User-Agent"] == IDENTIFIABLE_USER_AGENT
    assert pawchive["Referer"] == "https://pawchive.pw/"
    assert kemono == headers
    # The shared default headers must never be modified in place.
    assert headers["User-Agent"] == BROWSER_UA


def _recording_session(calls):
    def get(url, headers=None, **kwargs):
        calls.append((url, dict(headers or {})))
        raise RuntimeError("stop after the request is recorded")

    return lambda settings_tab=None: SimpleNamespace(get=get)


def _silence(thread):
    thread.progress = SimpleNamespace(emit=lambda *a: None)
    thread.preview_ready = SimpleNamespace(emit=lambda *a: None)
    thread.error = SimpleNamespace(emit=lambda *a: None)


@pytest.mark.parametrize("module", [pd, cd], ids=["post", "creator"])
def test_preview_sends_identifiable_user_agent_to_pawchive(
    module, monkeypatch, tmp_path
):
    # Pawchive's file server answers 403 to browser user agents.
    calls = []
    monkeypatch.setattr(module, "get_session", _recording_session(calls))
    monkeypatch.setattr(module, "get_headers", lambda: {"User-Agent": BROWSER_UA})

    url = "https://file.pawchive.pw/data/12/34/abc.png"
    thread = module.PreviewThread(url, str(tmp_path / "cache"))
    _silence(thread)
    thread.run()

    assert calls, "the preview made no request"
    assert calls[0][1]["User-Agent"] == IDENTIFIABLE_USER_AGENT


@pytest.mark.parametrize("module", [pd, cd], ids=["post", "creator"])
def test_preview_keeps_default_user_agent_elsewhere(module, monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(module, "get_session", _recording_session(calls))
    monkeypatch.setattr(module, "get_headers", lambda: {"User-Agent": BROWSER_UA})

    thread = module.PreviewThread(
        "https://kemono.cr/data/12/34/abc.png", str(tmp_path / "cache")
    )
    _silence(thread)
    thread.run()

    assert calls[0][1]["User-Agent"] == BROWSER_UA


def _post_tab_stub(page_text, status=200):
    logs = []
    response = SimpleNamespace(status_code=status, text=page_text)
    session = SimpleNamespace(get=lambda *a, **k: response)
    tab = SimpleNamespace(
        append_log_to_console=lambda msg, level="INFO": logs.append(level),
        parent=SimpleNamespace(settings_tab=None),
    )
    return tab, session


@pytest.mark.parametrize(
    "page_text, expected",
    [
        ("<title>Pawchive</title>", True),
        ("<title>Kemono</title>", True),  # previous behaviour still accepted
        ("<title>Some other site</title>", False),
    ],
)
def test_post_url_validation_accepts_the_sites_own_name(
    monkeypatch, page_text, expected
):
    tab, session = _post_tab_stub(page_text)
    monkeypatch.setattr(pd, "get_session", lambda settings_tab=None: session)

    url = "https://pawchive.pw/patreon/user/3786095/post/164093955"
    assert pd.PostDownloaderTab.check_post_url_validity(tab, url) is expected
