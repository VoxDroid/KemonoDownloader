"""Rate-limit handling (issues #100 and #101).

When a site answers HTTP 429, every request to it pauses until the cooldown
ends (the server's Retry-After, or a jittered exponential backoff), waits don't
use up anyone's normal retries, nothing is sent during a cooldown, a site that
keeps refusing is reported clearly, and a creator's post list is never
silently cut short.
"""

import asyncio
import contextlib
import email.utils
import json
import os
import threading
from types import SimpleNamespace

import pytest
import requests

from kemonodownloader import (
    creator_downloader as cd,
    download_policy as dp,
    kd_thumbnaildl as td,
    post_downloader as pd,
)
from kemonodownloader.download_policy import (
    DEFAULT_RATE_LIMIT_POLICY,
    RateLimitedError,
    RateLimitPolicy,
    RequestCancelled,
    SiteRateLimiter,
    is_rate_limit_error,
    is_rate_limited,
    is_transient_status,
    note_response,
    parse_retry_after,
    polite_get,
    rate_limit_hook,
    site_key,
)

WALL = 1_000_000_000.0  # 2001-09-09 01:46:40 UTC


# ------------------------------------------------------------------ doubles


class FakeTime:
    """A clock that only moves when something sleeps."""

    def __init__(self):
        self.now = 1000.0
        self.slept = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds


class Resp:
    def __init__(self, status=200, body=b"", headers=None, url=""):
        self.status_code = status
        self.content = body
        self.text = body.decode("utf-8", "replace")
        self.headers = headers or {}
        self.url = url
        self.closed = False

    def json(self):
        return json.loads(self.text)

    def close(self):
        self.closed = True

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error", response=self)

    def iter_content(self, chunk_size=8192):
        yield self.content


class Session:
    """Answers each GET with ``respond(url, call_number)``; records calls."""

    def __init__(self, respond):
        self.respond = respond
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(url)
        response = self.respond(url, len(self.calls))
        if not response.url:
            response.url = url
        return response


def too_many(retry_after=None):
    headers = {} if retry_after is None else {"Retry-After": retry_after}
    return Resp(429, headers=headers)


@pytest.fixture
def fake_limiter(monkeypatch):
    """The shared limiter, on a fake clock and with the real timings."""
    fake = FakeTime()
    limiter = SiteRateLimiter(
        policy=DEFAULT_RATE_LIMIT_POLICY,
        clock=fake.clock,
        wall_clock=lambda: WALL,
        sleep=fake.sleep,
        rng=lambda: 0.5,
    )
    monkeypatch.setattr(dp, "rate_limiter", limiter)
    return limiter, fake


# --------------------------------------------------------------- site keys


@pytest.mark.parametrize(
    "url, key",
    [
        ("https://kemono.cr/api/v1/x", "kemono.cr"),
        ("https://n1.kemono.cr/data/a.png", "kemono.cr"),
        ("https://N4.Kemono.CR./data/a.png", "kemono.cr"),
        ("https://www.coomer.st/x", "coomer.st"),
        ("https://img.pawchive.pw/x", "pawchive.pw"),
        ("http://127.0.0.1:8080/x", "127.0.0.1"),
        ("http://[::1]/x", "::1"),
        ("http://localhost/x", "localhost"),
        ("not a url", ""),
    ],
)
def test_site_key(url, key):
    assert site_key(url) == key


# ------------------------------------------------------------- Retry-After


@pytest.mark.parametrize(
    "value, expected",
    [
        ("120", 120.0),
        (" 5 ", 5.0),
        ("1.5", 1.5),
        ("0", 0.0),
        (b"30", 30.0),
        ("-1", None),
        ("nan", None),
        ("inf", None),
        ("", None),
        (None, None),
        (30, None),  # header values are text
        ("soon", None),
        (email.utils.formatdate(WALL + 90, usegmt=True), 90.0),
        (email.utils.formatdate(WALL - 90, usegmt=True), 0.0),  # already past
        ("Sun, 09 Sep 2001 01:48:10", 90.0),  # no zone: read as UTC
    ],
)
def test_parse_retry_after(value, expected):
    assert parse_retry_after(value, now=lambda: WALL) == expected


def test_what_counts_as_a_rate_limit():
    assert is_rate_limited(Resp(429))
    assert is_rate_limited(Resp(503, headers={"Retry-After": "10"}))
    assert not is_rate_limited(Resp(503))  # an ordinary server error
    assert not is_rate_limited(Resp(503, headers={"Retry-After": "later"}))
    assert not is_rate_limited(Resp(200))
    assert not is_rate_limited(None)
    assert not is_rate_limited(SimpleNamespace(status_code=True))
    assert not is_rate_limited(SimpleNamespace(status_code="429"))
    assert not is_rate_limited(SimpleNamespace())  # no status at all
    assert is_rate_limit_error(requests.HTTPError(response=Resp(429)))
    assert is_rate_limit_error(RateLimitedError("kemono.cr", 3))
    assert not is_rate_limit_error(requests.HTTPError(response=Resp(500)))
    assert not is_rate_limit_error(ValueError())
    assert is_transient_status(502) and is_transient_status(408)
    assert not is_transient_status(404) and not is_transient_status(None)


# ---------------------------------------------------------------- cooldowns


def test_retry_after_sets_the_cooldown(fake_limiter):
    limiter, _ = fake_limiter
    assert limiter.note("https://kemono.cr/a", too_many("30")) == 30
    assert limiter.remaining("https://kemono.cr/b") == 30


def test_cooldowns_are_capped_and_have_a_floor(fake_limiter):
    limiter, fake = fake_limiter
    assert limiter.note("https://kemono.cr/a", too_many("86400")) == 300
    fake.now += 300
    assert limiter.note("https://kemono.cr/a", too_many("0")) == 1


def test_backoff_grows_without_retry_after_and_is_capped(fake_limiter):
    limiter, fake = fake_limiter
    delays = []
    for _ in range(8):
        delays.append(limiter.note("https://kemono.cr/a", too_many()))
        fake.now += delays[-1]  # the next 429 comes after the cooldown
    # rng() is 0.5, so each wait is 3/4 of 2, 4, 8, ... capped at 60.
    assert delays == [1.5, 3, 6, 12, 24, 45, 45, 45]


def test_answers_in_flight_during_a_cooldown_are_one_strike(fake_limiter):
    limiter, fake = fake_limiter
    first = limiter.note("https://kemono.cr/a", too_many())
    for _ in range(4):  # four other workers' requests, sent before it began
        limiter.note("https://n2.kemono.cr/b", too_many())
    fake.now += first
    # The next real strike is the second, not the sixth.
    assert limiter.note("https://kemono.cr/a", too_many()) == 3


def test_a_cooldown_is_never_shortened(fake_limiter):
    limiter, _ = fake_limiter
    limiter.note("https://kemono.cr/a", too_many("120"))
    limiter.note("https://kemono.cr/a", too_many("5"))
    assert limiter.remaining("https://kemono.cr/a") == 120


def test_a_success_after_the_cooldown_resets_the_backoff(fake_limiter):
    limiter, fake = fake_limiter
    for _ in range(3):
        fake.now += limiter.note("https://kemono.cr/a", too_many())
    limiter.note("https://kemono.cr/a", Resp(200))
    assert limiter.note("https://kemono.cr/a", too_many()) == 1.5


def test_a_success_during_the_cooldown_does_not_reset_it(fake_limiter):
    limiter, fake = fake_limiter
    fake.now += limiter.note("https://kemono.cr/a", too_many())
    second = limiter.note("https://kemono.cr/a", too_many())
    limiter.note("https://kemono.cr/a", Resp(200))  # sent before the 429
    assert limiter.remaining("https://kemono.cr/a") == second
    fake.now += second
    assert limiter.note("https://kemono.cr/a", too_many()) == 6


def test_errors_that_are_not_rate_limits_change_nothing(fake_limiter):
    limiter, _ = fake_limiter
    assert limiter.note("https://kemono.cr/a", Resp(500)) is None
    assert limiter.note("https://kemono.cr/a", Resp(404)) is None
    assert limiter.remaining("https://kemono.cr/a") == 0


def test_a_cooldown_covers_the_whole_site_and_only_that_site(fake_limiter):
    limiter, _ = fake_limiter
    limiter.note("https://n3.kemono.cr/data/f.zip", too_many("20"))
    assert limiter.remaining("https://kemono.cr/api/v1/patreon/user/1") == 20
    assert limiter.remaining("https://n1.kemono.cr/data/g.zip") == 20
    assert limiter.remaining("https://coomer.st/api/v1/x") == 0


def test_wait_returns_at_once_without_a_cooldown(fake_limiter):
    limiter, fake = fake_limiter
    assert limiter.wait("https://kemono.cr/a")
    assert fake.slept == []


def test_wait_sleeps_through_the_cooldown_then_spreads_the_restart(fake_limiter):
    limiter, fake = fake_limiter
    limiter.note("https://kemono.cr/a", too_many("10"))
    start = fake.now
    assert limiter.wait("https://kemono.cr/b")
    # 10 s of cooldown, then rng() * resume_spread = 0.5 s of stagger, all
    # in slices short enough to notice a cancel.
    assert fake.now - start == pytest.approx(10.5)
    assert max(fake.slept) <= DEFAULT_RATE_LIMIT_POLICY.poll_interval


def test_wait_stops_promptly_when_cancelled(fake_limiter):
    limiter, fake = fake_limiter
    limiter.note("https://kemono.cr/a", too_many("300"))
    start = fake.now
    assert not limiter.wait("https://kemono.cr/a", lambda: fake.now - start < 2)
    assert fake.now - start < 2.2


def test_pause_backs_off_and_can_be_cancelled(fake_limiter):
    limiter, fake = fake_limiter
    start = fake.now
    assert limiter.pause(0)
    assert limiter.pause(1)
    assert fake.now - start == pytest.approx(1.5 + 3)
    assert not limiter.pause(10, lambda: False)


def test_reset_forgets_everything(fake_limiter):
    limiter, _ = fake_limiter
    limiter.note("https://kemono.cr/a", too_many("50"))
    limiter.reset()
    assert limiter.remaining("https://kemono.cr/a") == 0


def test_the_limiter_is_thread_safe():
    limiter = SiteRateLimiter(policy=RateLimitPolicy(max_cooldown=0.5))

    def hammer():
        for _ in range(200):
            limiter.note("https://kemono.cr/a", too_many("0.2"))
            limiter.remaining("https://n1.kemono.cr/b")

    workers = [threading.Thread(target=hammer) for _ in range(8)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()
    assert 0 < limiter.remaining("https://kemono.cr/a") <= 0.5


# ----------------------------------------------------- recording responses


def test_each_response_is_counted_once(fake_limiter):
    limiter, fake = fake_limiter
    response = too_many()
    response.url = "https://kemono.cr/a"
    rate_limit_hook(response)  # the session hook
    first = limiter.remaining("https://kemono.cr/a")
    fake.now += first
    note_response(response)  # polite_get seeing the same answer
    assert limiter.remaining("https://kemono.cr/a") == 0  # not a 2nd strike


def test_the_final_url_decides_the_site(fake_limiter):
    limiter, _ = fake_limiter
    response = too_many("7")
    response.url = "https://n2.coomer.st/data/x"  # after a redirect
    note_response(response, "https://coomer.st/data/x")
    assert limiter.remaining("https://coomer.st/api") == 7


def test_odd_responses_never_break_the_hook(fake_limiter):
    rate_limit_hook(None)
    rate_limit_hook(object())
    rate_limit_hook(SimpleNamespace(status_code=429))  # no url anywhere

    class Frozen:
        __slots__ = ("status_code", "url", "headers")

        def __init__(self):
            self.status_code = 429
            self.url = "https://kemono.cr/a"
            self.headers = {"Retry-After": "4"}

    rate_limit_hook(Frozen())  # takes no attributes: noted, not marked
    assert fake_limiter[0].remaining("https://kemono.cr/a") == 4


def test_sessions_report_to_the_limiter(qapp):
    from kemonodownloader import kd_network

    kd_network._thread_local.__dict__.clear()
    session = kd_network.get_session()
    assert rate_limit_hook in session.hooks["response"]
    socks = kd_network.get_session(
        SimpleNamespace(
            get_proxy_settings=lambda: {"https": "socks5h://127.0.0.1:9050"}
        )
    )
    assert socks is not session
    assert rate_limit_hook in socks.hooks["response"]
    # Asking again doesn't stack the hook.
    assert kd_network.get_session().hooks["response"].count(rate_limit_hook) == 1
    # Dropped connections are still retried, but urllib3 no longer sleeps
    # out a Retry-After on its own (uncancellable, and unseen by the limiter).
    for each in (session, socks):
        retries = each.get_adapter("https://kemono.cr/").max_retries
        assert retries.total == 3
        assert retries.respect_retry_after_header is False
        assert not retries.is_retry("GET", 429, has_retry_after=True)
        assert not retries.is_retry("GET", 503, has_retry_after=True)
    kd_network._thread_local.__dict__.clear()


def test_a_real_session_against_a_real_server(qapp):
    """The hook and polite_get with real sockets, redirects and headers."""
    import http.server

    from kemonodownloader import kd_network

    hits = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (http.server API)
            hits.append(self.path)
            if self.path == "/redirect":
                self.send_response(302)
                self.send_header("Location", "/limited")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if self.path == "/limited" and hits.count("/limited") == 1:
                self.send_response(429)
                self.send_header("Retry-After", "1")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    kd_network._thread_local.__dict__.clear()
    try:
        session = kd_network.get_session()
        # A plain request: the hook alone records the 429 behind a redirect.
        response = session.get(f"{base}/redirect", timeout=5)
        assert response.status_code == 429
        assert dp.rate_limiter.remaining(base) > 0
        # polite_get waits that cooldown out, then succeeds.
        response = polite_get(session, f"{base}/limited", timeout=5)
        assert response.status_code == 200 and response.text == "ok"
        assert hits == ["/redirect", "/limited", "/limited"]
    finally:
        server.shutdown()
        server.server_close()
        kd_network._thread_local.__dict__.clear()


# --------------------------------------------------------------- polite_get


def test_polite_get_passes_ordinary_answers_through(fake_limiter):
    session = Session(lambda url, n: Resp(200))
    response = polite_get(session, "https://kemono.cr/a", timeout=5)
    assert response.status_code == 200 and session.calls == ["https://kemono.cr/a"]
    assert fake_limiter[1].slept == []


def test_polite_get_waits_out_a_429_and_retries(fake_limiter):
    _, fake = fake_limiter
    answers = [too_many("12"), Resp(200)]
    session = Session(lambda url, n: answers[n - 1])
    reports = []
    response = polite_get(
        session,
        "https://kemono.cr/a",
        on_rate_limited=lambda *args: reports.append(args),
    )
    assert response.status_code == 200
    assert answers[0].closed  # the refused answer's connection is released
    assert reports == [("kemono.cr", 12, 1, DEFAULT_RATE_LIMIT_POLICY.max_retries)]
    assert sum(fake.slept) == pytest.approx(12.5)


def test_polite_get_gives_up_after_its_limit(fake_limiter):
    session = Session(lambda url, n: too_many())
    response = polite_get(session, "https://kemono.cr/a")
    assert response.status_code == 429
    assert len(session.calls) == DEFAULT_RATE_LIMIT_POLICY.max_retries + 1


def test_polite_get_can_skip_retrying(fake_limiter):
    session = Session(lambda url, n: too_many())
    assert polite_get(session, "https://kemono.cr/a", max_rate_limit_retries=0)
    assert len(session.calls) == 1


def test_polite_get_sends_nothing_during_another_workers_cooldown(fake_limiter):
    limiter, fake = fake_limiter
    limiter.note("https://n1.kemono.cr/x", too_many("40"))
    sent_at = []
    session = Session(lambda url, n: sent_at.append(fake.now) or Resp(200))
    polite_get(session, "https://kemono.cr/api/v1/y")
    assert sent_at[0] >= 1000.0 + 40


def test_polite_get_never_blocks_when_told_not_to_wait(fake_limiter):
    limiter, fake = fake_limiter
    limiter.note("https://kemono.cr/x", too_many("40"))
    session = Session(lambda url, n: Resp(200))
    with pytest.raises(RateLimitedError, match="try again in 40 s"):
        polite_get(session, "https://kemono.cr/y", max_wait=0)
    assert session.calls == [] and fake.slept == []


def test_polite_get_stops_when_cancelled_while_waiting(fake_limiter):
    limiter, fake = fake_limiter
    limiter.note("https://kemono.cr/x", too_many("60"))
    session = Session(lambda url, n: Resp(200))
    with pytest.raises(RequestCancelled):
        polite_get(session, "https://kemono.cr/y", is_running=lambda: fake.now < 1005)
    assert session.calls == []


def test_polite_get_does_not_send_after_a_cancel(fake_limiter):
    session = Session(lambda url, n: Resp(200))
    with pytest.raises(RequestCancelled):
        polite_get(session, "https://kemono.cr/y", is_running=lambda: False)
    assert session.calls == []
    # Cancelling is a RequestException, so every existing handler copes.
    assert issubclass(RequestCancelled, requests.RequestException)
    assert issubclass(RateLimitedError, requests.RequestException)


def test_polite_get_holds_the_guard_only_while_sending(fake_limiter):
    limiter, _ = fake_limiter
    limiter.note("https://kemono.cr/x", too_many("5"))
    lock = threading.Lock()
    held = []
    session = Session(lambda url, n: held.append(lock.locked()) or Resp(200))
    original_sleep = limiter._sleep

    def sleep(seconds):
        held.append(("waiting", lock.locked()))
        original_sleep(seconds)

    limiter._sleep = sleep
    polite_get(session, "https://kemono.cr/y", guard=lock)
    assert held[-1] is True  # sending: held
    assert all(entry == ("waiting", False) for entry in held[:-1])  # waiting: free
    assert not lock.locked()


def test_polite_get_copes_with_bare_responses(fake_limiter):
    class Bare:  # no headers, url or close(), like many test doubles
        status_code = 429

    class S:
        calls = 0

        def get(self, url, **kwargs):
            S.calls += 1
            return Bare() if S.calls == 1 else Resp(200)

    assert polite_get(S(), "https://kemono.cr/a").status_code == 200
    assert S.calls == 2


# ------------------------------------------------------ Creator: downloads


def creator_dummy(tmp_path, max_retries=50):
    logs, completed = [], []
    dummy = SimpleNamespace(
        service="patreon",
        creator_id="1",
        post_titles_map={},
        auto_rename_enabled=False,
        settings=SimpleNamespace(
            settings_tab=None, file_download_max_retries=max_retries
        ),
        files_to_download=[],
        files_to_posts_map={},
        domain_config={"referer": "https://kemono.cr/"},
        is_running=True,
        hash_db=SimpleNamespace(lookup=lambda h: None, store=lambda *a, **k: None),
        failed_files={},
        failed_files_lock=contextlib.nullcontext(),
        unavailable_files=set(),
        completed_files=set(),
        completed_files_lock=contextlib.nullcontext(),
        _ssl_lock=contextlib.nullcontext(),
        _safe_emit=lambda signal, *args: signal.emit(*args),
        log=SimpleNamespace(
            emit=lambda message, level="INFO": logs.append((level, message))
        ),
        file_progress=SimpleNamespace(emit=lambda *a: None),
        file_completed=SimpleNamespace(emit=lambda *a: completed.append(a)),
        check_post_completion=lambda url: None,
        download_text=False,
        generate_filename_and_folder=lambda *a: (str(tmp_path), "out.bin"),
    )
    return dummy, logs, completed


def run_creator_download(dummy, file_url):
    dummy.files_to_download = [file_url]
    dummy.files_to_posts_map = {file_url: "101"}
    asyncio.run(cd.CreatorDownloadThread.download_file(dummy, file_url, "", 0, 1))


def test_creator_file_429_does_not_use_up_attempts(monkeypatch, tmp_path):
    session = Session(lambda url, n: too_many("1") if n == 1 else Resp(200, b"hello"))
    monkeypatch.setattr(cd, "get_session", lambda s=None: session)
    dummy, logs, completed = creator_dummy(tmp_path, max_retries=1)
    run_creator_download(dummy, "https://kemono.cr/data/a/out.bin")
    # One attempt allowed, and it still succeeded after the rate limit.
    assert not dummy.failed_files
    assert (tmp_path / "out.bin").read_bytes() == b"hello"
    assert any("limiting requests" in m for level, m in logs if level == "WARNING")


def test_creator_file_kept_rate_limited_fails_once_clearly(monkeypatch, tmp_path):
    session = Session(lambda url, n: too_many())
    monkeypatch.setattr(cd, "get_session", lambda s=None: session)
    dummy, logs, completed = creator_dummy(tmp_path, max_retries=50)
    run_creator_download(dummy, "https://kemono.cr/data/a/out.bin")
    # polite_get's retries only: not 50 attempts of them.
    assert len(session.calls) == dp.rate_limiter.policy.max_retries + 1
    assert list(dummy.failed_files) == ["https://kemono.cr/data/a/out.bin"]
    assert completed == [(0, "https://kemono.cr/data/a/out.bin", False)]
    errors = [m for level, m in logs if level == "ERROR"]
    assert len(errors) == 1 and "kept limiting requests" in errors[0]
    assert not (tmp_path / "out.bin").exists()


def test_creator_file_rate_limit_from_the_direct_server_keeps_it(monkeypatch, tmp_path):
    file_url = "https://kemono.cr/data/b/out.bin"
    direct = "https://n2.kemono.cr/data/b/out.bin"
    cd.remember_direct_url(file_url, direct)
    try:
        session = Session(lambda url, n: too_many() if n == 1 else Resp(200, b"ok"))
        monkeypatch.setattr(cd, "get_session", lambda s=None: session)
        dummy, _, _ = creator_dummy(tmp_path)
        run_creator_download(dummy, file_url)
        # A 429 is not a broken server: the direct URL stays in use.
        assert session.calls == [direct, direct]
        assert cd.direct_url_for(file_url) == direct
    finally:
        cd.forget_direct_url(file_url)


def test_creator_file_cancelled_while_rate_limited(monkeypatch, tmp_path):
    dummy, logs, completed = creator_dummy(tmp_path)

    def respond(url, n):
        dummy.is_running = False  # the user cancels during the cooldown
        return too_many("5")

    session = Session(respond)
    monkeypatch.setattr(cd, "get_session", lambda s=None: session)
    run_creator_download(dummy, "https://kemono.cr/data/a/out.bin")
    assert len(session.calls) == 1
    assert not [
        m for level, m in logs if level in ("ERROR", "WARNING") and "limit" not in m
    ]
    assert completed and completed[0][2] is False


# ----------------------------------------------- Creator: post details


def file_prep(settings=None):
    class Check:
        def isChecked(self):
            return True

    return cd.FilePreparationThread(
        ["7"],
        {},
        {".jpg": Check()},
        True,
        True,
        True,
        settings or SimpleNamespace(post_data_max_retries=7, settings_tab=None),
    )


def test_post_details_kept_rate_limited_stop_without_multiplying(monkeypatch):
    session = Session(lambda url, n: too_many())
    monkeypatch.setattr(cd, "get_session", lambda s=None: session)
    thread = file_prep()
    logs = []
    thread.log.connect(lambda m, level: logs.append((level, m)))
    assert (
        thread.fetch_and_detect_files("7", "https://kemono.cr/patreon/user/1") is None
    )
    # Not 7 post retries x 9 tries each.
    assert len(session.calls) == dp.rate_limiter.policy.max_retries + 1
    assert any(level == "ERROR" and "post 7" in m for level, m in logs)


def test_post_details_cancelled_while_rate_limited(monkeypatch):
    thread = file_prep()

    def respond(url, n):
        thread.stop()
        return too_many("5")

    session = Session(respond)
    monkeypatch.setattr(cd, "get_session", lambda s=None: session)
    assert (
        thread.fetch_and_detect_files("7", "https://kemono.cr/patreon/user/1") is None
    )
    assert len(session.calls) == 1


# ------------------------------------------------ Creator: the post list


def page(count, start=0):
    posts = [{"id": str(start + i), "title": f"Post {start + i}"} for i in range(count)]
    return Resp(200, json.dumps(posts).encode())


def run_listing(monkeypatch, respond, max_pages=200, api_retries=3):
    session = Session(respond)
    monkeypatch.setattr(cd, "get_session", lambda s=None: session)
    monkeypatch.setattr(cd.time, "sleep", lambda s: None)
    settings = SimpleNamespace(
        creator_posts_max_attempts=max_pages,
        api_request_max_retries=api_retries,
        settings_tab=None,
    )
    thread = cd.PostDetectionThread("https://kemono.cr/patreon/user/1", {}, settings)
    logs, finished = [], []
    thread.log.connect(lambda m, level: logs.append((level, m)))
    thread.finished.connect(finished.append)
    thread.run()
    return session, logs, finished


def offset_of(url):
    for marker in ("?o=", "&o=", "?offset=", "&offset="):
        if marker in url:
            return int(url.split(marker, 1)[1].split("&")[0])
    return 0


def test_a_429_mid_list_waits_and_loads_everything(monkeypatch):
    def respond(url, n):
        if offset_of(url) == 50 and n == 2:
            return too_many("1")
        return page(50, 0) if offset_of(url) == 0 else page(20, 50)

    session, logs, finished = run_listing(monkeypatch, respond)
    assert len(finished[0]) == 70
    assert not [m for level, m in logs if level == "WARNING" and "incomplete" in m]


def test_a_list_kept_rate_limited_is_reported_incomplete(monkeypatch):
    def respond(url, n):
        return page(50, 0) if offset_of(url) == 0 else too_many()

    session, logs, finished = run_listing(monkeypatch, respond)
    # The 50 posts already read are kept, and the user is told the truth.
    assert len(finished[0]) == 50
    warnings = [m for level, m in logs if level == "WARNING"]
    assert any("Stopped loading posts at 50" in m for m in warnings)
    assert not any("last page" in m.lower() for level, m in logs if level == "INFO")
    # A 429 is not a sign of a wrong URL format: no other format was tried.
    second_page = [url for url in session.calls if offset_of(url) == 50]
    assert len(set(second_page)) == 1
    assert len(second_page) == dp.rate_limiter.policy.max_retries + 1


def test_a_list_rate_limited_from_the_start_is_an_error(monkeypatch):
    session, logs, finished = run_listing(monkeypatch, lambda url, n: too_many())
    assert finished == [[]]
    errors = [m for level, m in logs if level == "ERROR"]
    assert len(errors) == 1 and "kept limiting" in errors[0]
    assert "https://kemono.cr/patreon/user/1" in errors[0]  # names the creator
    assert len(set(session.calls)) == 1


def test_creator_link_validation_stops_on_a_lasting_rate_limit(monkeypatch):
    session = Session(lambda url, n: too_many())
    monkeypatch.setattr(cd, "get_session", lambda s=None: session)
    thread = cd.ValidationThread(
        "https://kemono.cr/patreon/user/1",
        SimpleNamespace(api_request_max_retries=3, settings_tab=None),
    )
    logs, results = [], []
    thread.log.connect(lambda m, level: logs.append((level, m)))
    thread.result.connect(results.append)
    thread.run()
    assert results == [False]
    # One polite_get's worth of tries, not 3 validation attempts of them.
    assert len(session.calls) == dp.rate_limiter.policy.max_retries + 1
    assert any(level == "ERROR" and "kept limiting" in m for level, m in logs)


def test_server_errors_mid_list_are_retried_then_reported(monkeypatch):
    def respond(url, n):
        return page(50, 0) if offset_of(url) == 0 else Resp(502)

    session, logs, finished = run_listing(monkeypatch, respond, api_retries=3)
    assert len(finished[0]) == 50
    second_page = [url for url in session.calls if offset_of(url) == 50]
    assert len(second_page) == 3 * 4  # 3 rounds of the 4 URL formats
    assert any(
        level == "WARNING" and "kept failing (HTTP 502)" in m for level, m in logs
    )


def test_a_server_error_that_clears_up_loses_nothing(monkeypatch):
    def respond(url, n):
        if offset_of(url) == 0:
            return page(50, 0)
        return Resp(503) if n <= 5 else page(10, 50)

    _, logs, finished = run_listing(monkeypatch, respond)
    assert len(finished[0]) == 60
    assert not [m for level, m in logs if level == "WARNING"]


def test_a_definite_no_past_the_first_page_still_ends_the_list(monkeypatch):
    def respond(url, n):
        return page(50, 0) if offset_of(url) == 0 else Resp(400)

    session, logs, finished = run_listing(monkeypatch, respond)
    assert len(finished[0]) == 50
    assert any(level == "INFO" and "last page" in m.lower() for level, m in logs)
    assert len([u for u in session.calls if offset_of(u) == 50]) == 4  # one round


def test_network_errors_mid_list_are_reported_not_hidden(monkeypatch):
    def respond(url, n):
        if offset_of(url) == 0:
            return page(50, 0)
        raise requests.ConnectionError("connection reset")

    _, logs, finished = run_listing(monkeypatch, respond)
    assert len(finished[0]) == 50
    assert any(level == "WARNING" and "connection reset" in m for level, m in logs)


def test_hitting_the_page_limit_is_reported(monkeypatch):
    _, logs, finished = run_listing(
        monkeypatch, lambda url, n: page(50, offset_of(url)), max_pages=2
    )
    assert len(finished[0]) == 100
    assert any(
        level == "WARNING"
        and "Stopped after 2 pages (100 posts)" in m
        and "Creator Posts Max Attempts" in m
        for level, m in logs
    )


def test_the_list_ending_on_the_last_allowed_page_is_not_a_warning(monkeypatch):
    def respond(url, n):
        return page(50, 0) if offset_of(url) == 0 else page(3, 50)

    _, logs, finished = run_listing(monkeypatch, respond, max_pages=2)
    assert len(finished[0]) == 53
    assert not [m for level, m in logs if level == "WARNING"]


# ------------------------------------------------------- Post tab


def test_post_api_get_waits_out_rate_limits_without_using_attempts(fake_limiter):
    session = Session(lambda url, n: too_many("3") if n < 3 else Resp(200))
    response = pd._robust_api_get(lambda: session, "https://kemono.cr/api/p", 1)
    assert response.status_code == 200 and len(session.calls) == 3


def test_post_api_get_returns_the_refusal_for_the_caller_to_report(fake_limiter):
    session = Session(lambda url, n: too_many())
    response = pd._robust_api_get(lambda: session, "https://kemono.cr/api/p", 3)
    assert is_rate_limited(response)
    assert len(session.calls) == DEFAULT_RATE_LIMIT_POLICY.max_retries + 1


def test_post_api_get_stops_at_once_for_a_missing_post(fake_limiter):
    session = Session(lambda url, n: Resp(404))
    assert pd._robust_api_get(lambda: session, "https://kemono.cr/api/p", 5) is None
    assert len(session.calls) == 1


def test_post_api_get_backs_off_on_server_errors(fake_limiter):
    _, fake = fake_limiter
    session = Session(lambda url, n: Resp(500) if n == 1 else Resp(200))
    response = pd._robust_api_get(lambda: session, "https://kemono.cr/api/p", 3)
    assert response.status_code == 200
    assert sum(fake.slept) == pytest.approx(1.5)


def test_post_api_get_on_the_gui_thread_never_waits(fake_limiter):
    limiter, fake = fake_limiter
    session = Session(lambda url, n: too_many("9"))
    with pytest.raises(RateLimitedError, match="try again in 9 s"):
        pd._robust_api_get(
            lambda: session,
            "https://kemono.cr/api/p",
            3,
            max_wait=0,
            rate_limit_retries=0,
        )
    with pytest.raises(RateLimitedError):  # now cooling down: nothing is sent
        pd._robust_api_get(
            lambda: session,
            "https://kemono.cr/api/p",
            3,
            max_wait=0,
            rate_limit_retries=0,
        )
    assert len(session.calls) == 1 and fake.slept == []


def gui_post_tab(session, logs):
    settings_tab = SimpleNamespace(get_proxy_settings=lambda: None)
    tab = SimpleNamespace(
        parent=SimpleNamespace(settings_tab=settings_tab),
        append_log_to_console=lambda m, level="INFO": logs.append((level, m)),
        _create_thread_settings=lambda: SimpleNamespace(api_request_max_retries=3),
    )
    return tab


def test_post_link_check_on_the_gui_thread_never_waits(monkeypatch, fake_limiter):
    limiter, fake = fake_limiter
    session = Session(lambda url, n: too_many("25"))
    monkeypatch.setattr(pd, "get_session", lambda s=None: session)
    logs = []
    tab = gui_post_tab(session, logs)
    url = "https://kemono.cr/patreon/user/1/post/2"
    assert pd.PostDownloaderTab.check_post_url_validity(tab, url) is False
    assert pd.PostDownloaderTab.check_post_url_validity(tab, url) is False
    assert len(session.calls) == 1  # the second check sent nothing
    assert fake.slept == []
    assert any("try again in 25 s" in m for level, m in logs if level == "ERROR")


def test_post_file_list_on_the_gui_thread_explains_a_rate_limit(
    monkeypatch, fake_limiter
):
    session = Session(lambda url, n: too_many("8"))
    monkeypatch.setattr(pd, "get_session", lambda s=None: session)
    logs = []
    tab = gui_post_tab(session, logs)
    tab.make_robust_request = lambda url: pd.PostDownloaderTab.make_robust_request(
        tab, url
    )
    pd.PostDownloaderTab.display_files_for_post(
        tab, "https://kemono.cr/patreon/user/1/post/2"
    )
    assert len(session.calls) == 1 and fake_limiter[1].slept == []
    assert any("try again in 8 s" in m for level, m in logs if level == "ERROR")


def test_post_file_prep_stops_on_a_lasting_rate_limit(monkeypatch):
    session = Session(lambda url, n: too_many())
    monkeypatch.setattr(pd, "get_session", lambda s=None: session)

    class Check:
        def isChecked(self):
            return True

    thread = pd.FilePreparationThread(
        ["7"],
        {},
        {".jpg": Check()},
        {},
        "https://kemono.cr/patreon/user/1/post/7",
        SimpleNamespace(
            post_data_max_retries=7, api_request_max_retries=3, settings_tab=None
        ),
    )
    logs = []
    thread.log.connect(lambda m, level: logs.append((level, m)))
    assert thread.fetch_post_data("7") is None
    assert len(session.calls) == dp.rate_limiter.policy.max_retries + 1
    assert any(level == "ERROR" and "kept limiting" in m for level, m in logs)


def post_download_thread(tmp_path, max_retries=50):
    from kemonodownloader.download_utils import ThreadSettings

    folder = tmp_path / "dl"
    folder.mkdir()
    file_url = "https://kemono.cr/data/c/pic.png"
    thread = pd.DownloadThread(
        url="https://kemono.cr/patreon/user/1/post/1",
        download_folder=str(folder),
        selected_files=[file_url],
        files_to_posts_map={file_url: "1"},
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_id="1",
        settings=ThreadSettings(1, 1, max_retries, 1, 1, settings_tab=None),
        max_concurrent=1,
        auto_rename=False,
        download_text=False,
    )
    return thread, file_url, folder


def test_post_file_429_does_not_use_up_attempts(monkeypatch, tmp_path):
    session = Session(lambda url, n: too_many("1") if n == 1 else Resp(200, b"png"))
    monkeypatch.setattr(pd, "get_session", lambda s=None: session)
    thread, file_url, folder = post_download_thread(tmp_path, max_retries=1)
    thread.download_file(file_url, str(folder), 0, total_files=1)
    assert file_url in thread.completed_files


def test_post_file_kept_rate_limited_fails_once_clearly(monkeypatch, tmp_path):
    session = Session(lambda url, n: too_many())
    monkeypatch.setattr(pd, "get_session", lambda s=None: session)
    thread, file_url, folder = post_download_thread(tmp_path, max_retries=50)
    logs, done = [], []
    thread.log.connect(lambda m, level: logs.append((level, m)))
    thread.file_completed.connect(lambda i, u, ok: done.append(ok))
    thread.download_file(file_url, str(folder), 0, total_files=1)
    assert len(session.calls) == dp.rate_limiter.policy.max_retries + 1
    assert done == [False]
    assert [m for level, m in logs if level == "ERROR" and "kept limiting" in m]
    assert not any(files for _, _, files in os.walk(folder))


def test_post_file_cancelled_while_rate_limited(monkeypatch, tmp_path):
    thread, file_url, folder = post_download_thread(tmp_path)

    def respond(url, n):
        thread.stop()
        return too_many("5")

    session = Session(respond)
    monkeypatch.setattr(pd, "get_session", lambda s=None: session)
    thread.download_file(file_url, str(folder), 0, total_files=1)
    assert len(session.calls) == 1


# ------------------------------------------------------- Thumbnail tab


def test_thumbnail_download_waits_out_a_429(monkeypatch, tmp_path):
    session = Session(lambda url, n: too_many("1") if n == 1 else Resp(200, b"jpg"))
    monkeypatch.setattr(td, "get_session", lambda s=None: session)
    thread = td.ThumbnailDownloadThread(
        [("[Creator] Post (ID: 1)", "1", ["https://img.kemono.cr/thumbnail/a.jpg"])],
        str(tmp_path),
        download_text=False,
    )
    finished = []
    thread.download_finished.connect(lambda ok, total: finished.append((ok, total)))
    thread.run()
    assert finished == [(1, 1)] and len(session.calls) == 2


def test_thumbnail_listing_reports_an_incomplete_list(monkeypatch):
    posts = [
        {"id": str(i), "title": "t", "file": {"path": "/a.jpg"}} for i in range(50)
    ]

    def respond(url, n):
        if url.endswith("/profile"):
            return Resp(200, b'{"name": "Someone"}')
        if "o=0" in url:
            return Resp(200, json.dumps(posts).encode())
        return too_many()

    session = Session(respond)
    monkeypatch.setattr(td, "get_session", lambda s=None: session)
    thread = td.ThumbnailDetectionThread(
        ["https://kemono.cr/patreon/user/1"], "creator"
    )
    messages, found = [], []
    thread.log_message.connect(messages.append)
    thread.detection_finished.connect(found.append)
    thread.run()
    assert len(found[0]) == 50
    assert any("Stopped loading posts at 50" in m for m in messages)
    later = [u for u in session.calls if "o=50" in u]
    assert len(later) == dp.rate_limiter.policy.max_retries + 1


def test_thumbnail_listing_rate_limited_from_the_start(monkeypatch):
    def respond(url, n):
        return Resp(200, b"{}") if url.endswith("/profile") else too_many()

    session = Session(respond)
    monkeypatch.setattr(td, "get_session", lambda s=None: session)
    creator = "https://kemono.cr/patreon/user/1"
    thread = td.ThumbnailDetectionThread([creator], "creator")
    messages, found = [], []
    thread.log_message.connect(messages.append)
    thread.detection_finished.connect(found.append)
    thread.run()
    assert found == [[]]
    assert any("kept limiting" in m and creator in m for m in messages)
    # The format probe stops at the 429 instead of trying the other format.
    probes = [u for u in session.calls if u.endswith("?o=0")]
    assert len(set(probes)) == 1


def test_thumbnail_listing_retries_a_server_error(monkeypatch):
    first = [
        {"id": str(i), "title": "t", "file": {"path": "/a.jpg"}} for i in range(50)
    ]
    rest = [{"id": "x", "title": "t", "file": {"path": "/b.jpg"}}]

    def respond(url, n):
        if url.endswith("/profile"):
            return Resp(200, b"{}")
        if "o=0" in url:
            return Resp(200, json.dumps(first).encode())
        return Resp(502) if n <= 4 else Resp(200, json.dumps(rest).encode())

    session = Session(respond)
    monkeypatch.setattr(td, "get_session", lambda s=None: session)
    thread = td.ThumbnailDetectionThread(
        ["https://kemono.cr/patreon/user/1"], "creator"
    )
    found = []
    thread.detection_finished.connect(found.append)
    thread.run()
    assert len(found[0]) == 51
