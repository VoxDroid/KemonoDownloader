from kemonodownloader import post_downloader


def test_translate_appends_args_when_missing(monkeypatch):
    # Make the kd_language.translate return just the key
    monkeypatch.setattr(
        "kemonodownloader.kd_language.translate", lambda key, *a, **k: key
    )
    out = post_downloader.translate("my_key", "A", "B")
    assert "my_key" in out and "A" in out and "B" in out


def test_get_headers_and_user_agent_cache():
    # Ensure headers contain expected keys and caching works
    h1 = post_downloader.get_headers()
    assert isinstance(h1, dict)
    assert "User-Agent" in h1
    # Call again to hit cached HEADERS
    h2 = post_downloader.get_headers()
    assert h1 is h2 or h1 == h2


def test_get_domain_config_variants():
    coomer = post_downloader.get_domain_config("https://coomer.st/user/1")
    assert "coomer.st" in coomer["domain"]
    kem = post_downloader.get_domain_config("https://kemono.cr/user/1")
    assert "kemono.cr" in kem["domain"]
