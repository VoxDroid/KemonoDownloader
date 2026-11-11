"""Last-resort handling for exceptions that nothing else caught.

PyQt6 turns an exception that escapes a slot, an event handler or
``QThread.run()`` into a call to ``qFatal()``, which aborts the whole app
without a message (on Windows the process ends with 0xC0000409). Installing
``sys.excepthook`` replaces that with: print the traceback, then show an error
dialog on the GUI thread so the user can report it, and keep running.
"""

import sys
import traceback
from typing import Optional

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox

from kemonodownloader.kd_language import translate


class _ErrorReporter(QObject):
    """Shows error dialogs on the thread it lives on (the GUI thread)."""

    report = pyqtSignal(str, str)  # one-line summary, full traceback

    def __init__(self):
        super().__init__()
        self._showing = False
        # Queued even from the GUI thread, so the dialog never opens in the
        # middle of the call stack that just failed. (PyQt6's type stubs omit
        # connect()'s `type` argument, which the runtime accepts.)
        self.report.connect(
            self._show,
            type=Qt.ConnectionType.QueuedConnection,  # pyright: ignore[reportCallIssue]
        )

    def _show(self, summary: str, details: str) -> None:
        # One dialog at a time; further errors are still printed.
        if self._showing:
            return
        self._showing = True
        try:
            box = QMessageBox(QApplication.activeWindow())
            box.setIcon(QMessageBox.Icon.Critical)
            box.setWindowTitle(translate("unexpected_error_title"))
            box.setText(translate("unexpected_error_text"))
            box.setInformativeText(summary)
            box.setDetailedText(details)
            box.exec()
        finally:
            self._showing = False


_reporter: Optional[_ErrorReporter] = None


def handle_exception(exc_type, exc, tb) -> None:
    """sys.excepthook: print the error and report it without aborting."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc, tb)
        return

    details = "".join(traceback.format_exception(exc_type, exc, tb))
    # A windowed build can run without a console, where stderr is None.
    if sys.stderr is not None:
        try:
            sys.stderr.write(details)
            sys.stderr.flush()
        except Exception:
            pass

    reporter = _reporter
    if reporter is not None and QApplication.instance() is not None:
        try:
            reporter.report.emit(f"{exc_type.__name__}: {exc}", details)
        except Exception:
            pass


def install_exception_hook() -> None:
    """Install the hook. Call on the GUI thread after creating QApplication."""
    global _reporter
    if _reporter is None:
        _reporter = _ErrorReporter()
    sys.excepthook = handle_exception
