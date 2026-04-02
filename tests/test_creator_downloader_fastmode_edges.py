import os
from types import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidgetItem, QMessageBox, QWidget

from kemonodownloader import creator_downloader as cd


class DummySignal:
    def connect(self, fn):
        self._fn = fn


def make_parent(tmp_path):
    parent = QWidget()
    parent.cache_folder = str(tmp_path / "cache")
    parent.other_files_folder = str(tmp_path / "other")
    parent.download_folder = str(tmp_path / "downloads")
    os.makedirs(parent.cache_folder, exist_ok=True)
    os.makedirs(parent.other_files_folder, exist_ok=True)
    os.makedirs(parent.download_folder, exist_ok=True)

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
    parent.status_label = SimpleNamespace(
        setText=lambda s: setattr(parent, "_status", s)
    )
    parent.animate_button = lambda b, v: None
    parent.creator_console = SimpleNamespace(
        toHtml=lambda: "<b>log</b>",
        clear=lambda: None,
        append=lambda html: None,
    )
    parent.append_log_to_console = lambda *a, **k: None
    return parent


def make_tab(tmp_path):
    return cd.CreatorDownloaderTab(make_parent(tmp_path))


def test_refresh_ui_resets_progress_when_not_downloading(tmp_path):
    tab = make_tab(tmp_path)
    tab.downloading = False
    tab.creator_file_progress.setValue(77)
    tab.creator_overall_progress.setValue(66)
    tab.background_task_progress.setRange(0, 0)
    tab.background_task_label.setText("busy")
    tab.current_file_index = 99
    tab.completed_posts = {"1"}
    tab.completed_files = {"a"}
    tab.total_files_to_download = 5

    tab.refresh_ui()

    assert tab.creator_file_progress.value() == 0
    assert tab.creator_overall_progress.value() == 0
    assert tab.current_file_index == -1
    assert tab.completed_posts == set()
    assert tab.completed_files == set()
    assert tab.total_files_to_download == 0
    assert tab.background_task_label.text() != "busy"


def test_add_creator_to_queue_validation_in_progress_warns(tmp_path):
    tab = make_tab(tmp_path)
    tab.creator_url_input.setText("https://kemono.cr/fanbox/user/1")
    tab.validation_thread = SimpleNamespace(isRunning=lambda: True)
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.add_creator_to_queue()

    assert not tab.creator_queue
    assert any(level == "WARNING" for _, level in logs)


def test_cleanup_validation_thread_removes_thread(tmp_path):
    tab = make_tab(tmp_path)
    deleted = []
    fake_thread = SimpleNamespace(deleteLater=lambda: deleted.append(True))
    tab.validation_thread = fake_thread
    tab.active_threads = [fake_thread]

    tab.cleanup_validation_thread()

    assert tab.validation_thread is None
    assert fake_thread not in tab.active_threads
    assert deleted


def test_check_creator_from_queue_invalid_type(tmp_path):
    tab = make_tab(tmp_path)
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.check_creator_from_queue(123)

    assert any(level == "ERROR" for _, level in logs)


def test_check_creator_from_queue_warns_when_detection_running(tmp_path):
    tab = make_tab(tmp_path)
    url = "https://kemono.cr/fanbox/user/1"
    tab.creator_queue = [(url, False)]
    tab.post_detection_thread = SimpleNamespace(isRunning=lambda: True)
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.check_creator_from_queue(url)

    assert any(level == "WARNING" for _, level in logs)


def test_start_creator_download_fast_mode_initializes_batch(tmp_path):
    tab = make_tab(tmp_path)
    tab.fast_mode = True
    tab.creator_queue = [
        ("https://kemono.cr/fanbox/user/1", False),
        ("https://coomer.st/fanbox/user/2", False),
    ]
    states = []
    calls = []
    tab.set_downloading_ui_state = lambda v: states.append(v)
    tab._fast_mode_process_next = lambda: calls.append(True)

    tab.start_creator_download()

    assert tab.downloading is True
    assert tab._fast_mode_downloading is True
    assert len(tab._fast_mode_pending_urls) == 2
    assert states and states[-1] is True
    assert calls


def test_start_creator_download_no_creator_viewed_calls_finished(tmp_path):
    tab = make_tab(tmp_path)
    tab.fast_mode = False
    tab.creator_queue = [("https://kemono.cr/fanbox/user/1", False)]
    tab.posts_to_download = ["101"]
    tab.current_creator_url = None

    called = []
    tab.creator_download_finished = lambda: called.append(True)

    tab.start_creator_download()

    assert called


def test_fast_mode_process_next_empty_finishes(tmp_path):
    tab = make_tab(tmp_path)
    tab._fast_mode_pending_urls = []
    tab._fast_mode_downloading = True
    tab.downloading = True
    states = []
    tab.set_downloading_ui_state = lambda v: states.append(v)

    tab._fast_mode_process_next()

    assert tab._fast_mode_downloading is False
    assert tab.downloading is False
    assert states and states[-1] is False


def test_fast_mode_auto_download_no_creator_processes_next(tmp_path):
    tab = make_tab(tmp_path)
    tab.current_creator_url = None
    calls = []
    tab._fast_mode_process_next = lambda: calls.append(True)

    tab._fast_mode_auto_download()

    assert calls


def test_fast_mode_auto_download_no_posts_removes_and_next(tmp_path):
    tab = make_tab(tmp_path)
    tab.current_creator_url = "https://kemono.cr/fanbox/user/1"
    tab.all_detected_posts = []
    removed = []
    called = []
    tab._fast_mode_remove_creator_url = lambda url: removed.append(url)
    tab._fast_mode_process_next = lambda: called.append(True)

    tab._fast_mode_auto_download()

    assert removed == ["https://kemono.cr/fanbox/user/1"]
    assert called


def test_prepare_files_for_download_in_progress_warns(tmp_path):
    tab = make_tab(tmp_path)
    tab.file_preparation_thread = SimpleNamespace(isRunning=lambda: True)
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.prepare_files_for_download(["https://kemono.cr/fanbox/user/1"])

    assert any(level == "WARNING" for _, level in logs)


def test_prepare_files_for_download_no_posts_available(tmp_path):
    tab = make_tab(tmp_path)
    tab.current_creator_url = "https://kemono.cr/fanbox/user/1"
    tab.posts_to_download = ["999"]
    tab.all_files_map = {
        tab.current_creator_url: [("Title", ("111", None))],
    }
    called = []
    tab.creator_download_finished = lambda: called.append(True)

    tab.prepare_files_for_download([tab.current_creator_url])

    assert called
    assert tab.background_task_progress.value() == 0


def test_cleanup_file_preparation_thread_removes_thread(tmp_path):
    tab = make_tab(tmp_path)
    deleted = []
    fake = SimpleNamespace(deleteLater=lambda: deleted.append(True))
    tab.file_preparation_thread = fake
    tab.active_threads = [fake]

    tab.cleanup_file_preparation_thread()

    assert fake not in tab.active_threads
    assert tab.file_preparation_thread is None
    assert deleted


def test_on_file_preparation_finished_no_files_detected_moves_next(tmp_path):
    tab = make_tab(tmp_path)
    moved = []
    tab.process_next_creator = lambda urls: moved.append(urls)

    tab.on_file_preparation_finished(
        ["https://kemono.cr/fanbox/user/1", "https://kemono.cr/fanbox/user/2"],
        [],
        {},
    )

    assert moved == [["https://kemono.cr/fanbox/user/2"]]


def test_fast_mode_remove_creator_url_updates_queue(tmp_path):
    tab = make_tab(tmp_path)
    tab.creator_queue = [
        ("https://kemono.cr/fanbox/user/1/", False),
        ("https://kemono.cr/fanbox/user/2", False),
    ]
    updated = []
    tab.update_creator_queue_list = lambda: updated.append(True)

    tab._fast_mode_remove_creator_url("https://kemono.cr/fanbox/user/1")

    assert len(tab.creator_queue) == 1
    assert tab.creator_queue[0][0].endswith("/2")
    assert updated


def test_update_post_completion_fast_mode_removes_creator(tmp_path):
    tab = make_tab(tmp_path)
    tab.fast_mode = True
    tab.current_creator_url = "https://kemono.cr/fanbox/user/1"
    tab.total_posts_to_download = 1
    tab.total_files_to_download = 1
    tab.completed_files = {"f1"}
    removed = []
    tab._fast_mode_remove_creator_url = lambda url: removed.append(url)

    tab.update_post_completion("101")

    assert removed == ["https://kemono.cr/fanbox/user/1"]


def test_toggle_check_all_all_in_progress_warns(tmp_path):
    tab = make_tab(tmp_path)
    tab.checkbox_toggle_thread = SimpleNamespace(isRunning=lambda: True)
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.toggle_check_all_all(2)

    assert any(level == "WARNING" for _, level in logs)


def test_toggle_check_all_all_starts_worker(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    tab.all_detected_posts = [("Post", ("1", None))]

    class FakeToggleThread:
        def __init__(self, visible_posts, checked_urls, state):
            self.visible_posts = visible_posts
            self.checked_urls = checked_urls
            self.state = state
            self.finished = DummySignal()
            self.log = DummySignal()
            self.started = False

        def start(self):
            self.started = True

    monkeypatch.setattr(cd, "CheckboxToggleThread", FakeToggleThread)

    tab.toggle_check_all_all(2)

    assert tab.checkbox_toggle_thread is not None
    assert tab.checkbox_toggle_thread.started is True
    assert tab.active_threads


def test_toggle_checkbox_state_no_post_id_logs_error(tmp_path):
    tab = make_tab(tmp_path)
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.toggle_checkbox_state("Missing Post")

    assert any(level == "ERROR" for _, level in logs)
    assert tab.background_task_progress.value() == 0


def test_update_current_preview_url_widget_and_none(tmp_path):
    tab = make_tab(tmp_path)

    item_with_widget = QListWidgetItem()
    item_with_widget.setData(Qt.ItemDataRole.UserRole, "https://example.com/a.jpg")
    tab.creator_post_list.addItem(item_with_widget)
    widget = QWidget()
    tab.creator_post_list.setItemWidget(item_with_widget, widget)

    tab.update_current_preview_url(item_with_widget, None)
    assert tab.current_preview_url == "https://example.com/a.jpg"
    assert tab.creator_view_button.isEnabled() is True

    item_without_widget = QListWidgetItem()
    item_without_widget.setData(Qt.ItemDataRole.UserRole, "https://example.com/b.jpg")
    tab.creator_post_list.addItem(item_without_widget)

    tab.update_current_preview_url(item_without_widget, None)
    assert tab.current_preview_url is None
    assert tab.creator_view_button.isEnabled() is False

    tab.update_current_preview_url(None, item_without_widget)
    assert tab.current_preview_url is None
    assert tab.creator_view_button.isEnabled() is False


def test_add_creators_from_file_logs_error_processing_url(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    links = tmp_path / "links.txt"
    links.write_text("https://kemono.cr/fanbox/user/1\n")

    monkeypatch.setattr(
        cd.QFileDialog, "getOpenFileName", lambda *a, **k: (str(links), "")
    )
    monkeypatch.setattr(cd.QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(cd.QMessageBox, "critical", lambda *a, **k: None)
    monkeypatch.setattr(
        cd,
        "get_domain_config",
        lambda url: (_ for _ in ()).throw(RuntimeError("bad domain parse")),
    )

    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.add_creators_from_file()

    assert any(level == "ERROR" for _, level in logs)


def test_cleanup_thread_all_files_attempted_finishes_and_clears(tmp_path):
    tab = make_tab(tmp_path)

    class FakeThread:
        def __init__(self, running=False):
            self._running = running
            self.deleted = False
            self.terminated = False
            self.waited = False
            self.failed_files = {"u": "err"}

        def isRunning(self):
            return self._running

        def wait(self, *args, **kwargs):
            self.waited = True

        def deleteLater(self):
            self.deleted = True

        def terminate(self):
            self.terminated = True

    main_thread = FakeThread(running=False)
    lingering = FakeThread(running=True)
    tab.active_threads = [main_thread, lingering]
    tab.total_files_to_download = 1
    tab.completed_files = set()
    tab.failed_files = {}

    finished = []
    tab.creator_download_finished = lambda: finished.append(True)
    tab.process_next_creator = lambda urls: None

    tab.cleanup_thread(main_thread, [])

    assert finished
    assert tab.active_threads == []
    assert lingering.terminated is True


def test_cancel_creator_download_fetching_path_filters_selected_posts(tmp_path):
    tab = make_tab(tmp_path)
    tab.active_threads = [SimpleNamespace()]

    stopped = []
    tab.post_detection_thread = SimpleNamespace(
        isRunning=lambda: True,
        stop=lambda: stopped.append(True),
    )
    tab.posts_to_download = ["1"]
    tab.all_detected_posts = [("A", ("1", None)), ("B", ("2", None))]
    tab.filtered_posts = [
        ("A", "1", None, True),
        ("B", "2", None, False),
    ]
    tab.current_creator_url = "https://kemono.cr/fanbox/user/1"
    tab.all_files_map = {}

    cleaned = []
    tab.cleanup_post_detection_thread = lambda: cleaned.append(True)
    tab.set_fetching_ui_state = lambda enabled: None
    tab.display_current_page = lambda: None
    tab.update_pagination_controls = lambda: None

    tab.cancel_creator_download()

    assert stopped
    assert cleaned
    assert tab.all_detected_posts == [("A", ("1", None))]
    assert tab.filtered_posts == [("A", "1", None, True)]


def test_cancellation_thread_runtimeerror_during_termination_logs_warning(monkeypatch):
    class FakeThread:
        def __init__(self):
            self.calls = 0

        def stop(self):
            pass

        def isRunning(self):
            self.calls += 1
            return self.calls >= 2

        def terminate(self):
            raise RuntimeError("already gone")

        def wait(self):
            pass

    thread = cd.CancellationThread([FakeThread()])
    logs = []
    thread.log = SimpleNamespace(emit=lambda msg, level: logs.append((msg, level)))
    thread.finished = SimpleNamespace(emit=lambda: logs.append(("finished", "INFO")))
    monkeypatch.setattr(cd.time, "sleep", lambda s: None)

    thread.run()

    assert any(level == "WARNING" for _, level in logs)


def test_start_creator_download_no_posts_selected_warns(tmp_path):
    tab = make_tab(tmp_path)
    tab.fast_mode = False
    tab.creator_queue = [("https://kemono.cr/fanbox/user/1", False)]
    tab.posts_to_download = []
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.start_creator_download()

    assert any(level == "WARNING" for _, level in logs)


def test_on_post_detection_error_without_cache_resets_fetch_ui(tmp_path):
    tab = make_tab(tmp_path)
    tab.current_creator_url = "https://kemono.cr/fanbox/user/1"
    tab.all_files_map = {}
    cleaned = []
    states = []
    tab.cleanup_post_detection_thread = lambda: cleaned.append(True)
    tab.set_fetching_ui_state = lambda enabled: states.append(enabled)
    tab.post_detection_thread = SimpleNamespace()

    tab.on_post_detection_error("boom")

    assert cleaned
    assert states and states[-1] is False
    assert tab.background_task_progress.value() == 0


def test_view_current_item_non_image_logs_warning(tmp_path):
    tab = make_tab(tmp_path)
    tab.current_preview_url = "https://example.com/file.zip"
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.view_current_item()

    assert any(level == "WARNING" for _, level in logs)


def test_on_selection_changed_updates_widget_style(tmp_path):
    tab = make_tab(tmp_path)
    tab.post_url_map["Post A"] = ("101", None)
    tab.add_list_item("Post A", None, True)
    item = tab.creator_post_list.item(0)
    item.setSelected(True)

    tab.on_selection_changed()

    assert tab.previous_selected_widgets


def test_append_log_to_console_updates_visible_logs_window(tmp_path):
    tab = make_tab(tmp_path)
    updates = []
    tab.logs_window = SimpleNamespace(
        isVisible=lambda: True,
        update_logs_content=lambda: updates.append(True),
    )

    tab.append_log_to_console("hello", "INFO")

    assert updates


def test_add_creators_from_file_empty_selection_returns(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    monkeypatch.setattr(cd.QFileDialog, "getOpenFileName", lambda *a, **k: ("", ""))

    tab.add_creators_from_file()

    assert tab.creator_queue == []


def test_add_creators_from_file_read_error_logs_and_shows_critical(
    tmp_path, monkeypatch
):
    tab = make_tab(tmp_path)
    links = tmp_path / "links.txt"
    links.write_text("https://kemono.cr/fanbox/user/1\n")

    monkeypatch.setattr(
        cd.QFileDialog, "getOpenFileName", lambda *a, **k: (str(links), "")
    )
    monkeypatch.setattr(
        "builtins.open",
        lambda *a, **k: (_ for _ in ()).throw(OSError("cannot read")),
    )

    critical = []
    monkeypatch.setattr(
        cd.QMessageBox, "critical", lambda *a, **k: critical.append(True)
    )

    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.add_creators_from_file()

    assert any(level == "ERROR" for _, level in logs)
    assert critical


def test_cancellation_thread_stop_and_wait_runtime_paths(monkeypatch):
    class FakeThread:
        def __init__(self):
            self.calls = 0

        def stop(self):
            raise RuntimeError("already deleted")

        def isRunning(self):
            self.calls += 1
            if self.calls == 1:
                return True
            return False

        def terminate(self):
            return None

        def wait(self):
            return None

    thread = cd.CancellationThread([FakeThread()])
    logs = []
    thread.log = SimpleNamespace(emit=lambda msg, level: logs.append((msg, level)))
    thread.finished = SimpleNamespace(emit=lambda: logs.append(("finished", "INFO")))

    # Trigger the while-loop RuntimeError handling path once.
    def flaky_sleep(_):
        raise RuntimeError("thread deleted while waiting")

    monkeypatch.setattr(cd.time, "sleep", flaky_sleep)
    t = [0.0, 0.1, 10.0]
    monkeypatch.setattr(cd.time, "time", lambda: t.pop(0) if t else 10.0)

    thread.run()

    assert any(level == "WARNING" for _, level in logs)


def test_show_fast_mode_info_calls_information(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    called = {}
    monkeypatch.setattr(
        cd.QMessageBox,
        "information",
        lambda *a, **k: called.setdefault("ok", True),
    )

    tab.show_fast_mode_info()

    assert called.get("ok") is True


def test_add_multiple_creators_to_queue_skips_blank_lines(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    tab.creator_multi_url_input.setPlainText("\nhttps://kemono.cr/fanbox/user/123\n")
    monkeypatch.setattr(cd, "get_domain_config", lambda url: {"domain": "kemono.cr"})

    tab.add_multiple_creators_to_queue()

    assert len(tab.creator_queue) == 1
    assert tab.creator_queue[0][0].endswith("/123")


def test_create_view_handler_calls_check_creator_from_queue(tmp_path):
    tab = make_tab(tmp_path)
    called = []
    tab.check_creator_from_queue = lambda url: called.append(url)
    handler = tab.create_view_handler("https://kemono.cr/fanbox/user/9", False)

    handler()

    assert called == ["https://kemono.cr/fanbox/user/9"]


def test_create_remove_handler_not_found_logs_warning(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    tab.creator_queue = [("https://kemono.cr/fanbox/user/1", False)]
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))
    monkeypatch.setattr(
        cd.QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes
    )

    handler = tab.create_remove_handler("https://kemono.cr/fanbox/user/2")
    handler()

    assert any(level == "WARNING" for _, level in logs)


def test_on_post_detection_finished_sets_map_and_detected_posts(tmp_path):
    tab = make_tab(tmp_path)
    tab.current_creator_url = "https://kemono.cr/fanbox/user/1"
    tab.all_files_map = {}
    tab.all_detected_posts = []
    started = []
    tab.start_population_thread = lambda posts: started.append(posts)
    detected_posts = [("Title", ("101", None))]

    tab.on_post_detection_finished(detected_posts)

    assert tab.all_files_map[tab.current_creator_url] == detected_posts
    assert tab.all_detected_posts == detected_posts
    assert started == [detected_posts]


def test_on_post_population_finished_fast_mode_triggers_auto_download(tmp_path):
    tab = make_tab(tmp_path)
    tab.current_creator_url = "https://kemono.cr/fanbox/user/1"
    tab.creator_queue = [(tab.current_creator_url, False)]
    tab._fast_mode_downloading = True
    tab.update_creator_queue_list = lambda: None
    tab.filter_items = lambda: None
    tab.set_fetching_ui_state = lambda enabled: None
    called = []
    tab._fast_mode_auto_download = lambda: called.append(True)

    tab.on_post_population_finished({}, [("Post", ("101", None))])

    assert called == [True]


def test_start_creator_download_no_queue_warns(tmp_path):
    tab = make_tab(tmp_path)
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.start_creator_download()

    assert any(level == "WARNING" for _, level in logs)


def test_update_background_progress_sets_progress_value(tmp_path):
    tab = make_tab(tmp_path)

    tab.update_background_progress(42)

    assert tab.background_task_progress.value() == 42


def test_on_file_preparation_finished_splits_query_from_service(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    tab.posts_to_download = ["101"]
    tab.total_posts_to_download = 1
    created = {}

    class FakeCreatorDownloadThread:
        def __init__(self, service, creator_id, *args, **kwargs):
            created["service"] = service
            created["creator_id"] = creator_id
            self.file_progress = DummySignal()
            self.file_completed = DummySignal()
            self.post_completed = DummySignal()
            self.log = DummySignal()
            self.finished = DummySignal()

        def start(self):
            created["started"] = True

    monkeypatch.setattr(cd, "CreatorDownloadThread", FakeCreatorDownloadThread)

    tab.on_file_preparation_finished(
        ["https://kemono.cr/fanbox?token=abc/user/42"],
        ["https://kemono.cr/files/a.jpg"],
        {"https://kemono.cr/files/a.jpg": "101"},
    )

    assert created["service"] == "fanbox"
    assert created["creator_id"] == "42"
    assert created["started"] is True


def test_cleanup_thread_transfers_non_dict_mapping(tmp_path):
    tab = make_tab(tmp_path)

    class FakeThread:
        failed_files = [("u1", "err1")]

        def isRunning(self):
            return False

        def wait(self, *_a, **_k):
            return None

        def deleteLater(self):
            return None

    tab.total_files_to_download = 5
    tab.completed_files = set()
    tab.failed_files = {}
    tab.creator_download_finished = lambda: None

    tab.cleanup_thread(FakeThread(), ["next"])

    assert tab.failed_files.get("u1") == "err1"


def test_cleanup_thread_ignores_first_transfer_exception(tmp_path):
    tab = make_tab(tmp_path)

    class FakeThread:
        failed_files = [("bad",)]

        def isRunning(self):
            return False

        def wait(self, *_a, **_k):
            return None

        def deleteLater(self):
            return None

    tab.total_files_to_download = 9
    tab.creator_download_finished = lambda: None

    # Should not raise despite invalid failed_files mapping.
    tab.cleanup_thread(FakeThread(), ["next"])


def test_cleanup_thread_active_thread_wait_and_runtime_delete(tmp_path):
    tab = make_tab(tmp_path)
    waited = []

    class FakeThread:
        failed_files = [("u2", "err2")]

        def isRunning(self):
            return True

        def wait(self, *_a, **_k):
            waited.append(True)

        def deleteLater(self):
            raise RuntimeError("already deleted")

    thread = FakeThread()
    tab.active_threads = [thread]
    tab.total_files_to_download = 7
    tab.failed_files = {}
    tab.creator_download_finished = lambda: None

    tab.cleanup_thread(thread, ["next"])

    assert waited
    assert tab.failed_files.get("u2") == "err2"


def test_cleanup_thread_runtime_during_lingering_termination_processes_next(tmp_path):
    tab = make_tab(tmp_path)

    class MainThread:
        failed_files = {"done": "err"}

        def isRunning(self):
            return False

        def wait(self, *_a, **_k):
            return None

        def deleteLater(self):
            return None

    class LingeringThread:
        def isRunning(self):
            return True

        def terminate(self):
            raise RuntimeError("boom")

        def wait(self, *_a, **_k):
            return None

        def deleteLater(self):
            return None

    main_thread = MainThread()
    tab.active_threads = [main_thread, LingeringThread()]
    tab.total_files_to_download = 1
    tab.completed_files = set()
    tab.failed_files = {}
    moved = []
    tab.process_next_creator = lambda urls: moved.append(urls)

    tab.cleanup_thread(main_thread, ["u2"])

    assert moved == [["u2"]]


def test_cleanup_thread_preserves_new_non_dict_failures(tmp_path):
    tab = make_tab(tmp_path)

    class FakeThread:
        failed_files = [("existing", "new-err"), ("new", "err")]

        def isRunning(self):
            return False

        def wait(self, *_a, **_k):
            return None

        def deleteLater(self):
            return None

    tab.total_files_to_download = 999
    tab.failed_files = {"existing": "old-err"}
    tab.creator_download_finished = lambda: None

    tab.cleanup_thread(FakeThread(), ["next"])

    assert tab.failed_files["existing"] == "new-err"
    assert tab.failed_files["new"] == "err"


def test_update_file_completion_all_attempted_and_reset_current_file(tmp_path):
    tab = make_tab(tmp_path)
    tab.total_files_to_download = 1
    tab.current_file_index = 0
    called = []
    tab.creator_download_finished = lambda: called.append(True)

    tab.update_file_completion(0, "https://kemono.cr/files/a.jpg", True)

    assert called == [True]
    assert tab.current_file_index == -1
    assert tab.creator_file_progress.value() == 0


def test_creator_download_finished_fast_mode_safety_removal(tmp_path):
    tab = make_tab(tmp_path)
    tab.fast_mode = True
    tab.current_creator_url = "https://kemono.cr/fanbox/user/1"
    removed = []
    states = []
    tab._fast_mode_remove_creator_url = lambda url: removed.append(url)
    tab.set_downloading_ui_state = lambda enabled: states.append(enabled)

    tab.creator_download_finished()

    assert removed == ["https://kemono.cr/fanbox/user/1"]
    assert states and states[-1] is False


def test_creator_download_finished_fast_mode_processes_next_and_returns(tmp_path):
    tab = make_tab(tmp_path)
    tab._fast_mode_downloading = True
    called = []
    tab._fast_mode_process_next = lambda: called.append(True)
    tab.set_downloading_ui_state = lambda enabled: called.append(False)

    tab.creator_download_finished()

    assert called == [True]


def test_expand_logs_creates_and_focuses_existing_window(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    events = []

    class FakeLogsWindow:
        def __init__(self, parent):
            self.parent = parent
            self._visible = False

        def isVisible(self):
            return self._visible

        def show(self):
            self._visible = True
            events.append("show")

        def raise_(self):
            events.append("raise")

        def activateWindow(self):
            events.append("activate")

        def update_logs_content(self):
            events.append("update")

    monkeypatch.setattr(cd, "LogsWindow", FakeLogsWindow)

    tab.expand_logs()
    tab.expand_logs()

    assert events == ["show", "raise", "activate", "update"]


def test_toggle_check_all_in_progress_logs_warning(tmp_path):
    tab = make_tab(tmp_path)
    tab.checkbox_toggle_thread = SimpleNamespace(isRunning=lambda: True)
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.toggle_check_all(2)

    assert any(level == "WARNING" for _, level in logs)


def test_filter_items_in_progress_logs_warning(tmp_path):
    tab = make_tab(tmp_path)
    tab.filter_thread = SimpleNamespace(isRunning=lambda: True)
    logs = []
    tab.append_log_to_console = lambda msg, level: logs.append((msg, level))

    tab.filter_items()

    assert any(level == "WARNING" for _, level in logs)


def test_update_checked_posts_adds_checked_ids_for_current_creator(tmp_path):
    tab = make_tab(tmp_path)
    tab.current_creator_url = "https://kemono.cr/fanbox/user/1"
    tab.all_files_map = {tab.current_creator_url: [("Post", ("101", None))]}
    tab.checked_urls = {"101": True, "202": True}

    tab.update_checked_posts()

    assert tab.posts_to_download == ["101"]


def test_on_filter_finished_resets_page_when_out_of_range(tmp_path):
    tab = make_tab(tmp_path)
    tab.current_page = 3
    tab.posts_per_page = 50
    tab.display_current_page = lambda: None
    tab.update_check_all_state = lambda: None
    tab.update_checked_posts = lambda: None

    tab.on_filter_finished([])

    assert tab.current_page == 1


def test_toggle_checkbox_state_single_item_path_uses_cached_widget(tmp_path):
    tab = make_tab(tmp_path)
    tab.current_creator_url = "https://kemono.cr/fanbox/user/1"
    tab.all_files_map = {tab.current_creator_url: [("Post A", ("101", None))]}
    tab.checked_urls = {"101": False}
    tab.post_url_map["Post A"] = ("101", None)
    tab.add_list_item("Post A", None, False)

    tab.toggle_checkbox_state("Post A")

    assert tab.checked_urls["101"] is True


def test_get_widget_for_post_title_cached_and_missing(tmp_path):
    tab = make_tab(tmp_path)
    tab.post_url_map["Post A"] = ("101", None)
    tab.add_list_item("Post A", None, False)

    assert tab.get_widget_for_post_title("Post A") is not None
    assert tab.get_widget_for_post_title("Missing") is None


def test_view_current_item_image_opens_modal(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    tab.current_preview_url = "https://example.com/a.jpg"
    called = []

    class FakeImageModal:
        def __init__(self, url, cache_dir, parent):
            called.append((url, cache_dir, parent))

        def exec(self):
            called.append("exec")

    monkeypatch.setattr(cd, "ImageModal", FakeImageModal)

    tab.view_current_item()

    assert called and called[-1] == "exec"


def test_on_selection_changed_ignores_runtimeerror_from_stale_widget(tmp_path):
    tab = make_tab(tmp_path)

    class BadWidget:
        def setStyleSheet(self, _style):
            raise RuntimeError("deleted")

    tab.previous_selected_widgets = [BadWidget()]

    tab.on_selection_changed()

    assert isinstance(tab.previous_selected_widgets, list)


def test_add_creators_from_file_skips_empty_lines(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    links = tmp_path / "links_empty.txt"
    links.write_text("\nhttps://kemono.cr/fanbox/user/77\n")
    monkeypatch.setattr(
        cd.QFileDialog, "getOpenFileName", lambda *a, **k: (str(links), "")
    )
    monkeypatch.setattr(cd, "get_domain_config", lambda url: {"domain": "kemono.cr"})
    monkeypatch.setattr(cd.QMessageBox, "information", lambda *a, **k: None)

    tab.add_creators_from_file()

    assert any(u.endswith("/77") for u, _ in tab.creator_queue)


def test_cancellation_thread_stop_sets_flag_and_run_returns_early():
    thread = cd.CancellationThread([])
    emitted = []
    thread.log = SimpleNamespace(emit=lambda *a, **k: emitted.append(True))

    thread.stop()
    thread.run()

    assert thread.is_running is False
    assert emitted == []


def test_cancellation_thread_outer_runtimeerror_logs_warning():
    class FlakyThread:
        def __init__(self):
            self.calls = 0

        def isRunning(self):
            self.calls += 1
            if self.calls == 1:
                return False
            raise RuntimeError("deleted")

    thread = cd.CancellationThread([FlakyThread()])
    logs = []
    thread.log = SimpleNamespace(emit=lambda msg, level: logs.append((msg, level)))
    thread.finished = SimpleNamespace(emit=lambda: None)

    thread.run()

    assert any(level == "WARNING" for _, level in logs)


def test_add_multiple_creators_to_queue_internal_blank_line(tmp_path, monkeypatch):
    tab = make_tab(tmp_path)
    tab.creator_multi_url_input.setPlainText(
        "https://kemono.cr/fanbox/user/11\n\nhttps://kemono.cr/fanbox/user/22"
    )
    monkeypatch.setattr(cd, "get_domain_config", lambda url: {"domain": "kemono.cr"})

    tab.add_multiple_creators_to_queue()

    assert len(tab.creator_queue) == 2


def test_cleanup_thread_outer_failed_files_exception_is_ignored(tmp_path):
    tab = make_tab(tmp_path)

    class BadFailedFilesThread:
        @property
        def failed_files(self):
            raise RuntimeError("missing")

        def isRunning(self):
            return False

        def wait(self, *_a, **_k):
            return None

        def deleteLater(self):
            return None

    tab.total_files_to_download = 3
    tab.creator_download_finished = lambda: None

    tab.cleanup_thread(BadFailedFilesThread(), ["next"])


def test_cleanup_thread_second_transfer_inner_exception_is_ignored(tmp_path):
    tab = make_tab(tmp_path)

    class BadMappingThread:
        failed_files = [("broken",)]

        def isRunning(self):
            return False

        def wait(self, *_a, **_k):
            return None

        def deleteLater(self):
            return None

    thread = BadMappingThread()
    tab.active_threads = [thread]
    tab.total_files_to_download = 10
    tab.creator_download_finished = lambda: None

    tab.cleanup_thread(thread, ["next"])


def test_cleanup_thread_second_transfer_outer_exception_is_ignored(tmp_path):
    tab = make_tab(tmp_path)

    class FlakyFailedFilesThread:
        def __init__(self):
            self._accesses = 0

        @property
        def failed_files(self):
            self._accesses += 1
            if self._accesses == 2:
                raise RuntimeError("deleted")
            return [("u", "e")]

        def isRunning(self):
            return False

        def wait(self, *_a, **_k):
            return None

        def deleteLater(self):
            return None

    thread = FlakyFailedFilesThread()
    tab.active_threads = [thread]
    tab.total_files_to_download = 10
    tab.creator_download_finished = lambda: None

    tab.cleanup_thread(thread, ["next"])
