import ctypes
import os
import runpy
import sys
from types import SimpleNamespace

from kemonodownloader import creator_downloader as cd


def _sync_frame_locals(frame):
    pyframe_locals_to_fast = ctypes.pythonapi.PyFrame_LocalsToFast
    pyframe_locals_to_fast.argtypes = [ctypes.py_object, ctypes.c_int]
    pyframe_locals_to_fast.restype = None
    pyframe_locals_to_fast(frame, 1)


def test_creator_post_detection_none_response_defensive_branch(monkeypatch):
    class Resp:
        status_code = 200
        content = b"[]"
        text = "[]"

    monkeypatch.setattr(
        cd,
        "get_session",
        lambda settings_tab=None: SimpleNamespace(get=lambda *a, **k: Resp()),
    )

    thread = cd.PostDetectionThread(
        "https://kemono.cr/fanbox/user/1",
        {},
        SimpleNamespace(creator_posts_max_attempts=1, settings_tab=None),
    )
    logs = []
    thread.log = SimpleNamespace(emit=lambda msg, level: logs.append((msg, level)))
    thread.error = SimpleNamespace(emit=lambda *a, **k: None)
    thread.finished = SimpleNamespace(emit=lambda *a, **k: None)
    thread.posts_batch = SimpleNamespace(emit=lambda *a, **k: None)

    target_file = os.path.abspath(cd.__file__)
    injected = {"done": False}

    def tracer(frame, event, arg):
        if event != "line":
            return tracer
        if os.path.abspath(frame.f_code.co_filename) != target_file:
            return tracer
        if frame.f_code.co_name != "run":
            return tracer
        if frame.f_lineno == 578 and not injected["done"]:
            frame.f_locals["response"] = None
            _sync_frame_locals(frame)
            injected["done"] = True
        return tracer

    previous = sys.gettrace()
    sys.settrace(tracer)
    try:
        thread.run()
    finally:
        sys.settrace(previous)

    assert injected["done"] is True
    assert any("No response received from any endpoint" in str(msg) for msg, _ in logs)


def test_app_main_guard_executes_line_without_running_real_main():
    import kemonodownloader.app as app_module

    called = {"n": 0}

    def fake_main():
        called["n"] += 1

    target_file = os.path.abspath(app_module.__file__)

    def tracer(frame, event, arg):
        if event == "line" and os.path.abspath(frame.f_code.co_filename) == target_file:
            if frame.f_lineno == 595:
                frame.f_globals["main"] = fake_main
        return tracer

    previous = sys.gettrace()
    sys.settrace(tracer)
    try:
        runpy.run_path(app_module.__file__, run_name="__main__")
    finally:
        sys.settrace(previous)

    assert called["n"] == 1
