"""DownloadTorThread against real tar.gz archives built in the test."""

import hashlib
import io
import os
import tarfile
import tempfile
from types import SimpleNamespace

import pytest

from kemonodownloader import kd_settings as ks
from kemonodownloader.kd_settings import (
    TOR_BUNDLE_SHA256,
    TOR_BUNDLE_VERSION,
    DownloadTorThread,
    tor_bundle_platform,
)


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


def _run(monkeypatch, tmp_path, response, expected_sha256=None):
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
    thread = DownloadTorThread(
        "https://example.invalid/tor.tar.gz", "", str(tor_path), expected_sha256
    )
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


def test_matching_checksum_is_installed(monkeypatch, tmp_path):
    data = _tar_gz([("tor/tor", b"tor program")])
    digest = hashlib.sha256(data).hexdigest()
    _, results, tor_path, _ = _run(monkeypatch, tmp_path, _Resp(data), digest.upper())

    assert results["err"] == []
    assert results["ok"] == [os.path.join(str(tor_path), "tor", "tor")]


def test_wrong_checksum_is_refused_before_extracting(monkeypatch, tmp_path):
    data = _tar_gz([("tor/tor", b"tampered program")])
    _, results, tor_path, temp_dir = _run(monkeypatch, tmp_path, _Resp(data), "0" * 64)

    assert results["ok"] == []
    assert len(results["err"]) == 1
    assert os.listdir(str(tor_path)) == [], "nothing may be extracted"
    assert os.listdir(temp_dir) == []


@pytest.mark.parametrize(
    "sys_platform, machine, expected",
    [
        ("win32", "AMD64", "windows-x86_64"),
        ("win32", "ARM64", "windows-x86_64"),  # runs under x64 emulation
        ("darwin", "arm64", "macos-aarch64"),
        ("darwin", "x86_64", "macos-x86_64"),
        ("linux", "x86_64", "linux-x86_64"),
        ("linux", "aarch64", "linux-aarch64"),
        ("linux", "armv7l", None),
        ("freebsd14", "amd64", None),
    ],
)
def test_tor_bundle_platform(sys_platform, machine, expected):
    assert tor_bundle_platform(sys_platform, machine) == expected


def test_every_bundle_has_a_sha256():
    assert TOR_BUNDLE_SHA256
    for name, digest in TOR_BUNDLE_SHA256.items():
        assert len(digest) == 64 and int(digest, 16) >= 0, name


def test_download_tor_passes_url_and_checksum(monkeypatch, qapp, tmp_path):
    created = []

    class FakeThread:
        def __init__(self, *args):
            created.append(args)
            self.progress = self.finished_success = self.finished_error = self

        def connect(self, *_a):
            pass

        def start(self):
            pass

    monkeypatch.setattr(ks, "DownloadTorThread", FakeThread)
    monkeypatch.setattr(ks, "tor_bundle_platform", lambda: "linux-x86_64")
    monkeypatch.setattr(ks.QMessageBox, "information", lambda *a, **k: None)
    tab = ks.SettingsTab(SimpleNamespace())
    tab.temp_settings["base_directory"] = str(tmp_path)
    tab.download_tor()

    url, extract_dir, _, sha = created[0]
    name = f"tor-expert-bundle-linux-x86_64-{TOR_BUNDLE_VERSION}"
    assert url == f"{ks.TOR_ARCHIVE_URL}/{TOR_BUNDLE_VERSION}/{name}.tar.gz"
    assert extract_dir == name
    assert sha == TOR_BUNDLE_SHA256["linux-x86_64"]


def test_download_tor_refuses_unsupported_platform(monkeypatch, qapp, tmp_path):
    warned = []
    monkeypatch.setattr(ks, "tor_bundle_platform", lambda: None)
    monkeypatch.setattr(ks.QMessageBox, "warning", lambda *a, **k: warned.append(a))
    monkeypatch.setattr(
        ks, "DownloadTorThread", lambda *a: pytest.fail("must not download")
    )
    tab = ks.SettingsTab(SimpleNamespace())
    tab.download_tor()

    assert warned
