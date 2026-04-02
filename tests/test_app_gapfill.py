from types import SimpleNamespace

from kemonodownloader.app import KemonoDownloader


def test_app_log_updates_status_and_prints(monkeypatch):
    called = {"text": None, "printed": None}

    dummy = SimpleNamespace(
        status_label=SimpleNamespace(setText=lambda m: called.__setitem__("text", m))
    )
    monkeypatch.setattr("builtins.print", lambda m: called.__setitem__("printed", m))

    KemonoDownloader.log(dummy, "hello")

    assert called["text"] == "hello"
    assert called["printed"] == "hello"
