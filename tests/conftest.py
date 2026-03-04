import os
import sys
from pathlib import Path

import pytest

# Add the src directory to the python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

# Hold a strong reference so the QApplication is not garbage-collected.
_qapp_instance = None


def pytest_configure(config):
    """Create a QApplication early so modules that import Qt at import-time can succeed.

    This runs before collection, preventing ImportError during test collection on headless CI.
    The offscreen platform is set via pyproject.toml [tool.pytest.ini_options]
    qt_qpa_platform = "offscreen", but we also apply it here as a safety net.
    """
    global _qapp_instance
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        import faulthandler

        from PyQt6.QtWidgets import QApplication

        # Enable faulthandler to get native tracebacks on crashes (useful for C-level faults)
        try:
            faulthandler.enable()
        except Exception:
            pass

        if QApplication.instance() is None:
            _qapp_instance = QApplication([])
    except Exception:
        # If PyQt is not available, allow tests to fail later rather than crash here.
        pass


# NOTE: No custom ``qapp`` fixture here.  pytest-qt provides a session-scoped
# ``qapp`` fixture that correctly manages the QApplication lifecycle.  Defining
# a function-scoped override previously shadowed it and could return None when
# the early QApplication created above was garbage-collected.


@pytest.fixture()
def isolated_settings(tmp_path):
    """Provide a QSettings instance backed by an isolated temp INI file.

    This prevents tests from reading/writing the real application settings.
    """
    from PyQt6.QtCore import QSettings

    ini_path = str(tmp_path / "test_settings.ini")
    settings = QSettings(ini_path, QSettings.Format.IniFormat)
    settings.clear()
    yield settings
    settings.clear()


@pytest.fixture()
def isolated_hash_dir(tmp_path):
    """Return a temp directory suitable for HashDB tests."""
    return str(tmp_path / "hash_store")
