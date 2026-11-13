"""Tests must never read or write the developer's real app settings."""

import os
import tempfile

from PyQt6.QtCore import QSettings


def test_app_settings_store_is_a_temporary_file():
    settings = QSettings("VoxDroid", "KemonoDownloader")
    assert settings.format() == QSettings.Format.IniFormat
    path = os.path.realpath(settings.fileName())
    assert path.startswith(os.path.realpath(tempfile.gettempdir()))
    assert "kd-test-settings-" in path


def test_settings_tab_uses_the_isolated_store(qapp):
    from types import SimpleNamespace

    from kemonodownloader.kd_settings import SettingsTab

    tab = SettingsTab(SimpleNamespace(log=lambda m: None))
    try:
        assert "kd-test-settings-" in tab.qsettings.fileName()
    finally:
        tab.deleteLater()


def test_ini_file_settings_still_open_their_own_file(tmp_path):
    path = str(tmp_path / "own.ini")
    settings = QSettings(path, QSettings.Format.IniFormat)
    assert os.path.realpath(settings.fileName()) == os.path.realpath(path)
