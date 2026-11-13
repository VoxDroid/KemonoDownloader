import gc
import os
import socket
import sys
from pathlib import Path

import pytest

# Add the src directory to the python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

# Hold a strong reference so the QApplication is not garbage-collected.
_qapp_instance = None

_LOOPBACK = {"127.0.0.1", "::1", "localhost"}


def _block_real_network():
    """Make any attempt to reach a real host fail at once.

    Tests must never touch the internet. Besides being slow and flaky, a test
    that accidentally starts a real request leaves a thread blocked in network
    I/O after it ends; the thread cleanup below then has to kill it, and
    killing a thread mid-read corrupts the interpreter and crashes a later
    test natively. Failing fast turns that into an ordinary handled error.
    """
    real_getaddrinfo = socket.getaddrinfo
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex

    def is_local(host):
        if isinstance(host, bytes):
            host = host.decode(errors="replace")
        return host in (None, "") or str(host) in _LOOPBACK

    def getaddrinfo(host, *args, **kwargs):
        if not is_local(host):
            raise socket.gaierror(f"network access is blocked in tests: {host}")
        return real_getaddrinfo(host, *args, **kwargs)

    def check(address):
        if isinstance(address, tuple) and not is_local(address[0]):
            raise OSError(f"network access is blocked in tests: {address[0]}")

    def connect(self, address):
        check(address)
        return real_connect(self, address)

    def connect_ex(self, address):
        check(address)
        return real_connect_ex(self, address)

    socket.getaddrinfo = getaddrinfo
    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex


def _isolate_settings_store():
    """Keep every test away from the real settings store.

    ``QSettings("VoxDroid", "KemonoDownloader")`` opens the app's real
    settings (the registry on Windows). Tests that saved or cleared settings
    through it replaced the developer's own save directory, proxy and
    language with test values. Each organisation/application pair now gets a
    throwaway INI file instead, for the whole run. This runs before any test
    module is imported, so ``from PyQt6.QtCore import QSettings`` there, and
    in the app, both pick up the isolated class.
    """
    import tempfile

    from PyQt6 import QtCore

    real = QtCore.QSettings
    if getattr(real, "_kd_isolated", False):
        return
    store = tempfile.mkdtemp(prefix="kd-test-settings-")

    class IsolatedQSettings(real):
        _kd_isolated = True
        _kd_store = store

        def __init__(self, *args, **kwargs):
            if len(args) == 2 and all(isinstance(a, str) for a in args) and not kwargs:
                path = os.path.join(store, f"{args[0]}__{args[1]}.ini")
                super().__init__(path, real.Format.IniFormat)
            else:
                super().__init__(*args, **kwargs)

    QtCore.QSettings = IsolatedQSettings


def pytest_configure(config):
    """Create a QApplication early so modules that import Qt at import-time can succeed.

    This runs before collection, preventing ImportError during test collection on headless CI.
    The offscreen platform is set via pyproject.toml [tool.pytest.ini_options]
    qt_qpa_platform = "offscreen", but we also apply it here as a safety net.
    """
    global _qapp_instance
    # Before anything is imported: importing the app starts a background
    # domain-list refresh.
    _block_real_network()
    _isolate_settings_store()
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


@pytest.fixture(autouse=True)
def restore_excepthook():
    """Undo sys.excepthook changes, e.g. from tests that run app.main()."""
    original = sys.excepthook
    yield
    sys.excepthook = original


@pytest.fixture(autouse=True)
def cleanup_qt_threads_after_test():
    """Best-effort cleanup for leaked QThreads.

    Some tests intentionally exercise cancellation/error paths and may leave
    thread objects alive briefly. On Linux CI, a surviving running QThread can
    trigger a native abort ("QThread: Destroyed while thread is still running").
    This fixture aggressively stops and joins any running QThread wrappers
    after each test to keep the process stable.
    """
    yield

    try:
        from PyQt6.QtCore import QCoreApplication, QThread
    except Exception:
        return

    app = QCoreApplication.instance()
    if app is not None:
        try:
            app.processEvents()
        except Exception:
            pass

    for obj in list(gc.get_objects()):
        try:
            if not isinstance(obj, QThread):
                continue
            if not obj.isRunning():
                continue

            # Cooperatively request shutdown first.
            for request in ("stop", "cancel"):
                try:
                    if hasattr(obj, request):
                        getattr(obj, request)()
                except Exception:
                    pass
            try:
                obj.requestInterruption()
            except Exception:
                pass
            try:
                obj.quit()
            except Exception:
                pass
            # Generous: terminate() below kills the thread wherever it is, and
            # killing one that is running Python corrupts the interpreter.
            try:
                obj.wait(10000)
            except Exception:
                pass

            # Last resort: terminate stubborn workers.
            try:
                if obj.isRunning():
                    obj.terminate()
                    obj.wait(1000)
            except Exception:
                pass
        except Exception:
            # Ignore invalid/deleted sip wrappers during GC traversal.
            pass

    if app is not None:
        try:
            app.processEvents()
        except Exception:
            pass
