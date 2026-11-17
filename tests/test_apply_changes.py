"""Every setting waits for Apply Changes; the proxy and Tor flow around it."""

from types import SimpleNamespace

import pytest
from PyQt6.QtWidgets import QMessageBox

from kemonodownloader import kd_settings as ks
from kemonodownloader.kd_language import translate
from kemonodownloader.kd_theme import DEFAULT_THEME

YES = QMessageBox.StandardButton.Yes
NO = QMessageBox.StandardButton.No


def start_from_defaults(settings_tab, base_directory):
    """Apply the defaults: the test settings store is shared by all tests."""
    settings_tab.temp_settings = dict(
        settings_tab.default_settings, base_directory=str(base_directory)
    )
    assert settings_tab.apply_pending_settings(confirm=False, closing=True)
    settings_tab._show_values()


@pytest.fixture
def tab(qapp, monkeypatch, tmp_path):
    settings_tab = ks.SettingsTab(SimpleNamespace(log=lambda m: None))
    start_from_defaults(settings_tab, tmp_path)
    # Nothing in these tests may reach a real Tor or real dialogs by accident.
    monkeypatch.setattr(ks, "tor_is_listening", lambda timeout=0.3: False)
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
    yield settings_tab
    monkeypatch.undo()
    settings_tab.tor_process = None
    start_from_defaults(settings_tab, tmp_path)
    settings_tab.qsettings.remove("base_directory")
    settings_tab.deleteLater()


def answer(monkeypatch, label_key):
    """Make the next custom QMessageBox click the button labelled *label_key*."""
    shown = []

    def exec_(box):
        shown.append(box.text())

    def clicked(box):
        if label_key is None:
            return None
        wanted = (
            box.button(QMessageBox.StandardButton.Cancel)
            if label_key == "cancel"
            else next(b for b in box.buttons() if b.text() == translate(label_key))
        )
        return wanted

    monkeypatch.setattr(QMessageBox, "exec", exec_)
    monkeypatch.setattr(QMessageBox, "clickedButton", clicked)
    return shown


# ------------------------------------------------------- nothing is instant


def change_everything(tab):
    """Touch every control the way a user would."""
    tab.folder_name_input.setText("Elsewhere")
    tab.download_slider.setValue(9)
    tab.save_previews_checkbox.setChecked(True)
    tab.creator_posts_max_attempts_spinbox.setValue(11)
    tab.post_data_max_retries_spinbox.setValue(4)
    tab.file_download_max_retries_spinbox.setValue(12)
    tab.api_request_max_retries_spinbox.setValue(6)
    tab.creator_filename_combo.setCurrentIndex(1)
    tab.creator_folder_strategy_combo.setCurrentIndex(2)
    tab.auto_update_checkbox.setChecked(False)
    tab.log_level_checkboxes["DEBUG"].setChecked(True)
    tab.font_combo.setCurrentIndex(tab.font_combo.findData("Poppins"))
    tab.theme_combo.setCurrentIndex(tab.theme_combo.findData("forest"))
    tab.use_proxy_checkbox.setChecked(True)
    tab.proxy_type_combo.setCurrentIndex(tab.proxy_type_combo.findData("custom"))
    tab.custom_proxy_input.setText("http://127.0.0.1:8080")


def test_every_control_waits_for_apply(tab, monkeypatch):
    saved, themes, fonts = [], [], []
    monkeypatch.setattr(tab, "save_settings", lambda: saved.append(True))
    tab.theme_changed.connect(themes.append)
    tab.font_changed.connect(fonts.append)
    before = dict(tab.settings)

    change_everything(tab)

    assert tab.settings == before and not saved and not themes and not fonts
    assert tab.get_proxy_settings() is None  # ticked, not applied
    assert not tab.is_log_level_shown("DEBUG")
    assert tab.get_theme() == before["theme"]
    pending = set(tab.pending_changes())
    assert {
        "base_folder_name",
        "simultaneous_downloads",
        "save_preview_images",
        "creator_posts_max_attempts",
        "post_data_max_retries",
        "file_download_max_retries",
        "api_request_max_retries",
        "creator_filename_template",
        "creator_folder_strategy",
        "auto_check_updates",
        "show_debug_logs",
        "font",
        "theme",
        "use_proxy",
        "proxy_type",
        "custom_proxy_url",
    } <= pending
    assert not tab.pending_label.isHidden() and tab.discard_button.isEnabled()
    assert tab.apply_button.property("kdRole") == "primary"

    assert tab.apply_pending_settings(confirm=False)
    assert saved and themes == ["forest"] and fonts == ["Poppins"]
    assert tab.get_simultaneous_downloads() == 9
    assert tab.is_log_level_shown("DEBUG")
    assert tab.get_proxy_settings() == {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080",
    }
    assert tab.pending_changes() == []
    assert tab.pending_label.isHidden() and not tab.discard_button.isEnabled()
    assert tab.apply_button.property("kdRole") is None


def test_language_applies_only_on_apply(tab, monkeypatch):
    changed = []
    tab.language_changed.connect(lambda: changed.append(True))
    tab.language_combo.setCurrentIndex(tab.language_combo.findData("korean"))
    assert changed == [] and tab.settings["language"] == "english"
    try:
        assert tab.apply_pending_settings(confirm=False)
        assert changed == [True]
    finally:
        tab.update_temp_setting("language", "english")
        tab.apply_pending_settings(confirm=False)


def test_apply_with_nothing_changed_says_so(tab, monkeypatch):
    told = []
    monkeypatch.setattr(QMessageBox, "information", lambda *a: told.append(a[2]))
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: pytest.fail("asked"))
    tab.confirm_and_apply_settings()
    assert told == [translate("nothing_to_apply")]


def test_the_confirmation_lists_only_what_changed(tab, monkeypatch):
    asked, told = [], []
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: asked.append(a[2]) or YES
    )
    monkeypatch.setattr(QMessageBox, "information", lambda *a: told.append(a[2]))
    tab.theme_combo.setCurrentIndex(tab.theme_combo.findData("plum"))
    tab.download_slider.setValue(7)
    tab.confirm_and_apply_settings()

    def label(key):
        return translate(key).strip().rstrip(":：")

    lines = asked[0].split("\n")[2:]
    assert lines == [
        f"• {label('simultaneous_downloads')}: 5 → 7",
        f"• {label('theme_label')}: {translate('theme_' + DEFAULT_THEME)}"
        f" → {translate('theme_plum')}",
    ]
    assert told[0].split("\n")[2:] == lines  # and the result repeats them


def test_saying_no_applies_nothing(tab, monkeypatch):
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: NO)
    tab.theme_combo.setCurrentIndex(tab.theme_combo.findData("ember"))
    tab.confirm_and_apply_settings()
    assert tab.get_theme() == DEFAULT_THEME
    assert tab.pending_changes() == ["theme"]


def test_values_are_shown_as_people_know_them(tab):
    show = tab._display_value
    assert show("auto_check_updates", True) == translate("enabled")
    assert show("language", "japanese") == translate("japanese")
    assert show("theme", "plum") == translate("theme_plum")
    assert show("creator_folder_strategy", "by_file_type") == translate(
        "subfolders_by_file_type"
    )
    assert show("proxy_type", "custom") == translate("custom_proxy")
    assert show("proxy_type", "tor") == "Tor"
    assert show("tor_path", "") == "—"


# ---------------------------------------------------------- discard, reset


def test_discard_puts_every_control_back(tab):
    before = dict(tab.settings)
    change_everything(tab)
    tab.discard_changes()
    assert tab.temp_settings == before and tab.pending_changes() == []
    assert tab.folder_name_input.text() == before["base_folder_name"]
    assert tab.download_spinbox.value() == before["simultaneous_downloads"]
    assert tab.theme_combo.currentData() == before["theme"]
    assert not tab.use_proxy_checkbox.isChecked()
    assert tab.proxy_group.isHidden()
    assert tab.pending_label.isHidden()


def test_reset_fills_in_defaults_without_applying_them(tab, monkeypatch):
    tab.theme_combo.setCurrentIndex(tab.theme_combo.findData("graphite"))
    tab.creator_folder_strategy_combo.setCurrentIndex(2)
    tab.log_level_checkboxes["DEBUG"].setChecked(True)
    assert tab.apply_pending_settings(confirm=False)
    tab.reset_to_defaults()
    # Shown...
    assert tab.theme_combo.currentData() == DEFAULT_THEME
    assert tab.creator_folder_strategy_combo.currentData() == "per_post"
    assert not tab.log_level_checkboxes["DEBUG"].isChecked()
    # ...but not in effect before Apply Changes.
    assert tab.get_theme() == "graphite" and tab.is_log_level_shown("DEBUG")
    assert tab.get_creator_folder_strategy() == "by_file_type"
    assert tab.apply_pending_settings(confirm=False)
    assert tab.get_theme() == DEFAULT_THEME
    assert tab.get_creator_folder_strategy() == "per_post"


# ------------------------------------------------------- filename template


def test_choosing_custom_template_keeps_the_template_in_use(tab):
    combo = tab.creator_filename_combo
    combo.setCurrentIndex(1)
    preset = combo.itemData(1)
    combo.setCurrentIndex(combo.count() - 1)  # "Custom..."
    # Not the label: the template carries on, ready to edit.
    assert tab.temp_settings["creator_filename_template"] == preset
    assert combo.currentText() == preset
    combo.lineEdit().setText("{post_title}_{file_index}")
    assert tab.temp_settings["creator_filename_template"] == "{post_title}_{file_index}"


# ------------------------------------------------------------------ proxy


def test_an_empty_custom_proxy_is_refused(tab, monkeypatch):
    warned = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: warned.append(a[2]))
    tab.use_proxy_checkbox.setChecked(True)
    tab.proxy_type_combo.setCurrentIndex(tab.proxy_type_combo.findData("custom"))
    tab.custom_proxy_input.setText("   ")
    assert not tab.apply_pending_settings(confirm=False)
    assert warned == [translate("custom_proxy_url_required")]
    assert tab.get_proxy_settings() is None and not tab.settings["use_proxy"]


def test_the_proxy_switch_is_not_remembered_between_launches(tab):
    tab.use_proxy_checkbox.setChecked(True)
    tab.proxy_type_combo.setCurrentIndex(tab.proxy_type_combo.findData("custom"))
    tab.custom_proxy_input.setText("socks5h://127.0.0.1:1080")
    assert tab.apply_pending_settings(confirm=False)
    assert tab.get_proxy_settings()
    reloaded = tab.load_settings()
    assert reloaded["use_proxy"] is False
    assert reloaded["custom_proxy_url"] == "socks5h://127.0.0.1:1080"


def test_turning_the_proxy_off_takes_effect_on_apply(tab):
    tab.use_proxy_checkbox.setChecked(True)
    tab.proxy_type_combo.setCurrentIndex(tab.proxy_type_combo.findData("custom"))
    tab.custom_proxy_input.setText("http://127.0.0.1:8080")
    assert tab.apply_pending_settings(confirm=False)
    tab.use_proxy_checkbox.setChecked(False)
    assert tab.get_proxy_settings() is not None  # still applied
    assert tab.apply_pending_settings(confirm=False)
    assert tab.get_proxy_settings() is None


def test_a_route_change_during_downloads_is_mentioned(tab, monkeypatch):
    asked = []
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: asked.append(a[2]) or NO
    )
    tab.parent = SimpleNamespace(
        post_tab=SimpleNamespace(downloading=True), log=lambda m: None
    )
    tab.theme_combo.setCurrentIndex(tab.theme_combo.findData("plum"))
    tab.confirm_and_apply_settings()  # no route change: nothing to mention
    tab.use_proxy_checkbox.setChecked(True)
    tab.proxy_type_combo.setCurrentIndex(tab.proxy_type_combo.findData("custom"))
    tab.custom_proxy_input.setText("http://127.0.0.1:8080")
    tab.confirm_and_apply_settings()
    note = translate("route_change_during_downloads")
    assert note not in asked[0] and note in asked[1]


# -------------------------------------------------------------------- Tor


def choose_tor(tab, tor_path=""):
    tab.update_temp_setting("tor_path", tor_path)
    tab.use_proxy_checkbox.setChecked(True)
    tab.proxy_type_combo.setCurrentIndex(tab.proxy_type_combo.findData("tor"))


def test_tor_not_running_can_be_started_while_applying(tab, monkeypatch, tmp_path):
    tor = tmp_path / "tor.exe"
    tor.write_text("x")
    shown = answer(monkeypatch, "start_tor_and_apply")
    started = []
    monkeypatch.setattr(
        tab,
        "start_tor",
        lambda: started.append(True) or setattr(tab, "tor_process", object()),
    )
    choose_tor(tab, str(tor))
    assert tab.apply_pending_settings(confirm=False)
    assert started and shown == [translate("tor_not_running_apply")]
    assert tab.get_proxy_settings()["https"] == ks.TOR_SOCKS_PROXY


def test_tor_that_fails_to_start_applies_nothing(tab, monkeypatch, tmp_path):
    tor = tmp_path / "tor.exe"
    tor.write_text("x")
    answer(monkeypatch, "start_tor_and_apply")
    monkeypatch.setattr(tab, "start_tor", lambda: None)  # explains, starts nothing
    choose_tor(tab, str(tor))
    assert not tab.apply_pending_settings(confirm=False)
    assert tab.get_proxy_settings() is None


def test_tor_not_running_can_be_applied_anyway(tab, monkeypatch):
    shown = answer(monkeypatch, "apply_anyway")
    choose_tor(tab)  # no Tor program: the dialog says how to set it up
    assert tab.apply_pending_settings(confirm=False)
    assert translate("tor_not_set_up_apply") in shown[0]
    # Fails closed: Tor's port, never a direct connection.
    assert tab.get_proxy_settings()["https"] == ks.TOR_SOCKS_PROXY


def test_tor_not_running_offers_no_start_without_a_program(tab, monkeypatch):
    buttons = []

    def exec_(box):
        buttons.extend(b.text() for b in box.buttons())

    monkeypatch.setattr(QMessageBox, "exec", exec_)
    monkeypatch.setattr(QMessageBox, "clickedButton", lambda box: None)
    choose_tor(tab, "")
    assert not tab.apply_pending_settings(confirm=False)  # closed: cancel
    assert translate("start_tor_and_apply") not in buttons
    assert translate("apply_anyway") in buttons


def test_cancelling_the_tor_question_applies_nothing(tab, monkeypatch):
    answer(monkeypatch, "cancel")
    choose_tor(tab)
    tab.theme_combo.setCurrentIndex(tab.theme_combo.findData("ember"))
    assert not tab.apply_pending_settings(confirm=False)
    assert tab.get_theme() == DEFAULT_THEME and tab.get_proxy_settings() is None
    assert "theme" in tab.pending_changes()


def test_a_tor_already_listening_needs_no_question(tab, monkeypatch):
    monkeypatch.setattr(ks, "tor_is_listening", lambda timeout=0.3: True)
    monkeypatch.setattr(QMessageBox, "exec", lambda box: pytest.fail("asked"))
    choose_tor(tab)
    assert tab.apply_pending_settings(confirm=False)


def test_the_apps_running_tor_needs_no_question(tab, monkeypatch):
    monkeypatch.setattr(tab, "is_tor_running", lambda: True)
    monkeypatch.setattr(QMessageBox, "exec", lambda box: pytest.fail("asked"))
    choose_tor(tab)
    assert tab.apply_pending_settings(confirm=False)


def test_other_changes_dont_ask_about_tor_again(tab, monkeypatch):
    answer(monkeypatch, "apply_anyway")
    choose_tor(tab)
    assert tab.apply_pending_settings(confirm=False)
    monkeypatch.setattr(QMessageBox, "exec", lambda box: pytest.fail("asked"))
    tab.theme_combo.setCurrentIndex(tab.theme_combo.findData("forest"))
    assert tab.apply_pending_settings(confirm=False)


@pytest.mark.parametrize("stop", [True, False])
def test_turning_tor_off_offers_to_stop_it(tab, monkeypatch, stop):
    answer(monkeypatch, "apply_anyway")
    choose_tor(tab)
    assert tab.apply_pending_settings(confirm=False)
    monkeypatch.setattr(tab, "is_tor_running", lambda: True)
    asked, stopped = [], []
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *a, **k: asked.append(a[1]) or (YES if stop else NO),
    )
    monkeypatch.setattr(
        tab, "stop_tor", lambda: stopped.append(tab.get_proxy_settings())
    )
    tab.use_proxy_checkbox.setChecked(False)
    assert tab.apply_pending_settings(confirm=False)
    assert asked == [translate("stop_tor_after_apply_title")]
    # Stopped only after the new route is in effect, never before.
    assert stopped == ([None] if stop else [])


def test_closing_never_asks_about_tor(tab, monkeypatch):
    monkeypatch.setattr(QMessageBox, "exec", lambda box: pytest.fail("asked"))
    choose_tor(tab)
    assert tab.apply_pending_settings(confirm=False, closing=True)


class FakeProcess:
    def __init__(self, parent=None):
        self.started = False
        signal = SimpleNamespace(connect=lambda f: None)
        self.readyReadStandardOutput = signal
        self.readyReadStandardError = signal
        self.finished = signal

    def setProgram(self, program):  # noqa: N802 (Qt API)
        pass

    def setArguments(self, args):  # noqa: N802
        pass

    def start(self):
        self.started = True

    def state(self):
        return ks.QProcess.ProcessState.Running

    def terminate(self):
        pass

    def waitForFinished(self, ms):  # noqa: N802
        return True


@pytest.mark.parametrize("applied", [False, True])
def test_starting_tor_says_whether_downloads_use_it(
    tab, monkeypatch, tmp_path, applied
):
    tor = tmp_path / "tor.exe"
    tor.write_text("x")
    monkeypatch.setattr(ks, "QProcess", FakeProcess)
    told = []
    monkeypatch.setattr(QMessageBox, "information", lambda *a: told.append(a[2]))
    if applied:
        tab.settings.update(use_proxy=True, proxy_type="tor")
    tab.update_temp_setting("tor_path", str(tor))
    tab.start_tor()
    hint = translate("tor_started_not_applied")
    assert (hint in told[-1]) is (not applied)
    tab.stop_tor()
    in_use = translate("tor_stopped_in_use")
    assert (in_use in told[-1]) is applied


# ------------------------------------------------------------ closing


@pytest.mark.parametrize(
    "button, closes, applied",
    [
        ("apply_changes", True, True),
        ("discard_changes", True, False),
        ("cancel", False, False),
    ],
)
def test_closing_with_unapplied_changes_asks(tab, monkeypatch, button, closes, applied):
    shown = answer(monkeypatch, button)
    tab.theme_combo.setCurrentIndex(tab.theme_combo.findData("ember"))
    assert tab.confirm_close_with_pending_changes() is closes
    assert translate("theme_ember") in shown[0]
    assert (tab.get_theme() == "ember") is applied


def test_closing_without_changes_just_closes(tab, monkeypatch):
    monkeypatch.setattr(QMessageBox, "exec", lambda box: pytest.fail("asked"))
    assert tab.confirm_close_with_pending_changes()
    # The proxy switch alone isn't worth asking about: never remembered.
    tab.use_proxy_checkbox.setChecked(True)
    assert tab.confirm_close_with_pending_changes()


def test_the_window_stays_open_when_closing_is_cancelled(qapp):
    from kemonodownloader.app import KemonoDownloader

    ignored = []
    fake = SimpleNamespace(
        isVisible=lambda: True,
        settings_tab=SimpleNamespace(confirm_close_with_pending_changes=lambda: False),
    )
    KemonoDownloader.closeEvent(fake, SimpleNamespace(ignore=lambda: ignored.append(1)))
    assert ignored == [1]
