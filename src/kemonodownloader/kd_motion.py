"""Motion helpers that make the interface feel fluid: eased progress, smooth
wheel scrolling, fades and button hover highlights.

Everything here is cheap to paint. Opacity effects are applied only for the
length of an animation and removed afterwards, because a widget that keeps a
QGraphicsEffect is re-rendered off-screen on every repaint.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QEvent,
    QObject,
    QPropertyAnimation,
    QRect,
    Qt,
    QVariantAnimation,
)
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QApplication,
    QGraphicsOpacityEffect,
    QLabel,
    QProgressBar,
    QPushButton,
    QWidget,
)

PROGRESS_GLIDE_MS = 240
WHEEL_GLIDE_MS = 200
FADE_IN_MS = 420
CROSSFADE_MS = 260
TAB_FADE_MS = 160
HOVER_MS = 160


class SmoothProgressBar(QProgressBar):
    """A progress bar that glides forward to new values instead of jumping.

    ``value()`` reports the latest requested value straight away, so callers
    never see the in-between frames. Going backwards (a new file starting at
    0), range changes and hidden bars update instantly, as a plain
    QProgressBar would.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._target: Optional[int] = None
        self._glide = QVariantAnimation(self)
        self._glide.setDuration(PROGRESS_GLIDE_MS)
        self._glide.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._glide.valueChanged.connect(self._show_frame)

    def _show_frame(self, frame) -> None:
        QProgressBar.setValue(self, int(frame))

    def setValue(self, value: int) -> None:  # noqa: N802 (Qt API)
        value = int(value)
        if not self.minimum() <= value <= self.maximum():
            return  # QProgressBar ignores out-of-range values too
        self._target = value
        shown = QProgressBar.value(self)
        self._glide.stop()
        if value <= shown or self.minimum() == self.maximum() or not self.isVisible():
            QProgressBar.setValue(self, value)
            return
        self._glide.setStartValue(shown)
        self._glide.setEndValue(value)
        self._glide.start()

    def value(self) -> int:
        return QProgressBar.value(self) if self._target is None else self._target

    def setRange(self, minimum: int, maximum: int) -> None:  # noqa: N802
        self._glide.stop()
        self._target = None
        super().setRange(minimum, maximum)

    def reset(self) -> None:
        self._glide.stop()
        self._target = None
        super().reset()


class SmoothWheelScroller(QObject):
    """Application-wide filter that eases mouse-wheel scrolling.

    A wheel notch normally jumps the view a fixed distance in one frame. This
    turns each notch into a short eased glide; notches that arrive mid-glide
    extend it rather than restarting it. Touchpads already deliver smooth
    pixel deltas, and modified wheels (Ctrl-zoom, Shift-scroll) keep their
    usual meaning, so both pass straight through.
    """

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() != QEvent.Type.Wheel:
            return False
        # This filter sees every wheel event in the application, and PyQt
        # aborts the whole process when an event filter raises. Losing one
        # glide is the right trade for never taking the app down with it.
        try:
            return self._glide(obj, event)
        except Exception:
            return False

    def _glide(self, obj: QObject, event: QEvent) -> bool:
        # Called through the class: several widgets in this app store their
        # owner in a `parent` attribute, which hides the Qt method.
        area = QWidget.parentWidget(obj) if isinstance(obj, QWidget) else None
        if not isinstance(area, QAbstractScrollArea) or area.viewport() is not obj:
            return False
        if event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        if not event.pixelDelta().isNull() or event.angleDelta().x() != 0:
            return False
        notches = event.angleDelta().y() / 120
        if notches == 0:
            return False

        bar = area.verticalScrollBar()
        glide = bar.findChild(QVariantAnimation, "kd_wheel_glide")
        running = (
            glide is not None and glide.state() == QAbstractAnimation.State.Running
        )
        start = int(glide.endValue()) if running else bar.value()
        step = bar.singleStep() * QApplication.wheelScrollLines()
        target = max(bar.minimum(), min(bar.maximum(), round(start - notches * step)))
        if target == start:
            # Already at the edge: let Qt hand the wheel to an outer view.
            return False

        if glide is None:
            glide = QVariantAnimation(bar)
            glide.setObjectName("kd_wheel_glide")
            glide.setDuration(WHEEL_GLIDE_MS)
            glide.setEasingCurve(QEasingCurve.Type.OutCubic)
            glide.valueChanged.connect(lambda v, b=bar: b.setValue(int(v)))
            # Grabbing the scrollbar takes over from the animation.
            bar.sliderPressed.connect(glide.stop)
        glide.stop()
        glide.setStartValue(bar.value())
        glide.setEndValue(target)
        glide.start()
        return True


def _when_completed(animation: QAbstractAnimation, action) -> None:
    """Run *action* once *animation* has played to its end.

    Qt also stops an animation, emitting ``finished``, when its target is
    destroyed, which can happen while the owning widget is mid-destruction.
    Touching that widget then crashes, so cleanup runs only after a full play.
    """

    def on_finished() -> None:
        if animation.currentTime() >= animation.duration():
            action()

    animation.finished.connect(on_finished)


def enable_pixel_scrolling(root: QWidget) -> None:
    """Scroll item views by pixels so rows slide instead of snapping."""
    for view in root.findChildren(QAbstractItemView):
        view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)


def fade_in(widget: QWidget, duration: int = FADE_IN_MS) -> QPropertyAnimation:
    """Fade *widget* in, then drop the effect so later paints stay cheap."""
    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(0.0)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    _when_completed(animation, lambda: widget.setGraphicsEffect(None))
    animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    return animation


def fade_out_snapshot(
    host: QWidget, snapshot: QPixmap, geometry: QRect, duration: int = CROSSFADE_MS
) -> QPropertyAnimation:
    """Lay *snapshot* over *host* and fade it away, revealing what is beneath.

    Fading a picture of the old screen costs one blended pixmap per frame,
    however complex the newly shown screen is.
    """
    overlay = QLabel(host)
    overlay.setPixmap(snapshot)
    overlay.setGeometry(geometry)
    overlay.setScaledContents(True)
    effect = QGraphicsOpacityEffect(overlay)
    overlay.setGraphicsEffect(effect)
    overlay.show()
    overlay.raise_()
    animation = QPropertyAnimation(effect, b"opacity", overlay)
    animation.setDuration(duration)
    animation.setStartValue(1.0)
    animation.setEndValue(0.0)
    animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
    _when_completed(animation, overlay.deleteLater)
    animation.start()
    return animation


class HoverHighlight(QObject):
    """Brightens a button while the pointer is over it.

    Only colours are animated. The button's size and position belong to its
    layout: animating its geometry, as this app once did, fought the layout,
    and quick passes over a button left it shrunken or shifted. Padding and
    border width never change here, so the button cannot change shape.
    """

    def __init__(
        self,
        button: QPushButton,
        base: str = "#4A5B7A",
        hover: str = "#5E77A3",
        pressed: str = "#3A4A66",
        padding: str = "7px",
    ) -> None:
        super().__init__(button)
        self.setObjectName("kd_hover_highlight")
        self._button = button
        self._base = QColor(base)
        self._hover = QColor(hover)
        self._pressed = pressed
        self._padding = padding
        self._current = QColor(self._base)
        self._style = ""
        self._fade = QVariantAnimation(self)
        self._fade.setDuration(HOVER_MS)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade.valueChanged.connect(self._paint)
        self._paint(self._base)
        button.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        # PyQt aborts the process when an event filter raises; a missed
        # highlight is not worth that.
        try:
            kind = event.type()
            if kind == QEvent.Type.Enter:
                self.animate(True)
            elif kind == QEvent.Type.Leave:
                self.animate(False)
            elif kind == QEvent.Type.EnabledChange and not self._button.isEnabled():
                self._fade.stop()
                self._paint(self._base)
        except Exception:
            pass
        return False

    def animate(self, hovered: bool) -> None:
        """Fade towards the hover colour, or back to the resting colour."""
        target = self._hover if hovered and self._button.isEnabled() else self._base
        self._fade.stop()
        if self._current == target:
            return
        self._fade.setStartValue(QColor(self._current))
        self._fade.setEndValue(QColor(target))
        self._fade.start()

    def _paint(self, color) -> None:
        self._current = QColor(color)
        fill = self._current.name()
        edge = self._current.lighter(118).name()
        style = (
            f"QPushButton {{ background: {fill}; border: 1px solid {edge}; "
            f"border-radius: 5px; padding: {self._padding}; color: white; }}"
            f"QPushButton:pressed {{ background: {self._pressed}; }}"
            "QPushButton:disabled { background: #3A4760; border-color: #44536F; "
            "color: #8E9BB3; }"
        )
        if style != self._style:
            self._style = style
            self._button.setStyleSheet(style)


def hover_highlight(button: QPushButton, **colors: str) -> HoverHighlight:
    """Give *button* a hover highlight, reusing one it already has."""
    existing = button.findChild(HoverHighlight, "kd_hover_highlight")
    if isinstance(existing, HoverHighlight):
        return existing
    return HoverHighlight(button, **colors)
