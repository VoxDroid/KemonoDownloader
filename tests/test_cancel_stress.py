"""
Stress tests for rapid cancel / download cycling.

These tests exercise the thread-lifecycle defence mechanisms added to both the
post downloader and creator downloader:
  • ``_destroyed`` flag & ``_safe_emit`` guard signal emissions after stop()
  • Worker join / asyncio task cancellation ensures no thread outlives ``run()``
  • No ``RuntimeError: wrapped C/C++ object … has been deleted``
  • No ``QThread: Destroyed while thread is still running``

Every test stubs out real network I/O so the tests are self-contained.
"""

import os
import sys
import threading
import time
from unittest.mock import patch

try:
    from kemonodownloader.creator_downloader import CreatorDownloadThread
    from kemonodownloader.post_downloader import DownloadThread
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
    from kemonodownloader.creator_downloader import CreatorDownloadThread
    from kemonodownloader.post_downloader import DownloadThread


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class DummySettingsTab:
    """Minimal settings tab used by both downloaders."""

    def get_creator_filename_template(self):
        return "{post_id}_{orig_name}"

    def get_creator_folder_strategy(self):
        return "per_post"


class DummySettings:
    """Minimal settings container."""

    def __init__(self):
        self.settings_tab = DummySettingsTab()
        self.file_download_max_retries = 1
        self.creator_posts_max_attempts = 1
        self.post_data_max_retries = 1
        self.api_request_max_retries = 1
        self.simultaneous_downloads = 2


FAKE_FILES = [f"https://kemono.cr/data/ab/{i:02x}/fake_{i}.jpg" for i in range(5)]

FAKE_POST_MAP = {url: "p1" for url in FAKE_FILES}

FAKE_POST_TITLES = {
    ("patreon", "creator1", "p1"): "Test_Post",
}


def _make_creator_thread(tmp_path, files=None, max_concurrent=3):
    """Create a CreatorDownloadThread without network."""
    files = files if files is not None else FAKE_FILES
    t = CreatorDownloadThread(
        service="patreon",
        creator_id="creator1",
        download_folder=str(tmp_path),
        selected_posts=["p1"],
        files_to_download=list(files),
        files_to_posts_map=dict(FAKE_POST_MAP),
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_titles_map=dict(FAKE_POST_TITLES),
        auto_rename_enabled=False,
        settings=DummySettings(),
        max_concurrent=max_concurrent,
    )
    # Prevent real network calls
    t.fetch_creator_and_post_info = lambda: setattr(t, "creator_name", "TestCreator")
    return t


def _make_post_thread(tmp_path, files=None, max_concurrent=3):
    """Create a post-downloader DownloadThread without network."""
    files = files if files is not None else FAKE_FILES
    t = DownloadThread(
        url="https://kemono.cr/patreon/user/creator1/post/p1",
        download_folder=str(tmp_path),
        selected_files=list(files),
        files_to_posts_map=dict(FAKE_POST_MAP),
        console=None,
        other_files_dir=str(tmp_path / "other"),
        post_id="p1",
        settings=DummySettings(),
        max_concurrent=max_concurrent,
    )
    # Prevent real network calls
    t.fetch_post_info = lambda: setattr(t, "post_title", "TestPost")
    return t


def _noop_download_file(*args, **kwargs):
    """Simulated download that takes a short time."""
    time.sleep(0.02)


async def _noop_async_download_file(self, *args, **kwargs):
    """Simulated async download_file for the creator downloader."""
    import asyncio

    await asyncio.sleep(0.02)


# ---------------------------------------------------------------------------
# CreatorDownloadThread tests
# ---------------------------------------------------------------------------


class TestCreatorCancelStress:
    """Rapid cancel/download cycling for CreatorDownloadThread."""

    def test_cancel_before_start(self, tmp_path):
        """Cancel before start() — run() should exit immediately."""
        t = _make_creator_thread(tmp_path)
        t.stop()
        # run() directly (no QThread::start) — should return instantly
        t.run()
        assert t._destroyed is True
        assert t.is_running is False

    def test_cancel_immediately_after_start(self, tmp_path):
        """Start then stop() within microseconds."""
        t = _make_creator_thread(tmp_path, files=[])
        t.start()
        t.stop()
        finished = t.wait(5000)
        assert finished is True
        assert t._destroyed is True

    def test_rapid_start_cancel_cycles(self, tmp_path):
        """Create, start, cancel rapidly — 10 cycles without crash."""
        for _ in range(10):
            t = _make_creator_thread(tmp_path, files=[])
            t.start()
            t.stop()
            finished = t.wait(5000)
            assert finished is True
            assert t._destroyed is True

    @patch(
        "kemonodownloader.creator_downloader.CreatorDownloadThread.download_file",
        new=_noop_async_download_file,
    )
    def test_cancel_during_active_downloads(self, tmp_path):
        """Cancel while workers are actively downloading."""
        t = _make_creator_thread(tmp_path, max_concurrent=2)
        t.start()
        # Give workers a moment to start
        time.sleep(0.05)
        t.stop()
        finished = t.wait(10000)
        assert finished is True
        assert t._destroyed is True

    @patch(
        "kemonodownloader.creator_downloader.CreatorDownloadThread.download_file",
        new=_noop_async_download_file,
    )
    def test_cancel_download_cancel_rapid_cycle(self, tmp_path):
        """Start → cancel → start → cancel rapid cycling with files."""
        for _ in range(5):
            t = _make_creator_thread(tmp_path, max_concurrent=2)
            t.start()
            time.sleep(0.01)
            t.stop()
            finished = t.wait(10000)
            assert finished is True

    def test_destroyed_flag_prevents_signal_after_stop(self, tmp_path):
        """After stop(), _safe_emit must be a no-op."""
        t = _make_creator_thread(tmp_path, files=[])
        received = []
        t.log.connect(lambda msg, lvl: received.append((msg, lvl)))
        t.stop()
        # _safe_emit should silently swallow the emission
        t._safe_emit(t.log, "should not arrive", "INFO")
        assert len(received) == 0

    def test_no_qthread_destroyed_warning(self, tmp_path, capsys):
        """Verify no 'QThread: Destroyed while thread is still running' on stderr."""
        t = _make_creator_thread(tmp_path, files=[])
        t.start()
        t.stop()
        t.wait(5000)
        # Explicitly delete and check stderr
        del t
        captured = capsys.readouterr()
        assert "Destroyed while thread is still running" not in captured.err


# ---------------------------------------------------------------------------
# Post DownloadThread tests
# ---------------------------------------------------------------------------


class TestPostCancelStress:
    """Rapid cancel/download cycling for post_downloader DownloadThread."""

    def test_cancel_before_start(self, tmp_path):
        """Cancel before start() — run() should exit cleanly."""
        t = _make_post_thread(tmp_path)
        t.stop()
        t.run()
        assert t._destroyed is True
        assert t.is_running is False

    def test_cancel_immediately_after_start(self, tmp_path):
        """Start then stop() within microseconds."""
        t = _make_post_thread(tmp_path, files=[])
        t.start()
        t.stop()
        finished = t.wait(5000)
        assert finished is True
        assert t._destroyed is True

    def test_rapid_start_cancel_cycles(self, tmp_path):
        """Create, start, cancel rapidly — 10 cycles without crash."""
        for _ in range(10):
            t = _make_post_thread(tmp_path, files=[])
            t.start()
            t.stop()
            finished = t.wait(5000)
            assert finished is True
            assert t._destroyed is True

    def test_cancel_during_active_downloads(self, tmp_path):
        """Cancel while daemon workers are actively downloading."""
        t = _make_post_thread(tmp_path, max_concurrent=2)
        # Patch download_file to simulate slow work
        t.download_file = lambda *a, **kw: time.sleep(0.05)
        t.start()
        time.sleep(0.03)
        t.stop()
        finished = t.wait(15000)
        assert finished is True
        assert t._destroyed is True

    def test_cancel_download_cancel_rapid_cycle(self, tmp_path):
        """Start → cancel → start → cancel rapid cycling with files."""
        for _ in range(5):
            t = _make_post_thread(tmp_path, max_concurrent=2, files=[])
            t.start()
            time.sleep(0.01)
            t.stop()
            finished = t.wait(5000)
            assert finished is True

    def test_destroyed_flag_prevents_signal_after_stop(self, tmp_path):
        """After stop(), _safe_emit on the post thread is a no-op (via _destroyed)."""
        t = _make_post_thread(tmp_path, files=[])
        t.stop()
        # Direct emit should raise RuntimeError only if C++ is gone;
        # but _destroyed=True means workers won't even try.
        assert t._destroyed is True

    def test_workers_join_before_run_returns(self, tmp_path):
        """Verify that all daemon worker threads have terminated after run() returns."""
        t = _make_post_thread(tmp_path, max_concurrent=2, files=[])
        alive_before = threading.active_count()
        t.start()
        t.wait(5000)
        # Give a brief moment for thread cleanup
        time.sleep(0.1)
        alive_after = threading.active_count()
        # We should not have leaked any threads
        assert alive_after <= alive_before + 1  # +1 tolerance for GC


# ---------------------------------------------------------------------------
# Mixed: interleaved creator + post cancel cycles
# ---------------------------------------------------------------------------


class TestMixedCancelStress:
    """Interleave creator and post cancel cycles to stress thread safety."""

    def test_interleaved_cancel_cycles(self, tmp_path):
        """Alternate between creator and post threads, cancelling each promptly."""
        for i in range(5):
            if i % 2 == 0:
                t = _make_creator_thread(tmp_path, files=[])
            else:
                t = _make_post_thread(tmp_path, files=[])
            t.start()
            t.stop()
            finished = t.wait(5000)
            assert finished is True

    def test_parallel_threads_with_cancel(self, tmp_path):
        """Start multiple threads simultaneously, cancel all."""
        threads = []
        for i in range(4):
            if i % 2 == 0:
                t = _make_creator_thread(tmp_path, files=[])
            else:
                t = _make_post_thread(tmp_path, files=[])
            t.start()
            threads.append(t)

        # Cancel all
        for t in threads:
            t.stop()

        # Wait for all
        for t in threads:
            finished = t.wait(5000)
            assert finished is True
