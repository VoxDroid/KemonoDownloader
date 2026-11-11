"""Settings tab text follows the language and the real Tor state."""

from types import SimpleNamespace

import pytest
from PyQt6.QtCore import QProcess

from kemonodownloader import kd_settings as ks
from kemonodownloader.kd_language import language_manager


@pytest.fixture
def tab(qapp):
    previous = language_manager.get_language()
    tab = ks.SettingsTab(SimpleNamespace())
    yield tab
    language_manager.set_language(previous)
    tab.deleteLater()


def test_language_change_translates_help_button_and_custom_proxy(tab):
    language_manager.set_language("japanese")
    tab.update_ui_text()

    custom = tab.proxy_type_combo.findData("custom")
    assert tab.help_tor_button.text() == ks.translate("help_button") == "ヘルプ"
    assert tab.proxy_type_combo.itemText(custom) == "カスタムプロキシ"
    # The stored value is unchanged, only the label is translated.
    assert tab.proxy_type_combo.itemData(custom) == "custom"


@pytest.mark.parametrize(
    "state, key",
    [
        (QProcess.ProcessState.Running, "tor_status_running"),
        (QProcess.ProcessState.NotRunning, "tor_status_stopped"),
    ],
)
def test_language_change_keeps_real_tor_status(tab, state, key):
    tab.tor_process = SimpleNamespace(state=lambda: state)
    tab.update_ui_text()
    assert tab.tor_status_label.text() == ks.translate(key)
