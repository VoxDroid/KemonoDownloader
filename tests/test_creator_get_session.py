import requests

from kemonodownloader import kd_network


def test_get_session_caching():
    import kemonodownloader.creator_downloader as cd

    # Ensure thread-local state is clean
    if hasattr(kd_network._thread_local, "session"):
        del kd_network._thread_local.session
    s1 = cd.get_session()
    s2 = cd.get_session()
    assert s1 is s2
    # cleanup
    try:
        del kd_network._thread_local.session
    except Exception:
        pass


def test_get_session_http_and_socks_proxy(tmp_path):
    from types import SimpleNamespace

    import kemonodownloader.creator_downloader as cd

    # Clean thread-local session state
    for attr in ("session", "socks_session"):
        if hasattr(kd_network._thread_local, attr):
            try:
                delattr(kd_network._thread_local, attr)
            except Exception:
                try:
                    delattr(kd_network._thread_local, attr)
                except Exception:
                    pass

    # HTTP proxy should be applied to the per-thread session
    http_settings = SimpleNamespace(
        get_proxy_settings=lambda: {"http": "http://proxy:8080"}
    )
    s_http = cd.get_session(http_settings)
    assert isinstance(s_http, requests.Session)
    assert s_http.proxies.get("http") == "http://proxy:8080"

    # Clean and test socks proxy path returns a separate socks_session
    try:
        del kd_network._thread_local.session
    except Exception:
        pass
    if hasattr(kd_network._thread_local, "socks_session"):
        try:
            del kd_network._thread_local.socks_session
        except Exception:
            pass

    socks_settings = SimpleNamespace(
        get_proxy_settings=lambda: {"http": "socks5://localhost:1080"}
    )
    s_socks = cd.get_session(socks_settings)
    # socks_session should be created on thread-local and returned
    assert hasattr(kd_network._thread_local, "socks_session")
    assert s_socks is kd_network._thread_local.socks_session
    assert str(s_socks.proxies.get("http")).startswith("socks5://")

    # cleanup
    for attr in ("session", "socks_session"):
        if hasattr(kd_network._thread_local, attr):
            try:
                delattr(kd_network._thread_local, attr)
            except Exception:
                try:
                    delattr(kd_network._thread_local, attr)
                except Exception:
                    pass
