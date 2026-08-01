"""
domain_config.py
================
Fetches the list of supported domains dynamically from the remote config URL.

Domain list URL:
    https://raw.githubusercontent.com/VoxDroid/KemonoDownloader/refs/heads/main/assets/config/domain

The remote list is fetched once per process and cached in memory.  If the
fetch fails (network error, timeout, etc.) the module falls back to:

1. The bundled ``assets/config/domain`` file (relative to the repository
   root, resolved at import time).
2. A hardcoded list of known-good domains so the application can always
   start even offline.

Each domain in the list follows a consistent API structure:

    base_url  = https://<domain>
    api_base  = https://<domain>/api/v1
    referer   = https://<domain>/

``get_domain_config(url)`` inspects the URL and returns the matching
config dict, defaulting to the first domain in the list (kemono.cr).
"""

from __future__ import annotations

import os
import threading
from typing import Dict, List, Optional

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOMAIN_LIST_URL = (
    "https://raw.githubusercontent.com/VoxDroid/KemonoDownloader"
    "/refs/heads/main/assets/config/domain"
)

# Path to the bundled fallback file (assets/config/domain) relative to this
# source file:  src/kemonodownloader/domain_config.py
#               ↑ two levels up → repo root → assets/config/domain
_HERE = os.path.dirname(os.path.abspath(__file__))
_LOCAL_DOMAIN_FILE = os.path.join(_HERE, "..", "..", "assets", "config", "domain")

# Hardcoded last-resort fallback (used when both remote fetch and local file
# are unavailable).
_FALLBACK_DOMAINS: List[str] = [
    "kemono.cr",
    "coomer.st",
    "pawchive.pw",
]

# ---------------------------------------------------------------------------
# Internal cache
# ---------------------------------------------------------------------------

_domains_cache: Optional[List[str]] = None
_cache_lock = threading.Lock()


def _load_domains_from_text(text: str) -> List[str]:
    """Parse a newline-separated domain list, ignoring blank lines."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def _fetch_remote_domains() -> Optional[List[str]]:
    """Attempt to download the domain list from GitHub.  Returns None on any error."""
    try:
        response = requests.get(DOMAIN_LIST_URL, timeout=5)
        response.raise_for_status()
        domains = _load_domains_from_text(response.text)
        if domains:
            return domains
    except Exception:
        pass
    return None


def _load_local_domains() -> Optional[List[str]]:
    """Attempt to read the bundled assets/config/domain file."""
    try:
        path = os.path.normpath(_LOCAL_DOMAIN_FILE)
        with open(path, encoding="utf-8") as fh:
            domains = _load_domains_from_text(fh.read())
            if domains:
                return domains
    except Exception:
        pass
    return None


def get_domains() -> List[str]:
    """Return the list of supported domains.

    The list is fetched from the remote config URL on the first call and
    cached for the lifetime of the process.  If the remote fetch fails the
    function falls back to the local bundled file, then to the hardcoded list.
    """
    global _domains_cache
    if _domains_cache is not None:
        return _domains_cache

    with _cache_lock:
        # Double-checked locking
        if _domains_cache is not None:
            return _domains_cache

        domains = _fetch_remote_domains()
        if domains is None:
            domains = _load_local_domains()
        if domains is None:
            domains = list(_FALLBACK_DOMAINS)

        _domains_cache = domains

    return _domains_cache


def _is_pawchive_domain(domain: str) -> bool:
    """Return True when *domain* is a pawchive domain (any suffix)."""
    return domain.startswith("pawchive.")


def _build_config(domain: str) -> Dict[str, str]:
    """Build a domain config dict for the given domain string."""
    # Special case for file download servers, e.g. pawchive.<suffix> -> file.pawchive.<suffix>
    if _is_pawchive_domain(domain):
        file_base_url = f"https://file.{domain}"
    else:
        file_base_url = f"https://{domain}"

    return {
        "domain": domain,
        "base_url": f"https://{domain}",
        "api_base": f"https://{domain}/api/v1",
        "referer": f"https://{domain}/",
        "file_base_url": file_base_url,
    }


def clean_file_url(file_url: str, domain_config: Dict[str, str]) -> str:
    """Ensure that the file URL uses the correct download server.

    For example, pawchive.<suffix> uses file.pawchive.<suffix> for file downloads.
    """
    if "/thumbnail/" in file_url or "img." in file_url:
        return file_url

    from urllib.parse import urljoin, urlparse, urlunparse

    base = domain_config.get("base_url", "")
    file_base_url = domain_config.get("file_base_url") or base
    full_url = urljoin(file_base_url, file_url)
    domain = str(domain_config.get("domain", "") or "")

    if _is_pawchive_domain(domain):
        parsed = urlparse(full_url)
        pawchive_file_host = f"file.{domain}"

        # Rewrite direct pawchive.<suffix> URLs to file.pawchive.<suffix>.
        if parsed.netloc == domain:
            parsed = parsed._replace(netloc=pawchive_file_host)
        elif parsed.netloc.startswith(f"{domain}:"):
            parsed = parsed._replace(
                netloc=parsed.netloc.replace(domain, pawchive_file_host, 1)
            )

        # For pawchive domains, the file path must contain /data/.
        path = parsed.path
        if not path.startswith("/data/"):
            cleaned_path = "/data/" + path.lstrip("/")
            parsed = parsed._replace(path=cleaned_path)

        full_url = urlunparse(parsed)

    return full_url


def get_domain_config(url: str) -> Dict[str, str]:
    """Return the domain configuration that matches *url*.

    The function checks each known domain (in order) against the URL.  The
    first match wins.  If no domain matches, the first domain in the list
    (kemono.cr) is used as the default.
    """
    domains = get_domains()
    for domain in domains:
        if domain in url:
            return _build_config(domain)
    # Default: first domain in list
    return _build_config(domains[0])
