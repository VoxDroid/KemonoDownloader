"""The global exception hook keeps the app alive and reports the error."""

import os
import subprocess
import sys
import textwrap

from kemonodownloader import kd_errors

SRC = os.path.join(os.path.dirname(__file__), "..", "src")


def _run_probe(install_hook):
    """Raise inside a Qt slot in a child process; return (exit code, output)."""
    code = textwrap.dedent(
        f"""
        import os, sys
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        sys.path.insert(0, {os.path.abspath(SRC)!r})
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication(sys.argv)
        # Record the dialog instead of showing it.
        QMessageBox.exec = lambda self: print("DIALOG", self.informativeText(), flush=True)
        if {install_hook!r}:
            from kemonodownloader.kd_errors import install_exception_hook
            install_exception_hook()
        def boom():
            raise RuntimeError("unhandled in slot")
        QTimer.singleShot(0, boom)
        QTimer.singleShot(300, lambda: (print("ALIVE", flush=True), app.quit()))
        app.exec()
        """
    )
    proc = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    )
    return proc.returncode, proc.stdout + proc.stderr


def test_without_hook_pyqt_aborts():
    # Documents why the hook exists: PyQt6 aborts on an unhandled exception.
    code, output = _run_probe(install_hook=False)
    assert code != 0
    assert "ALIVE" not in output


def test_hook_keeps_app_running_and_reports_error():
    code, output = _run_probe(install_hook=True)
    assert code == 0, output
    assert "ALIVE" in output
    assert "DIALOG RuntimeError: unhandled in slot" in output
    assert "Traceback" in output  # also printed for the console/log


def test_handle_exception_prints_without_reporter(monkeypatch, capsys):
    monkeypatch.setattr(kd_errors, "_reporter", None)
    try:
        raise ValueError("bad value")
    except ValueError:
        kd_errors.handle_exception(*sys.exc_info())
    assert "ValueError: bad value" in capsys.readouterr().err


def test_handle_exception_survives_missing_stderr(monkeypatch):
    # Windowed builds can run with sys.stderr set to None.
    monkeypatch.setattr(kd_errors, "_reporter", None)
    monkeypatch.setattr(sys, "stderr", None)
    try:
        raise ValueError("no console")
    except ValueError:
        kd_errors.handle_exception(*sys.exc_info())


def test_keyboard_interrupt_goes_to_default_hook(monkeypatch):
    calls = []
    monkeypatch.setattr(sys, "__excepthook__", lambda *a: calls.append(a[0]))
    kd_errors.handle_exception(KeyboardInterrupt, KeyboardInterrupt(), None)
    assert calls == [KeyboardInterrupt]


def test_reporter_shows_one_dialog_at_a_time(qapp, monkeypatch):
    shown = []
    reporter = kd_errors._ErrorReporter()

    def fake_exec(box):
        shown.append(box.informativeText())
        # A second error while this dialog is open must not stack another.
        reporter._show("second", "details")

    monkeypatch.setattr(kd_errors.QMessageBox, "exec", fake_exec)
    reporter._show("first", "details")
    assert shown == ["first"]
    reporter._show("third", "details")
    assert shown == ["first", "third"]
