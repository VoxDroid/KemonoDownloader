"""One visual theme for the whole app.

Every tab used to style its own widgets inline, with slightly different
colours, padding and corner radii, so the same kind of button looked
different from tab to tab. The app now loads a single style sheet built from
the palette below, and widgets only say what they are:

* buttons: ``set_role(button, "primary" | "danger" | "icon")`` (plain buttons
  need nothing),
* labels: ``set_role(label, "title" | "heading" | "muted" | "note" | "pill")``
  (section notes come from ``kd_notes``) and
  ``set_tone(label, "success" | "warning" | "error" | "info")``,
* text views: ``set_role(view, "console")`` for log output,
* progress bars: ``set_progress_state(bar, "paused" | "done")``.

Hover and pressed states change colours only; borders and padding stay the
same in every state, so nothing changes size under the pointer. The sheet
names no font family, so the font chosen in Settings applies everywhere
(logs included), and sets no minimum sizes: Qt applies those over a
widget's own fixed size, which squashed the square icon buttons.
"""

from __future__ import annotations

import os
import tempfile
from typing import Dict, Optional

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QWidget

# ---------------------------------------------------------------- palette --
# Colours that stay the same in every theme: log and status colours, and
# the progress states, chosen to read well on any of the dark backgrounds.
_SHARED = {
    "SUCCESS": "#6BCF7F",
    "WARNING": "#FFD93D",
    "ERROR": "#FF6B6B",
    "PROGRESS_PAUSED": "#D4A017",
    "PROGRESS_DONE": "#4CAF50",
}


def _theme(**colors: str) -> Dict[str, str]:
    palette = dict(_SHARED)
    palette.update(colors)
    palette.setdefault("PROGRESS", palette["ACCENT_HOVER"])
    palette.setdefault("SELECTION", palette["ACCENT"])
    return palette


# Every theme is dark: icons across the app are drawn in white, which a light
# background would hide. Each theme names the same colour roles.
THEMES: Dict[str, Dict[str, str]] = {
    "midnight": _theme(
        BG="#1A2A44",
        SURFACE="#2A3B5A",
        SURFACE_ALT="#2F4163",
        CONSOLE="#15233C",
        BORDER="#3A4B6A",
        BORDER_STRONG="#4A5B7A",
        CONTROL="#4A5B7A",
        CONTROL_HOVER="#5A6E94",
        CONTROL_PRESSED="#3A4B6A",
        ACCENT="#4A6B9A",
        ACCENT_HOVER="#5A7BA9",
        ACCENT_PRESSED="#3A5B7A",
        DANGER="#A94A4A",
        DANGER_HOVER="#BC5959",
        DANGER_PRESSED="#8A3A3A",
        FOCUS="#7F9FD9",
        DISABLED_BG="#34435F",
        NOTE_BG="#22334F",
        TEXT="#FFFFFF",
        TEXT_SOFT="#D0D0D0",
        TEXT_MUTED="#A9B6CC",
        TEXT_DISABLED="#8A93A6",
        INFO="#A0C0FF",
    ),
    "graphite": _theme(
        BG="#1E1F22",
        SURFACE="#2B2D31",
        SURFACE_ALT="#313338",
        CONSOLE="#18191C",
        BORDER="#3A3C42",
        BORDER_STRONG="#4A4D55",
        CONTROL="#45484F",
        CONTROL_HOVER="#555861",
        CONTROL_PRESSED="#3A3C42",
        ACCENT="#4863B8",
        ACCENT_HOVER="#5A76C9",
        ACCENT_PRESSED="#3D55A0",
        DANGER="#B5474B",
        DANGER_HOVER="#C75A5E",
        DANGER_PRESSED="#943A3D",
        FOCUS="#8AA4F0",
        DISABLED_BG="#323439",
        NOTE_BG="#26282C",
        TEXT="#F2F3F5",
        TEXT_SOFT="#D4D6DA",
        TEXT_MUTED="#A3A6AD",
        TEXT_DISABLED="#7C7F87",
        INFO="#9DB8FF",
    ),
    "plum": _theme(
        BG="#221A2E",
        SURFACE="#2F2540",
        SURFACE_ALT="#362B4A",
        CONSOLE="#1B1525",
        BORDER="#43365A",
        BORDER_STRONG="#554670",
        CONTROL="#554670",
        CONTROL_HOVER="#66578A",
        CONTROL_PRESSED="#43365A",
        ACCENT="#7E52BA",
        ACCENT_HOVER="#9066CC",
        ACCENT_PRESSED="#6A43A0",
        DANGER="#B0455C",
        DANGER_HOVER="#C2586F",
        DANGER_PRESSED="#91384B",
        FOCUS="#B696F0",
        DISABLED_BG="#382E48",
        NOTE_BG="#2A2139",
        TEXT="#FFFFFF",
        TEXT_SOFT="#DCD3E8",
        TEXT_MUTED="#B3A6C7",
        TEXT_DISABLED="#8B7FA0",
        INFO="#C9A8FF",
    ),
    "forest": _theme(
        BG="#17241F",
        SURFACE="#20332B",
        SURFACE_ALT="#263C33",
        CONSOLE="#121D19",
        BORDER="#2F4A3F",
        BORDER_STRONG="#3D5E50",
        CONTROL="#3D5E50",
        CONTROL_HOVER="#4B7363",
        CONTROL_PRESSED="#2F4A3F",
        ACCENT="#357D5D",
        ACCENT_HOVER="#43926F",
        ACCENT_PRESSED="#2B674C",
        DANGER="#A94848",
        DANGER_HOVER="#BC5A5A",
        DANGER_PRESSED="#8A3A3A",
        FOCUS="#7FD1AA",
        DISABLED_BG="#283A32",
        NOTE_BG="#1C2D26",
        TEXT="#FFFFFF",
        TEXT_SOFT="#D3E3DA",
        TEXT_MUTED="#A3BCB0",
        TEXT_DISABLED="#7D968A",
        INFO="#9FE0C0",
    ),
    "ember": _theme(
        BG="#241B17",
        SURFACE="#33261F",
        SURFACE_ALT="#3B2C24",
        CONSOLE="#1C1512",
        BORDER="#4A372D",
        BORDER_STRONG="#5E463A",
        CONTROL="#5E463A",
        CONTROL_HOVER="#725648",
        CONTROL_PRESSED="#4A372D",
        ACCENT="#A85A2A",
        ACCENT_HOVER="#BC6C3A",
        ACCENT_PRESSED="#8E4B22",
        DANGER="#A9434F",
        DANGER_HOVER="#BC5662",
        DANGER_PRESSED="#8A3641",
        FOCUS="#F0B07A",
        DISABLED_BG="#3A2D26",
        NOTE_BG="#2C211C",
        TEXT="#FFFFFF",
        TEXT_SOFT="#EADBD0",
        TEXT_MUTED="#C2AA9A",
        TEXT_DISABLED="#957F71",
        INFO="#FFC48F",
    ),
}
DEFAULT_THEME = "midnight"
_current_theme = DEFAULT_THEME


def current_theme() -> str:
    """Name of the theme on show."""
    return _current_theme


def color(role: str) -> str:
    """A colour of the current theme, such as ``color("SURFACE")``."""
    return THEMES[_current_theme][role]


def _palette(theme: Optional[str]) -> Dict[str, str]:
    return THEMES.get(theme or _current_theme, THEMES[DEFAULT_THEME])


# The default theme's colours under their own names, for code that only needs
# a colour that is the same in every theme (or the default's).
globals().update(THEMES[DEFAULT_THEME])
BG: str
SURFACE: str
SURFACE_ALT: str
CONSOLE: str
BORDER: str
BORDER_STRONG: str
CONTROL: str
CONTROL_HOVER: str
CONTROL_PRESSED: str
ACCENT: str
ACCENT_HOVER: str
ACCENT_PRESSED: str
DANGER: str
DANGER_HOVER: str
DANGER_PRESSED: str
FOCUS: str
DISABLED_BG: str
NOTE_BG: str
TEXT: str
TEXT_SOFT: str
TEXT_MUTED: str
TEXT_DISABLED: str
INFO: str
SUCCESS: str
WARNING: str
ERROR: str
PROGRESS: str
PROGRESS_PAUSED: str
PROGRESS_DONE: str
SELECTION: str

RADIUS = 6

# Glyphs drawn into the style sheet (check marks and arrows): icon, colour
# role, size.
_GLYPHS = {
    "check": ("fa5s.check", "TEXT", 12),
    "arrow-down": ("fa5s.chevron-down", "TEXT_MUTED", 10),
    "arrow-up": ("fa5s.chevron-up", "TEXT_MUTED", 10),
    "arrow-down-disabled": ("fa5s.chevron-down", "TEXT_DISABLED", 10),
    "arrow-up-disabled": ("fa5s.chevron-up", "TEXT_DISABLED", 10),
}


def _render_glyphs(directory: str, theme: Optional[str] = None) -> Dict[str, str]:
    """Draw the theme's glyphs to PNG files and return their QSS paths.

    Style sheets can only show images from files. Returns an empty mapping if
    the icons cannot be drawn, in which case Qt's defaults show instead.
    """
    palette = _palette(theme)
    try:
        import qtawesome as qta

        os.makedirs(directory, exist_ok=True)
        paths = {}
        for name, (icon, role, size) in _GLYPHS.items():
            path = os.path.join(directory, f"{name}.png")
            pixmap = qta.icon(icon, color=palette[role]).pixmap(size * 2, size * 2)
            pixmap.setDevicePixelRatio(2.0)
            if not pixmap.save(path, "PNG"):
                return {}
            paths[name] = path.replace(os.sep, "/")
        return paths
    except Exception:
        return {}


def stylesheet(
    glyphs: Optional[Dict[str, str]] = None, theme: Optional[str] = None
) -> str:
    """Return the app-wide style sheet, in *theme* (the current one by default)."""
    glyphs = glyphs or {}
    p = _palette(theme)
    BG, SURFACE, SURFACE_ALT, CONSOLE = (
        p["BG"],
        p["SURFACE"],
        p["SURFACE_ALT"],
        p["CONSOLE"],
    )
    BORDER, BORDER_STRONG = p["BORDER"], p["BORDER_STRONG"]
    CONTROL, CONTROL_HOVER, CONTROL_PRESSED = (
        p["CONTROL"],
        p["CONTROL_HOVER"],
        p["CONTROL_PRESSED"],
    )
    ACCENT, ACCENT_HOVER, ACCENT_PRESSED = (
        p["ACCENT"],
        p["ACCENT_HOVER"],
        p["ACCENT_PRESSED"],
    )
    DANGER, DANGER_HOVER, DANGER_PRESSED = (
        p["DANGER"],
        p["DANGER_HOVER"],
        p["DANGER_PRESSED"],
    )
    FOCUS, DISABLED_BG, NOTE_BG = p["FOCUS"], p["DISABLED_BG"], p["NOTE_BG"]
    TEXT, TEXT_SOFT, TEXT_MUTED, TEXT_DISABLED, INFO = (
        p["TEXT"],
        p["TEXT_SOFT"],
        p["TEXT_MUTED"],
        p["TEXT_DISABLED"],
        p["INFO"],
    )
    SUCCESS, WARNING, ERROR = p["SUCCESS"], p["WARNING"], p["ERROR"]
    PROGRESS, PROGRESS_PAUSED, PROGRESS_DONE = (
        p["PROGRESS"],
        p["PROGRESS_PAUSED"],
        p["PROGRESS_DONE"],
    )
    SELECTION = p["SELECTION"]

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
    background: {CONSOLE}; padding: 6px;
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
QLabel[kdRole="note"] {{
    color: {TEXT_SOFT}; background: {NOTE_BG}; border-left: 3px solid {ACCENT_HOVER};
    border-radius: 4px; padding: 6px 10px;
}}
QLabel[kdRole="pill"] {{
    background: {SURFACE_ALT}; border: 1px solid {BORDER}; border-radius: 11px;
    padding: 3px 10px;
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
/* No padding: it would shrink the widgets that queue and file rows are
   made of and cut off their buttons and check boxes. Lists of plain text
   rows opt in to padding with the "roomy" role. */
QListWidget::item, QListView::item {{ border-radius: 4px; }}
QListWidget[kdRole="roomy"]::item {{ padding: 4px 6px; }}
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


_applied_to: Optional[tuple] = None


def theme_name(theme: Optional[str]) -> str:
    """*theme* if it exists, otherwise the default theme."""
    return theme if theme in THEMES else DEFAULT_THEME


def apply_theme(app: QApplication, theme: Optional[str] = None) -> None:
    """Load *theme* (the current theme by default) into *app*.

    Calling it again with the same app and theme does nothing; a different
    theme restyles every widget at once.
    """
    global _applied_to, _current_theme
    name = _current_theme if theme is None else theme_name(theme)
    if _applied_to == (id(app), name):
        return
    set_sheet = getattr(app, "setStyleSheet", None)
    if not callable(set_sheet):
        return  # not a real application object; Qt's default look stays
    _current_theme = name
    glyph_dir = os.path.join(tempfile.gettempdir(), "kemonodownloader-theme", name)
    set_sheet(stylesheet(_render_glyphs(glyph_dir, name), name))
    if isinstance(app, QApplication):
        app.setPalette(qt_palette(app.palette(), name))
    _applied_to = (id(app), name)


def use_theme(theme: Optional[str]) -> str:
    """Make *theme* the current theme for ``color()`` without restyling an
    application. Returns the theme's name."""
    global _current_theme
    _current_theme = theme_name(theme)
    return _current_theme


def is_themed(app: object) -> bool:
    """Whether ``apply_theme`` has styled *app*."""
    return _applied_to is not None and _applied_to[0] == id(app)


def qt_palette(base: QPalette, theme: Optional[str] = None) -> QPalette:
    """*base* with the theme's colours, for what the style sheet doesn't
    reach: rich-text links, and widgets drawn from the palette."""
    p = _palette(theme)
    palette = QPalette(base)
    roles = {
        QPalette.ColorRole.Window: p["BG"],
        QPalette.ColorRole.WindowText: p["TEXT"],
        QPalette.ColorRole.Base: p["SURFACE"],
        QPalette.ColorRole.AlternateBase: p["SURFACE_ALT"],
        QPalette.ColorRole.Text: p["TEXT"],
        QPalette.ColorRole.Button: p["CONTROL"],
        QPalette.ColorRole.ButtonText: p["TEXT"],
        QPalette.ColorRole.Highlight: p["SELECTION"],
        QPalette.ColorRole.HighlightedText: p["TEXT"],
        QPalette.ColorRole.ToolTipBase: p["SURFACE"],
        QPalette.ColorRole.ToolTipText: p["TEXT"],
        QPalette.ColorRole.PlaceholderText: p["TEXT_DISABLED"],
        QPalette.ColorRole.Link: p["INFO"],
        QPalette.ColorRole.LinkVisited: p["INFO"],
    }
    for role, value in roles.items():
        palette.setColor(role, QColor(value))
    return palette


ROW_PROPERTY = "kdRowState"


def style_row(widget: QWidget, selected: bool = False) -> None:
    """Colour a custom list row (the Post and Creator file and post rows).

    The row's state is remembered, so ``restyle_rows`` can repaint it in a
    new theme.
    """
    role = "CONTROL" if selected else "SURFACE"
    widget.setStyleSheet(f"background-color: {color(role)}; border-radius: 5px;")
    widget.setProperty(ROW_PROPERTY, "selected" if selected else "normal")


def restyle_rows(root: QWidget) -> None:
    """Repaint every custom list row under *root* in the current theme."""
    for widget in root.findChildren(QWidget):
        state = widget.property(ROW_PROPERTY)
        if state in ("normal", "selected"):
            style_row(widget, state == "selected")


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
