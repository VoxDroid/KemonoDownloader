from types import SimpleNamespace

from kemonodownloader import kd_network


def test_get_user_agent_fallback_creator(monkeypatch):
    import kemonodownloader.creator_downloader as cd

    class BadUA:
        def __init__(self):
            raise Exception("no ua")

    monkeypatch.setattr(kd_network, "UserAgent", BadUA)
    monkeypatch.setattr(kd_network, "_user_agent", None)
    ua = cd.get_user_agent()
    assert "Mozilla/5.0" in ua


def test_get_domain_config_creator():
    import kemonodownloader.creator_downloader as cd

    assert cd.get_domain_config("https://coomer.st/whatever")["domain"] == "coomer.st"
    assert cd.get_domain_config("https://kemono.cr/whatever")["domain"] == "kemono.cr"


def test_get_session_thread_local(monkeypatch):
    import kemonodownloader.creator_downloader as cd

    # Reset thread-local sessions
    if hasattr(cd, "_thread_local"):
        kd_network._thread_local.session = None
        kd_network._thread_local.socks_session = None

    s1 = cd.get_session()
    s2 = cd.get_session()
    assert s1 is s2

    # Test with a settings_tab providing SOCKS proxies
    class StubSettings:
        def get_proxy_settings(self):
            return {
                "http": "socks5h://127.0.0.1:9050",
                "https": "socks5h://127.0.0.1:9050",
            }

    # Reset to force creation of socks session
    kd_network._thread_local.socks_session = None
    socks = cd.get_session(StubSettings())
    assert hasattr(socks, "proxies")


def test_post_detection_thread_invalid_url(monkeypatch):
    from kemonodownloader.creator_downloader import PostDetectionThread

    monkeypatch.setattr(
        "kemonodownloader.creator_downloader.translate", lambda s, *a: s
    )

    errors = []
    thread = PostDetectionThread("https://kemono.cr/", {}, SimpleNamespace())
    thread.error.connect(lambda e: errors.append(e))
    thread.run()
    assert errors and errors[0] == "invalid_url_format"
