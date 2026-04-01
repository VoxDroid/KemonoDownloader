from types import SimpleNamespace

from kemonodownloader import creator_downloader as cd
from kemonodownloader.creator_downloader import CreatorDownloaderTab, ThreadSettings


def test_create_thread_settings_reads_parent_settings(qapp, tmp_path):
    # Minimal fake settings_tab with required methods and signals
    settings_tab = SimpleNamespace()
    settings_tab.settings_applied = SimpleNamespace(connect=lambda fn: None)
    settings_tab.language_changed = SimpleNamespace(connect=lambda fn: None)
    settings_tab.get_creator_posts_max_attempts = lambda: 10
    settings_tab.get_post_data_max_retries = lambda: 5
    settings_tab.get_file_download_max_retries = lambda: 7
    settings_tab.get_api_request_max_retries = lambda: 2
    settings_tab.get_simultaneous_downloads = lambda: 3

    parent = SimpleNamespace(
        cache_folder=str(tmp_path / "cache"),
        other_files_folder=str(tmp_path / "other"),
        settings_tab=settings_tab,
    )

    tab = CreatorDownloaderTab(parent)
    ts: ThreadSettings = tab._create_thread_settings()
    assert ts.creator_posts_max_attempts == 10
    assert ts.post_data_max_retries == 5
    assert ts.file_download_max_retries == 7
    assert ts.api_request_max_retries == 2
    assert ts.simultaneous_downloads == 3


def test_create_thread_settings_defaults():
    tab = cd.CreatorDownloaderTab.__new__(cd.CreatorDownloaderTab)
    tab._parent = None
    ts = tab._create_thread_settings()
    assert ts.creator_posts_max_attempts == 1
    assert ts.settings_tab is None


def test_create_thread_settings_from_parent():
    parent = SimpleNamespace()

    class FakeSettingsTab:
        def get_creator_posts_max_attempts(self):
            return 10

        def get_post_data_max_retries(self):
            return 4

        def get_file_download_max_retries(self):
            return 3

        def get_api_request_max_retries(self):
            return 2

        def get_simultaneous_downloads(self):
            return 7

    parent.settings_tab = FakeSettingsTab()
    tab = cd.CreatorDownloaderTab.__new__(cd.CreatorDownloaderTab)
    tab._parent = parent
    ts = tab._create_thread_settings()
    assert ts.creator_posts_max_attempts == 10
    assert ts.post_data_max_retries == 4
    assert ts.simultaneous_downloads == 7
