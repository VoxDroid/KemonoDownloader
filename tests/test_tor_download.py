"""DownloadTorThread against real tar.gz archives built in the test."""

import io
import os
import tarfile
import tempfile
from types import SimpleNamespace

import pytest

from kemonodownloader.kd_settings import DownloadTorThread


def _tar_gz(entries):
    """Build a tar.gz in memory; entries are (name, bytes) or (name, None, link)."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for entry in entries:
            name = entry[0]
            info = tarfile.TarInfo(name)
            if len(entry) == 3:
                info.type = tarfile.SYMTYPE
                info.linkname = entry[2]
                tar.addfile(info)
            else:
                info.size = len(entry[1])
                info.mode = 0o700
                tar.addfile(info, io.BytesIO(entry[1]))
    return buf.getvalue()


class _Resp:
    def __init__(self, data, fail_midway=False):
        self._data = data
        self._fail = fail_midway
        self.headers = {"content-length": str(len(data))}

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size=8192):
        yield self._data[:10]
        if self._fail:
            raise ConnectionError("connection dropped")
        yield self._data[10:]


def _run(monkeypatch, tmp_path, response):
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs)
        return response

    monkeypatch.setattr("requests.get", fake_get)
    # Keep the temporary archive inside the test folder so leftovers show up.
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(temp_dir))

    tor_path = tmp_path / "tor_root"
    tor_path.mkdir()
    results = {"ok": [], "err": []}
    thread = DownloadTorThread("https://example.invalid/tor.tar.gz", "", str(tor_path))
    thread.progress = SimpleNamespace(emit=lambda v: None)
    thread.finished_success = SimpleNamespace(emit=results["ok"].append)
    thread.finished_error = SimpleNamespace(emit=results["err"].append)
    thread.run()
    return calls, results, tor_path, temp_dir


def test_prefers_tor_folder_over_linux_debug_symbols(monkeypatch, tmp_path):
    # Layout of the real Linux expert bundle: debug/tor holds debug symbols
    # and cannot run; the program is tor/tor.
    data = _tar_gz(
        [
            ("debug/tor", b"debug symbols"),
            ("tor/tor", b"tor program"),
            ("data/geoip", b"geo"),
        ]
    )
    calls, results, tor_path, temp_dir = _run(monkeypatch, tmp_path, _Resp(data))

    assert results["err"] == []
    assert results["ok"] == [os.path.join(str(tor_path), "tor", "tor")]
    assert calls[0].get("timeout"), "the download must not wait forever"
    assert os.listdir(temp_dir) == []


def test_windows_layout_finds_tor_exe(monkeypatch, tmp_path):
    data = _tar_gz([("tor/tor.exe", b"tor program"), ("data/geoip", b"geo")])
    _, results, tor_path, _ = _run(monkeypatch, tmp_path, _Resp(data))

    assert results["ok"] == [os.path.join(str(tor_path), "tor", "tor.exe")]


@pytest.mark.skipif(
    not hasattr(tarfile, "data_filter"), reason="tarfile extraction filters missing"
)
def test_rejects_links_that_escape_the_folder(monkeypatch, tmp_path):
    data = _tar_gz(
        [
            ("tor/tor", b"tor program"),
            ("tor/escape", None, "../../outside"),
        ]
    )
    _, results, tor_path, temp_dir = _run(monkeypatch, tmp_path, _Resp(data))

    assert results["ok"] == []
    assert results["err"], "an archive with an escaping link must be refused"
    assert not os.path.lexists(os.path.join(str(tor_path), "tor", "escape"))
    assert os.listdir(temp_dir) == []


def test_failed_download_removes_partial_archive(monkeypatch, tmp_path):
    data = _tar_gz([("tor/tor", b"tor program")])
    _, results, _, temp_dir = _run(monkeypatch, tmp_path, _Resp(data, fail_midway=True))

    assert results["ok"] == []
    assert results["err"] == ["connection dropped"]
    assert os.listdir(temp_dir) == []
