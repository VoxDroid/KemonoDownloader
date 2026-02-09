import os
import sys
from pathlib import Path

# Add the src directory to the python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

# Use offscreen Qt platform for headless testing in CI
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def pytest_configure(config):
    """Create a QApplication early so modules that import Qt at import-time can succeed.

    This runs before collection, preventing ImportError during test collection on headless CI.
    """
    try:
        import faulthandler

        from PyQt6.QtWidgets import QApplication

        # Enable faulthandler to get native tracebacks on crashes (useful for C-level faults)
        try:
            faulthandler.enable()
        except Exception:
            pass

        if QApplication.instance() is None:
            QApplication([])
    except Exception:
        # If PyQt is not available, allow tests to fail later rather than crash here.
        pass
