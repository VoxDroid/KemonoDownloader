"""Per-host request policies for responsible downloading.

Two policies live here:

* Pawchive asks for at most five downloads at once, one new request a second
  (``acquire_pawchive_download``).
* Every site: when it answers HTTP 429 (Too Many Requests), or 503 with a
  ``Retry-After``, the whole site cools down. No request to it leaves the app
  until the cooldown ends, whichever worker it comes from. The cooldown is the
  server's ``Retry-After`` when it sends one, otherwise an exponential backoff
  with jitter. ``polite_get`` waits out cooldowns and retries rate-limited
  requests without using up the caller's own retries.
"""

import contextlib
import datetime
import math
import random
import threading
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Any, Callable, ContextManager, Dict, Optional
from urllib.parse import urlparse

import requests

IDENTIFIABLE_USER_AGENT = "KemonoDownloader/5.15.0 (+mailto:izeno.contact@gmail.com)"
PAWCHIVE_MAX_ACTIVE_DOWNLOADS = 5
PAWCHIVE_REQUEST_INTERVAL = 1.0


def is_pawchive_url(url: str) -> bool:
    """Return whether *url* belongs to pawchive or one of its servers.

    Matches ``pawchive.<suffix>`` and its subdomains (``file.``, ``img.``) for
    any suffix, since the site has moved between domains (see domain_config).
    """
    hostname = (urlparse(url).hostname or "").lower().rstrip(".")
    labels = hostname.split(".")
    return len(labels) >= 2 and labels[-2] == "pawchive" and bool(labels[-1])


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


# ---------------------------------------------------------------------------
# Rate limits (HTTP 429)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RateLimitPolicy:
    """How long to stay away from a site that is limiting requests."""

    # A cooldown never ends sooner than this, even after "Retry-After: 0".
    min_cooldown: float = 1.0
    # Nor later than this. A server asking for hours would otherwise stall a
    # download indefinitely; coming back after the cap costs one request, and
    # a second 429 just starts another cooldown.
    max_cooldown: float = 300.0
    # Without Retry-After: 2, 4, 8, ... seconds, up to the cap, then jittered
    # down by up to half so separate apps don't come back in lockstep.
    backoff_base: float = 2.0
    backoff_cap: float = 60.0
    # Workers released together by the end of a cooldown each start within
    # this many seconds of it, instead of all at the same instant.
    resume_spread: float = 1.0
    # Rate-limited answers one request may get before it is reported as
    # failed. They don't count towards the caller's own retries.
    max_retries: int = 8
    # How often a waiting worker checks whether it was cancelled.
    poll_interval: float = 0.1


DEFAULT_RATE_LIMIT_POLICY = RateLimitPolicy()

# Longest a preview someone is looking at waits for a site's cooldown before
# it reports the rate limit instead.
PREVIEW_MAX_RATE_LIMIT_WAIT = 10.0


class RateLimitedError(requests.RequestException):
    """A site is limiting requests and the caller chose not to wait."""

    def __init__(self, site: str, retry_in: float) -> None:
        self.site = site
        self.retry_in = retry_in
        super().__init__(
            f"{site} is limiting requests (HTTP 429); try again in "
            f"{max(1, math.ceil(retry_in))} s"
        )


class RequestCancelled(requests.RequestException):
    """The caller was cancelled while waiting for a site's rate limit."""


def site_key(url: str) -> str:
    """The site a URL belongs to: ``n1.kemono.cr`` and ``kemono.cr`` are one.

    The sites serve their API and files from subdomains of one domain behind
    one front end, and a 429 from any of them means this client is going too
    fast for the site, so they share a cooldown.
    """
    hostname = (urlparse(url).hostname or "").lower().rstrip(".")
    if not hostname or ":" in hostname or hostname.replace(".", "").isdigit():
        return hostname  # empty, IPv6 or IPv4 address
    labels = hostname.split(".")
    return ".".join(labels[-2:]) if len(labels) > 2 else hostname


def parse_retry_after(
    value: Any, now: Optional[Callable[[], float]] = None
) -> Optional[float]:
    """Seconds to wait from a ``Retry-After`` value, or None if unusable.

    The header is either a number of seconds or an HTTP date. A date already
    past means "now" (0). Negative, non-finite and malformed values are None.
    """
    if isinstance(value, bytes):
        value = value.decode("latin-1", "replace")
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    try:
        seconds = float(text)
    except ValueError:
        pass
    else:
        if not math.isfinite(seconds) or seconds < 0:
            return None
        return seconds
    try:
        when = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=datetime.timezone.utc)
    current = (now or time.time)()
    return max(0.0, when.timestamp() - current)


def _status_code(response: Any) -> Optional[int]:
    status = getattr(response, "status_code", None)
    # bool is an int too, and test doubles may hold anything.
    if isinstance(status, int) and not isinstance(status, bool):
        return status
    return None


def _retry_after_header(response: Any) -> Any:
    headers = getattr(response, "headers", None)
    getter = getattr(headers, "get", None)
    if not callable(getter):
        return None
    try:
        return getter("Retry-After")
    except Exception:
        return None


def is_rate_limited(response: Any) -> bool:
    """Whether *response* asks the client to slow down.

    429 always does. 503 does only with a usable Retry-After; a bare 503 is an
    ordinary server error and keeps the caller's usual handling.
    """
    status = _status_code(response)
    if status == 429:
        return True
    return (
        status == 503 and parse_retry_after(_retry_after_header(response)) is not None
    )


def is_rate_limit_error(error: BaseException) -> bool:
    """Whether *error* (e.g. from ``raise_for_status``) is a rate limit."""
    if isinstance(error, RateLimitedError):
        return True
    return is_rate_limited(getattr(error, "response", None))


class SiteRateLimiter:
    """Cooldowns shared by every request to a site, across all workers.

    Thread-safe. The clock, wall clock, sleep and random source are
    injectable so the timing can be tested without waiting.
    """

    def __init__(
        self,
        policy: RateLimitPolicy = DEFAULT_RATE_LIMIT_POLICY,
        clock: Callable[[], float] = time.monotonic,
        wall_clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
        rng: Callable[[], float] = random.random,
    ) -> None:
        self.policy = policy
        self._clock = clock
        self._wall_clock = wall_clock
        self._sleep = sleep
        self._rng = rng
        self._lock = threading.Lock()
        self._until: Dict[str, float] = {}
        self._strikes: Dict[str, int] = {}

    def reset(self) -> None:
        with self._lock:
            self._until.clear()
            self._strikes.clear()

    def remaining(self, url: str) -> float:
        """Seconds until the site of *url* may be contacted again."""
        key = site_key(url)
        with self._lock:
            return max(0.0, self._until.get(key, 0.0) - self._clock())

    def note(self, url: str, response: Any) -> Optional[float]:
        """Record the outcome of a request to *url*.

        Returns the site's cooldown in seconds when *response* is a rate
        limit, else None. A success after the cooldown has ended clears the
        backoff, so the next 429 starts again from the shortest wait.
        """
        key = site_key(url)
        if not key:
            return None
        if not is_rate_limited(response):
            status = _status_code(response)
            if status is not None and status < 400:
                with self._lock:
                    if self._clock() >= self._until.get(key, 0.0):
                        self._strikes.pop(key, None)
            return None
        policy = self.policy
        retry_after = parse_retry_after(
            _retry_after_header(response), now=self._wall_clock
        )
        with self._lock:
            now = self._clock()
            until = self._until.get(key, 0.0)
            cooling = now < until
            # Answers to requests sent before the cooldown began say nothing
            # new: they don't make the backoff grow (five workers hitting a
            # 429 together are one strike, not five).
            strikes = self._strikes.get(key, 0) + (0 if cooling else 1)
            strikes = max(strikes, 1)
            self._strikes[key] = strikes
            if retry_after is not None:
                delay = retry_after
            elif cooling:
                delay = 0.0  # keep the cooldown already running
            else:
                full = min(
                    policy.backoff_cap,
                    policy.backoff_base * (2 ** min(strikes - 1, 30)),
                )
                delay = full / 2 + self._rng() * full / 2
            delay = min(max(delay, policy.min_cooldown), policy.max_cooldown)
            # Never shorten a cooldown another answer already set.
            self._until[key] = max(until, now + delay)
            return self._until[key] - now

    def wait(self, url: str, is_running: Optional[Callable[[], bool]] = None) -> bool:
        """Block until *url*'s site may be contacted. False if cancelled."""
        policy = self.policy
        waited = False
        while True:
            left = self.remaining(url)
            if left <= 0:
                break
            if is_running is not None and not is_running():
                return False
            self._sleep(min(policy.poll_interval, left))
            waited = True
        if waited and policy.resume_spread > 0:
            stagger = self._rng() * policy.resume_spread
            while stagger > 0:
                if is_running is not None and not is_running():
                    return False
                step = min(policy.poll_interval, stagger)
                self._sleep(step)
                stagger -= step
        return is_running is None or is_running()

    def pause(
        self, attempt: int, is_running: Optional[Callable[[], bool]] = None
    ) -> bool:
        """Back off before retry *attempt* (0-based) after an ordinary failure.

        For server errors and dropped connections, which aren't rate limits
        and set no cooldown: the same growing, jittered schedule, so a
        struggling server isn't asked again right away. False if cancelled.
        """
        policy = self.policy
        full = min(
            policy.backoff_cap, policy.backoff_base * (2 ** min(max(attempt, 0), 30))
        )
        left = full / 2 + self._rng() * full / 2
        while left > 0:
            if is_running is not None and not is_running():
                return False
            step = min(policy.poll_interval, left)
            self._sleep(step)
            left -= step
        return is_running is None or is_running()


def is_transient_status(status: Any) -> bool:
    """Whether an HTTP status is worth retrying later (timeouts, 5xx)."""
    return isinstance(status, int) and (status >= 500 or status in (408, 425))


rate_limiter = SiteRateLimiter()


# Other modules go through these instead of importing ``rate_limiter`` by
# name, so they always reach the one current limiter.


def cooldown_remaining(url: str) -> float:
    """Seconds until *url*'s site may be contacted again."""
    return rate_limiter.remaining(url)


def backoff_pause(
    attempt: int, is_running: Optional[Callable[[], bool]] = None
) -> bool:
    """``SiteRateLimiter.pause`` on the shared limiter."""
    return rate_limiter.pause(attempt, is_running)


def rate_limit_tries() -> int:
    """How many times one request is sent before a rate limit is final."""
    return rate_limiter.policy.max_retries + 1


_NOTED = "_kd_rate_limit_noted"


def note_response(response: Any, url: Optional[str] = None) -> Optional[float]:
    """Record *response* with the shared limiter, once per response.

    Called by the session hook on every response and again by
    ``polite_get``; the mark on the response keeps one answer from counting
    twice. Returns the site's cooldown when it is a rate limit.
    """
    if response is None or getattr(response, _NOTED, False) is True:
        return (
            rate_limiter.remaining(url) if url and is_rate_limited(response) else None
        )
    target = getattr(response, "url", None)
    if not isinstance(target, str) or not target:
        target = url
    if not target:
        return None
    try:
        setattr(response, _NOTED, True)
    except Exception:
        pass  # a response that takes no attributes is just noted again
    return rate_limiter.note(target, response)


def rate_limit_hook(response: Any, *args: Any, **kwargs: Any) -> None:
    """A requests response hook that feeds every answer to the limiter."""
    try:
        note_response(response)
    except Exception:
        pass  # never let bookkeeping break a request


def _close_quietly(response: Any) -> None:
    close = getattr(response, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass


def polite_get(
    session: Any,
    url: str,
    *,
    is_running: Optional[Callable[[], bool]] = None,
    on_rate_limited: Optional[Callable[[str, float, int, int], None]] = None,
    max_rate_limit_retries: Optional[int] = None,
    max_wait: Optional[float] = None,
    guard: Optional[ContextManager] = None,
    **kwargs: Any,
) -> Any:
    """``session.get(url, **kwargs)`` that respects the site's rate limit.

    Before sending, waits until the site's cooldown is over. A rate-limited
    answer is recorded, and the request is sent again once the cooldown
    ends, up to *max_rate_limit_retries* times (the policy's by default);
    these don't count towards the caller's own retries. After that the last
    rate-limited response is returned for the caller to report.

    * *is_running*: checked while waiting; when it turns False,
      ``RequestCancelled`` is raised and nothing more is sent.
    * *on_rate_limited(site, wait_seconds, retry, max_retries)*: called
      before each wait caused by this request's own 429, e.g. to log it.
    * *max_wait*: wait at most this long for a cooldown. Longer cooldowns
      raise ``RateLimitedError`` at once; use 0 on the GUI thread, which
      must never block.
    * *guard*: held only while sending (not while waiting), for the
      connection lock some callers need.
    """
    limit = (
        rate_limiter.policy.max_retries
        if max_rate_limit_retries is None
        else max(0, max_rate_limit_retries)
    )
    retries = 0
    while True:
        left = rate_limiter.remaining(url)
        if max_wait is not None and left > max_wait:
            raise RateLimitedError(site_key(url), left)
        if not rate_limiter.wait(url, is_running):
            raise RequestCancelled(f"Cancelled while waiting for {site_key(url)}")
        with guard if guard is not None else contextlib.nullcontext():
            if is_running is not None and not is_running():
                raise RequestCancelled(f"Cancelled before contacting {site_key(url)}")
            response = session.get(url, **kwargs)
        note_response(response, url)
        if not is_rate_limited(response) or retries >= limit:
            return response
        retries += 1
        _close_quietly(response)
        if on_rate_limited is not None:
            on_rate_limited(site_key(url), rate_limiter.remaining(url), retries, limit)
