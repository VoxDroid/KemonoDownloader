"""HTTP plumbing shared by every downloader: sessions, user agent and headers."""

import ctypes
import locale
import threading
from typing import Optional

import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter  # type: ignore[import]
from urllib3.util.retry import Retry

from kemonodownloader.domain_config import get_domain_config
from kemonodownloader.download_policy import rate_limit_hook

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    locale.setlocale(locale.LC_ALL, "C")

if hasattr(ctypes, "windll"):
    lcid = ctypes.windll.kernel32.GetUserDefaultLCID()
    system_language = locale.windows_locale.get(lcid, "en_US")
else:
    locale_info = locale.getlocale(locale.LC_CTYPE)
    system_language = locale_info[0] if locale_info and locale_info[0] else "en_US"

system_language = system_language.replace("_", "-")
accept_language = f"{system_language},en;q=0.9"

_user_agent: Optional[str] = None


def get_user_agent() -> str:
    global _user_agent
    if _user_agent is None:
        try:
            ua = UserAgent()
            _user_agent = ua.chrome
        except Exception:
            _user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
    assert _user_agent is not None
    return _user_agent


# Default headers (will be updated per request based on domain)
def _build_headers() -> dict:
    # Use the first/default domain's referer for the generic header set
    default_referer = get_domain_config("")["referer"]
    return {
        "User-Agent": get_user_agent(),
        "Referer": default_referer,
        "Accept": "text/css",
        "Accept-Language": accept_language,
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


HEADERS = None  # Built lazily via get_headers()


def get_headers() -> dict:
    global HEADERS
    if HEADERS is None:
        HEADERS = _build_headers()
    return HEADERS


def connection_retries() -> Retry:
    """Retry dropped connections, as ``max_retries=3`` did, minus Retry-After.

    By default urllib3 also answers a 429 or 503 that carries Retry-After by
    sleeping that long inside ``session.get`` and asking again, up to three
    times. That sleep can't be cancelled, holds the caller's connection lock
    meanwhile, and hides the 429 from the shared rate limiter, so other
    workers keep sending. The limiter handles those answers instead (see
    ``download_policy.polite_get``).
    """
    return Retry(total=3, respect_retry_after_header=False)


# Thread-local storage for per-thread sessions.
# Using a shared session across ThreadPoolExecutor workers causes
# concurrent SSL handshakes through the same connection pool, which
# triggers access-violation crashes on Windows (Python 3.14 / OpenSSL).
# Giving each thread its own session avoids the problem entirely.
_thread_local = threading.local()


def get_session(settings_tab=None):
    """Get or create a per-thread requests session with connection pooling.

    Each thread receives its own ``requests.Session`` (and connection pool)
    so that concurrent SSL handshakes never share underlying OpenSSL state,
    preventing access-violation crashes on Windows.
    """
    session: Optional[requests.Session] = getattr(_thread_local, "session", None)
    if session is None:
        session = requests.Session()
        # Disable automatic environment/registry proxy lookup.
        # On Windows, concurrent threads calling proxy_bypass_registry
        # via winreg cause "access violation" crashes.  The app manages
        # its own proxy settings through the Settings tab instead.
        session.trust_env = False
        # Configure connection pool (per-thread, so modest sizes suffice)
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=connection_retries(),
            pool_block=False,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        # Every answer reaches the shared rate limiter, so a 429 seen by any
        # request pauses the whole site, not just the request that got it.
        session.hooks["response"].append(rate_limit_hook)
        _thread_local.session = session

    # Set proxies if settings_tab is provided
    if settings_tab:
        proxies = settings_tab.get_proxy_settings()
        if proxies:
            # Check if this is a SOCKS proxy
            is_socks = any(
                proxy_url.startswith(("socks4://", "socks5://", "socks5h://"))
                for proxy_url in proxies.values()
            )
            if is_socks:
                # Reuse a per-thread SOCKS session to avoid creating one
                # on every call while still keeping threads isolated.
                socks_session: Optional[requests.Session] = getattr(
                    _thread_local, "socks_session", None
                )
                if socks_session is None:
                    socks_session = requests.Session()
                    socks_session.trust_env = False
                    socks_adapter = HTTPAdapter(
                        pool_connections=5,
                        pool_maxsize=5,
                        max_retries=connection_retries(),
                        pool_block=False,
                    )
                    socks_session.mount("http://", socks_adapter)
                    socks_session.mount("https://", socks_adapter)
                    socks_session.hooks["response"].append(rate_limit_hook)
                    _thread_local.socks_session = socks_session
                socks_session.proxies.update(proxies)
                return socks_session
            else:
                # For HTTP proxies, use the per-thread session
                session.proxies.update(proxies)
        else:
            session.proxies.clear()

    return session
