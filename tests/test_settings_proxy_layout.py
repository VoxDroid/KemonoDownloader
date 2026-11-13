"""Layout of the reworked proxy section in Settings."""

import pytest

from kemonodownloader import kd_settings as ks
from kemonodownloader.kd_settings import SettingsTab


class _Parent:
    def log(self, message):
        pass


@pytest.fixture
def tab(qapp):
    settings_tab = SettingsTab(_Parent())
    yield settings_tab
    settings_tab.deleteLater()


def _select(tab, proxy_type):
    tab.proxy_type_combo.setCurrentIndex(tab.proxy_type_combo.findData(proxy_type))


def test_switch_and_explanation_live_inside_the_group(tab):
    tab.use_proxy_checkbox.setChecked(False)
    group_widgets = tab.network_group.findChildren(type(tab.use_proxy_checkbox))
    assert tab.use_proxy_checkbox in group_widgets
    assert tab.proxy_intro_label.parent() is tab.network_group
    # Off: the group and its switch stay, the options go.
    assert not tab.network_group.isHidden()
    assert tab.proxy_group.isHidden()


def test_only_the_chosen_type_takes_up_room(tab):
    tab.use_proxy_checkbox.setChecked(True)
    _select(tab, "custom")
    assert not tab.custom_proxy_panel.isHidden()
    assert tab.tor_panel.isHidden()
    _select(tab, "tor")
    assert tab.custom_proxy_panel.isHidden()
    assert not tab.tor_panel.isHidden()


def test_controls_sit_in_their_panels(tab):
    custom = tab.custom_proxy_panel
    tor = tab.tor_panel
    for widget in (
        tab.custom_proxy_input,
        tab.test_custom_proxy_button,
        tab.custom_proxy_hint_label,
    ):
        assert custom.isAncestorOf(widget)
    for widget in (
        tab.tor_path_input,
        tab.browse_tor_button,
        tab.download_tor_button,
        tab.start_tor_button,
        tab.stop_tor_button,
        tab.test_tor_button,
        tab.help_tor_button,
        tab.tor_status_label,
        tab.tor_hint_label,
        tab.tor_progress_bar,
        tab.tor_output_text,
    ):
        assert tor.isAncestorOf(widget)


def test_buttons_and_status_use_theme_roles(tab):
    assert tab.start_tor_button.property("kdRole") == "primary"
    assert tab.stop_tor_button.property("kdRole") == "danger"
    assert tab.tor_status_label.property("kdRole") == "pill"
    assert tab.tor_status_label.property("kdTone") in {"error", "warning", "success"}


def test_hints_are_translated(tab, monkeypatch):
    monkeypatch.setattr(ks, "translate", lambda key, *args: f"<{key}>")
    tab.update_ui_text()
    assert tab.network_group.title() == "<proxy_settings>"
    assert tab.proxy_intro_label.text() == "<proxy_intro>"
    assert tab.custom_proxy_hint_label.text() == "<custom_proxy_hint>"
    assert tab.tor_hint_label.text() == "<tor_hint>"


def test_placeholder_is_a_valid_address(tab):
    host, port = tab.custom_proxy_input.placeholderText().rsplit(":", 1)
    assert all(0 <= int(part) <= 255 for part in host.split("."))
    assert 0 < int(port) < 65536
