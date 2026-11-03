import threading

import requests

from kemonodownloader import creator_downloader as cd, kd_network


def test_get_user_agent_fallback(monkeypatch):
    class BadUA:
        def __init__(self):
            raise Exception("no ua")

    monkeypatch.setattr(kd_network, "UserAgent", BadUA)
    # Force reset of cached value
    monkeypatch.setattr(kd_network, "_user_agent", None)
    ua = cd.get_user_agent()
    assert ua and "Mozilla" in ua


def test_get_domain_config_variants():
    coomer = cd.get_domain_config("https://coomer.st/user/1")
    assert coomer["domain"] == "coomer.st"
    kemono = cd.get_domain_config("https://kemono.cr/user/1")
    assert kemono["domain"] == "kemono.cr"


def test_get_headers_is_cached(monkeypatch):
    # Reset module HEADERS
    monkeypatch.setattr(kd_network, "HEADERS", None, raising=False)
    h1 = cd.get_headers()
    h2 = cd.get_headers()
    assert h1 is h2


def test_sanitize_filename_edge_cases():
    assert cd.sanitize_filename("") == "unnamed"
    assert cd.sanitize_filename("a<>:b/c\\d|?*") == "a_b_c_d"
    long_name = "x" * 500
    shortened = cd.sanitize_filename(long_name, max_length=50)
    assert len(shortened) <= 50
    assert not shortened.endswith(".")


def test_get_session_with_proxies(monkeypatch):
    # Isolate thread-local storage for test
    monkeypatch.setattr(kd_network, "_thread_local", threading.local())

    class Settings:
        def __init__(self, proxies):
            self._proxies = proxies

        def get_proxy_settings(self):
            return self._proxies

    # Test HTTP proxy updates session.proxies
    s_http = Settings({"http": "http://proxy:8080"})
    sess = cd.get_session(s_http)
    assert isinstance(sess, requests.Session)
    assert sess.proxies.get("http") == "http://proxy:8080"

    # Reset thread local
    monkeypatch.setattr(kd_network, "_thread_local", threading.local())

    # Test SOCKS proxy returns a socks_session on the thread-local
    s_socks = Settings({"http": "socks5://127.0.0.1:9050"})
    sess2 = cd.get_session(s_socks)
    # socks_session stored on _thread_local
    assert getattr(kd_network._thread_local, "socks_session", None) is sess2
