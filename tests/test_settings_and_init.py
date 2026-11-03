import importlib
import importlib.util
import runpy
import sys
from types import SimpleNamespace

from kemonodownloader import creator_downloader as cd, kd_network, kd_settings as ks


def test___main_calls_app_main(monkeypatch):
    called = []

    def fake_main():
        called.append(True)

    monkeypatch.setattr("kemonodownloader.app.main", fake_main)
    # Execute package as __main__ which should call our patched main
    runpy.run_module("kemonodownloader", run_name="__main__")
    assert called


def test_get_default_base_directory_various_platforms(monkeypatch):
    # Windows-like
    monkeypatch.setattr(sys, "platform", "win32")
    p = ks.SettingsTab.get_default_base_directory(None)
    assert "Kemono Downloader" in p

    # macOS-like
    monkeypatch.setattr(sys, "platform", "darwin")
    p = ks.SettingsTab.get_default_base_directory(None)
    assert "Library/Application Support" in p or "Kemono Downloader" in p

    # Linux-like
    monkeypatch.setattr(sys, "platform", "linux")
    p = ks.SettingsTab.get_default_base_directory(None)
    assert "Kemono Downloader" in p


def test_get_proxy_settings_custom_and_tor(monkeypatch, tmp_path):
    # Custom proxy (using settings dict)
    fake_self = SimpleNamespace()
    fake_self.settings = {
        "use_proxy": True,
        "proxy_type": "custom",
        "custom_proxy_url": "http://1.2.3.4:8080",
    }
    fake_self.temp_settings = {}
    fake_self.tor_process = None

    res = ks.SettingsTab.get_proxy_settings(fake_self)
    assert res == {"http": "http://1.2.3.4:8080", "https": "http://1.2.3.4:8080"}

    # Tor proxy: simulate running tor process and presence of socks
    class FakeProc:
        def state(self):
            return ks.QProcess.ProcessState.Running

    fake_self2 = SimpleNamespace()
    fake_self2.settings = {"use_proxy": True, "proxy_type": "tor"}
    fake_self2.temp_settings = {"use_proxy": True, "proxy_type": "tor", "tor_path": ""}
    fake_self2.tor_process = FakeProc()

    monkeypatch.setattr(
        importlib.util, "find_spec", lambda name: object() if name == "socks" else None
    )
    res2 = ks.SettingsTab.get_proxy_settings(fake_self2)
    assert res2["http"].startswith("socks5h://") or res2["http"].startswith("http://")


def test_get_user_agent_fallback(monkeypatch):
    # Force UserAgent to raise to exercise fallback
    class BadUA:
        def __init__(self):
            raise Exception("no ua")

    monkeypatch.setattr(kd_network, "UserAgent", BadUA)
    # Reset cached agent
    monkeypatch.setattr(kd_network, "_user_agent", None)
    ua = cd.get_user_agent()
    assert isinstance(ua, str) and "Mozilla" in ua


def test_get_domain_config_coomer_and_default():
    co = cd.get_domain_config("https://coomer.st/some/path")
    assert co["domain"] == "coomer.st"
    km = cd.get_domain_config("https://kemono.cr/some/path")
    assert km["domain"] == "kemono.cr"
