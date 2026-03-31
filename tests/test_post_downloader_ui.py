from kemonodownloader.post_downloader import PostDownloaderTab


class DummyWidget:
    def __init__(self):
        self.enabled = []
        self.visible = []
        self.checked = None

    def setEnabled(self, v):
        self.enabled.append(v)

    def setVisible(self, v):
        self.visible.append(v)

    def setChecked(self, v):
        self.checked = v


def test_toggle_fast_mode():
    tab = PostDownloaderTab.__new__(PostDownloaderTab)
    # Provide minimal attributes used by toggle_fast_mode
    tab.auto_rename_checkbox = DummyWidget()
    tab.post_download_text_check = DummyWidget()
    tab.post_check_all = DummyWidget()
    tab.download_all_links = DummyWidget()
    tab.multi_url_input = DummyWidget()
    tab.multi_url_add_btn = DummyWidget()
    tab.fast_mode = False

    # Avoid calling methods that require full init
    tab.append_log_to_console = lambda *a, **k: None

    # Call toggle with Checked state (2)
    PostDownloaderTab.toggle_fast_mode(tab, 2)

    # When fast_mode is True, controls should be disabled
    assert (
        tab.auto_rename_checkbox.enabled
        and tab.auto_rename_checkbox.enabled[-1] is False
    )
    assert (
        tab.post_download_text_check.enabled
        and tab.post_download_text_check.enabled[-1] is False
    )
    assert tab.multi_url_input.visible and tab.multi_url_input.visible[-1] is True
