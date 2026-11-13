"""The full-logs window's live mirroring of a tab's console."""

import pytest
from PyQt6.QtWidgets import QApplication, QTextEdit, QWidget

from kemonodownloader import creator_downloader as cd, post_downloader as pd
from kemonodownloader.kd_language import translate
from kemonodownloader.kd_logs import counted, format_log_line


def _console(lines=300, width=320):
    console = QTextEdit()
    console.setReadOnly(True)
    console.resize(width, 200)
    for i in range(lines):
        console.append(format_log_line(f"line {i} " + "word " * 12))
    return console


def _settle(qapp):
    for _ in range(3):
        qapp.processEvents()


@pytest.fixture
def live(qapp):
    console = _console()
    console.show()
    window = pd.LogsWindow(console)
    window.show()
    _settle(qapp)
    yield console, window
    window.close()
    window.deleteLater()
    console.deleteLater()
    _settle(qapp)


def _append(qapp, console, window, count, text="new"):
    for i in range(count):
        console.append(format_log_line(f"{text} {i}", "WARNING"))
    _settle(qapp)
    window.refresh_now()
    _settle(qapp)


def test_window_opens_at_the_newest_line(live):
    console, window = live
    bar = window.logs_display.verticalScrollBar()
    assert bar.maximum() > 0
    assert bar.value() == bar.maximum()
    assert window.is_following()
    assert not window.jump_btn.isVisible()
    assert window.logs_display.toPlainText() == console.toPlainText()


def test_new_lines_keep_a_reader_who_scrolled_up_in_place(qapp, live):
    console, window = live
    bar = window.logs_display.verticalScrollBar()
    bar.setValue(bar.maximum() // 3)
    _settle(qapp)
    held = bar.value()
    assert not window.is_following()

    for round_ in range(4):
        # The tab's console re-wraps as the main window lays out; that used to
        # move the shared text under the reader.
        console.resize(320 + 40 * (round_ % 2), 200)
        _append(qapp, console, window, 25, f"burst {round_}")

    assert bar.value() == held
    assert window.jump_btn.isVisible()
    assert window.jump_btn.text() == counted("logs_new_lines", 100)
    assert window.logs_display.toPlainText() == console.toPlainText()


def test_new_lines_scroll_into_view_while_following(qapp, live):
    console, window = live
    _append(qapp, console, window, 30)
    bar = window.logs_display.verticalScrollBar()
    assert bar.value() == bar.maximum()
    assert window.logs_display.toPlainText().splitlines()[-1] == "new 29"


def test_jump_to_latest_resumes_following(qapp, live):
    console, window = live
    bar = window.logs_display.verticalScrollBar()
    bar.setValue(0)
    _append(qapp, console, window, 3)
    assert bar.value() == 0

    window.jump_btn.click()
    _append(qapp, console, window, 3, "after jump")
    assert window.is_following()
    assert bar.value() == bar.maximum()
    assert not window.jump_btn.isVisible()


def test_scrolling_back_to_the_bottom_resumes_following(qapp, live):
    _console_, window = live
    bar = window.logs_display.verticalScrollBar()
    bar.setValue(0)
    _settle(qapp)
    assert not window.is_following()
    bar.setValue(bar.maximum())
    _settle(qapp)
    assert window.is_following()


def test_reader_cursor_and_selection_survive_new_lines(qapp, live):
    console, window = live
    cursor = window.logs_display.textCursor()
    cursor.setPosition(5)
    cursor.setPosition(9, cursor.MoveMode.KeepAnchor)
    window.logs_display.setTextCursor(cursor)
    _append(qapp, console, window, 5)
    assert window.logs_display.textCursor().selectedText() == "0 wo"


def test_console_clear_rebuilds_the_copy(qapp, live):
    console, window = live
    console.clear()
    _settle(qapp)
    window.refresh_now()
    assert window.logs_display.toPlainText() == ""
    assert window.line_count_label.text() == counted("logs_line_count", 0)

    _append(qapp, console, window, 1, "fresh")
    assert window.logs_display.toPlainText() == "fresh 0"
    assert window.line_count_label.text() == counted("logs_line_count", 1)


def test_console_edits_schedule_a_refresh(qapp, live):
    console, window = live
    window.update_timer.stop()
    window.needs_update = False
    console.append("scheduled")
    assert window.needs_update
    assert window.update_timer.isActive()
    window._do_update()
    assert window.logs_display.toPlainText().endswith("scheduled")
    # A tick with nothing new stops the timer instead of idling.
    window._do_update()
    assert not window.update_timer.isActive()


def test_line_count_label(live):
    _console_, window = live
    assert window.line_count_label.text() == counted("logs_line_count", 300)


def test_search_highlights_and_wraps(qapp, live):
    console, window = live
    console.append("needle one")
    console.append("needle two")
    _settle(qapp)
    window.refresh_now()

    window.search_input.setText("needle")
    assert window.match_label.text() == counted("logs_match_count", 2)
    assert len(window.logs_display.extraSelections()) == 2
    first = window.logs_display.textCursor().blockNumber()
    assert window.find_in_logs()
    second = window.logs_display.textCursor().blockNumber()
    assert second == first + 1
    assert window.find_in_logs()  # wraps back to the first match
    assert window.logs_display.textCursor().blockNumber() == first
    assert window.find_in_logs(backward=True)
    assert window.logs_display.textCursor().blockNumber() == second

    window.search_input.setText("absent")
    assert window.match_label.text() == translate("logs_no_matches")
    assert window.match_label.property("kdTone") == "error"
    assert not window.find_in_logs()

    window.search_input.clear()
    assert window.match_label.text() == ""
    assert window.logs_display.extraSelections() == []


def test_copy_logs_puts_plain_text_on_the_clipboard(qapp, live):
    console, window = live
    window.copy_logs()
    assert QApplication.clipboard().text() == console.toPlainText()


def test_copy_logs_ignores_an_empty_log(qapp):
    window = pd.LogsWindow(QTextEdit())
    try:
        QApplication.clipboard().setText("untouched")
        window.copy_logs()
        assert QApplication.clipboard().text() == "untouched"
    finally:
        window.deleteLater()


def test_close_disconnects_from_the_console(qapp, live):
    console, window = live
    window.close()
    window.needs_update = False
    console.append("after close")
    assert not window.needs_update


def test_counted_uses_the_singular_form():
    assert counted("logs_line_count", 1) == translate("logs_line_count_one")
    assert counted("logs_line_count", 1234) == translate("logs_line_count", "1,234")


def test_log_colours_are_readable_hex_values():
    assert "color:#6FD08C" in format_log_line("ok")
    assert "color:#F5C451" in format_log_line("careful", "WARNING")
    assert "color:#E6EDF7" in format_log_line("plain", "DEBUG")


def test_creator_window_follows_the_creator_console(qapp):
    console = _console(lines=20)
    tab = QWidget()
    tab.creator_console = console
    window = cd.LogsWindow(tab)
    try:
        assert window.logs_display.toPlainText() == console.toPlainText()
        console.append("creator line")
        window.refresh_now()
        assert window.logs_display.toPlainText().endswith("creator line")
    finally:
        tab.deleteLater()
        console.deleteLater()


def test_logs_follow_the_font_chosen_in_settings(qapp):
    from PyQt6.QtGui import QFont

    console = _console(lines=3)
    window = pd.LogsWindow(console)
    try:
        # The app applies the Settings font to every widget, this view too.
        window.logs_display.setFont(QFont("Poppins", 11))
        console.clear()  # forces a full rebuild of the window's copy
        console.append("after the font change")
        window.refresh_now()
        assert window.logs_display.document().defaultFont().family() == "Poppins"
    finally:
        window.deleteLater()
        console.deleteLater()


def test_copied_label_timer_dies_with_the_window(qapp, live):
    console, window = live
    window.copy_logs()
    assert window.copy_logs_btn.text() == translate("logs_copied")
    timer = window._copied_timer
    assert timer.isActive() and timer.parent() is window
    window._copied_timer.timeout.emit()
    assert window.copy_logs_btn.text() == translate("copy_logs")
    window.copy_logs()
    window.close()
    assert not window._copied_timer.isActive()


def test_rebuilt_copies_belong_to_qt_alone(qapp):
    import gc

    from PyQt6 import sip

    console = _console(lines=5)
    window = pd.LogsWindow(console)
    try:
        for round_ in range(20):
            # Each clear forces a new copy; the old one used to be freed by
            # both Qt and Python, which crashed the app later on.
            console.clear()
            console.append(f"round {round_}")
            window.refresh_now()
            gc.collect()
            qapp.processEvents()
            assert not sip.ispyowned(window.logs_display.document())
        assert window.logs_display.toPlainText() == "round 19"
    finally:
        window.deleteLater()
        console.deleteLater()
