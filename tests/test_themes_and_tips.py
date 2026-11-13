"""Colour themes (Settings › Appearance) and tooltips across the app."""

from types import SimpleNamespace

import pytest
from PyQt6.QtWidgets import (
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QSlider,
    QWidget,
)

from kemonodownloader import kd_theme
from kemonodownloader.kd_language import language_manager
from kemonodownloader.kd_notes import TIP_KEY_PROPERTY, retranslate_notes, tip, tips
from kemonodownloader.kd_theme import (
    DEFAULT_THEME,
    THEMES,
    color,
    restyle_rows,
    style_row,
    stylesheet,
    theme_name,
    use_theme,
)


@pytest.fixture
def default_theme():
    yield
    use_theme(DEFAULT_THEME)


def _luminance(hex_color):
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    channels = [
        c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast(a, b):
    high, low = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


# ------------------------------------------------------------------ themes --


def test_every_theme_defines_the_same_colours():
    roles = set(THEMES[DEFAULT_THEME])
    for name, palette in THEMES.items():
        assert set(palette) == roles, name
        assert all(
            value.startswith("#") and len(value) == 7 for value in palette.values()
        )


@pytest.mark.parametrize("name", list(THEMES))
def test_every_theme_is_readable(name):
    p = THEMES[name]
    for background in ("BG", "SURFACE", "CONSOLE", "CONTROL", "ACCENT", "DANGER"):
        assert _contrast(p["TEXT"], p[background]) >= 4.5, (name, background)
    assert _contrast(p["TEXT_MUTED"], p["SURFACE"]) >= 4.5, name
    assert _contrast(p["TEXT_SOFT"], p["NOTE_BG"]) >= 4.5, name
    assert _contrast(p["TEXT_DISABLED"], p["DISABLED_BG"]) >= 3, name


@pytest.mark.parametrize("name", list(THEMES))
def test_stylesheet_uses_the_theme_colours(name):
    sheet = stylesheet({}, name)
    assert f"background: {THEMES[name]['BG']}" in sheet
    assert THEMES[name]["ACCENT"] in sheet
    if name != DEFAULT_THEME:
        assert THEMES[DEFAULT_THEME]["BG"] not in sheet


def test_unknown_themes_fall_back_to_the_default(default_theme):
    assert theme_name("no-such-theme") == DEFAULT_THEME
    assert theme_name(None) == DEFAULT_THEME
    assert use_theme("no-such-theme") == DEFAULT_THEME
    assert color("BG") == THEMES[DEFAULT_THEME]["BG"]


def test_color_follows_the_current_theme(default_theme):
    use_theme("forest")
    assert color("SURFACE") == THEMES["forest"]["SURFACE"]
    assert kd_theme.current_theme() == "forest"


def test_rows_repaint_in_a_new_theme(qapp, default_theme):
    host = QWidget()
    row = QWidget(host)
    selected = QWidget(host)
    style_row(row)
    style_row(selected, selected=True)
    # The default theme keeps the strings the rows always had.
    assert row.styleSheet() == "background-color: #2A3B5A; border-radius: 5px;"
    use_theme("plum")
    restyle_rows(host)
    assert THEMES["plum"]["SURFACE"] in row.styleSheet()
    assert THEMES["plum"]["CONTROL"] in selected.styleSheet()
    host.deleteLater()


def test_apply_theme_switches_and_skips_repeats(default_theme, monkeypatch):
    class App:
        def __init__(self):
            self.sheets = []

        def setStyleSheet(self, sheet):  # noqa: N802
            self.sheets.append(sheet)

    monkeypatch.setattr(kd_theme, "_applied_to", None)
    monkeypatch.setattr(kd_theme, "_render_glyphs", lambda *a, **k: {})
    app = App()
    kd_theme.apply_theme(app, "ember")
    kd_theme.apply_theme(app, "ember")
    kd_theme.apply_theme(app, "graphite")
    assert len(app.sheets) == 2
    assert THEMES["graphite"]["BG"] in app.sheets[-1]
    assert kd_theme.is_themed(app)
    assert kd_theme.current_theme() == "graphite"


def test_window_only_restyles_an_app_main_styled(qapp, default_theme, monkeypatch):
    from kemonodownloader import app as kd_app

    calls = []
    monkeypatch.setattr(kd_app, "apply_theme", lambda *a: calls.append(a))
    monkeypatch.setattr(kd_app, "is_themed", lambda app: False)
    fake = QWidget()
    fake.apply_palette = lambda: calls.append("palette")
    kd_app.KemonoDownloader.apply_app_theme(fake, "forest")
    assert calls == ["palette"]
    assert kd_theme.current_theme() == "forest"
    fake.deleteLater()


@pytest.fixture
def settings(qapp, default_theme):
    from kemonodownloader.kd_settings import SettingsTab

    tab = SettingsTab(SimpleNamespace(log=lambda m: None))
    yield tab
    tab.deleteLater()


def test_settings_lists_every_theme_and_saves_the_choice(settings, monkeypatch):
    saved, changed = [], []
    monkeypatch.setattr(settings, "save_settings", lambda: saved.append(True))
    settings.theme_changed.connect(changed.append)
    names = [
        settings.theme_combo.itemData(i) for i in range(settings.theme_combo.count())
    ]
    assert names == list(THEMES)
    settings.theme_combo.setCurrentIndex(names.index("plum"))
    assert changed == ["plum"]
    assert saved
    assert settings.get_theme() == "plum"


def test_saved_unknown_theme_loads_as_the_default(settings):
    settings.qsettings.setValue("theme", "retired-theme")
    assert settings.load_settings()["theme"] == DEFAULT_THEME
    settings.qsettings.remove("theme")


def test_reset_to_defaults_brings_back_the_default_theme(settings, monkeypatch):
    from kemonodownloader import kd_settings as ks

    monkeypatch.setattr(settings, "save_settings", lambda: None)
    monkeypatch.setattr(ks.QMessageBox, "information", lambda *a, **k: None)
    settings.theme_combo.setCurrentIndex(settings.theme_combo.findData("ember"))
    settings.reset_to_defaults()
    assert settings.get_theme() == DEFAULT_THEME


def test_theme_names_are_translated():
    for name in THEMES:
        entry = language_manager.translations[f"theme_{name}"]
        assert all(entry[lang] for lang in language_manager.get_available_languages())


# -------------------------------------------------------------------- tips --


def test_tip_remembers_its_key_and_retranslates(qapp, monkeypatch):
    from kemonodownloader import kd_notes

    host = QWidget()
    button = QPushButton(host)
    check = QCheckBox(host)
    tip(button, "tip_cancel")
    tips([check], "tip_auto_rename")
    assert button.property(TIP_KEY_PROPERTY) == "tip_cancel"
    assert button.toolTip() == language_manager.get_text("tip_cancel")
    monkeypatch.setattr(kd_notes, "translate", lambda key, *a: f"<{key}>")
    retranslate_notes(host)
    assert button.toolTip() == "<tip_cancel>"
    assert check.toolTip() == "<tip_auto_rename>"
    host.deleteLater()


def test_every_control_in_the_tabs_explains_itself(qapp):
    from kemonodownloader.app import KemonoDownloader

    window = KemonoDownloader()
    window.setup_main_ui()
    kinds = (QPushButton, QCheckBox, QLineEdit, QComboBox, QAbstractSpinBox, QSlider)
    try:
        missing = []
        for name in (
            "post_tab",
            "creator_tab",
            "thumbnail_tab",
            "settings_tab",
            "history_tab",
        ):
            for widget in getattr(window, name).findChildren(QWidget):
                if not isinstance(widget, kinds):
                    continue
                if isinstance(widget, QLineEdit) and isinstance(
                    widget.parent(), (QComboBox, QAbstractSpinBox)
                ):
                    continue  # the editor inside a combo or spin box
                if not widget.toolTip():
                    missing.append(
                        f"{name}: {type(widget).__name__} {widget.objectName()}"
                    )
        assert not missing, missing
    finally:
        window.deleteLater()
