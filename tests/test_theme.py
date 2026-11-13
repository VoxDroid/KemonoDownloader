"""The app-wide theme: one style sheet, roles instead of inline styles."""

import ast
import inspect
import os

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QPushButton, QWidget

from kemonodownloader import kd_theme
from kemonodownloader.kd_theme import (
    apply_theme,
    set_progress_state,
    set_role,
    set_tone,
    stylesheet,
)


class RecordingApp:
    """Stands in for QApplication: restyling the shared test application would
    repolish every widget earlier tests left behind."""

    def __init__(self):
        self.sheets = []

    def setStyleSheet(self, sheet):  # noqa: N802 (Qt API)
        self.sheets.append(sheet)


@pytest.fixture
def fresh_theme(monkeypatch):
    monkeypatch.setattr(kd_theme, "_applied_to", None)


def test_apply_theme_loads_the_sheet_and_its_glyphs(qapp, fresh_theme):
    app = RecordingApp()
    apply_theme(app)
    (sheet,) = app.sheets
    assert 'QPushButton[kdRole="primary"]' in sheet
    paths = [
        part.split("'")[1] for part in sheet.split("url(")[1:] if part.startswith("'")
    ]
    assert paths, "check marks and arrows should be drawn from files"
    assert all(os.path.isfile(path) for path in paths)


def test_apply_theme_runs_once_per_app(qapp, fresh_theme):
    app = RecordingApp()
    apply_theme(app)
    apply_theme(app)
    assert len(app.sheets) == 1


def test_apply_theme_ignores_objects_without_style_sheets(fresh_theme):
    apply_theme(object())
    assert kd_theme._applied_to is None


def test_stylesheet_falls_back_without_glyphs():
    sheet = stylesheet({})
    assert "url(" not in sheet
    assert "QCheckBox::indicator:checked" in sheet


@pytest.mark.parametrize("role", [None, "primary", "danger"])
def test_button_states_never_change_size(qapp, role):
    """Hover, press, focus and disable change colours only, never the shape."""
    themed = qapp
    host = QWidget()
    host.setStyleSheet(stylesheet())
    layout = QHBoxLayout(host)
    button = QPushButton("Download")
    set_role(button, role)
    layout.addWidget(button)
    host.show()
    themed.processEvents()
    resting = (button.sizeHint(), button.geometry())

    def same_shape():
        themed.processEvents()
        return (button.sizeHint(), button.geometry()) == resting

    try:
        button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, True)
        kd_theme.repolish(button)
        assert same_shape()
        button.setDown(True)
        assert same_shape()
        button.setDown(False)
        button.setFocus()
        assert same_shape()
        button.setEnabled(False)
        assert same_shape()
    finally:
        host.deleteLater()


def test_roles_tones_and_states_are_properties(qapp):
    button = QPushButton()
    label = QLabel()
    bar = QProgressBar()
    assert set_role(button, "primary") is button
    assert button.property("kdRole") == "primary"
    set_tone(label, "error")
    assert label.property("kdTone") == "error"
    set_progress_state(bar, "paused")
    assert bar.property("kdState") == "paused"
    set_progress_state(bar, None)
    assert bar.property("kdState") is None


def test_unchanged_properties_skip_the_repolish(qapp, monkeypatch):
    button = QPushButton()
    set_role(button, "danger")
    calls = []
    monkeypatch.setattr(kd_theme, "repolish", lambda w: calls.append(w))
    set_role(button, "danger")
    assert calls == []


def _inline_style_targets(module):
    tree = ast.parse(inspect.getsource(module))
    return {
        ast.unparse(node.func.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "setStyleSheet"
    }


def test_tabs_take_their_look_from_the_theme():
    from kemonodownloader import (
        creator_downloader,
        kd_extension,
        kd_help,
        kd_history,
        kd_logs,
        kd_settings,
        kd_thumbnaildl,
        post_downloader,
    )

    # Only the selection highlight of the custom file rows stays inline.
    row_highlight = {"widget", "w"}
    assert _inline_style_targets(post_downloader) <= row_highlight | {"label"}
    assert _inline_style_targets(creator_downloader) <= row_highlight
    for module in (
        kd_extension,
        kd_help,
        kd_history,
        kd_logs,
        kd_settings,
        kd_thumbnaildl,
    ):
        assert _inline_style_targets(module) == set(), module.__name__


def test_tab_action_buttons_have_roles():
    from kemonodownloader import creator_downloader, post_downloader

    post = inspect.getsource(post_downloader.PostDownloaderTab)
    creator = inspect.getsource(creator_downloader.CreatorDownloaderTab)
    for source, prefix in ((post, "post"), (creator, "creator")):
        assert f'set_role(self.{prefix}_download_btn, "primary")' in source
        assert f'set_role(self.{prefix}_cancel_btn, "danger")' in source
        assert ".enterEvent =" not in source
