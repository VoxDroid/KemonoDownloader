from __future__ import annotations

import os
import sys
import warnings

import qtawesome as qta
import requests
from bs4 import MarkupResemblesLocatorWarning
from packaging import version
from PyQt6.QtCore import QPoint, QRect, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QFont, QFontDatabase, QIcon, QPalette, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from kemonodownloader.creator_downloader import CreatorDownloaderTab
from kemonodownloader.domain_config import startup_request_lock
from kemonodownloader.history_store import HistoryStore
from kemonodownloader.kd_errors import install_exception_hook
from kemonodownloader.kd_extension import ExtensionTab
from kemonodownloader.kd_help import HelpTab
from kemonodownloader.kd_history import HistoryTab
from kemonodownloader.kd_language import language_manager, translate
from kemonodownloader.kd_motion import (
    FADE_IN_MS,
    TAB_FADE_MS,
    SmoothWheelScroller,
    enable_pixel_scrolling,
    fade_in,
    fade_out_snapshot,
)
from kemonodownloader.kd_settings import SettingsTab
from kemonodownloader.kd_theme import apply_theme, set_role
from kemonodownloader.kd_thumbnaildl import ThumbnailDownloaderTab
from kemonodownloader.post_downloader import PostDownloaderTab

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

CURRENT_VERSION = "5.15.0"
GITHUB_REPO = "VoxDroid/KemonoDownloader"

# Kept alive for the whole run; installed on the application by main().
_wheel_scroller = SmoothWheelScroller()

# Available Google Fonts bundled with the app
BUNDLED_FONTS = {
    "JetBrains Mono": [
        "JetBrainsMono-Regular.ttf",
        "JetBrainsMono-Bold.ttf",
        "JetBrainsMono-Medium.ttf",
    ],
    "Poppins": [
        "Poppins-Regular.ttf",
        "Poppins-Bold.ttf",
        "Poppins-Medium.ttf",
    ],
}


def load_bundled_fonts():
    """Load all bundled Google Fonts into the application font database."""
    fonts_dir = os.path.join(os.path.dirname(__file__), "resources", "fonts")
    for font_family, font_files in BUNDLED_FONTS.items():
        for font_file in font_files:
            font_path = os.path.join(fonts_dir, font_file)
            if os.path.exists(font_path):
                QFontDatabase.addApplicationFont(font_path)


class VersionChecker(QThread):
    update_available = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            with startup_request_lock:
                response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            latest_version = data["tag_name"].lstrip("v")
            release_url = data["html_url"]
            if version.parse(latest_version) > version.parse(CURRENT_VERSION):
                self.update_available.emit(latest_version, release_url)
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit(translate("no_internet_connection"))
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(
                f"{translate('failed_to_check_updates')}: {str(e)}"
            )


class IntroScreen(QWidget):
    def __init__(self, main_window: "KemonoDownloader"):
        super().__init__()
        self._parent: "KemonoDownloader" = main_window
        self.setup_ui()
        self.start_fade_in()
        self._parent.settings_tab.language_changed.connect(self.update_ui_text)

    def setup_ui(self):
        self.setStyleSheet("background-color: #1A2A44; border: none;")
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Top spacer
        main_layout.addStretch()

        # App Image
        self.app_image = QLabel()
        pixmap = QPixmap(resource_path("resources/KemonoDownloader.png"))
        if not pixmap.isNull():
            # Scale the image to a reasonable size, e.g., 200x200 or based on aspect ratio
            scaled_pixmap = pixmap.scaled(
                300,
                300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.app_image.setPixmap(scaled_pixmap)
        self.app_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_image.setStyleSheet("background: transparent; border: none;")
        main_layout.addWidget(self.app_image, alignment=Qt.AlignmentFlag.AlignCenter)

        # Version Label
        self.version_label = QLabel(f"Version {CURRENT_VERSION}")
        self.version_label.setFont(QFont(self._get_font_family(), 12))
        self.version_label.setStyleSheet("color: #CCCCCC; background: transparent;")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(
            self.version_label, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Launch Button
        self.launch_button = QPushButton(translate("launch_button"))
        self.launch_button.setFont(
            QFont(self._get_font_family(), 16, QFont.Weight.Medium)
        )
        # larger width for launch button
        self.launch_button.setFixedSize(300, 60)
        self.launch_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A6B9A, stop:1 #3A5B7A);
                color: #FFFFFF;
                border-radius: 18px;
                border: 2px solid #5A7BA9;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5A7BA9, stop:1 #4A6B9A);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3A5B7A, stop:1 #2A4B6A);
            }
        """
        )
        button_shadow = QGraphicsDropShadowEffect()
        button_shadow.setBlurRadius(20)
        button_shadow.setColor(QColor(0, 0, 0, 100))
        button_shadow.setOffset(0, 5)
        self.launch_button.setGraphicsEffect(button_shadow)
        self.launch_button.clicked.connect(self._parent.transition_to_main)
        main_layout.addWidget(
            self.launch_button, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Bottom spacer
        main_layout.addStretch()

        # Footer with small text
        footer_widget = QWidget()
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setSpacing(5)
        footer_layout.setContentsMargins(0, 0, 0, 0)

        self.title = QLabel(translate("app_title"))
        self.title.setFont(QFont(self._get_font_family(), 14, QFont.Weight.Bold))
        self.title.setStyleSheet("color: #FFFFFF; background: transparent;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(self.title)

        self.dev_label = QLabel(translate("developed_by"))
        self.dev_label.setFont(QFont(self._get_font_family(), 10))
        self.dev_label.setStyleSheet("color: #CCCCCC; background: transparent;")
        self.dev_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(self.dev_label)

        self.github_label = QLabel(
            '<a href="https://github.com/VoxDroid" style="color: #A0C0FF; text-decoration: none; font-size: 10px;">github.com/VoxDroid</a>'
        )
        self.github_label.setFont(QFont(self._get_font_family(), 10))
        self.github_label.setOpenExternalLinks(True)
        self.github_label.setStyleSheet(
            "QLabel { background: transparent; } QLabel:hover { color: #C0E0FF; }"
        )
        self.github_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.github_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(self.github_label)

        main_layout.addWidget(footer_widget, alignment=Qt.AlignmentFlag.AlignCenter)

    def _get_font_family(self):
        """Get the current font family from settings."""
        return self._parent.settings_tab.get_font()

    def apply_font(self, font_family: str):
        """Update all fonts in the intro screen to use the new font family."""
        self.version_label.setFont(QFont(font_family, 12))
        self.launch_button.setFont(QFont(font_family, 16, QFont.Weight.Medium))
        self.title.setFont(QFont(font_family, 14, QFont.Weight.Bold))
        self.dev_label.setFont(QFont(font_family, 10))
        self.github_label.setFont(QFont(font_family, 10))

    def update_ui_text(self):
        self.title.setText(translate("app_title"))
        self.dev_label.setText(translate("developed_by"))
        self.launch_button.setText(translate("launch_button"))

    def start_fade_in(self):
        # Window opacity only applies to top-level windows; an opacity effect
        # fades this embedded screen.
        self.fade_in_animation = fade_in(self, FADE_IN_MS)


def resource_path(relative_path):
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return os.path.join(meipass, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


class KemonoDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(translate("app_title"))
        self.setGeometry(100, 100, 1000, 700)

        self.settings_tab = SettingsTab(self)
        self.settings_tab.download_started.connect(self.disable_other_tabs)
        self.settings_tab.download_finished.connect(self.enable_other_tabs)
        self.base_folder = os.path.join(
            self.settings_tab.settings["base_directory"],
            self.settings_tab.settings["base_folder_name"],
        )
        self.download_folder = os.path.join(self.base_folder, "Downloads")
        self.cache_folder = os.path.join(self.base_folder, "Cache")
        self.other_files_folder = os.path.join(self.base_folder, "Other Files")
        self.ensure_folders_exist()
        # History and favorites live beside the hash database.
        self.history_store = HistoryStore(self.other_files_folder)

        self.setWindowIcon(QIcon(resource_path("resources/KemonoDownloader.png")))

        self.intro_screen = IntroScreen(self)
        self.main_widget = None
        self._main_ui_builder = None
        self._prebuilt_main_widget = None
        self.setCentralWidget(self.intro_screen)
        self.apply_palette()

        self.settings_tab.language_changed.connect(self.update_all_ui)
        self.settings_tab.font_changed.connect(self.apply_font)

        # Apply the saved font setting
        self.apply_font(self.settings_tab.get_font())

        if self.settings_tab.is_auto_check_updates_enabled():
            self.check_for_updates()

    def apply_font(self, font_family: str):
        """Apply the selected font family to the entire application and all widgets."""
        app = QApplication.instance()
        if app:
            font = QFont(font_family)
            font.setPointSize(app.font().pointSize())
            app.setFont(font)
        # Update all existing widgets that have explicit fonts set
        self._apply_font_recursive(self, font_family)
        # Update the intro screen if it still exists
        if hasattr(self, "intro_screen") and self.intro_screen is not None:
            try:
                self.intro_screen.apply_font(font_family)
            except RuntimeError:
                # C++ object already deleted after intro-to-main transition
                self.intro_screen = None
        # Refresh help and extension tabs if they exist
        if hasattr(self, "help_tab"):
            self.help_tab.update_ui_text()
        if hasattr(self, "extension_tab"):
            self.extension_tab.update_ui_text()

    def _apply_font_recursive(self, widget, font_family: str):
        """Recursively update the font family on all child widgets."""
        current_font = widget.font()
        current_font.setFamily(font_family)
        widget.setFont(current_font)
        for child in widget.findChildren(QWidget):
            child_font = child.font()
            child_font.setFamily(font_family)
            child.setFont(child_font)

    def apply_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1A2A44"))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor("#2A3B5A"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#3A4B6A"))
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor("#3A5B7A"))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        self.setPalette(palette)

    def ensure_folders_exist(self):
        for folder in [
            self.base_folder,
            self.download_folder,
            self.cache_folder,
            self.other_files_folder,
        ]:
            os.makedirs(folder, exist_ok=True)

    def disable_other_tabs(self):
        if hasattr(self, "tabs"):
            current = self.tabs.currentWidget()
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if w != current and w != self.settings_tab:
                    self.tabs.setTabEnabled(i, False)

    def enable_other_tabs(self):
        if hasattr(self, "tabs"):
            for i in range(self.tabs.count()):
                self.tabs.setTabEnabled(i, True)

    def setup_main_ui(self):
        builder = self._build_main_ui()
        while True:
            try:
                next(builder)
            except StopIteration as done:
                return done.value

    def start_background_build(self):
        """Build the tabs a piece at a time while the intro screen is showing.

        Constructing and styling every tab takes around a second. Spread over
        idle moments it goes unnoticed, and Launch then only has to swap
        screens.
        """
        if self.main_widget is not None or self._main_ui_builder is not None:
            return
        self._main_ui_builder = self._build_main_ui()
        QTimer.singleShot(0, self._advance_background_build)

    def _advance_background_build(self):
        builder = self._main_ui_builder
        if builder is None:
            return
        try:
            next(builder)
        except StopIteration as done:
            self._prebuilt_main_widget = done.value
            self._main_ui_builder = None
            return
        QTimer.singleShot(0, self._advance_background_build)

    def _take_main_ui(self):
        """Return the main UI, finishing whatever the background build left."""
        if self._prebuilt_main_widget is not None:
            main_widget, self._prebuilt_main_widget = self._prebuilt_main_widget, None
            return main_widget
        builder, self._main_ui_builder = self._main_ui_builder, None
        if builder is None:
            return self.setup_main_ui()
        while True:
            try:
                next(builder)
            except StopIteration as done:
                return done.value

    def _settle(self, widget):
        """Style *widget* now, while nobody is waiting on it.

        Qt otherwise applies every style sheet in the tree at the moment the
        tabs first appear. It is only worth doing ahead of time on screen.
        """
        if self.isVisible():
            widget.ensurePolished()
            enable_pixel_scrolling(widget)

    def _build_main_ui(self):
        """Generator that builds the main UI, yielding between heavy steps."""
        # Parented from the start, so styling happens once, in its final place.
        # (Not hidden explicitly: that would keep it hidden once it becomes the
        # central widget. A child added to a shown window stays hidden anyway.)
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        main_widget.setObjectName("kdMain")

        # Tab Widget
        self.tabs = QTabWidget()
        # Seven tabs: shorten labels when the window is narrow instead of
        # hiding tabs behind scroll arrows.
        self.tabs.tabBar().setElideMode(Qt.TextElideMode.ElideRight)
        self.tabs.tabBar().setUsesScrollButtons(False)
        main_layout.addWidget(self.tabs)
        self._tab_snapshot = None
        self.tabs.tabBarClicked.connect(self._snapshot_current_tab)
        self.tabs.currentChanged.connect(self._fade_from_snapshot)
        yield

        # Add Tabs
        self.post_tab = PostDownloaderTab(self)
        self.tabs.addTab(
            self.post_tab,
            qta.icon("fa5s.download", color="white"),
            translate("post_downloader_tab"),
        )
        yield
        self._settle(self.post_tab)
        yield

        self.creator_tab = CreatorDownloaderTab(self)
        self.tabs.addTab(
            self.creator_tab,
            qta.icon("fa5s.user-edit", color="white"),
            translate("creator_downloader_tab"),
        )
        yield
        self._settle(self.creator_tab)
        yield

        self.thumbnail_tab = ThumbnailDownloaderTab(self)
        self.tabs.addTab(
            self.thumbnail_tab,
            qta.icon("fa5s.images", color="white"),
            translate("thumbnail_downloader_tab"),
        )
        yield
        self._settle(self.thumbnail_tab)
        yield

        self.history_tab = HistoryTab(self)
        self.tabs.addTab(
            self.history_tab,
            qta.icon("fa5s.history", color="white"),
            translate("history_tab"),
        )
        yield
        self._settle(self.history_tab)
        yield

        self.tabs.addTab(
            self.settings_tab,
            qta.icon("fa5s.cog", color="white"),
            translate("settings_tab"),
        )
        yield
        self._settle(self.settings_tab)
        yield

        self.help_tab = HelpTab(self)
        self.tabs.addTab(
            self.help_tab,
            qta.icon("fa5s.question-circle", color="white"),
            translate("help_tab"),
        )
        yield
        self._settle(self.help_tab)
        yield

        self.extension_tab = ExtensionTab(self)
        self.tabs.addTab(
            self.extension_tab,
            qta.icon("fa5s.puzzle-piece", color="white"),
            translate("extension_tab"),
        )
        yield
        self._settle(self.extension_tab)
        yield

        # Footer
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        self.status_label = QLabel(translate("idle"))
        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        self.dev_label = QLabel(
            f"{translate('developed_by')} | GitHub: @VoxDroid | {translate('current_version', CURRENT_VERSION)}"
        )
        footer_layout.addWidget(self.dev_label)
        main_layout.addWidget(footer)
        self._settle(main_widget)

        return main_widget

    def _snapshot_current_tab(self, index):
        """Picture the page being left, just before a click switches tabs."""
        self._tab_snapshot = None
        page = self.tabs.currentWidget()
        if (
            page is None
            or index == self.tabs.currentIndex()
            or not self.tabs.isTabEnabled(index)
            or not page.isVisible()
        ):
            return
        top_left = page.mapTo(self.tabs, QPoint(0, 0))
        self._tab_snapshot = (page.grab(), QRect(top_left, page.size()))

    def _fade_from_snapshot(self, _index):
        """Dissolve from the previous page instead of cutting to the new one."""
        snapshot, self._tab_snapshot = self._tab_snapshot, None
        if snapshot is not None:
            pixmap, geometry = snapshot
            self.tab_fade = fade_out_snapshot(self.tabs, pixmap, geometry, TAB_FADE_MS)

    def update_all_ui(self):
        self.setWindowTitle(translate("app_title"))

        if self.centralWidget() == self.intro_screen:
            self.intro_screen.update_ui_text()

        if self.main_widget:
            # By widget, not position, so adding a tab cannot shift the labels.
            for tab, key in (
                (self.post_tab, "post_downloader_tab"),
                (self.creator_tab, "creator_downloader_tab"),
                (self.thumbnail_tab, "thumbnail_downloader_tab"),
                (self.history_tab, "history_tab"),
                (self.settings_tab, "settings_tab"),
                (self.help_tab, "help_tab"),
                (self.extension_tab, "extension_tab"),
            ):
                index = self.tabs.indexOf(tab)
                if index >= 0:
                    self.tabs.setTabText(index, translate(key))

            idle_texts = {
                language_manager.get_text("idle", language)
                for language in language_manager.get_available_languages()
            }
            if self.status_label.text() in idle_texts:
                self.status_label.setText(translate("idle"))

            self.dev_label.setText(
                f"{translate('developed_by')} | GitHub: @VoxDroid | {translate('current_version', CURRENT_VERSION)}"
            )

            self.post_tab.refresh_ui()
            self.creator_tab.refresh_ui()
            self.thumbnail_tab.refresh_ui()
            self.history_tab.update_ui_text()
            self.settings_tab.update_ui_text()
            self.help_tab.update_ui_text()
            self.extension_tab.update_ui_text()

    def transition_to_main(self):
        self.main_widget = self._take_main_ui()
        intro = self.intro_screen
        snapshot = intro.grab() if self.isVisible() else None
        geometry = intro.geometry()
        # Swap screens at once, then fade a picture of the intro away on top.
        self._finish_intro_transition()
        if snapshot is not None:
            self.intro_fade = fade_out_snapshot(self, snapshot, geometry)

    def _finish_intro_transition(self):
        """Complete the intro-to-main transition and release the intro screen."""
        self.setCentralWidget(self.main_widget)
        self.main_widget.show()
        self.intro_screen = None

    def check_for_updates(self):
        self.version_checker = VersionChecker()
        self.version_checker.update_available.connect(self.show_update_notification)
        self.version_checker.error_occurred.connect(self.show_error_notification)
        self.version_checker.start()

    def show_update_notification(self, new_version, url):
        msg = QMessageBox(self)
        msg.setWindowTitle(translate("update_available"))
        msg.setText(translate("update_available_message", new_version))
        msg.setInformativeText(
            f"{translate('current_version', CURRENT_VERSION)}\n"
            f'<a href="{url}" style="color: #A0C0FF; text-decoration: none;">{translate("click_release_page")}</a>'
        )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Ignore
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)
        ok_button = msg.button(QMessageBox.StandardButton.Ok)
        if ok_button is not None:
            set_role(ok_button, "primary")
        msg.setTextFormat(Qt.TextFormat.RichText)
        reply = msg.exec()
        if reply == QMessageBox.StandardButton.Ok:
            import webbrowser

            webbrowser.open(url)

    def show_error_notification(self, error_message):
        msg = QMessageBox(self)
        msg.setWindowTitle(translate("update_check_failed"))
        msg.setText(translate("unable_check_updates"))
        msg.setInformativeText(error_message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def log(self, message):
        self.status_label.setText(message)
        print(message)


def main():
    app = QApplication(sys.argv)
    # Without this, any exception that escapes a slot or thread aborts the app.
    install_exception_hook()
    app.setStyle("Fusion")
    apply_theme(app)
    load_bundled_fonts()
    install_filter = getattr(app, "installEventFilter", None)
    if install_filter is not None:
        install_filter(_wheel_scroller)
    window = KemonoDownloader()
    window.show()
    start_build = getattr(window, "start_background_build", None)
    if start_build is not None:
        # After the intro has faded in, so the fade itself stays smooth.
        QTimer.singleShot(FADE_IN_MS + 80, start_build)
    exit_code = app.exec()
    # Detach before shutdown: Qt keeps dispatching events while it destroys
    # the window, and calling into a Python filter while the interpreter is
    # being torn down crashes natively (an access violation on exit).
    remove_filter = getattr(app, "removeEventFilter", None)
    if remove_filter is not None:
        remove_filter(_wheel_scroller)
    store = getattr(window, "history_store", None)
    if isinstance(store, HistoryStore):
        store.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()  # pragma: no cover
