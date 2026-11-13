"""History tab: past downloads and saved favorites."""

from __future__ import annotations

import csv
import datetime
import os
from typing import Callable, List, Optional, Tuple

import qtawesome as qta
from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    QSortFilterProxyModel,
    Qt,
    QTimer,
    QUrl,
)
from PyQt6.QtGui import QAction, QColor, QDesktopServices, QKeySequence
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QStackedLayout,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from kemonodownloader.history_store import (
    KIND_CREATOR,
    KIND_POST,
    KIND_THUMBNAIL,
    QUEUE_ADDED,
    QUEUE_BUSY,
    QUEUE_DUPLICATE,
    QUEUE_MODE_MISMATCH,
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PARTIAL,
    Favorite,
    HistoryEntry,
    HistoryStore,
    link_kind,
    normalize_link,
)
from kemonodownloader.kd_language import translate
from kemonodownloader.kd_notes import add_note, retranslate_notes, tip, tips
from kemonodownloader.kd_theme import set_role, set_tone

SORT_ROLE = Qt.ItemDataRole.UserRole + 1

_KIND_KEYS = {
    KIND_POST: "history_type_post",
    KIND_CREATOR: "history_type_creator",
    KIND_THUMBNAIL: "history_type_thumbnail",
}
_STATUS_KEYS = {
    STATUS_COMPLETED: "history_status_completed",
    STATUS_PARTIAL: "history_status_partial",
    STATUS_FAILED: "history_status_failed",
    STATUS_CANCELLED: "history_status_cancelled",
}
_STATUS_COLORS = {
    STATUS_COMPLETED: "#7CD992",
    STATUS_PARTIAL: "#E8C468",
    STATUS_FAILED: "#FF7B7B",
    STATUS_CANCELLED: "#B0B8C8",
}
_MISSING_COLOR = "#FF7B7B"


def format_size(size: Optional[int]) -> str:
    if size is None:
        return "—"
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"  # pragma: no cover - loop always returns


def format_duration(seconds: Optional[float]) -> str:
    if seconds is None:
        return "—"
    seconds = int(round(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def format_time(timestamp: Optional[float]) -> str:
    if not timestamp:
        return "—"
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


def nearest_existing_folder(path: str) -> Optional[str]:
    """Walk up from *path* to the closest folder that still exists."""
    current = os.path.abspath(path) if path else ""
    while current:
        if os.path.isdir(current):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent
    return None


class HistoryModel(QAbstractTableModel):
    COLUMNS = (
        "history_col_date",
        "history_col_type",
        "history_col_title",
        "history_col_files",
        "history_col_posts",
        "history_col_size",
        "history_col_duration",
        "history_col_status",
        "history_col_folder",
        "history_col_link",
    )
    (DATE, TYPE, TITLE, FILES, POSTS, SIZE, DURATION, STATUS, FOLDER, LINK) = range(10)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.entries: List[HistoryEntry] = []
        self._folder_exists: dict = {}

    def set_entries(self, entries: List[HistoryEntry]) -> None:
        self.beginResetModel()
        self.entries = entries
        self._folder_exists = {}
        self.endResetModel()

    def folder_exists(self, entry: HistoryEntry) -> Optional[bool]:
        """Cached per refresh; only rows that are actually drawn are checked."""
        if not entry.folder:
            return None
        if entry.id not in self._folder_exists:
            self._folder_exists[entry.id] = os.path.isdir(entry.folder)
        return self._folder_exists[entry.id]

    def rowCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.entries)

    def columnCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(
        self, section, orientation, role=Qt.ItemDataRole.DisplayRole
    ):  # noqa: N802
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return translate(self.COLUMNS[section])
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        entry = self.entries[index.row()]
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._display(entry, column)
        if role == SORT_ROLE:
            return self._sort_key(entry, column)
        if role == Qt.ItemDataRole.ToolTipRole:
            if column == self.FOLDER:
                return entry.folder or translate("history_no_folder")
            if column == self.LINK:
                return "\n".join(entry.links)
            if column == self.TITLE:
                return entry.title
            if column == self.FILES and (
                entry.files_preview_only or entry.files_missing
            ):
                return translate(
                    "history_files_tooltip",
                    entry.files_done,
                    entry.files_total,
                    entry.files_preview_only,
                    entry.files_missing,
                )
        if role == Qt.ItemDataRole.ForegroundRole:
            if column == self.STATUS:
                return QColor(_STATUS_COLORS.get(entry.status, "white"))
            if column == self.FOLDER and self.folder_exists(entry) is False:
                return QColor(_MISSING_COLOR)
        if role == Qt.ItemDataRole.TextAlignmentRole and column in (
            self.FILES,
            self.POSTS,
            self.SIZE,
            self.DURATION,
        ):
            return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return None

    def _display(self, entry: HistoryEntry, column: int):
        if column == self.DATE:
            return format_time(entry.finished_at)
        if column == self.TYPE:
            return translate(_KIND_KEYS.get(entry.kind, "history_type_post"))
        if column == self.TITLE:
            return entry.title or entry.url
        if column == self.FILES:
            text = f"{entry.files_done}/{entry.files_total}"
            return f"{text} (−{entry.files_failed})" if entry.files_failed else text
        if column == self.POSTS:
            return f"{entry.posts_done}/{entry.posts_total}"
        if column == self.SIZE:
            return format_size(entry.size_bytes)
        if column == self.DURATION:
            return format_duration(entry.duration)
        if column == self.STATUS:
            return translate(_STATUS_KEYS.get(entry.status, "history_status_failed"))
        if column == self.FOLDER:
            exists = self.folder_exists(entry)
            if exists is None:
                return translate("history_folder_unknown")
            return translate(
                "history_folder_ok" if exists else "history_folder_missing"
            )
        if column == self.LINK:
            extra = len(entry.links) - 1
            return f"{entry.url} (+{extra})" if extra else entry.url
        return None

    def _sort_key(self, entry: HistoryEntry, column: int):
        keys = {
            self.DATE: entry.finished_at or 0,
            self.FILES: entry.files_done,
            self.POSTS: entry.posts_done,
            self.SIZE: entry.size_bytes if entry.size_bytes is not None else -1,
            self.DURATION: entry.duration if entry.duration is not None else -1,
        }
        if column in keys:
            return keys[column]
        return str(self._display(entry, column) or "").lower()


class FavoritesModel(QAbstractTableModel):
    COLUMNS = (
        "favorites_col_title",
        "history_col_type",
        "history_col_link",
        "favorites_col_note",
        "favorites_col_added",
        "favorites_col_last_download",
    )
    (TITLE, TYPE, LINK, NOTE, ADDED, LAST) = range(6)
    EDITABLE = (TITLE, NOTE)

    def __init__(self, store: HistoryStore, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.favorites: List[Favorite] = []
        self.last_downloaded: dict = {}

    def set_favorites(self, favorites: List[Favorite], last_downloaded: dict) -> None:
        self.beginResetModel()
        self.favorites = favorites
        self.last_downloaded = last_downloaded
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.favorites)

    def columnCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(
        self, section, orientation, role=Qt.ItemDataRole.DisplayRole
    ):  # noqa: N802
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return translate(self.COLUMNS[section])
        return None

    def flags(self, index):
        flags = super().flags(index)
        if index.isValid() and index.column() in self.EDITABLE:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        favorite = self.favorites[index.row()]
        column = index.column()
        if role == Qt.ItemDataRole.EditRole:
            if column == self.TITLE:
                return favorite.title
            if column == self.NOTE:
                return favorite.note
        if role in (Qt.ItemDataRole.DisplayRole, SORT_ROLE):
            last = self.last_downloaded.get(favorite.url)
            if role == SORT_ROLE and column == self.ADDED:
                return favorite.added_at
            if role == SORT_ROLE and column == self.LAST:
                return last or 0
            values = {
                self.TITLE: favorite.title or favorite.url,
                self.TYPE: translate(
                    _KIND_KEYS.get(favorite.kind, "history_type_post")
                ),
                self.LINK: favorite.url,
                self.NOTE: favorite.note,
                self.ADDED: format_time(favorite.added_at),
                self.LAST: format_time(last) if last else translate("favorites_never"),
            }
            value = values.get(column)
            return value.lower() if role == SORT_ROLE else value
        if role == Qt.ItemDataRole.ToolTipRole and column in (self.LINK, self.TITLE):
            return favorite.url
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):  # noqa: N802
        if role != Qt.ItemDataRole.EditRole or index.column() not in self.EDITABLE:
            return False
        favorite = self.favorites[index.row()]
        text = str(value).strip()
        if index.column() == self.TITLE:
            favorite.title = text
            self.store.update_favorite(favorite.id, title=text)
        else:
            favorite.note = text
            self.store.update_favorite(favorite.id, note=text)
        self.dataChanged.emit(index, index)
        return True


class LibraryFilter(QSortFilterProxyModel):
    """Filters rows by type and by text across their visible columns."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.kind: Optional[str] = None
        self.text = ""
        self.setSortRole(SORT_ROLE)

    def set_kind(self, kind: Optional[str]) -> None:
        self.kind = kind
        self.invalidateFilter()

    def set_text(self, text: str) -> None:
        self.text = text.strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent) -> bool:  # noqa: N802
        model = self.sourceModel()
        item = (
            model.entries[row]
            if isinstance(model, HistoryModel)
            else model.favorites[row]
        )
        if self.kind and item.kind != self.kind:
            return False
        if not self.text:
            return True
        haystack = [item.url, item.title]
        if isinstance(item, HistoryEntry):
            haystack += [item.creator, item.service, item.folder] + item.extra_urls
        else:
            haystack.append(item.note)
        return any(self.text in (value or "").lower() for value in haystack)


def _make_table(model, proxy) -> QTableView:
    proxy.setSourceModel(model)
    table = QTableView()
    table.setModel(proxy)
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(True)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    table.setWordWrap(False)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(30)
    header = table.horizontalHeader()
    header.setHighlightSections(False)
    header.setStretchLastSection(True)
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    return table


def _size_columns(table: QTableView, widths: dict, stretch: Tuple[int, ...]) -> None:
    """Fixed starting widths; the *stretch* columns share the room left.

    Fixed widths rather than fit-to-contents, which would measure every row.
    """
    header = table.horizontalHeader()
    header.setStretchLastSection(False)
    for column, width in widths.items():
        header.resizeSection(column, width)
    for column in stretch:
        header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
    header.setMinimumSectionSize(50)


def _button(icon: str, handler: Callable) -> QPushButton:
    button = QPushButton(qta.icon(icon, color="white"), "")
    button.clicked.connect(handler)
    return button


class HistoryTab(QWidget):
    POLL_MS = 800

    def __init__(self, window) -> None:
        super().__init__()
        # Not `self.parent`: that would hide QObject.parent().
        self.window_ref = window
        self.store: HistoryStore = window.history_store
        self._seen_revision = -1

        # Folder sizes are filled in by a background thread; pick them up
        # while the tab is on screen.
        self._poll = QTimer(self)
        self._poll.setInterval(self.POLL_MS)
        self._poll.timeout.connect(self._refresh_if_changed)
        self._status_clear = QTimer(self)
        self._status_clear.setSingleShot(True)
        self._status_clear.setInterval(5000)

        self.setup_ui()
        # Tooltips, for when a section's note isn't enough.
        tip(self.history_search, "tip_history_search")
        tip(self.kind_filter, "tip_history_kind")
        tip(self.record_check, "tip_history_record")
        tip(self.open_folder_btn, "tip_history_open_folder")
        tips((self.copy_history_btn, self.copy_favorite_btn), "tip_history_copy")
        tips((self.queue_history_btn, self.queue_favorite_btn), "tip_history_queue")
        tip(self.favorite_history_btn, "tip_history_favorite")
        tip(self.export_history_btn, "tip_history_export")
        tips((self.remove_history_btn, self.remove_favorite_btn), "tip_history_remove")
        tip(self.clear_history_btn, "tip_history_clear")
        tip(self.favorite_input, "tip_favorite_input")
        tip(self.favorite_add_btn, "tip_favorite_save")
        tip(self.favorites_search, "tip_favorites_search")
        tip(self.browser_favorite_btn, "tip_favorites_open")
        tip(self.import_favorites_btn, "tip_favorites_import")
        tip(self.export_favorites_btn, "tip_favorites_export")
        self.update_ui_text()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        self.storage_warning = QLabel()
        self.storage_warning.setWordWrap(True)
        set_role(self.storage_warning, "notice")
        self.storage_warning.setVisible(False)
        layout.addWidget(self.storage_warning)

        self.views = QTabWidget()
        self.views.setDocumentMode(True)
        self.views.addTab(
            self._build_history_page(), qta.icon("fa5s.history", color="white"), ""
        )
        self.views.addTab(
            self._build_favorites_page(), qta.icon("fa5s.star", color="white"), ""
        )
        layout.addWidget(self.views, stretch=1)
        # Adopt the models only now, after the views: Qt destroys children in
        # the order they were added, so the tables go first. Models destroyed
        # before their tables make the tables call back into half-destroyed
        # Python objects, which crashes natively.
        models: Tuple[QObject, ...] = (
            self.history_proxy,
            self.history_model,
            self.favorites_proxy,
            self.favorites_model,
        )
        for model in models:
            model.setParent(self)

        self.status_label = QLabel()
        set_tone(self.status_label, "info")
        layout.addWidget(self.status_label)
        # A Qt slot, not a Python lambda: nothing to call back into Python.
        self._status_clear.timeout.connect(self.status_label.clear)

    def _build_history_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        add_note(layout, "note_history")

        toolbar = QHBoxLayout()
        self.history_search = QLineEdit()
        self.history_search.setClearButtonEnabled(True)
        toolbar.addWidget(self.history_search, stretch=1)
        self.kind_filter = QComboBox()
        toolbar.addWidget(self.kind_filter)
        self.record_check = QCheckBox()
        self.record_check.setChecked(self.store.recording_enabled)
        self.record_check.toggled.connect(self._set_recording)
        toolbar.addWidget(self.record_check)
        layout.addLayout(toolbar)

        self.summary_label = QLabel()
        set_role(self.summary_label, "soft")
        layout.addWidget(self.summary_label)

        self.history_model = HistoryModel()
        self.history_proxy = LibraryFilter()
        self.history_table = _make_table(self.history_model, self.history_proxy)
        self.history_table.sortByColumn(HistoryModel.DATE, Qt.SortOrder.DescendingOrder)
        _size_columns(
            self.history_table,
            {
                HistoryModel.DATE: 125,
                HistoryModel.TYPE: 90,
                HistoryModel.FILES: 100,
                HistoryModel.POSTS: 60,
                HistoryModel.SIZE: 80,
                HistoryModel.DURATION: 75,
                HistoryModel.STATUS: 90,
                HistoryModel.FOLDER: 100,
            },
            stretch=(HistoryModel.TITLE, HistoryModel.LINK),
        )
        self.history_table.doubleClicked.connect(self._history_double_clicked)
        self.history_table.customContextMenuRequested.connect(self._history_menu)
        self.history_table.selectionModel().selectionChanged.connect(
            self._update_buttons
        )
        self.history_empty = self._empty_label()
        self.history_stack = self._stack(self.history_table, self.history_empty)
        layout.addLayout(self.history_stack, stretch=1)

        self.history_search.textChanged.connect(self._filter_history)
        self.kind_filter.currentIndexChanged.connect(self._filter_history)

        buttons = QHBoxLayout()
        self.open_folder_btn = _button("fa5s.folder-open", self.open_selected_folder)
        self.copy_history_btn = _button("fa5s.copy", self.copy_history_links)
        self.queue_history_btn = _button("fa5s.plus", self.queue_history_links)
        self.favorite_history_btn = _button("fa5s.star", self.favorite_history_links)
        self.export_history_btn = _button("fa5s.file-export", self.export_history)
        self.remove_history_btn = _button("fa5s.trash", self.remove_history)
        self.clear_history_btn = _button("fa5s.broom", self.clear_history)
        for button in (
            self.open_folder_btn,
            self.copy_history_btn,
            self.queue_history_btn,
            self.favorite_history_btn,
        ):
            buttons.addWidget(button)
        buttons.addStretch()
        for button in (
            self.export_history_btn,
            self.remove_history_btn,
            self.clear_history_btn,
        ):
            buttons.addWidget(button)
        layout.addLayout(buttons)

        self._add_shortcuts(
            self.history_table, self.copy_history_links, self.remove_history
        )
        return page

    def _build_favorites_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        add_note(layout, "note_favorites")

        add_row = QHBoxLayout()
        self.favorite_input = QLineEdit()
        self.favorite_input.returnPressed.connect(self.add_favorite_from_input)
        add_row.addWidget(self.favorite_input, stretch=1)
        self.favorite_add_btn = _button("fa5s.star", self.add_favorite_from_input)
        add_row.addWidget(self.favorite_add_btn)
        layout.addLayout(add_row)

        self.favorites_search = QLineEdit()
        self.favorites_search.setClearButtonEnabled(True)
        layout.addWidget(self.favorites_search)

        self.favorites_model = FavoritesModel(self.store)
        self.favorites_proxy = LibraryFilter()
        self.favorites_table = _make_table(self.favorites_model, self.favorites_proxy)
        self.favorites_table.sortByColumn(
            FavoritesModel.ADDED, Qt.SortOrder.DescendingOrder
        )
        self.favorites_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )
        _size_columns(
            self.favorites_table,
            {
                FavoritesModel.TYPE: 90,
                FavoritesModel.NOTE: 150,
                FavoritesModel.ADDED: 130,
                FavoritesModel.LAST: 140,
            },
            stretch=(FavoritesModel.TITLE, FavoritesModel.LINK),
        )
        self.favorites_table.doubleClicked.connect(self._favorite_double_clicked)
        self.favorites_table.customContextMenuRequested.connect(self._favorites_menu)
        self.favorites_table.selectionModel().selectionChanged.connect(
            self._update_buttons
        )
        self.favorites_empty = self._empty_label()
        self.favorites_stack = self._stack(self.favorites_table, self.favorites_empty)
        layout.addLayout(self.favorites_stack, stretch=1)
        self.favorites_search.textChanged.connect(self.favorites_proxy.set_text)

        buttons = QHBoxLayout()
        self.queue_favorite_btn = _button("fa5s.plus", self.queue_favorite_links)
        self.copy_favorite_btn = _button("fa5s.copy", self.copy_favorite_links)
        self.browser_favorite_btn = _button(
            "fa5s.external-link-alt", self.open_favorites
        )
        self.import_favorites_btn = _button("fa5s.file-import", self.import_favorites)
        self.export_favorites_btn = _button("fa5s.file-export", self.export_favorites)
        self.remove_favorite_btn = _button("fa5s.trash", self.remove_favorites)
        for button in (
            self.queue_favorite_btn,
            self.copy_favorite_btn,
            self.browser_favorite_btn,
        ):
            buttons.addWidget(button)
        buttons.addStretch()
        for button in (
            self.import_favorites_btn,
            self.export_favorites_btn,
            self.remove_favorite_btn,
        ):
            buttons.addWidget(button)
        layout.addLayout(buttons)

        self._add_shortcuts(
            self.favorites_table, self.copy_favorite_links, self.remove_favorites
        )
        return page

    @staticmethod
    def _empty_label() -> QLabel:
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        set_role(label, "empty")
        return label

    @staticmethod
    def _stack(table: QTableView, empty: QLabel) -> QStackedLayout:
        stack = QStackedLayout()
        stack.addWidget(table)
        stack.addWidget(empty)
        return stack

    def _add_shortcuts(
        self, table: QTableView, copy: Callable, remove: Callable
    ) -> None:
        for sequence, handler in (
            (QKeySequence.StandardKey.Copy, copy),
            (QKeySequence.StandardKey.Delete, remove),
        ):
            action = QAction(table)
            action.setShortcut(sequence)
            action.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
            action.triggered.connect(handler)
            table.addAction(action)

    # ------------------------------------------------------------------
    # Text
    # ------------------------------------------------------------------

    def update_ui_text(self) -> None:
        retranslate_notes(self)
        self.views.setTabText(0, translate("history_downloads_view"))
        self.views.setTabText(1, translate("favorites_view"))
        self.history_search.setPlaceholderText(translate("history_search_placeholder"))
        self.favorites_search.setPlaceholderText(
            translate("history_search_placeholder")
        )
        self.favorite_input.setPlaceholderText(translate("favorites_add_placeholder"))
        self.record_check.setText(translate("history_record_toggle"))

        current = self.kind_filter.currentData()
        self.kind_filter.blockSignals(True)
        self.kind_filter.clear()
        self.kind_filter.addItem(translate("history_filter_all"), None)
        for kind in (KIND_POST, KIND_CREATOR, KIND_THUMBNAIL):
            self.kind_filter.addItem(translate(_KIND_KEYS[kind]), kind)
        self.kind_filter.setCurrentIndex(max(0, self.kind_filter.findData(current)))
        self.kind_filter.blockSignals(False)

        for button, key in (
            (self.open_folder_btn, "history_open_folder"),
            (self.copy_history_btn, "history_copy_link"),
            (self.queue_history_btn, "history_add_to_queue"),
            (self.favorite_history_btn, "history_add_favorite"),
            (self.export_history_btn, "history_export"),
            (self.remove_history_btn, "history_remove"),
            (self.clear_history_btn, "history_clear"),
            (self.favorite_add_btn, "favorites_add"),
            (self.queue_favorite_btn, "history_add_to_queue"),
            (self.copy_favorite_btn, "history_copy_link"),
            (self.browser_favorite_btn, "favorites_open_browser"),
            (self.import_favorites_btn, "favorites_import"),
            (self.export_favorites_btn, "favorites_export"),
            (self.remove_favorite_btn, "history_remove"),
        ):
            button.setText(translate(key))

        self.history_empty.setText(translate("history_empty"))
        self.favorites_empty.setText(translate("favorites_empty"))
        if self.store.error:
            self.storage_warning.setText(
                translate("history_storage_error", self.store.error)
            )
        self.storage_warning.setVisible(bool(self.store.error))
        models: Tuple[QAbstractTableModel, ...] = (
            self.history_model,
            self.favorites_model,
        )
        for model in models:
            model.headerDataChanged.emit(
                Qt.Orientation.Horizontal, 0, model.columnCount() - 1
            )
        self.refresh()

    def refresh_ui(self) -> None:
        self.update_ui_text()

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        self._seen_revision = self.store.revision
        self.history_model.set_entries(self.store.history())
        self.favorites_model.set_favorites(
            self.store.favorites(), self.store.last_downloaded()
        )
        self._update_summary()
        self._update_empty_states()
        self._update_buttons()

    def _refresh_if_changed(self) -> None:
        if self.store.revision != self._seen_revision:
            self._keep_selection(self.refresh)

    def _keep_selection(self, action: Callable) -> None:
        """Run *action* (a model reset) without losing the selected rows."""
        selected = {e.id for e in self.selected_history()}
        action()
        if not selected:
            return
        selection = self.history_table.selectionModel()
        for row in range(self.history_proxy.rowCount()):
            source = self.history_proxy.mapToSource(self.history_proxy.index(row, 0))
            if self.history_model.entries[source.row()].id in selected:
                selection.select(
                    self.history_proxy.index(row, 0),
                    selection.SelectionFlag.Select | selection.SelectionFlag.Rows,
                )

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._refresh_if_changed()
        self._poll.start()

    def hideEvent(self, event) -> None:  # noqa: N802
        self._poll.stop()
        super().hideEvent(event)

    def _visible_history(self) -> List[HistoryEntry]:
        rows = []
        for row in range(self.history_proxy.rowCount()):
            source = self.history_proxy.mapToSource(self.history_proxy.index(row, 0))
            rows.append(self.history_model.entries[source.row()])
        return rows

    def _update_summary(self) -> None:
        entries = self._visible_history()
        files = sum(e.files_done for e in entries)
        failed = sum(e.files_failed for e in entries)
        posts = sum(e.posts_done for e in entries)
        size = sum(e.size_bytes or 0 for e in entries)
        self.summary_label.setText(
            translate(
                "history_summary", len(entries), files, failed, posts, format_size(size)
            )
        )

    def _update_empty_states(self) -> None:
        self._show_table_or_empty(
            self.history_stack,
            self.history_table,
            self.history_empty,
            self.history_model.rowCount(),
        )
        self._show_table_or_empty(
            self.favorites_stack,
            self.favorites_table,
            self.favorites_empty,
            self.favorites_model.rowCount(),
        )

    @staticmethod
    def _show_table_or_empty(
        stack: QStackedLayout, table: QTableView, empty: QLabel, rows: int
    ) -> None:
        stack.setCurrentWidget(table if rows else empty)

    def _filter_history(self) -> None:
        self.history_proxy.set_kind(self.kind_filter.currentData())
        self.history_proxy.set_text(self.history_search.text())
        self._update_summary()

    def _set_recording(self, enabled: bool) -> None:
        self.store.recording_enabled = enabled

    def _update_buttons(self, *_args) -> None:
        has_history = bool(self.history_table.selectionModel().selectedRows())
        for button in (
            self.open_folder_btn,
            self.copy_history_btn,
            self.queue_history_btn,
            self.favorite_history_btn,
            self.remove_history_btn,
        ):
            button.setEnabled(has_history)
        self.clear_history_btn.setEnabled(self.history_model.rowCount() > 0)
        self.export_history_btn.setEnabled(self.history_model.rowCount() > 0)
        has_favorite = bool(self.favorites_table.selectionModel().selectedRows())
        for button in (
            self.queue_favorite_btn,
            self.copy_favorite_btn,
            self.browser_favorite_btn,
            self.remove_favorite_btn,
        ):
            button.setEnabled(has_favorite)
        self.export_favorites_btn.setEnabled(self.favorites_model.rowCount() > 0)

    def show_status(self, message: str) -> None:
        self.status_label.setText(message)
        self._status_clear.start()

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def selected_history(self) -> List[HistoryEntry]:
        rows = self.history_table.selectionModel().selectedRows()
        return [
            self.history_model.entries[self.history_proxy.mapToSource(i).row()]
            for i in sorted(rows, key=lambda i: i.row())
        ]

    def selected_favorites(self) -> List[Favorite]:
        rows = self.favorites_table.selectionModel().selectedRows()
        return [
            self.favorites_model.favorites[self.favorites_proxy.mapToSource(i).row()]
            for i in sorted(rows, key=lambda i: i.row())
        ]

    # ------------------------------------------------------------------
    # History actions
    # ------------------------------------------------------------------

    def _history_double_clicked(self, index) -> None:
        entry = self.history_model.entries[self.history_proxy.mapToSource(index).row()]
        self.open_folder(entry)

    def open_selected_folder(self) -> None:
        selected = self.selected_history()
        if not selected:
            self.show_status(translate("history_select_entry"))
            return
        self.open_folder(selected[0])

    def open_folder(self, entry: HistoryEntry) -> None:
        if not entry.folder:
            QMessageBox.information(
                self,
                translate("history_folder_missing_title"),
                translate("history_no_folder"),
            )
            return
        if os.path.isdir(entry.folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(entry.folder))
            return
        self._handle_missing_folder(entry)

    def _handle_missing_folder(self, entry: HistoryEntry) -> None:
        """The folder was moved, renamed or deleted: offer ways forward."""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(translate("history_folder_missing_title"))
        box.setText(translate("history_folder_missing_message", entry.folder))
        locate = box.addButton(
            translate("history_locate_folder"), QMessageBox.ButtonRole.ActionRole
        )
        parent_folder = nearest_existing_folder(os.path.dirname(entry.folder))
        open_parent = None
        if parent_folder:
            open_parent = box.addButton(
                translate("history_open_parent"), QMessageBox.ButtonRole.ActionRole
            )
        again = box.addButton(
            translate("history_redownload"), QMessageBox.ButtonRole.ActionRole
        )
        box.addButton(QMessageBox.StandardButton.Cancel)
        box.exec()
        clicked = box.clickedButton()
        if clicked is locate:
            folder = QFileDialog.getExistingDirectory(
                self, translate("history_locate_folder"), parent_folder or ""
            )
            if folder:
                if entry.id is not None:
                    self.store.update_folder(entry.id, folder)
                self._keep_selection(self.refresh)
        elif open_parent is not None and clicked is open_parent:
            QDesktopServices.openUrl(QUrl.fromLocalFile(parent_folder))
        elif clicked is again:
            self.queue_entries([entry])

    def copy_history_links(self) -> None:
        links = [link for e in self.selected_history() for link in e.links]
        self._copy(links)

    def queue_history_links(self) -> None:
        self.queue_entries(self.selected_history())

    def queue_entries(self, entries: List[HistoryEntry]) -> None:
        jobs = []
        for entry in entries:
            to_thumbnails = entry.kind == KIND_THUMBNAIL
            jobs += [(link, to_thumbnails) for link in entry.links]
        self._queue(jobs)

    def favorite_history_links(self) -> None:
        added = 0
        for entry in self.selected_history():
            for link in entry.links:
                title = entry.title if link == entry.url else ""
                added += self.store.add_favorite(link, title=title)
        self.show_status(translate("favorites_added_count", added))
        self.refresh_favorites()

    def remove_history(self) -> None:
        selected = self.selected_history()
        if not selected:
            return
        reply = QMessageBox.question(
            self,
            translate("history_remove"),
            translate("history_remove_confirm", len(selected)),
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.store.delete_history(e.id for e in selected if e.id is not None)
            self.refresh()

    def clear_history(self) -> None:
        count = self.history_model.rowCount()
        if not count:
            return
        reply = QMessageBox.question(
            self,
            translate("history_clear"),
            translate("history_clear_confirm", count),
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.store.clear_history()
            self.refresh()

    def export_history(self) -> None:
        entries = self._visible_history()
        if not entries:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            translate("history_export"),
            f"kemono_history_{datetime.date.today():%Y%m%d}.csv",
            "CSV (*.csv)",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.writer(handle)
                writer.writerow(
                    [
                        "finished_at",
                        "type",
                        "title",
                        "creator",
                        "service",
                        "status",
                        "files_done",
                        "files_total",
                        "files_failed",
                        "files_preview_only",
                        "files_missing",
                        "posts_done",
                        "posts_total",
                        "size_bytes",
                        "duration_seconds",
                        "folder",
                        "links",
                    ]
                )
                for e in entries:
                    writer.writerow(
                        [
                            format_time(e.finished_at),
                            e.kind,
                            e.title,
                            e.creator,
                            e.service,
                            e.status,
                            e.files_done,
                            e.files_total,
                            e.files_failed,
                            e.files_preview_only,
                            e.files_missing,
                            e.posts_done,
                            e.posts_total,
                            "" if e.size_bytes is None else e.size_bytes,
                            "" if e.duration is None else round(e.duration),
                            e.folder,
                            " ".join(e.links),
                        ]
                    )
        except OSError as exc:
            QMessageBox.critical(
                self,
                translate("history_export"),
                translate("history_export_failed", str(exc)),
            )
            return
        self.show_status(translate("history_exported", len(entries), path))

    def _history_menu(self, position) -> None:
        if not self.selected_history():
            return
        menu = QMenu(self)
        for key, icon, handler in (
            ("history_open_folder", "fa5s.folder-open", self.open_selected_folder),
            ("history_copy_link", "fa5s.copy", self.copy_history_links),
            ("history_add_to_queue", "fa5s.plus", self.queue_history_links),
            ("history_add_favorite", "fa5s.star", self.favorite_history_links),
            ("history_remove", "fa5s.trash", self.remove_history),
        ):
            action = menu.addAction(qta.icon(icon, color="#333333"), translate(key))
            action.triggered.connect(handler)
        menu.exec(self.history_table.viewport().mapToGlobal(position))

    # ------------------------------------------------------------------
    # Favorite actions
    # ------------------------------------------------------------------

    def refresh_favorites(self) -> None:
        self.favorites_model.set_favorites(
            self.store.favorites(), self.store.last_downloaded()
        )
        self._update_empty_states()
        self._update_buttons()

    def add_favorite_from_input(self) -> None:
        url = normalize_link(self.favorite_input.text())
        if not url:
            return
        if link_kind(url) is None:
            self.show_status(translate("library_invalid_link", url))
            return
        if self.store.add_favorite(url):
            self.favorite_input.clear()
            self.show_status(translate("favorites_added", url))
            self.refresh_favorites()
        else:
            self.show_status(translate("favorites_already", url))

    def _favorite_double_clicked(self, index) -> None:
        if index.column() not in FavoritesModel.EDITABLE:
            self.queue_favorite_links()

    def queue_favorite_links(self) -> None:
        self._queue([(f.url, False) for f in self.selected_favorites()])

    def copy_favorite_links(self) -> None:
        self._copy([f.url for f in self.selected_favorites()])

    def open_favorites(self) -> None:
        for favorite in self.selected_favorites():
            QDesktopServices.openUrl(QUrl(favorite.url))

    def remove_favorites(self) -> None:
        selected = self.selected_favorites()
        if not selected:
            return
        reply = QMessageBox.question(
            self,
            translate("history_remove"),
            translate("favorites_remove_confirm", len(selected)),
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.store.remove_favorites(f.id for f in selected if f.id is not None)
            self.refresh_favorites()

    def import_favorites(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, translate("favorites_import"), "", "Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                lines = handle.readlines()
        except OSError as exc:
            QMessageBox.critical(
                self,
                translate("favorites_import"),
                translate("file_read_error", str(exc)),
            )
            return
        added = skipped = 0
        for line in lines:
            link = normalize_link(line)
            if not link:
                continue
            if self.store.add_favorite(link):
                added += 1
            else:
                skipped += 1
        self.show_status(translate("favorites_imported", added, skipped))
        self.refresh_favorites()

    def export_favorites(self) -> None:
        favorites = self.favorites_model.favorites
        if not favorites:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            translate("favorites_export"),
            "kemono_favorites.txt",
            "Text Files (*.txt)",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("\n".join(f.url for f in favorites) + "\n")
        except OSError as exc:
            QMessageBox.critical(
                self,
                translate("favorites_export"),
                translate("history_export_failed", str(exc)),
            )
            return
        self.show_status(translate("history_exported", len(favorites), path))

    def _favorites_menu(self, position) -> None:
        if not self.selected_favorites():
            return
        menu = QMenu(self)
        for key, icon, handler in (
            ("history_add_to_queue", "fa5s.plus", self.queue_favorite_links),
            ("history_copy_link", "fa5s.copy", self.copy_favorite_links),
            ("favorites_open_browser", "fa5s.external-link-alt", self.open_favorites),
            ("history_remove", "fa5s.trash", self.remove_favorites),
        ):
            action = menu.addAction(qta.icon(icon, color="#333333"), translate(key))
            action.triggered.connect(handler)
        menu.exec(self.favorites_table.viewport().mapToGlobal(position))

    # ------------------------------------------------------------------
    # Shared
    # ------------------------------------------------------------------

    def _copy(self, links: List[str]) -> None:
        if not links:
            return
        QApplication.clipboard().setText("\n".join(dict.fromkeys(links)))
        self.show_status(translate("history_copied", len(set(links))))

    def _target_tab(self, link: str, to_thumbnails: bool):
        window = self.window_ref
        if to_thumbnails:
            return getattr(window, "thumbnail_tab", None)
        kind = link_kind(link)
        if kind == KIND_POST:
            return getattr(window, "post_tab", None)
        if kind == KIND_CREATOR:
            return getattr(window, "creator_tab", None)
        return None

    def _queue(self, jobs) -> None:
        """Queue (link, to_thumbnails) pairs in the right downloader tabs."""
        if not jobs:
            return
        added, problems, last_tab = 0, [], None
        for link, to_thumbnails in jobs:
            tab = self._target_tab(link, to_thumbnails)
            if tab is None or not hasattr(tab, "enqueue_from_library"):
                problems.append(translate("library_invalid_link", link))
                continue
            result = tab.enqueue_from_library(link)
            if result == QUEUE_ADDED:
                added += 1
                last_tab = tab
            elif result == QUEUE_DUPLICATE:
                problems.append(translate("history_queue_duplicate", link))
            elif result == QUEUE_BUSY:
                problems.append(translate("history_queue_busy"))
            elif result == QUEUE_MODE_MISMATCH:
                problems.append(translate("history_queue_mode_mismatch"))
            else:
                problems.append(translate("library_invalid_link", link))
        message = translate("history_queued", added)
        if problems:
            message += " — " + "; ".join(dict.fromkeys(problems))
        self.show_status(message)
        tabs = getattr(self.window_ref, "tabs", None)
        if last_tab is not None and tabs is not None:
            index = tabs.indexOf(last_tab)
            if index >= 0 and tabs.isTabEnabled(index):
                tabs.setCurrentIndex(index)
