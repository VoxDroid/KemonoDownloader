"""Settings › Log Settings: which console messages are shown."""

from types import SimpleNamespace

import pytest
from PyQt6.QtWidgets import QTextEdit

from kemonodownloader import creator_downloader as cd, post_downloader as pd
from kemonodownloader.kd_language import language_manager, translate
from kemonodownloader.kd_logs import log_level_shown, message_level
from kemonodownloader.kd_settings import LOG_LEVEL_SETTINGS, SettingsTab


@pytest.fixture
def settings(qapp):
    tab = SettingsTab(SimpleNamespace(log=lambda m: None))
    yield tab
    tab.deleteLater()


def test_debug_is_off_and_the_rest_on_by_default(settings):
    defaults = settings.default_settings
    assert defaults["show_debug_logs"] is False
    assert all(
        defaults[key]
        for level, (key, _label, _default) in LOG_LEVEL_SETTINGS.items()
        if level != "DEBUG"
    )
    assert not settings.is_log_level_shown("DEBUG")
    assert settings.is_log_level_shown("info")  # any case
    assert settings.is_log_level_shown("WARNING")
    assert settings.is_log_level_shown("ERROR")
    assert settings.is_log_level_shown("SOMETHING_ELSE")


def test_checkboxes_save_straight_away(settings, monkeypatch):
    saved = []
    monkeypatch.setattr(settings, "save_settings", lambda: saved.append(True))
    settings.log_level_checkboxes["DEBUG"].setChecked(True)
    assert settings.is_log_level_shown("DEBUG")
    assert settings.temp_settings["show_debug_logs"] is True
    assert saved
    settings.log_level_checkboxes["WARNING"].setChecked(False)
    assert not settings.is_log_level_shown("WARNING")


def test_reset_to_defaults_hides_debug_again(settings, monkeypatch):
    from kemonodownloader import kd_settings as ks

    monkeypatch.setattr(settings, "save_settings", lambda: None)
    monkeypatch.setattr(ks.QMessageBox, "information", lambda *a, **k: None)
    settings.log_level_checkboxes["DEBUG"].setChecked(True)
    settings.reset_to_defaults()
    assert not settings.log_level_checkboxes["DEBUG"].isChecked()
    assert not settings.is_log_level_shown("DEBUG")


def test_settings_survive_a_restart(settings, monkeypatch):
    settings.set_log_level_shown("show_debug_logs", True)
    settings.set_log_level_shown("show_info_logs", False)
    reloaded = settings.load_settings()
    assert reloaded["show_debug_logs"] is True
    assert reloaded["show_info_logs"] is False
    settings.set_log_level_shown("show_debug_logs", False)
    settings.set_log_level_shown("show_info_logs", True)


def test_group_has_its_note_and_translated_labels(settings, monkeypatch):
    from kemonodownloader import kd_settings as ks

    monkeypatch.setattr(ks, "translate", lambda key, *a: f"<{key}>")
    settings.update_ui_text()
    assert settings.log_group.title() == "<log_settings>"
    assert settings.log_level_checkboxes["DEBUG"].text() == "<log_level_debug>"
    notes = [
        label.property("kdNoteKey")
        for label in settings.log_group.findChildren(type(settings.proxy_intro_label))
        if label.property("kdNoteKey")
    ]
    assert notes == ["note_log_settings"]


@pytest.mark.parametrize(
    "language", ["english", "japanese", "korean", "chinese-simplified"]
)
def test_message_level_reads_the_tag_in_any_language(language, monkeypatch):
    monkeypatch.setattr(language_manager, "current_language", language)
    debug = translate("log_debug", "Trying endpoint")
    assert message_level(debug, "INFO") == "DEBUG"
    assert message_level(translate("log_error", "x"), "INFO") == "ERROR"
    assert message_level(translate("log_warning", "x")) == "WARNING"
    assert message_level("no tag", "warning") == "WARNING"
    assert message_level("no tag", None) == "INFO"
    assert message_level("no tag", "TRACE") == "INFO"
    # English tags still count after switching language.
    assert message_level("[DEBUG] old line", "INFO") == "DEBUG"


def test_log_level_shown_without_settings_shows_everything():
    assert log_level_shown(None, "DEBUG")
    assert log_level_shown(SimpleNamespace(), "DEBUG")
    broken = SimpleNamespace(is_log_level_shown=lambda level: 1 / 0)
    assert log_level_shown(broken, "DEBUG")


def _settings_showing(*levels):
    return SimpleNamespace(is_log_level_shown=lambda level: level in levels)


def test_post_console_hides_unwanted_levels(qapp):
    tab = SimpleNamespace(
        parent=SimpleNamespace(settings_tab=_settings_showing("INFO", "ERROR")),
        post_console=QTextEdit(),
    )
    pd.PostDownloaderTab.append_log_to_console(tab, translate("log_debug", "d"), "INFO")
    pd.PostDownloaderTab.append_log_to_console(tab, "careful", "WARNING")
    pd.PostDownloaderTab.append_log_to_console(tab, "done", "INFO")
    pd.PostDownloaderTab.append_log_to_console(tab, "broken", "ERROR")
    assert tab.post_console.toPlainText().splitlines() == ["done", "broken"]


def test_creator_console_hides_debug_by_default(qapp, settings):
    tab = SimpleNamespace(
        _parent=SimpleNamespace(settings_tab=settings),
        creator_console=QTextEdit(),
    )
    cd.CreatorDownloaderTab.append_log_to_console(
        tab, translate("log_debug", "page 2"), "DEBUG"
    )
    cd.CreatorDownloaderTab.append_log_to_console(tab, "found 3 posts", "INFO")
    assert tab.creator_console.toPlainText() == "found 3 posts"


def test_thumbnail_log_hides_by_tag(qapp):
    from kemonodownloader.kd_thumbnaildl import ThumbnailDownloaderTab

    tab = SimpleNamespace(
        parent=SimpleNamespace(settings_tab=_settings_showing("INFO")),
        log_console=QTextEdit(),
    )
    ThumbnailDownloaderTab.append_log(tab, translate("log_warning", "slow"))
    ThumbnailDownloaderTab.append_log(tab, "3 thumbnails detected")
    assert tab.log_console.toPlainText() == "3 thumbnails detected"


def test_debug_messages_are_sent_as_debug():
    import ast
    import inspect

    for module in (pd, cd):
        tree = ast.parse(inspect.getsource(module))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and len(node.args) > 1):
                continue
            first = node.args[0]
            if (
                isinstance(first, ast.Call)
                and getattr(first.func, "id", None) == "translate"
                and first.args
                and getattr(first.args[0], "value", None) == "log_debug"
            ):
                level = node.args[1]
                assert getattr(level, "value", "DEBUG") == "DEBUG", node.lineno
