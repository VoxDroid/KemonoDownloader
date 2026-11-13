"""Persistent download history and favorites.

Stored in one SQLite file beside the hash database. The store never takes the
app down: a damaged file is set aside and a fresh one started, and when the
folder cannot be written at all the store keeps working in memory for the
session and reports why through :attr:`HistoryStore.error`.

Everything here is plain Python. Folder sizes are measured on a background
thread, which writes only to the database; views notice through
:attr:`HistoryStore.revision` instead of a Qt signal, so nothing calls into Qt
from that thread (which is unsafe while the app shuts down).
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

KIND_POST = "post"
KIND_CREATOR = "creator"
KIND_THUMBNAIL = "thumbnail"

STATUS_COMPLETED = "completed"
STATUS_PARTIAL = "partial"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"

# What a downloader tab reports back when asked to queue a library link.
QUEUE_ADDED = "added"
QUEUE_DUPLICATE = "duplicate"
QUEUE_BUSY = "busy"
QUEUE_INVALID = "invalid"
QUEUE_MODE_MISMATCH = "mode_mismatch"

_POST_LINK = re.compile(r"https?://(?:www\.)?[^/]+/[^/]+/user/[^/]+/post/[^/?#]+")
_CREATOR_LINK = re.compile(r"https?://(?:www\.)?[^/]+/[^/]+/user/[^/?#]+")


def normalize_link(url: str) -> str:
    """Trim whitespace and trailing slashes so one link has one spelling."""
    return url.strip().rstrip("/")


def link_kind(url: str) -> Optional[str]:
    """Return ``"post"`` or ``"creator"`` for a supported link, else None."""
    url = normalize_link(url)
    if _POST_LINK.match(url):
        return KIND_POST
    if _CREATOR_LINK.match(url):
        return KIND_CREATOR
    return None


def download_status(files_total: int, files_done: int, cancelled: bool) -> str:
    """Summarise how a download ended."""
    if cancelled:
        return STATUS_CANCELLED
    if files_total > 0 and files_done >= files_total:
        return STATUS_COMPLETED
    if files_done > 0:
        return STATUS_PARTIAL
    return STATUS_FAILED


@dataclass
class HistoryEntry:
    kind: str
    url: str
    title: str = ""
    service: str = ""
    creator: str = ""
    folder: str = ""
    files_total: int = 0
    files_done: int = 0
    files_failed: int = 0
    posts_total: int = 0
    posts_done: int = 0
    status: str = STATUS_COMPLETED
    started_at: Optional[float] = None
    finished_at: float = field(default_factory=time.time)
    size_bytes: Optional[int] = None
    extra_urls: List[str] = field(default_factory=list)
    id: Optional[int] = None
    # Files the site only had previews of (skipped), and files its media
    # server didn't have (HTTP 404/410, part of files_failed).
    files_preview_only: int = 0
    files_missing: int = 0

    @property
    def duration(self) -> Optional[float]:
        if self.started_at is None:
            return None
        return max(0.0, self.finished_at - self.started_at)

    @property
    def links(self) -> List[str]:
        """Every source link of the entry, the primary one first."""
        return [self.url] + [u for u in self.extra_urls if u != self.url]


@dataclass
class Favorite:
    url: str
    kind: str
    title: str = ""
    note: str = ""
    added_at: float = field(default_factory=time.time)
    id: Optional[int] = None


_HISTORY_COLUMNS = (
    "kind, url, title, service, creator, folder, files_total, files_done, "
    "files_failed, posts_total, posts_done, status, started_at, finished_at, "
    "size_bytes, extra_urls, files_preview_only, files_missing"
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    kind         TEXT    NOT NULL,
    url          TEXT    NOT NULL,
    title        TEXT    NOT NULL DEFAULT '',
    service      TEXT    NOT NULL DEFAULT '',
    creator      TEXT    NOT NULL DEFAULT '',
    folder       TEXT    NOT NULL DEFAULT '',
    files_total  INTEGER NOT NULL DEFAULT 0,
    files_done   INTEGER NOT NULL DEFAULT 0,
    files_failed INTEGER NOT NULL DEFAULT 0,
    posts_total  INTEGER NOT NULL DEFAULT 0,
    posts_done   INTEGER NOT NULL DEFAULT 0,
    status       TEXT    NOT NULL,
    started_at   REAL,
    finished_at  REAL    NOT NULL,
    size_bytes   INTEGER,
    extra_urls   TEXT    NOT NULL DEFAULT '[]',
    files_preview_only INTEGER NOT NULL DEFAULT 0,
    files_missing      INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS history_finished ON history (finished_at);
CREATE INDEX IF NOT EXISTS history_url ON history (url);
CREATE TABLE IF NOT EXISTS favorites (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    url      TEXT    NOT NULL UNIQUE,
    kind     TEXT    NOT NULL,
    title    TEXT    NOT NULL DEFAULT '',
    note     TEXT    NOT NULL DEFAULT '',
    added_at REAL    NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

SCHEMA_VERSION = 2

# Columns added after version 1; older databases get them on open. Older
# app versions name their columns explicitly, so they keep working.
_ADDED_COLUMNS = (
    ("files_preview_only", "INTEGER NOT NULL DEFAULT 0"),
    ("files_missing", "INTEGER NOT NULL DEFAULT 0"),
)


class HistoryStore:
    DB_FILENAME = "library.db"

    def __init__(self, directory: str) -> None:
        self._lock = threading.Lock()
        self.error: Optional[str] = None
        self.path: Optional[str] = None
        self.revision = 0
        self._closed = False
        self._conn = self._open(directory)

    # ------------------------------------------------------------------
    # Opening
    # ------------------------------------------------------------------

    def _open(self, directory: str) -> sqlite3.Connection:
        path = os.path.join(directory, self.DB_FILENAME)
        try:
            os.makedirs(directory, exist_ok=True)
            try:
                conn = self._connect(path)
            except sqlite3.DatabaseError:
                # Unreadable file: keep it for inspection, start a new one.
                os.replace(path, f"{path}.corrupt-{int(time.time())}")
                conn = self._connect(path)
            self.path = path
            return conn
        except (OSError, sqlite3.Error) as exc:
            self.error = str(exc) or exc.__class__.__name__
            return self._connect(":memory:")

    @staticmethod
    def _connect(path: str) -> sqlite3.Connection:
        conn = sqlite3.connect(path, timeout=30, check_same_thread=False)
        try:
            if path != ":memory:":
                conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.executescript(_SCHEMA)
            existing = {row[1] for row in conn.execute("PRAGMA table_info(history)")}
            for name, definition in _ADDED_COLUMNS:
                if name not in existing:
                    conn.execute(f"ALTER TABLE history ADD COLUMN {name} {definition}")
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version < SCHEMA_VERSION:
                conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            conn.commit()
        except sqlite3.Error:
            conn.close()
            raise
        return conn

    @property
    def is_persistent(self) -> bool:
        return self.path is not None

    def close(self) -> None:
        with self._lock:
            if not self._closed:
                self._closed = True
                self._conn.close()

    def _execute(self, sql: str, params: Iterable = ()) -> List[tuple]:
        """Run one statement; a closed or failing store behaves as empty."""
        with self._lock:
            if self._closed:
                return []
            try:
                rows = self._conn.execute(sql, tuple(params)).fetchall()
                self._conn.commit()
            except sqlite3.Error as exc:
                self.error = str(exc)
                return []
            if not sql.lstrip().upper().startswith("SELECT"):
                self.revision += 1
            return rows

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    @property
    def recording_enabled(self) -> bool:
        rows = self._execute("SELECT value FROM meta WHERE key = 'record_history'")
        return not rows or rows[0][0] != "0"

    @recording_enabled.setter
    def recording_enabled(self, enabled: bool) -> None:
        self._execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('record_history', ?)",
            ("1" if enabled else "0",),
        )

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def record(self, entry: HistoryEntry) -> Optional[int]:
        """Save a finished download; returns its id, or None when not recorded."""
        if not self.recording_enabled:
            return None
        entry.url = normalize_link(entry.url)
        entry.extra_urls = [normalize_link(u) for u in entry.extra_urls]
        with self._lock:
            if self._closed:
                return None
            try:
                cursor = self._conn.execute(
                    f"INSERT INTO history ({_HISTORY_COLUMNS}) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        entry.kind,
                        entry.url,
                        entry.title,
                        entry.service,
                        entry.creator,
                        entry.folder,
                        entry.files_total,
                        entry.files_done,
                        entry.files_failed,
                        entry.posts_total,
                        entry.posts_done,
                        entry.status,
                        entry.started_at,
                        entry.finished_at,
                        entry.size_bytes,
                        json.dumps(entry.extra_urls),
                        entry.files_preview_only,
                        entry.files_missing,
                    ),
                )
                self._conn.commit()
            except sqlite3.Error as exc:
                self.error = str(exc)
                return None
            entry_id = cursor.lastrowid
            entry.id = entry_id
            self.revision += 1
        if (
            entry_id is not None
            and entry.size_bytes is None
            and entry.folder
            and os.path.isdir(entry.folder)
        ):
            self.measure_folder_later(entry_id, entry.folder)
        return entry_id

    def history(self) -> List[HistoryEntry]:
        rows = self._execute(
            f"SELECT id, {_HISTORY_COLUMNS} FROM history ORDER BY finished_at DESC, id DESC"
        )
        entries = []
        for row in rows:
            try:
                extra = json.loads(row[16] or "[]")
            except ValueError:
                extra = []
            entries.append(
                HistoryEntry(
                    id=row[0],
                    kind=row[1],
                    url=row[2],
                    title=row[3],
                    service=row[4],
                    creator=row[5],
                    folder=row[6],
                    files_total=row[7],
                    files_done=row[8],
                    files_failed=row[9],
                    posts_total=row[10],
                    posts_done=row[11],
                    status=row[12],
                    started_at=row[13],
                    finished_at=row[14],
                    size_bytes=row[15],
                    extra_urls=extra if isinstance(extra, list) else [],
                    files_preview_only=row[17] or 0,
                    files_missing=row[18] or 0,
                )
            )
        return entries

    def last_downloaded(self) -> dict:
        """Map each recorded link to when it last finished downloading."""
        rows = self._execute("SELECT url, MAX(finished_at) FROM history GROUP BY url")
        return {url: finished for url, finished in rows}

    def delete_history(self, ids: Iterable[int]) -> None:
        ids = list(ids)
        if ids:
            marks = ",".join("?" * len(ids))
            self._execute(f"DELETE FROM history WHERE id IN ({marks})", ids)

    def clear_history(self) -> None:
        self._execute("DELETE FROM history")

    def update_folder(self, entry_id: int, folder: str) -> None:
        self._execute(
            "UPDATE history SET folder = ?, size_bytes = NULL WHERE id = ?",
            (folder, entry_id),
        )
        if os.path.isdir(folder):
            self.measure_folder_later(entry_id, folder)

    def measure_folder_later(self, entry_id: int, folder: str) -> None:
        threading.Thread(
            target=self._measure_folder, args=(entry_id, folder), daemon=True
        ).start()

    def _measure_folder(self, entry_id: int, folder: str) -> None:
        total = 0
        for root, _dirs, files in os.walk(folder):
            for name in files:
                try:
                    total += os.path.getsize(os.path.join(root, name))
                except OSError:
                    pass
        self._execute(
            "UPDATE history SET size_bytes = ? WHERE id = ?", (total, entry_id)
        )

    # ------------------------------------------------------------------
    # Favorites
    # ------------------------------------------------------------------

    def add_favorite(self, url: str, title: str = "", note: str = "") -> bool:
        """Save a link; False if it is not a supported link or already saved."""
        url = normalize_link(url)
        kind = link_kind(url)
        if kind is None or self.is_favorite(url):
            return False
        self._execute(
            "INSERT OR IGNORE INTO favorites (url, kind, title, note, added_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (url, kind, title.strip(), note.strip(), time.time()),
        )
        return self.is_favorite(url)

    def is_favorite(self, url: str) -> bool:
        rows = self._execute(
            "SELECT 1 FROM favorites WHERE url = ?", (normalize_link(url),)
        )
        return bool(rows)

    def favorites(self) -> List[Favorite]:
        rows = self._execute(
            "SELECT id, url, kind, title, note, added_at FROM favorites "
            "ORDER BY added_at DESC, id DESC"
        )
        return [
            Favorite(id=r[0], url=r[1], kind=r[2], title=r[3], note=r[4], added_at=r[5])
            for r in rows
        ]

    def update_favorite(
        self, favorite_id: int, title: Optional[str] = None, note: Optional[str] = None
    ) -> None:
        if title is not None:
            self._execute(
                "UPDATE favorites SET title = ? WHERE id = ?",
                (title.strip(), favorite_id),
            )
        if note is not None:
            self._execute(
                "UPDATE favorites SET note = ? WHERE id = ?",
                (note.strip(), favorite_id),
            )

    def remove_favorites(self, ids: Iterable[int]) -> None:
        ids = list(ids)
        if ids:
            marks = ",".join("?" * len(ids))
            self._execute(f"DELETE FROM favorites WHERE id IN ({marks})", ids)
