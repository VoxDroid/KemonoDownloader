import os

from kemonodownloader.kd_settings import DownloadTorThread


def test_download_tor_thread_skips_path_traversal(monkeypatch, tmp_path):
    # Prepare fake response for requests.get
    class FakeResp:
        status_code = 200

        def __init__(self, chunks):
            self._chunks = chunks
            self.headers = {"content-length": str(sum(len(c) for c in chunks))}

        def iter_content(self, chunk_size=8192):
            for c in self._chunks:
                yield c

        def raise_for_status(self):
            return None

    monkeypatch.setattr(
        "requests.get",
        lambda *a, **k: FakeResp([b"data"]),
    )

    # Fake tarfile object that records extracted member names
    class FakeMember:
        def __init__(self, name):
            self.name = name

    class FakeTar:
        def __init__(self, members):
            self._members = [FakeMember(n) for n in members]
            self.extracted = []

        def getmembers(self):
            return self._members

        def extract(self, member, path):
            # record the member name that would be extracted
            self.extracted.append(member.name)

        def close(self):
            return None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    # Create tar_ref with a safe and an unsafe member
    members = ["tor/tor", "../../etc/passwd", "tor/bin/tor"]
    fake_tar = FakeTar(members)

    monkeypatch.setattr("tarfile.open", lambda *a, **k: fake_tar)

    # Ensure os.unlink doesn't remove anything important during test
    monkeypatch.setattr("os.unlink", lambda p: None)

    # Run the DownloadTorThread
    tor_path = str(tmp_path / "tor_dir")
    os.makedirs(tor_path, exist_ok=True)
    thread = DownloadTorThread("http://example.com/tor.tar.gz", str(tmp_path), tor_path)
    # Connect signals to no-op to avoid Qt requirements
    thread.progress.connect(lambda v: None)
    thread.finished_success.connect(lambda p: None)
    thread.finished_error.connect(lambda e: None)

    # Execute run() directly
    thread.run()

    # After run, only safe members should have been extracted
    assert all(".." not in name for name in fake_tar.extracted)
    assert any(name.startswith("tor/") for name in fake_tar.extracted)
