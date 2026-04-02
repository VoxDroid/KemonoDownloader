import os
from types import SimpleNamespace

from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

from kemonodownloader import creator_downloader as cd


def make_parent(tmp_path):
    parent = QWidget()
    parent.cache_folder = str(tmp_path / "cache")
    parent.other_files_folder = str(tmp_path / "other")
    os.makedirs(parent.cache_folder, exist_ok=True)
    os.makedirs(parent.other_files_folder, exist_ok=True)

    st = SimpleNamespace()
    st.get_creator_posts_max_attempts = lambda: 1
    st.get_post_data_max_retries = lambda: 1
    st.get_file_download_max_retries = lambda: 1
    st.get_api_request_max_retries = lambda: 1
    st.get_simultaneous_downloads = lambda: 1
    st.get_creator_filename_template = lambda: None
    st.get_creator_folder_strategy = lambda: "per_post"
    st.settings_applied = SimpleNamespace(connect=lambda f: None)
    st.language_changed = SimpleNamespace(connect=lambda f: None)
    parent.settings_tab = st

    class Tabs:
        def __init__(self):
            self._count = 3

        def count(self):
            return self._count

        def currentIndex(self):
            return 0

        def setTabEnabled(self, i, v):
            pass

    parent.tabs = Tabs()
    parent.status_label = SimpleNamespace(setText=lambda s: None)
    parent.animate_button = lambda b, v: None
    parent.creator_console = SimpleNamespace(
        toHtml=lambda: "<b>log</b>", clear=lambda: None, append=lambda html: None
    )
    parent.append_log_to_console = lambda *a, **k: None
    return parent


def test_append_log_and_toggle_fast_mode(tmp_path):
    parent = make_parent(tmp_path)
    tab = cd.CreatorDownloaderTab(parent)

    tab.append_log_to_console("Test message", "INFO")
    assert "Test message" in tab.creator_console.toHtml()

    tab.toggle_fast_mode(2)  # enable
    assert tab.fast_mode is True
    tab.toggle_fast_mode(0)  # disable
    assert tab.fast_mode is False


def test_add_multiple_creators_and_remove(monkeypatch, tmp_path):
    parent = make_parent(tmp_path)
    tab = cd.CreatorDownloaderTab(parent)

    text = "https://kemono.cr/user/1\nnot a url\nhttps://coomer.st/user/2"
    tab.creator_multi_url_input.setPlainText(text)
    tab.add_multiple_creators_to_queue()
    # Should have added the two valid URLs
    assert any("kemono.cr/user/1" in u[0] for u in tab.creator_queue)
    assert any("coomer.st/user/2" in u[0] for u in tab.creator_queue)

    # Test remove handler: confirm removal via QMessageBox.question
    # Add a known URL and remove it
    url = "https://kemono.cr/user/99"
    tab.creator_queue.append((url, False))
    monkeypatch.setattr(
        cd.QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes
    )
    handler = tab.create_remove_handler(url)
    handler()
    assert not any(item[0] == url for item in tab.creator_queue)


def test_add_creators_from_file(monkeypatch, tmp_path):
    parent = make_parent(tmp_path)
    tab = cd.CreatorDownloaderTab(parent)

    # Create a temp file with urls
    fp = tmp_path / "links.txt"
    fp.write_text("https://kemono.cr/user/10\ninvalid\nhttps://coomer.st/user/11\n")

    monkeypatch.setattr(
        cd.QFileDialog, "getOpenFileName", lambda *a, **k: (str(fp), "")
    )
    monkeypatch.setattr(cd.QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(cd.QMessageBox, "critical", lambda *a, **k: None)

    tab.add_creators_from_file()
    assert any("/user/10" in u[0] for u in tab.creator_queue)
    assert any("/user/11" in u[0] for u in tab.creator_queue)


def test_pagination_and_display(tmp_path):
    parent = make_parent(tmp_path)
    tab = cd.CreatorDownloaderTab(parent)

    # Populate filtered_posts to force multiple pages
    for i in range(1, 10):
        tab.filtered_posts.append((f"Post{i}", str(i), None, False))
    tab.posts_per_page = 3
    tab.total_pages = (
        len(tab.filtered_posts) + tab.posts_per_page - 1
    ) // tab.posts_per_page
    tab.current_page = 2
    tab.display_current_page()
    # creator_post_list should have items for page 2
    assert tab.creator_post_list.count() > 0


def test_set_fetching_and_downloading_states(tmp_path):
    parent = make_parent(tmp_path)
    tab = cd.CreatorDownloaderTab(parent)
    tab.set_fetching_ui_state(True)
    tab.set_fetching_ui_state(False)
    tab.set_downloading_ui_state(True)
    tab.set_downloading_ui_state(False)


def test_creator_tab_basic_interactions(tmp_path, monkeypatch):
    class Parent:
        def __init__(self, base):
            self.cache_folder = str(base / "cache")
            self.other_files_folder = str(base / "other")
            self.download_folder = str(base / "dl")

        def animate_button(self, btn, flag):
            pass

    parent = Parent(tmp_path)
    tab = cd.CreatorDownloaderTab(parent)

    # Fast mode toggle disables category checkboxes
    tab.toggle_fast_mode(2)
    assert tab.fast_mode is True
    assert not tab.creator_main_check.isEnabled()

    # Add a creator url via multi-url input
    test_url = "https://kemono.cr/user/1"
    tab.creator_multi_url_input.setPlainText(test_url)
    tab.add_multiple_creators_to_queue()
    assert any(test_url == item[0] for item in tab.creator_queue)

    # toggle_check_all should return early when no visible posts
    tab.toggle_check_all(2)

    # Test adding creators from file (monkeypatch file dialog)
    file_path = tmp_path / "links.txt"
    file_path.write_text(test_url + "\n")
    monkeypatch.setattr(
        QFileDialog, "getOpenFileName", lambda *a, **k: (str(file_path), "")
    )
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    tab.add_creators_from_file()
    assert any(test_url == item[0] for item in tab.creator_queue)
