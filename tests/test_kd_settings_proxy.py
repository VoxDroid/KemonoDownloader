import importlib
import importlib.util
from types import SimpleNamespace

from PyQt6.QtCore import QProcess

from kemonodownloader.kd_settings import TOR_SOCKS_PROXY, SettingsTab


def test_get_proxy_settings_none_when_disabled():
    fake = SimpleNamespace(
        settings={"use_proxy": False},
        temp_settings={"use_proxy": False},
        tor_process=None,
    )
    assert SettingsTab.get_proxy_settings(fake) is None


def test_get_proxy_settings_custom():
    s = SimpleNamespace(
        settings={
            "use_proxy": True,
            "proxy_type": "custom",
            "custom_proxy_url": "http://1.2.3.4:8080",
        },
        temp_settings={
            "use_proxy": True,
            "proxy_type": "custom",
            "custom_proxy_url": "http://1.2.3.4:8080",
        },
        tor_process=None,
    )
    proxies = SettingsTab.get_proxy_settings(s)
    assert proxies == {"http": "http://1.2.3.4:8080", "https": "http://1.2.3.4:8080"}


TOR_PROXIES = {"http": TOR_SOCKS_PROXY, "https": TOR_SOCKS_PROXY}


def test_get_proxy_settings_tor_not_running_still_uses_tor():
    # Fail closed: with Tor selected but not running, requests must still go
    # to Tor's port (and fail) rather than straight to the site.
    fake = SimpleNamespace(
        settings={"use_proxy": True, "proxy_type": "tor"},
        temp_settings={"use_proxy": True, "proxy_type": "tor"},
        tor_process=None,
    )
    assert SettingsTab.get_proxy_settings(fake) == TOR_PROXIES


def test_get_proxy_settings_tor_without_pysocks_has_no_fallback(monkeypatch):
    # There used to be a fallback to a Privoxy port nothing starts; requests
    # refuses a SOCKS URL without PySocks, which also fails closed.
    fake_proc = SimpleNamespace(state=lambda: QProcess.ProcessState.Running)
    fake = SimpleNamespace(
        settings={"use_proxy": True, "proxy_type": "tor"},
        temp_settings={"use_proxy": True, "proxy_type": "tor"},
        tor_process=fake_proc,
    )
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)

    assert SettingsTab.get_proxy_settings(fake) == TOR_PROXIES


def test_get_proxy_settings_tor_with_socks(monkeypatch):
    fake_proc = SimpleNamespace(state=lambda: QProcess.ProcessState.Running)
    fake = SimpleNamespace(
        settings={"use_proxy": True, "proxy_type": "tor"},
        temp_settings={"use_proxy": True, "proxy_type": "tor"},
        tor_process=fake_proc,
    )
    # Monkeypatch find_spec to pretend socks is available
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())

    proxies = SettingsTab.get_proxy_settings(fake)
    assert proxies is not None
    assert proxies["http"].startswith(("socks5h://", "http://"))
