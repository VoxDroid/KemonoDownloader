"""Tests for Creator Downloader fast-mode UI lock behaviour.

When fast mode is active and a download is running, ALL UI controls
(buttons, inputs, checkboxes, pagination, multi-URL field, etc.) must
stay disabled until the entire batch completes or is cancelled.
"""

import os

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QLabel, QTabWidget, QWidget

from kemonodownloader.creator_downloader import CreatorDownloaderTab
from kemonodownloader.kd_settings import SettingsTab

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _MinimalParent(QWidget):
    """Lightweight stand-in for the main KemonoDownloader window."""

    def __init__(self, tmp_path):
        super().__init__()
        self.cache_folder = str(tmp_path / "cache")
        self.other_files_folder = str(tmp_path / "other")
        os.makedirs(self.cache_folder, exist_ok=True)
        os.makedirs(self.other_files_folder, exist_ok=True)

        ini = str(tmp_path / "settings.ini")
        self.settings_tab = SettingsTab(None)
        self.settings_tab.settings = QSettings(ini, QSettings.Format.IniFormat)

        self.tabs = QTabWidget()
        self.status_label = QLabel("idle")

        # Add a dummy tab so tab-index logic in set_downloading_ui_state works
        self.tabs.addTab(QWidget(), "dummy")


def _make_tab(tmp_path):
    """Return (parent, tab) ready for testing."""
    parent = _MinimalParent(tmp_path)
    tab = CreatorDownloaderTab(parent)
    parent.tabs.addTab(tab, "Creator")
    parent.tabs.setCurrentWidget(tab)
    return parent, tab


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFastModeDownloadLock:
    """Controls must stay disabled throughout a fast-mode download."""

    # Helpers ---------------------------------------------------------------

    @staticmethod
    def _all_controls_disabled(tab):
        """Return True if every user-interactive control is disabled."""
        controls = [
            tab.creator_download_btn,
            tab.creator_url_input,
            tab.creator_add_to_queue_btn,
            tab.creator_add_from_file_btn,
            tab.creator_queue_list,
            tab.creator_multi_url_input,
            tab.creator_multi_url_add_btn,
            tab.creator_main_check,
            tab.creator_attachments_check,
            tab.creator_content_check,
            tab.creator_fast_mode_check,
            tab.creator_auto_rename_check,
            tab.creator_download_text_check,
            tab.creator_search_input,
            tab.creator_check_all,
            tab.creator_check_all_all,
            tab.creator_post_list,
            tab.creator_view_button,
            tab.prev_page_btn,
            tab.next_page_btn,
        ]
        return all(not c.isEnabled() for c in controls)

    @staticmethod
    def _cancel_btn_enabled(tab):
        return tab.creator_cancel_btn.isEnabled()

    # Tests -----------------------------------------------------------------

    def test_set_downloading_ui_state_locks_everything(self, qapp, tmp_path):
        """set_downloading_ui_state(True) must disable all interactive controls."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.set_downloading_ui_state(True)
            assert self._all_controls_disabled(tab)
            assert self._cancel_btn_enabled(tab)
        finally:
            parent.deleteLater()

    def test_set_downloading_ui_state_unlocks(self, qapp, tmp_path):
        """set_downloading_ui_state(False) must re-enable controls."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.set_downloading_ui_state(True)
            tab.set_downloading_ui_state(False)
            # All controls should be enabled
            assert tab.creator_download_btn.isEnabled()
            assert tab.creator_url_input.isEnabled()
            assert tab.creator_multi_url_input.isEnabled()
        finally:
            parent.deleteLater()

    def test_fast_mode_controls_stay_locked_after_unlock(self, qapp, tmp_path):
        """When fast mode is on and download ends, fast-mode-locked controls stay disabled."""
        parent, tab = _make_tab(tmp_path)
        try:
            # Enable fast mode
            tab.creator_fast_mode_check.setChecked(True)
            assert tab.fast_mode is True

            # Simulate download cycle
            tab.set_downloading_ui_state(True)
            tab.set_downloading_ui_state(False)

            # Fast-mode-locked controls must remain disabled
            assert not tab.creator_main_check.isEnabled()
            assert not tab.creator_attachments_check.isEnabled()
            assert not tab.creator_content_check.isEnabled()
            assert not tab.creator_auto_rename_check.isEnabled()
            assert not tab.creator_download_text_check.isEnabled()
            assert not tab.creator_check_all.isEnabled()
            assert not tab.creator_check_all_all.isEnabled()

            # But non-fast-mode controls should be re-enabled
            assert tab.creator_download_btn.isEnabled()
            assert tab.creator_url_input.isEnabled()
            assert tab.creator_multi_url_input.isEnabled()
        finally:
            parent.deleteLater()

    def test_set_fetching_ui_state_blocked_during_fast_download(self, qapp, tmp_path):
        """set_fetching_ui_state(False) must be a no-op during fast-mode download."""
        parent, tab = _make_tab(tmp_path)
        try:
            # Enter fast-mode downloading state
            tab.fast_mode = True
            tab._fast_mode_downloading = True
            tab.downloading = True
            tab.set_downloading_ui_state(True)

            assert self._all_controls_disabled(tab)

            # Simulate what happens when post detection finishes mid-download
            tab.set_fetching_ui_state(False)

            # Everything should STILL be disabled
            assert self._all_controls_disabled(tab)
            assert self._cancel_btn_enabled(tab)
        finally:
            parent.deleteLater()

    def test_set_fetching_ui_state_works_normally_outside_fast_mode(
        self, qapp, tmp_path
    ):
        """set_fetching_ui_state(False) re-enables controls when not fast-downloading."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.set_fetching_ui_state(True)
            assert not tab.creator_download_btn.isEnabled()
            assert not tab.creator_url_input.isEnabled()

            tab.set_fetching_ui_state(False)
            assert tab.creator_download_btn.isEnabled()
            assert tab.creator_url_input.isEnabled()
        finally:
            parent.deleteLater()

    def test_multi_url_input_disabled_during_fast_download(self, qapp, tmp_path):
        """The multi-URL text area must be disabled during fast-mode download."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.creator_fast_mode_check.setChecked(True)
            # isVisibleTo checks visibility relative to ancestor (works without show())
            assert not tab.creator_multi_url_input.isHidden()

            # Start fast-mode download
            tab._fast_mode_downloading = True
            tab.downloading = True
            tab.set_downloading_ui_state(True)

            assert not tab.creator_multi_url_input.isEnabled()
            assert not tab.creator_multi_url_add_btn.isEnabled()
        finally:
            parent.deleteLater()

    def test_pagination_disabled_during_download(self, qapp, tmp_path):
        """Pagination buttons must stay disabled during any download."""
        parent, tab = _make_tab(tmp_path)
        try:
            # Simulate multiple pages
            tab.current_page = 1
            tab.total_pages = 3

            tab.downloading = True
            tab.set_downloading_ui_state(True)

            # Even with multiple pages, buttons stay off
            assert not tab.prev_page_btn.isEnabled()
            assert not tab.next_page_btn.isEnabled()

            # update_pagination_controls respects downloading flag
            tab.update_pagination_controls()
            assert not tab.prev_page_btn.isEnabled()
            assert not tab.next_page_btn.isEnabled()
        finally:
            parent.deleteLater()

    def test_pagination_enabled_when_not_downloading(self, qapp, tmp_path):
        """Pagination buttons work normally when not downloading."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.current_page = 2
            tab.total_pages = 3
            tab.downloading = False

            tab.update_pagination_controls()
            assert tab.prev_page_btn.isEnabled()
            assert tab.next_page_btn.isEnabled()
        finally:
            parent.deleteLater()

    def test_fast_mode_toggle_off_restores_controls(self, qapp, tmp_path):
        """Turning fast mode off after download should re-enable all controls."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.creator_fast_mode_check.setChecked(True)
            tab.downloading = True
            tab.set_downloading_ui_state(True)

            # End download
            tab.downloading = False
            tab._fast_mode_downloading = False
            tab.set_downloading_ui_state(False)

            # Turn off fast mode
            tab.creator_fast_mode_check.setChecked(False)

            # All controls should now be fully enabled
            assert tab.creator_main_check.isEnabled()
            assert tab.creator_attachments_check.isEnabled()
            assert tab.creator_content_check.isEnabled()
            assert tab.creator_auto_rename_check.isEnabled()
            assert tab.creator_download_text_check.isEnabled()
        finally:
            parent.deleteLater()

    def test_fast_mode_download_then_complete_restores_ui(self, qapp, tmp_path):
        """Full cycle: fast-mode download → finish → UI restored with fast-mode locks."""
        parent, tab = _make_tab(tmp_path)
        try:
            # Enable fast mode
            tab.creator_fast_mode_check.setChecked(True)

            # Simulate start_creator_download fast-mode branch
            tab._fast_mode_pending_urls = []
            tab._fast_mode_downloading = True
            tab.downloading = True
            tab.set_downloading_ui_state(True)
            assert self._all_controls_disabled(tab)

            # Simulate _fast_mode_process_next with empty queue (batch done)
            tab._fast_mode_downloading = False
            tab.downloading = False
            tab.set_downloading_ui_state(False)

            # Non-fast-mode controls restored
            assert tab.creator_download_btn.isEnabled()
            assert tab.creator_url_input.isEnabled()
            assert tab.creator_queue_list.isEnabled()
            assert tab.creator_multi_url_input.isEnabled()

            # Fast-mode-locked controls still disabled
            assert not tab.creator_main_check.isEnabled()
            assert not tab.creator_auto_rename_check.isEnabled()
        finally:
            parent.deleteLater()

    def test_cancel_restores_ui(self, qapp, tmp_path):
        """Cancellation should fully restore UI even in fast mode."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.creator_fast_mode_check.setChecked(True)
            tab._fast_mode_downloading = True
            tab.downloading = True
            tab.set_downloading_ui_state(True)

            # Simulate what on_cancellation_finished does
            tab._fast_mode_downloading = False
            tab._fast_mode_pending_urls.clear()
            tab.downloading = False
            tab.set_downloading_ui_state(False)

            # Non-fast-mode controls restored
            assert tab.creator_download_btn.isEnabled()
            assert tab.creator_url_input.isEnabled()

            # Fast-mode controls still locked
            assert not tab.creator_main_check.isEnabled()
        finally:
            parent.deleteLater()


class TestFastModeBatchURLValidation:
    """Batch URL input must reject non-creator URLs (e.g. post URLs)."""

    def test_post_url_rejected(self, qapp, tmp_path):
        """A post-level URL must not be added to the creator queue."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.creator_multi_url_input.setPlainText(
                "https://kemono.cr/fanbox/user/28894824/post/11447661"
            )
            tab.add_multiple_creators_to_queue()
            assert len(tab.creator_queue) == 0
        finally:
            parent.deleteLater()

    def test_creator_url_accepted(self, qapp, tmp_path):
        """A valid creator-level URL should be added."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.creator_multi_url_input.setPlainText(
                "https://kemono.cr/fanbox/user/28894824"
            )
            tab.add_multiple_creators_to_queue()
            assert len(tab.creator_queue) == 1
            assert "28894824" in tab.creator_queue[0][0]
        finally:
            parent.deleteLater()

    def test_mixed_urls_only_valid_added(self, qapp, tmp_path):
        """Mix of valid and invalid URLs: only creator URLs are queued."""
        parent, tab = _make_tab(tmp_path)
        try:
            text = (
                "https://kemono.cr/fanbox/user/111\n"
                "https://kemono.cr/fanbox/user/222/post/999\n"
                "https://coomer.st/onlyfans/user/333\n"
                "not-a-url\n"
                "https://kemono.cr/patreon/user/444\n"
            )
            tab.creator_multi_url_input.setPlainText(text)
            tab.add_multiple_creators_to_queue()
            urls = [u for u, _ in tab.creator_queue]
            assert len(urls) == 3
            assert any("111" in u for u in urls)
            assert any("333" in u for u in urls)
            assert any("444" in u for u in urls)
            # Post URL and garbage must not appear
            assert not any("post" in u for u in urls)
            assert not any("not-a-url" in u for u in urls)
        finally:
            parent.deleteLater()

    def test_duplicate_urls_skipped(self, qapp, tmp_path):
        """Duplicate URLs should be skipped, not double-added."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.creator_multi_url_input.setPlainText(
                "https://kemono.cr/fanbox/user/111\n"
                "https://kemono.cr/fanbox/user/111\n"
            )
            tab.add_multiple_creators_to_queue()
            assert len(tab.creator_queue) == 1
        finally:
            parent.deleteLater()

    def test_trailing_slash_handled(self, qapp, tmp_path):
        """URLs with trailing slashes should still be validated correctly."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.creator_multi_url_input.setPlainText(
                "https://kemono.cr/fanbox/user/28894824/"
            )
            tab.add_multiple_creators_to_queue()
            assert len(tab.creator_queue) == 1
        finally:
            parent.deleteLater()

    def test_empty_input_does_nothing(self, qapp, tmp_path):
        """Empty multi-URL input should not add anything."""
        parent, tab = _make_tab(tmp_path)
        try:
            tab.creator_multi_url_input.setPlainText("")
            tab.add_multiple_creators_to_queue()
            assert len(tab.creator_queue) == 0
        finally:
            parent.deleteLater()
