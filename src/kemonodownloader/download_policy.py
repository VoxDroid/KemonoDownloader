"""Per-host request policies for responsible file downloading."""

import threading
import time
from typing import Callable
from urllib.parse import urlparse

IDENTIFIABLE_USER_AGENT = "KemonoDownloader/5.14.0 (+mailto:izeno.contact@gmail.com)"
PAWCHIVE_MAX_ACTIVE_DOWNLOADS = 5
PAWCHIVE_REQUEST_INTERVAL = 1.0


def is_pawchive_url(url: str) -> bool:
    """Return whether *url* belongs to pawchive or its file server."""
    hostname = (urlparse(url).hostname or "").lower()
    return hostname == "pawchive.pw" or hostname.endswith(".pawchive.pw")


def get_request_headers(headers: dict, url: str) -> dict:
    """Return request headers with an identifiable UA for pawchive."""
    request_headers = headers.copy()
    if is_pawchive_url(url):
        request_headers["User-Agent"] = IDENTIFIABLE_USER_AGENT
    return request_headers


class _PawchiveDownloadLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active = 0
        self._next_request_at = 0.0

    def acquire(self, is_running: Callable[[], bool]) -> bool:
        """Reserve a download slot and wait for the request-rate interval."""
        while is_running():
            with self._lock:
                now = time.monotonic()
                if (
                    self._active < PAWCHIVE_MAX_ACTIVE_DOWNLOADS
                    and now >= self._next_request_at
                ):
                    self._active += 1
                    self._next_request_at = now + PAWCHIVE_REQUEST_INTERVAL
                    return True
                wait_for = max(0.05, self._next_request_at - now)
            time.sleep(min(wait_for, 0.1))
        return False

    def release(self) -> None:
        with self._lock:
            self._active = max(0, self._active - 1)


_pawchive_limiter = _PawchiveDownloadLimiter()


def acquire_pawchive_download(url: str, is_running: Callable[[], bool]) -> bool:
    if not is_pawchive_url(url):
        return True
    return _pawchive_limiter.acquire(is_running)


def release_pawchive_download(url: str) -> None:
    if is_pawchive_url(url):
        _pawchive_limiter.release()
