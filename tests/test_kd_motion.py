"""Tests for the motion helpers and the staged main-window build."""

import time

from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QLabel,
    QListWidget,
    QWidget,
)
from tests.test_app import mock_app_dependencies  # noqa: F401  (fixture)

from kemonodownloader.kd_motion import (
    SmoothProgressBar,
    SmoothWheelScroller,
    enable_pixel_scrolling,
    fade_in,
)


def pump(qapp, seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        qapp.processEvents()
        time.sleep(0.005)


def wheel(widget, angle_y=-120, pixel=QPoint(0, 0), modifiers=None):
    return QWheelEvent(
        QPointF(10, 10),
        QPointF(10, 10),
        pixel,
        QPoint(0, angle_y),
        Qt.MouseButton.NoButton,
        modifiers or Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )


def test_progress_bar_reports_target_while_gliding(qapp):
    bar = SmoothProgressBar()
    bar.show()
    bar.setValue(80)
    assert bar.value() == 80
    pump(qapp, 0.4)
    assert super(SmoothProgressBar, bar).value() == 80
    bar.deleteLater()


def test_progress_bar_jumps_back_and_when_hidden(qapp):
    bar = SmoothProgressBar()
    bar.setValue(60)  # hidden: no animation
    assert super(SmoothProgressBar, bar).value() == 60
    bar.show()
    bar.setValue(10)  # backwards: instant
    assert super(SmoothProgressBar, bar).value() == 10
    bar.setValue(500)  # out of range is ignored, like QProgressBar
    assert bar.value() == 10
    bar.setRange(0, 0)  # busy indicator
    assert bar.value() == super(SmoothProgressBar, bar).value()
    bar.deleteLater()


def make_list(qapp, rows=300):
    view = QListWidget()
    view.resize(200, 150)
    for i in range(rows):
        view.addItem(f"row {i}")
    enable_pixel_scrolling(view.parentWidget() or view)
    view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    view.show()
    qapp.processEvents()
    return view


def test_wheel_glides_and_accumulates(qapp):
    view = make_list(qapp)
    scroller = SmoothWheelScroller()
    bar = view.verticalScrollBar()
    assert scroller.eventFilter(view.viewport(), wheel(view.viewport())) is True
    assert scroller.eventFilter(view.viewport(), wheel(view.viewport())) is True
    pump(qapp, 0.5)
    expected = 2 * bar.singleStep() * qapp.wheelScrollLines()
    assert bar.value() == min(expected, bar.maximum())
    view.deleteLater()


def test_wheel_passes_through_when_it_should(qapp):
    view = make_list(qapp)
    scroller = SmoothWheelScroller()
    port = view.viewport()
    # Already at the top: let Qt hand the wheel to an outer view.
    assert scroller.eventFilter(port, wheel(port, angle_y=120)) is False
    # Touchpads send pixel deltas that are already smooth.
    assert scroller.eventFilter(port, wheel(port, pixel=QPoint(0, -5))) is False
    # Ctrl+wheel keeps meaning zoom.
    ctrl = Qt.KeyboardModifier.ControlModifier
    assert scroller.eventFilter(port, wheel(port, modifiers=ctrl)) is False
    # Widgets that are not scroll-area viewports are left alone.
    assert scroller.eventFilter(view, wheel(view)) is False
    view.deleteLater()


def test_wheel_over_widget_with_shadowed_parent_does_not_crash(qapp):
    # Regression: the tabs store their owner in `self.parent`, hiding
    # QObject.parent(); an exception in an app-wide filter aborts the app.
    # Deliver through the real event path, as a mouse wheel would.
    class Tab(QWidget):
        def __init__(self, owner):
            super().__init__()
            self.parent = owner

    owner = QWidget()
    tab = Tab(owner)
    view = QListWidget(tab)
    view.parent = owner  # shadowed on the scroll area too
    for i in range(300):
        view.addItem(f"row {i}")
    tab.resize(200, 150)
    view.resize(200, 150)
    tab.show()
    qapp.processEvents()
    scroller = SmoothWheelScroller()
    qapp.installEventFilter(scroller)
    try:
        for target in (tab, view, view.viewport()):
            QApplication.sendEvent(target, wheel(target))
        pump(qapp, 0.4)
        assert view.verticalScrollBar().value() > 0  # viewport wheel glided
    finally:
        qapp.removeEventFilter(scroller)
        tab.deleteLater()
        owner.deleteLater()


def test_wheel_filter_swallows_its_own_errors(qapp, monkeypatch):
    scroller = SmoothWheelScroller()

    def boom(*_):
        raise RuntimeError("unexpected")

    monkeypatch.setattr(scroller, "_glide", boom)
    widget = QWidget()
    assert scroller.eventFilter(widget, wheel(widget)) is False
    widget.deleteLater()


def test_main_detaches_wheel_filter_before_exit(monkeypatch):
    # Regression: leaving the app-wide filter installed while Python shuts
    # down crashed natively when the window was closed.
    from kemonodownloader import app as app_mod

    calls = []

    class FakeApp:
        def __init__(self, argv):
            pass

        def setStyle(self, _):
            pass

        def installEventFilter(self, f):
            calls.append(("install", f))

        def exec(self):
            calls.append(("exec", None))
            return 0

        def removeEventFilter(self, f):
            calls.append(("remove", f))

    class FakeWindow:
        def show(self):
            pass

    monkeypatch.setattr(app_mod, "QApplication", FakeApp)
    monkeypatch.setattr(app_mod, "KemonoDownloader", FakeWindow)
    monkeypatch.setattr(app_mod, "load_bundled_fonts", lambda: None)
    monkeypatch.setattr(
        app_mod.sys, "exit", lambda code=0: calls.append(("exit", code))
    )

    app_mod.main()

    scroller = app_mod._wheel_scroller
    assert calls == [
        ("install", scroller),
        ("exec", None),
        ("remove", scroller),
        ("exit", 0),
    ]


def test_destroying_widget_mid_fade_is_safe(qapp):
    # Regression: the target being destroyed stops the animation and emits
    # finished; cleanup must not then touch the half-destroyed widget.
    widget = QWidget()
    QLabel("x", widget)
    widget.show()
    fade_in(widget, 400)
    pump(qapp, 0.05)
    widget.deleteLater()
    pump(qapp, 0.1)


def test_fade_in_removes_effect_when_done(qapp):
    widget = QWidget()
    widget.show()
    fade_in(widget, 60)
    assert widget.graphicsEffect() is not None
    pump(qapp, 0.3)
    assert widget.graphicsEffect() is None
    widget.deleteLater()


def test_background_build_then_instant_launch(
    qapp, mock_app_dependencies, monkeypatch  # noqa: F811
):
    import os
    from unittest.mock import MagicMock

    from kemonodownloader.app import KemonoDownloader

    monkeypatch.setattr(os, "makedirs", MagicMock())
    window = KemonoDownloader()
    window.show()
    try:
        window.start_background_build()
        window.start_background_build()  # second call is a no-op
        deadline = time.monotonic() + 5
        while window._prebuilt_main_widget is None and time.monotonic() < deadline:
            qapp.processEvents()
        prebuilt = window._prebuilt_main_widget
        assert prebuilt is not None
        assert window.tabs.count() == 7  # History tab added

        window.transition_to_main()
        assert window.main_widget is prebuilt
        assert window.centralWidget() is prebuilt
        assert prebuilt.isVisible() and window.tabs.currentWidget().isVisible()
        assert window.intro_screen is None
        assert window.intro_fade is not None  # crossfade over the new screen
        pump(qapp, 0.4)
    finally:
        window.deleteLater()


def test_tab_click_crossfades_but_programmatic_switch_does_not(
    qapp, mock_app_dependencies, monkeypatch  # noqa: F811
):
    import os
    from unittest.mock import MagicMock

    from kemonodownloader.app import KemonoDownloader

    monkeypatch.setattr(os, "makedirs", MagicMock())
    window = KemonoDownloader()
    window.resize(900, 600)
    window.show()
    try:
        window.transition_to_main()
        pump(qapp, 0.35)
        window.tabs.setCurrentIndex(1)  # code-driven: no fade
        assert getattr(window, "tab_fade", None) is None

        window.tabs.tabBarClicked.emit(2)  # what a real click emits first
        window.tabs.setCurrentIndex(2)
        assert window.tab_fade is not None
        pump(qapp, 0.3)

        window.tabs.setTabEnabled(3, False)
        window.tab_fade = None
        window.tabs.tabBarClicked.emit(3)  # disabled tab: nothing to fade
        assert window._tab_snapshot is None
    finally:
        window.deleteLater()


def test_launch_during_background_build_finishes_it(
    qapp, mock_app_dependencies, monkeypatch  # noqa: F811
):
    import os
    from unittest.mock import MagicMock

    from kemonodownloader.app import KemonoDownloader

    monkeypatch.setattr(os, "makedirs", MagicMock())
    window = KemonoDownloader()
    window.show()
    try:
        window.start_background_build()
        window._advance_background_build()  # partway through
        window.transition_to_main()
        assert window.centralWidget() is window.main_widget
        assert window.main_widget.isVisible()
        assert window.tabs.count() == 7  # History tab added
        assert window._main_ui_builder is None
        pump(qapp, 0.05)  # pending build steps must not run again
        assert window.tabs.count() == 7  # History tab added
    finally:
        window.deleteLater()
