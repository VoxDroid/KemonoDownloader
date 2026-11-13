"""Qt-free helpers shared by the post, creator and thumbnail downloaders."""

from __future__ import annotations

import contextlib
import gzip
import hashlib
import json
import os
import re
import sys
import threading
import time
from typing import (
    Any,
    Callable,
    ContextManager,
    Dict,
    Iterator,
    NamedTuple,
    Optional,
    Tuple,
)

from bs4 import BeautifulSoup

from kemonodownloader.domain_config import clean_file_url

# Large enough to keep Python's per-chunk overhead negligible on fast links, small
# enough that cancellation is still noticed quickly on slow ones.
DOWNLOAD_CHUNK_SIZE = 64 * 1024
HASH_CHUNK_SIZE = 1024 * 1024

# How long a cancelled job waits for its workers before giving up on them.
CANCEL_GRACE_SECONDS = 30.0

ALLOWED_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".zip",
    ".mp4",
    ".pdf",
    ".7z",
    ".mp3",
    ".wav",
    ".flac",
    ".var",
    ".rar",
    ".mov",
    ".docx",
    ".psd",
    ".clip",
    ".jpe",
    ".webp",
)


class ThreadSettings:
    """Settings container for thread operations"""

    def __init__(
        self,
        creator_posts_max_attempts,
        post_data_max_retries,
        file_download_max_retries,
        api_request_max_retries,
        simultaneous_downloads,
        settings_tab=None,
    ):
        self.creator_posts_max_attempts = creator_posts_max_attempts
        self.post_data_max_retries = post_data_max_retries
        self.file_download_max_retries = file_download_max_retries
        self.api_request_max_retries = api_request_max_retries
        self.simultaneous_downloads = simultaneous_downloads
        self.settings_tab = settings_tab


def sanitize_filename(name, max_length=100):
    """Sanitize a filename by removing invalid characters, trailing dots, and limiting length."""
    if not name:
        return "unnamed"
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")
    # Remove multiple consecutive underscores
    sanitized = re.sub(r"_+", "_", sanitized)
    # Remove trailing dots (Windows compatibility)
    sanitized = sanitized.rstrip(".")
    # Remove leading dots to avoid hidden/unsafe filenames
    sanitized = sanitized.lstrip(".")
    # Trim leading/trailing underscores
    sanitized = sanitized.strip("_")
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip(".").strip("_")
    # Ensure non-empty
    return sanitized if sanitized else "unnamed"


def safe_local_filename(name: str) -> str:
    """Make a server-supplied file name safe to join onto a folder.

    Unlike :func:`sanitize_filename` this keeps the name as close to the original
    as it can (spaces and case survive). It only removes what would stop the file
    being created, or let the name escape the target folder: path separators, the
    other characters Windows rejects, and trailing dots or spaces.
    """
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).rstrip(". ")
    return cleaned if cleaned.strip("._ ") else "unnamed"


def filename_from_url(file_url: str) -> str:
    """Return the file name carried by a download URL's ``f=`` hint or its path."""
    if "f=" in file_url:
        return file_url.split("f=")[-1]
    return file_url.split("/")[-1].split("?")[0]


def response_content_length(response: Any) -> int:
    """Return the size the body will have once decoded, or 0 when it is unknown.

    ``Content-Length`` counts the bytes on the wire, so it says nothing about the
    size of a body that ``iter_content`` decompresses. Treating it as the expected
    size would fail every compressed download with a false size mismatch.
    """
    headers = response.headers
    if headers.get("content-encoding") not in (None, "", "identity"):
        return 0
    try:
        return int(headers.get("content-length"))
    except (TypeError, ValueError):
        return 0


def parse_response_content(response: Any) -> Any:
    """Decode a possibly gzipped JSON response body. Raises on invalid content."""
    content = response.content
    # Check if content is gzipped by looking for gzip magic number
    if content.startswith(b"\x1f\x8b"):
        try:
            content = gzip.decompress(content)
        except Exception:
            pass  # If decompression fails, use original content
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    return json.loads(content)


def md5_file(path: str) -> str:
    """Hash a file without loading it into memory."""
    digest = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(HASH_CHUNK_SIZE)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)


class ProgressTracker:
    """Turns a stream of byte counts into at most one update per percentage point.

    Signals are queued on the GUI thread, so reporting every chunk of a fast
    download floods its event loop and is what makes the window stutter.
    """

    def __init__(self, total_size: int) -> None:
        self.total_size = total_size
        self.downloaded = 0
        self._last_percent: Optional[int] = None

    def advance(self, chunk_size: int) -> Optional[int]:
        """Record *chunk_size* more bytes; return the percentage if it changed."""
        self.downloaded += chunk_size
        percent = 0
        if self.total_size > 0:
            percent = min(int(self.downloaded * 100 / self.total_size), 100)
        if percent == self._last_percent:
            return None
        self._last_percent = percent
        return percent


def wait_for_workers(
    workers: list,
    is_running: Callable[[], bool],
    grace_seconds: float = CANCEL_GRACE_SECONDS,
) -> None:
    """Wait for worker threads so that none outlives the owning QThread.

    A running job waits for as long as its workers need: a large file can take
    hours, and reporting completion early would have the GUI delete the QThread
    while workers still use it. Only a cancelled job gives up, after
    *grace_seconds*.

    Thread.join() internally uses Event.wait() which triggers Condition.notify()
    access violations on Python 3.14 + Windows, so poll is_alive() instead.
    """
    deadline = None
    for worker in workers:
        while worker.is_alive():
            if not is_running():
                now = time.monotonic()
                if deadline is None:
                    deadline = now + grace_seconds
                elif now >= deadline:
                    return
            time.sleep(0.05)


def create_connection_guard() -> ContextManager:
    """Return the guard that serializes opening connections across workers.

    On Windows + Python 3.14, concurrent SSL handshakes / reads in OpenSSL trigger
    native access-violation crashes. Serialising only the session.get() call (which
    does SSL + redirects) while allowing concurrent body streaming avoids the
    problem. Everywhere else connections can be opened in parallel.
    """
    if sys.platform == "win32" and sys.version_info >= (3, 14):
        return threading.Lock()
    return contextlib.nullcontext()


def abbreviate(items: Any, limit: int = 10) -> str:
    """Render a collection for a log line without dumping all of it."""
    if len(items) <= limit:
        return str(items)
    if isinstance(items, dict):
        shown = list(items.items())[:limit]
    else:
        shown = list(items)[:limit]
    return f"{shown} ... (+{len(items) - limit} more)"


def effective_extension(file_path: str, file_name: str) -> str:
    """Return the lowercase extension of *file_name*, falling back to *file_path*."""
    name_ext = os.path.splitext(file_name)[1].lower()
    path_ext = os.path.splitext(file_path)[1].lower()
    return name_ext if name_ext else path_ext


def extension_allowed(extension: str, allowed_extensions: Any) -> bool:
    """Return whether *extension* passes the filter; ``.jpg`` also covers ``.jpeg``."""
    if ".jpg" in allowed_extensions and extension in (".jpg", ".jpeg"):
        return True
    return extension in allowed_extensions


# HTTP statuses meaning the media server doesn't have the file at all, so
# retrying can't help.
MISSING_FILE_STATUSES = (404, 410)


class PostFile(NamedTuple):
    """A file a post references."""

    kind: str  # "main", "attachment" or "content"
    name: str
    url: str
    extension: str
    # The site lists the file but only keeps its preview image (see
    # is_preview_only), so downloading the full file fails with 404.
    preview_only: bool = False


class PreviewOnlyFile(NamedTuple):
    """A file skipped because the site only has its preview."""

    post_id: str
    post_title: str
    name: str
    url: str


def is_preview_only(entry: Any) -> bool:
    """Return whether the site lists *entry* but only keeps its preview.

    Pawchive marks such files with ``"preview_only": true`` (and gives them no
    ``server``): the thumbnail exists, the full file does not.
    """
    return isinstance(entry, dict) and entry.get("preview_only") is True


def is_missing_file_error(error: BaseException) -> bool:
    """Return whether *error* is an HTTP error saying the file doesn't exist."""
    response = getattr(error, "response", None)
    status = getattr(response, "status_code", None)
    return status in MISSING_FILE_STATUSES


def iter_post_file_entries(
    post: Dict[str, Any],
    domain_config: Dict[str, str],
    main: bool = True,
    attachments: bool = True,
    content: bool = True,
) -> Iterator[PostFile]:
    """Yield a :class:`PostFile` for every file a post references.

    Filtering is left to the caller; ``preview_only`` tells which files the
    site has no full copy of.
    """

    def describe(kind: str, entry: Dict[str, Any]) -> PostFile:
        path = entry["path"]
        name = entry.get("name", "")
        url = clean_file_url(path, domain_config)
        if "f=" not in url and name:
            url += f"?f={name}"
        return PostFile(
            kind, name, url, effective_extension(path, name), is_preview_only(entry)
        )

    if main and "file" in post and post["file"] and "path" in post["file"]:
        yield describe("main", post["file"])

    if attachments and "attachments" in post:
        for attachment in post["attachments"]:
            if isinstance(attachment, dict) and "path" in attachment:
                yield describe("attachment", attachment)

    if content and "content" in post and post["content"]:
        soup = BeautifulSoup(post["content"], "html.parser")
        for img in soup.select("img[src]"):
            img_url = clean_file_url(str(img["src"]), domain_config)
            img_ext = os.path.splitext(img_url)[1].lower()
            yield PostFile("content", os.path.basename(img_url), img_url, img_ext)


def iter_post_files(
    post: Dict[str, Any],
    domain_config: Dict[str, str],
    main: bool = True,
    attachments: bool = True,
    content: bool = True,
) -> Iterator[Tuple[str, str, str, str]]:
    """Yield ``(kind, name, url, extension)`` for every file a post references.

    *kind* is ``"main"``, ``"attachment"`` or ``"content"``. Filtering is left to
    the caller. Use :func:`iter_post_file_entries` to also see which files are
    preview-only.
    """
    for entry in iter_post_file_entries(
        post, domain_config, main, attachments, content
    ):
        yield entry.kind, entry.name, entry.url, entry.extension
