"""Section notes, the Help guide and the Browser Extension tab."""

import re
from html.parser import HTMLParser
from types import SimpleNamespace

import pytest
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QApplication,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from kemonodownloader import kd_extension, kd_help, kd_notes
from kemonodownloader.kd_language import language_manager
from kemonodownloader.kd_notes import (
    NOTE_KEY_PROPERTY,
    NoteLabel,
    add_note,
    retranslate_notes,
    section_note,
    with_note,
)


class _Signal:
    def connect(self, _slot):
        pass


def _parent():
    settings = SimpleNamespace(
        language_changed=_Signal(),
        font_changed=_Signal(),
        get_font=lambda: "JetBrains Mono",
    )
    return SimpleNamespace(settings_tab=settings)


# ------------------------------------------------------------------ notes --


def test_note_labels_remember_their_key_and_retranslate(qapp, monkeypatch):
    host = QWidget()
    layout = QVBoxLayout(host)
    note = add_note(layout, "note_history")
    assert layout.itemAt(0).widget() is note
    assert note.property(NOTE_KEY_PROPERTY) == "note_history"
    assert note.property("kdRole") == "note"
    assert note.wordWrap()

    monkeypatch.setattr(kd_notes, "translate", lambda key, *a: f"<{key}>")
    retranslate_notes(host)
    assert note.text() == "<note_history>"
    host.deleteLater()


def test_with_note_puts_the_note_above_the_grid(qapp):
    from PyQt6.QtWidgets import QGridLayout

    grid = QGridLayout()
    column = with_note(grid, "note_folder_settings")
    assert isinstance(column.itemAt(0).widget(), NoteLabel)
    assert column.itemAt(1).layout() is grid


def test_note_height_follows_its_real_width(qapp):
    host = QWidget()
    layout = QVBoxLayout(host)
    note = section_note("note_folder_settings")
    layout.addWidget(note)
    host.resize(900, 300)
    host.show()
    qapp.processEvents()
    wide = note.minimumSizeHint().height()
    host.resize(300, 300)
    qapp.processEvents()
    narrow = note.minimumSizeHint().height()
    assert narrow > wide
    assert note.sizeHint() == QSize(note.sizeHint().width(), narrow)
    host.deleteLater()


def test_every_settings_section_has_a_note(qapp):
    from kemonodownloader.kd_settings import SettingsTab

    tab = SettingsTab(SimpleNamespace(log=lambda m: None))
    try:
        groups = [
            tab.folder_group,
            tab.download_group,
            tab.retry_group,
            tab.creator_custom_group,
            tab.update_group,
            tab.language_group,
            tab.font_group,
        ]
        for group in groups:
            keys = [
                label.property(NOTE_KEY_PROPERTY)
                for label in group.findChildren(QLabel)
                if label.property(NOTE_KEY_PROPERTY)
            ]
            assert len(keys) == 1, group.title()
        assert tab.proxy_intro_label.property("kdRole") == "note"
    finally:
        tab.deleteLater()


def test_note_keys_in_the_tabs_are_all_translated():
    from pathlib import Path

    source = Path(kd_notes.__file__).parent
    keys = set()
    for path in source.glob("*.py"):
        keys |= set(
            re.findall(
                r'(?:section_note|add_note|with_note)\([^"]*"([a-z_]+)"\)',
                path.read_text(encoding="utf-8"),
            )
        )
    defined = {k for k in language_manager.translations if k.startswith("note_")}
    assert keys == defined  # every note is shown somewhere, and translated
    for key in keys:
        entry = language_manager.translations[key]
        assert all(entry[lang] for lang in language_manager.get_available_languages())


def test_no_unrenderable_info_symbol_in_texts():
    for key, entry in language_manager.translations.items():
        for text in entry.values():
            assert "ⓘ" not in text, key


# ------------------------------------------------------------------- help --


class _TagChecker(HTMLParser):
    VOID = {"br"}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> after {self.stack}")
        else:
            self.stack.pop()


@pytest.mark.parametrize("_title_key, body_key", kd_help.HELP_SECTIONS)
def test_guide_topics_are_balanced_html_in_every_language(_title_key, body_key):
    for language in language_manager.get_available_languages():
        checker = _TagChecker()
        checker.feed(language_manager.get_text(body_key, language))
        assert not checker.errors and not checker.stack, (body_key, language)


def test_guide_links_point_to_the_project():
    for _title, body in kd_help.HELP_SECTIONS:
        for language in language_manager.get_available_languages():
            text = language_manager.get_text(body, language)
            for url in re.findall(r"href='([^']+)'", text):
                assert url.startswith("https://github.com/VoxDroid/KemonoDownloader")


@pytest.fixture
def help_tab(qapp):
    tab = kd_help.HelpTab(_parent())
    tab.resize(1100, 700)
    tab.show()
    qapp.processEvents()
    yield tab
    tab.deleteLater()
    qapp.processEvents()


def test_help_lists_every_topic_and_opens_the_first(help_tab):
    assert help_tab.nav_list.count() == len(kd_help.HELP_SECTIONS)
    assert help_tab.current_section() == "guide_start_title"
    assert help_tab.section_title.text() == language_manager.get_text(
        "guide_start_title"
    )
    assert not help_tab.prev_button.isEnabled()
    assert help_tab.next_button.isEnabled()


def test_help_previous_and_next_walk_the_topics(help_tab):
    help_tab.next_button.click()
    assert help_tab.current_section() == "guide_post_title"
    help_tab.prev_button.click()
    assert help_tab.current_section() == "guide_start_title"
    help_tab.nav_list.setCurrentRow(len(kd_help.HELP_SECTIONS) - 1)
    assert not help_tab.next_button.isEnabled()


def test_help_search_filters_topics_and_highlights(help_tab):
    help_tab.search_input.setText("socks5h")
    visible = [
        help_tab.nav_list.item(row).data(256)
        for row in range(help_tab.nav_list.count())
        if not help_tab.nav_list.item(row).isHidden()
    ]
    assert visible == ["guide_proxy_title"]
    assert help_tab.current_section() == "guide_proxy_title"
    assert help_tab.manual.extraSelections()
    assert help_tab.no_results_label.isHidden()

    help_tab.search_input.setText("zzzz-no-such-text")
    assert not help_tab.no_results_label.isHidden()
    assert not help_tab.prev_button.isEnabled()

    help_tab.search_input.clear()
    assert all(
        not help_tab.nav_list.item(row).isHidden()
        for row in range(help_tab.nav_list.count())
    )
    assert help_tab.manual.extraSelections() == []


def test_help_retranslates(help_tab, monkeypatch):
    monkeypatch.setattr(kd_help, "translate", lambda key, *a: f"<{key}>")
    help_tab.update_ui_text()
    assert help_tab.title_label.text() == "<help_title>"
    assert help_tab.nav_list.item(0).text() == "<guide_start_title>"
    assert help_tab.next_button.text() == "<help_next>"


# -------------------------------------------------------------- extension --


@pytest.fixture
def extension_tab(qapp, monkeypatch):
    opened = []
    monkeypatch.setattr(
        kd_extension.QDesktopServices, "openUrl", lambda url: opened.append(url)
    )
    tab = kd_extension.ExtensionTab(_parent())
    tab.opened = opened
    yield tab
    tab.deleteLater()
    qapp.processEvents()


def test_extension_buttons_open_the_release_page_and_folder(extension_tab):
    extension_tab.releases_button.click()
    extension_tab.folder_button.click()
    urls = [url.toString() for url in extension_tab.opened]
    assert urls == [kd_extension.RELEASES_URL, kd_extension.EXTENSION_FOLDER_URL]


def test_extension_copy_buttons_copy_their_command(extension_tab):
    button = extension_tab.copy_buttons[1]
    button.click()
    assert QApplication.clipboard().text() == kd_extension.MANIFEST_COMMANDS[1][1]
    assert button.text() == language_manager.get_text("ext_copied")
    timer = extension_tab._copied_timer
    assert timer.isActive() and timer.parent() is extension_tab
    timer.timeout.emit()
    assert button.text() == language_manager.get_text("ext_copy_command")


def test_extension_shows_every_feature_and_step(extension_tab):
    assert len(extension_tab.feature_labels) == len(kd_extension.FEATURES)
    for title, text, _title_key, _text_key in extension_tab.feature_labels:
        assert title.text() and text.text()
    for label in (
        extension_tab.step_get_text,
        extension_tab.step_manifest_text,
        extension_tab.step_chrome_text,
        extension_tab.step_firefox_text,
        extension_tab.use_text,
        extension_tab.trouble_text,
    ):
        assert label.text()


# ----------------------------------------------------------------- window --


def test_window_size_is_restored_after_the_intro(qapp):
    from kemonodownloader.app import KemonoDownloader

    class Fake:
        def __init__(self):
            self.resized = None

        def isMaximized(self):  # noqa: N802
            return False

        def isFullScreen(self):  # noqa: N802
            return False

        def minimumSizeHint(self):  # noqa: N802
            return QSize(800, 705)

        def resize(self, w, h):
            self.resized = (w, h)

    fake = Fake()
    KemonoDownloader._restore_size(fake, QSize(1000, 700))
    assert fake.resized == (1000, 705)

    fake.isMaximized = lambda: True
    fake.resized = None
    KemonoDownloader._restore_size(fake, QSize(1000, 700))
    assert fake.resized is None


def test_groups_keep_working_with_notes(qapp):
    group = QGroupBox()
    inner = QVBoxLayout()
    inner.addWidget(QPushButton("x"))
    group.setLayout(with_note(inner, "note_post_queue"))
    assert group.findChildren(NoteLabel)
    group.deleteLater()
