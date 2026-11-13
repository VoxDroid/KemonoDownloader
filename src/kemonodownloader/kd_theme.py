"""One visual theme for the whole app.

Every tab used to style its own widgets inline, with slightly different
colours, padding and corner radii, so the same kind of button looked
different from tab to tab. The app now loads a single style sheet built from
the palette below, and widgets only say what they are:

* buttons: ``set_role(button, "primary" | "danger" | "icon")`` (plain buttons
  need nothing),
* labels: ``set_role(label, "title" | "heading" | "muted")`` and
  ``set_tone(label, "success" | "warning" | "error" | "info")``,
* text views: ``set_role(view, "console")`` for log output,
* progress bars: ``set_progress_state(bar, "paused" | "done")``.

Hover and pressed states change colours only; borders and padding stay the
same in every state, so nothing changes size under the pointer. The sheet
sets no minimum sizes either: Qt applies those over a widget's own fixed
size, which squashed the square icon buttons.
"""

from __future__ import annotations

import os
import tempfile
from typing import Dict, Optional

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QWidget

# ---------------------------------------------------------------- palette --
BG = "#1A2A44"
SURFACE = "#2A3B5A"
SURFACE_ALT = "#2F4163"
CONSOLE = "#15233C"
BORDER = "#3A4B6A"
BORDER_STRONG = "#4A5B7A"

CONTROL = "#4A5B7A"
CONTROL_HOVER = "#5A6E94"
CONTROL_PRESSED = "#3A4B6A"
ACCENT = "#4A6B9A"
ACCENT_HOVER = "#5A7BA9"
ACCENT_PRESSED = "#3A5B7A"
DANGER = "#A94A4A"
DANGER_HOVER = "#BC5959"
DANGER_PRESSED = "#8A3A3A"
FOCUS = "#7F9FD9"
DISABLED_BG = "#34435F"

TEXT = "#FFFFFF"
TEXT_SOFT = "#D0D0D0"
TEXT_MUTED = "#A9B6CC"
TEXT_DISABLED = "#8A93A6"
INFO = "#A0C0FF"
SUCCESS = "#6BCF7F"
WARNING = "#FFD93D"
ERROR = "#FF6B6B"

PROGRESS = ACCENT_HOVER
PROGRESS_PAUSED = "#D4A017"
PROGRESS_DONE = "#4CAF50"
SELECTION = ACCENT

RADIUS = 6
MONOSPACE = "'JetBrains Mono', 'Cascadia Mono', Consolas, Menlo, monospace"

# Glyphs drawn into the style sheet (check marks and arrows).
_GLYPHS = {
    "check": ("fa5s.check", TEXT, 12),
    "arrow-down": ("fa5s.chevron-down", TEXT_MUTED, 10),
    "arrow-up": ("fa5s.chevron-up", TEXT_MUTED, 10),
    "arrow-down-disabled": ("fa5s.chevron-down", TEXT_DISABLED, 10),
    "arrow-up-disabled": ("fa5s.chevron-up", TEXT_DISABLED, 10),
}


def _render_glyphs(directory: str) -> Dict[str, str]:
    """Draw the theme's glyphs to PNG files and return their QSS paths.

    Style sheets can only show images from files. Returns an empty mapping if
    the icons cannot be drawn, in which case Qt's defaults show instead.
    """
    try:
        import qtawesome as qta

        os.makedirs(directory, exist_ok=True)
        paths = {}
        for name, (icon, color, size) in _GLYPHS.items():
            path = os.path.join(directory, f"{name}.png")
            pixmap = qta.icon(icon, color=color).pixmap(size * 2, size * 2)
            pixmap.setDevicePixelRatio(2.0)
            if not pixmap.save(path, "PNG"):
                return {}
            paths[name] = path.replace(os.sep, "/")
        return paths
    except Exception:
        return {}


def stylesheet(glyphs: Optional[Dict[str, str]] = None) -> str:
    """Return the app-wide style sheet."""
    glyphs = glyphs or {}

    def image(name: str) -> str:
        path = glyphs.get(name)
        return f"image: url('{path}');" if path else ""

    return f"""
* {{ color: {TEXT}; }}
QMainWindow, QDialog, QWidget#kdMain {{ background: {BG}; }}
QToolTip {{
    background: {SURFACE}; color: {TEXT}; border: 1px solid {BORDER_STRONG};
    border-radius: 4px; padding: 5px 8px;
}}

/* ---- buttons ---- */
QPushButton {{
    background: {CONTROL}; color: {TEXT}; border: 1px solid {CONTROL};
    border-radius: {RADIUS}px; padding: 6px 12px;
}}
QPushButton:hover {{ background: {CONTROL_HOVER}; border-color: {CONTROL_HOVER}; }}
QPushButton:pressed {{ background: {CONTROL_PRESSED}; border-color: {CONTROL_PRESSED}; }}
QPushButton:focus {{ border-color: {FOCUS}; }}
QPushButton:disabled {{
    background: {DISABLED_BG}; border-color: {DISABLED_BG}; color: {TEXT_DISABLED};
}}
QPushButton[kdRole="primary"] {{ background: {ACCENT}; border-color: {ACCENT}; font-weight: bold; }}
QPushButton[kdRole="primary"]:hover {{ background: {ACCENT_HOVER}; border-color: {ACCENT_HOVER}; }}
QPushButton[kdRole="primary"]:pressed {{ background: {ACCENT_PRESSED}; border-color: {ACCENT_PRESSED}; }}
QPushButton[kdRole="danger"] {{ background: {DANGER}; border-color: {DANGER}; }}
QPushButton[kdRole="danger"]:hover {{ background: {DANGER_HOVER}; border-color: {DANGER_HOVER}; }}
QPushButton[kdRole="danger"]:pressed {{ background: {DANGER_PRESSED}; border-color: {DANGER_PRESSED}; }}
QPushButton[kdRole="primary"]:focus, QPushButton[kdRole="danger"]:focus {{ border-color: {FOCUS}; }}
QPushButton[kdRole="primary"]:disabled, QPushButton[kdRole="danger"]:disabled {{
    background: {DISABLED_BG}; border-color: {DISABLED_BG}; color: {TEXT_DISABLED};
}}
QPushButton[kdRole="icon"] {{ padding: 0px; }}

/* ---- text inputs ---- */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{
    background: {SURFACE}; color: {TEXT}; border: 1px solid {BORDER};
    border-radius: {RADIUS}px; selection-background-color: {SELECTION};
}}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{ padding: 5px 8px; }}
QPlainTextEdit, QTextEdit {{ padding: 4px; }}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus,
QPlainTextEdit:focus, QTextEdit:focus {{ border-color: {FOCUS}; }}
QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled,
QPlainTextEdit:disabled, QTextEdit:disabled {{ color: {TEXT_DISABLED}; background: {DISABLED_BG}; }}
QTextEdit[kdRole="console"], QPlainTextEdit[kdRole="console"] {{
    background: {CONSOLE}; font-family: {MONOSPACE}; padding: 6px;
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox::down-arrow {{ {image("arrow-down")} width: 10px; height: 10px; }}
QComboBox::down-arrow:disabled {{ {image("arrow-down-disabled")} }}
QComboBox QAbstractItemView {{
    background: {SURFACE}; border: 1px solid {BORDER_STRONG}; outline: none;
    selection-background-color: {SELECTION}; padding: 2px;
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    border: none; width: 18px; background: transparent;
}}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{ {image("arrow-up")} width: 8px; height: 8px; }}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{ {image("arrow-down")} width: 8px; height: 8px; }}
QSpinBox::up-arrow:disabled, QDoubleSpinBox::up-arrow:disabled {{ {image("arrow-up-disabled")} }}
QSpinBox::down-arrow:disabled, QDoubleSpinBox::down-arrow:disabled {{ {image("arrow-down-disabled")} }}

/* ---- check boxes ---- */
QCheckBox, QRadioButton {{ spacing: 7px; background: transparent; }}
QCheckBox:disabled, QRadioButton:disabled {{ color: {TEXT_DISABLED}; }}
QCheckBox[kdRole="heading"] {{ font-weight: bold; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border-radius: 4px;
    background: {SURFACE}; border: 1px solid {BORDER_STRONG};
}}
QCheckBox::indicator:hover {{ border-color: {FOCUS}; }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT_HOVER}; {image("check")} }}
QCheckBox::indicator:disabled {{ background: {DISABLED_BG}; border-color: {DISABLED_BG}; }}

/* ---- labels ---- */
QLabel {{ background: transparent; }}
QLabel[kdRole="title"] {{ font-size: 16px; font-weight: bold; }}
QLabel[kdRole="heading"] {{ font-weight: bold; }}
QLabel[kdRole="muted"] {{ color: {TEXT_MUTED}; }}
QLabel[kdRole="soft"] {{ color: {TEXT_SOFT}; }}
QLabel[kdRole="empty"] {{
    color: {TEXT_DISABLED}; background: {SURFACE}; border-radius: {RADIUS}px; padding: 30px;
}}
QLabel[kdRole="notice"] {{
    color: #E8C468; background: #3A3524; border-radius: {RADIUS}px; padding: 8px;
}}
QLabel[kdTone="success"] {{ color: {SUCCESS}; font-weight: bold; }}
QLabel[kdTone="warning"] {{ color: {WARNING}; font-weight: bold; }}
QLabel[kdTone="error"] {{ color: {ERROR}; font-weight: bold; }}
QLabel[kdTone="info"] {{ color: {INFO}; }}

/* ---- groups and panels ---- */
QGroupBox {{
    border: 1px solid {BORDER}; border-radius: 8px; margin-top: 14px;
    padding: 12px 10px 10px 10px; font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin; subcontrol-position: top left;
    left: 10px; padding: 0 5px; color: {TEXT};
}}
QFrame[kdRole="card"] {{ background: {SURFACE}; border-radius: 8px; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QScrollArea[kdRole="card"], QScrollArea[kdRole="card"] > QWidget#qt_scrollarea_viewport {{
    background: {SURFACE}; border-radius: 8px;
}}
QTextBrowser[kdRole="plain"], QTextEdit[kdRole="plain"] {{
    background: transparent; border: none; padding: 0px;
}}

/* ---- lists and tables ---- */
QListWidget, QListView, QTreeView, QTableView {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: {RADIUS}px;
    outline: none; selection-background-color: {SELECTION}; selection-color: {TEXT};
}}
QListWidget::item, QListView::item {{ padding: 3px 4px; border-radius: 4px; }}
QListWidget::item:hover, QListView::item:hover {{ background: {SURFACE_ALT}; }}
QListWidget::item:selected, QListView::item:selected {{ background: {SELECTION}; }}
QTableView {{ alternate-background-color: {SURFACE_ALT}; gridline-color: transparent; }}
QHeaderView::section {{ background: {BORDER}; color: {TEXT}; padding: 6px; border: none; }}
QTableCornerButton::section {{ background: {BORDER}; border: none; }}

/* ---- progress and sliders ---- */
QProgressBar {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: {RADIUS}px;
    text-align: center; color: {TEXT};
}}
QProgressBar::chunk {{ background: {PROGRESS}; border-radius: 5px; }}
QProgressBar[kdState="paused"]::chunk {{ background: {PROGRESS_PAUSED}; }}
QProgressBar[kdState="done"]::chunk {{ background: {PROGRESS_DONE}; }}
QSlider::groove:horizontal {{
    height: 6px; background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 3px;
}}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 3px; }}
QSlider::handle:horizontal {{
    background: {TEXT}; border: 2px solid {ACCENT}; width: 12px; height: 12px;
    margin: -5px 0; border-radius: 8px;
}}
QSlider::handle:horizontal:hover {{ border-color: {ACCENT_HOVER}; }}

/* ---- scroll bars ---- */
QScrollBar:vertical {{ background: transparent; width: 12px; margin: 3px; }}
QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 3px; }}
QScrollBar::handle:vertical {{ background: {BORDER_STRONG}; border-radius: 3px; min-height: 28px; }}
QScrollBar::handle:horizontal {{ background: {BORDER_STRONG}; border-radius: 3px; min-width: 28px; }}
QScrollBar::handle:hover {{ background: {CONTROL_HOVER}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0px; height: 0px; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}

/* ---- tabs ---- */
QTabWidget::pane {{ border: none; background: {BG}; }}
QTabBar {{ qproperty-drawBase: 0; }}
QTabBar::tab {{
    background: {SURFACE}; color: {TEXT_MUTED}; padding: 9px 14px; margin-right: 3px;
    border-top-left-radius: 8px; border-top-right-radius: 8px; min-width: 70px;
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:hover {{ background: {SURFACE_ALT}; color: {TEXT}; }}
QTabBar::tab:selected {{ background: {CONTROL}; color: {TEXT}; border-bottom-color: {FOCUS}; }}
QTabBar::tab:disabled {{ color: {TEXT_DISABLED}; }}

/* ---- menus and message boxes ---- */
QMenu {{ background: {SURFACE}; border: 1px solid {BORDER_STRONG}; padding: 4px; }}
QMenu::item {{ padding: 6px 18px; border-radius: 4px; }}
QMenu::item:selected {{ background: {SELECTION}; }}
QMessageBox {{ background: {BG}; }}
QMessageBox QLabel {{ color: {TEXT}; }}
QMessageBox QPushButton {{ min-width: 80px; }}
"""


_applied_to: Optional[int] = None


def apply_theme(app: QApplication) -> None:
    """Load the theme into *app* (once per application object)."""
    global _applied_to
    if _applied_to == id(app):
        return
    set_sheet = getattr(app, "setStyleSheet", None)
    if not callable(set_sheet):
        return  # not a real application object; Qt's default look stays
    glyph_dir = os.path.join(tempfile.gettempdir(), "kemonodownloader-theme")
    set_sheet(stylesheet(_render_glyphs(glyph_dir)))
    if isinstance(app, QApplication):
        # Links in rich text follow the palette, not the style sheet.
        palette = app.palette()
        palette.setColor(QPalette.ColorRole.Link, QColor(INFO))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(INFO))
        app.setPalette(palette)
    _applied_to = id(app)


def repolish(widget: QWidget) -> None:
    """Re-apply style rules after a property the style sheet reads changed."""
    style = widget.style()
    if style is not None:
        style.unpolish(widget)
        style.polish(widget)
    widget.update()


def _set_property(widget: QWidget, name: str, value: Optional[str]) -> QWidget:
    if widget.property(name) != value:
        widget.setProperty(name, value)
        repolish(widget)
    return widget


def set_role(widget: QWidget, role: Optional[str]) -> QWidget:
    """Mark what *widget* is (see the module docstring); None clears it."""
    return _set_property(widget, "kdRole", role)


def set_tone(widget: QWidget, tone: Optional[str]) -> QWidget:
    """Colour a label as success, warning, error or info; None clears it."""
    return _set_property(widget, "kdTone", tone)


def set_progress_state(bar: QWidget, state: Optional[str]) -> QWidget:
    """Colour a progress bar as paused or done; None is the normal colour."""
    return _set_property(bar, "kdState", state)
