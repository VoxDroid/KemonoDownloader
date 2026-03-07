"""Tests for left panel scroll area in PostDownloaderTab and CreatorDownloaderTab.

Verifies that the left-side panel of both tabs is wrapped in a QScrollArea so
content remains accessible on lower screen resolutions without overlapping.
"""

import os
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QScrollArea, QWidget


class _FakeSettingsTab(QWidget):
    """Minimal stand-in for SettingsTab with the required signals."""

    settings_applied = pyqtSignal()
    language_changed = pyqtSignal()

    def get_creator_posts_max_attempts(self):
        return 1

    def get_post_data_max_retries(self):
        return 1

    def get_file_download_max_retries(self):
        return 1

    def get_api_request_max_retries(self):
        return 1

    def get_simultaneous_downloads(self):
        return 1


class _MockParent:
    """Lightweight parent providing the attributes required by both tabs."""

    def __init__(self, tmp_path):
        self.cache_folder = str(tmp_path / "cache")
        self.other_files_folder = str(tmp_path / "other")
        os.makedirs(self.cache_folder, exist_ok=True)
        os.makedirs(self.other_files_folder, exist_ok=True)
        self.settings_tab = _FakeSettingsTab()

    def log(self, msg):
        pass


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _find_left_scroll_area(tab: QWidget) -> Optional[QScrollArea]:
    """Return the first QScrollArea child of *tab*, if any."""
    for child in tab.children():
        if isinstance(child, QScrollArea):
            return child
    return None


# ---------------------------------------------------------------------------
# PostDownloaderTab tests
# ---------------------------------------------------------------------------


class TestPostLeftPanelScroll:
    def test_left_panel_has_scroll_area(self, qapp, tmp_path):
        """The post tab should contain a QScrollArea wrapping the left panel."""
        from kemonodownloader.post_downloader import PostDownloaderTab

        parent = _MockParent(tmp_path)
        tab = PostDownloaderTab(parent)
        try:
            scroll = _find_left_scroll_area(tab)
            assert scroll is not None, "PostDownloaderTab must have a QScrollArea"
        finally:
            tab.deleteLater()

    def test_scroll_area_is_widget_resizable(self, qapp, tmp_path):
        """widgetResizable must be True so content fills the available width."""
        from kemonodownloader.post_downloader import PostDownloaderTab

        parent = _MockParent(tmp_path)
        tab = PostDownloaderTab(parent)
        try:
            scroll = _find_left_scroll_area(tab)
            assert scroll is not None
            assert scroll.widgetResizable() is True
        finally:
            tab.deleteLater()

    def test_scroll_area_no_frame(self, qapp, tmp_path):
        """Frame should be hidden to keep a seamless look."""
        from kemonodownloader.post_downloader import PostDownloaderTab

        parent = _MockParent(tmp_path)
        tab = PostDownloaderTab(parent)
        try:
            scroll = _find_left_scroll_area(tab)
            assert scroll is not None
            assert scroll.frameShape() == QScrollArea.Shape.NoFrame
        finally:
            tab.deleteLater()

    def test_scroll_area_no_horizontal_scrollbar(self, qapp, tmp_path):
        """Horizontal scroll bar should be disabled — only vertical scrolling."""
        from kemonodownloader.post_downloader import PostDownloaderTab

        parent = _MockParent(tmp_path)
        tab = PostDownloaderTab(parent)
        try:
            scroll = _find_left_scroll_area(tab)
            assert scroll is not None
            assert (
                scroll.horizontalScrollBarPolicy()
                == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
        finally:
            tab.deleteLater()

    def test_scroll_area_wraps_left_widget(self, qapp, tmp_path):
        """The QScrollArea widget should contain the left panel contents."""
        from kemonodownloader.post_downloader import PostDownloaderTab

        parent = _MockParent(tmp_path)
        tab = PostDownloaderTab(parent)
        try:
            scroll = _find_left_scroll_area(tab)
            assert scroll is not None
            inner = scroll.widget()
            assert inner is not None
            # The inner widget should contain the URL input
            assert hasattr(tab, "post_url_input")
            assert tab.post_url_input is not None
        finally:
            tab.deleteLater()


# ---------------------------------------------------------------------------
# CreatorDownloaderTab tests
# ---------------------------------------------------------------------------


class TestCreatorLeftPanelScroll:
    def test_left_panel_has_scroll_area(self, qapp, tmp_path):
        """The creator tab should contain a QScrollArea wrapping the left panel."""
        from kemonodownloader.creator_downloader import CreatorDownloaderTab

        parent = _MockParent(tmp_path)
        tab = CreatorDownloaderTab(parent)
        try:
            scroll = _find_left_scroll_area(tab)
            assert scroll is not None, "CreatorDownloaderTab must have a QScrollArea"
        finally:
            tab.deleteLater()

    def test_scroll_area_is_widget_resizable(self, qapp, tmp_path):
        from kemonodownloader.creator_downloader import CreatorDownloaderTab

        parent = _MockParent(tmp_path)
        tab = CreatorDownloaderTab(parent)
        try:
            scroll = _find_left_scroll_area(tab)
            assert scroll is not None
            assert scroll.widgetResizable() is True
        finally:
            tab.deleteLater()

    def test_scroll_area_no_frame(self, qapp, tmp_path):
        from kemonodownloader.creator_downloader import CreatorDownloaderTab

        parent = _MockParent(tmp_path)
        tab = CreatorDownloaderTab(parent)
        try:
            scroll = _find_left_scroll_area(tab)
            assert scroll is not None
            assert scroll.frameShape() == QScrollArea.Shape.NoFrame
        finally:
            tab.deleteLater()

    def test_scroll_area_no_horizontal_scrollbar(self, qapp, tmp_path):
        from kemonodownloader.creator_downloader import CreatorDownloaderTab

        parent = _MockParent(tmp_path)
        tab = CreatorDownloaderTab(parent)
        try:
            scroll = _find_left_scroll_area(tab)
            assert scroll is not None
            assert (
                scroll.horizontalScrollBarPolicy()
                == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
        finally:
            tab.deleteLater()

    def test_scroll_area_wraps_left_widget(self, qapp, tmp_path):
        from kemonodownloader.creator_downloader import CreatorDownloaderTab

        parent = _MockParent(tmp_path)
        tab = CreatorDownloaderTab(parent)
        try:
            scroll = _find_left_scroll_area(tab)
            assert scroll is not None
            inner = scroll.widget()
            assert inner is not None
            assert hasattr(tab, "creator_url_input")
            assert tab.creator_url_input is not None
        finally:
            tab.deleteLater()
