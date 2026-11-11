"""Every place that states the app version must agree."""

import os
import re

from kemonodownloader.app import CURRENT_VERSION
from kemonodownloader.download_policy import IDENTIFIABLE_USER_AGENT

ROOT = os.path.join(os.path.dirname(__file__), "..")


def _pyproject_version():
    with open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8") as fh:
        match = re.search(r'^version\s*=\s*"([^"]+)"', fh.read(), re.M)
    assert match, "pyproject.toml has no version"
    return match.group(1)


def test_app_version_matches_pyproject():
    assert CURRENT_VERSION == _pyproject_version()


def test_pawchive_user_agent_names_current_version():
    # Pawchive sees this agent; a stale version would misreport the client.
    assert IDENTIFIABLE_USER_AGENT.startswith(f"KemonoDownloader/{CURRENT_VERSION} ")
