"""Tests for the SQLite-based HashDB module (file deduplication store)."""

import hashlib
import json
import os

from kemonodownloader.hash_db import HashDB


class TestHashDBInit:
    """Test HashDB initialisation and table creation."""

    def test_creates_directory_and_db(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        assert os.path.isdir(isolated_hash_dir)
        assert os.path.isfile(db.db_path)

    def test_db_filename(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        assert db.db_path.endswith("file_hashes.db")

    def test_empty_db_count(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        assert db.count() == 0


class TestHashDBStoreAndLookup:
    """Test basic CRUD operations."""

    def test_store_and_lookup(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        db.store("abc123", "/path/to/file.jpg", "deadbeef", "https://example.com/f.jpg")
        entry = db.lookup("abc123")
        assert entry is not None
        assert entry["file_path"] == "/path/to/file.jpg"
        assert entry["file_hash"] == "deadbeef"
        assert entry["url"] == "https://example.com/f.jpg"

    def test_lookup_missing_key(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        assert db.lookup("nonexistent") is None

    def test_store_replaces_existing(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        db.store("abc", "/old.jpg", "hash1", "url1")
        db.store("abc", "/new.jpg", "hash2", "url2")
        entry = db.lookup("abc")
        assert entry["file_path"] == "/new.jpg"
        assert entry["file_hash"] == "hash2"
        assert db.count() == 1

    def test_contains(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        assert not db.contains("k1")
        db.store("k1", "/f.jpg", "h", "u")
        assert db.contains("k1")

    def test_delete(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        db.store("k1", "/f.jpg", "h", "u")
        db.delete("k1")
        assert not db.contains("k1")
        assert db.count() == 0

    def test_clear(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        for i in range(5):
            db.store(f"k{i}", f"/f{i}.jpg", f"h{i}", f"u{i}")
        assert db.count() == 5
        db.clear()
        assert db.count() == 0

    def test_all_entries(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        db.store("k1", "/a.jpg", "ha", "ua")
        db.store("k2", "/b.jpg", "hb", "ub")
        entries = db.all_entries()
        assert len(entries) == 2
        assert "k1" in entries
        assert entries["k2"]["file_path"] == "/b.jpg"


class TestHashDBMigration:
    """Test automatic migration from legacy file_hashes.json."""

    def test_migrates_json(self, isolated_hash_dir):
        os.makedirs(isolated_hash_dir, exist_ok=True)
        legacy_data = {
            "aaa": {
                "file_path": "/old/img.png",
                "file_hash": "oldhash",
                "url": "https://example.com/img.png",
            },
            "bbb": {
                "file_path": "/old/vid.mp4",
                "file_hash": "oldhash2",
                "url": "https://example.com/vid.mp4",
            },
        }
        json_path = os.path.join(isolated_hash_dir, "file_hashes.json")
        with open(json_path, "w") as f:
            json.dump(legacy_data, f)

        db = HashDB(isolated_hash_dir)
        assert db.count() == 2
        entry = db.lookup("aaa")
        assert entry is not None
        assert entry["file_path"] == "/old/img.png"

        # JSON file should be renamed
        assert not os.path.exists(json_path)
        assert os.path.exists(json_path + ".migrated")

    def test_no_migration_when_no_json(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        assert db.count() == 0

    def test_corrupt_json_ignored(self, isolated_hash_dir):
        os.makedirs(isolated_hash_dir, exist_ok=True)
        json_path = os.path.join(isolated_hash_dir, "file_hashes.json")
        with open(json_path, "w") as f:
            f.write("NOT VALID JSON {{{")
        # Should not raise
        db = HashDB(isolated_hash_dir)
        assert db.count() == 0


class TestHashDBThreadSafety:
    """Basic concurrency tests for the hash database."""

    def test_concurrent_writes(self, isolated_hash_dir):
        import threading

        db = HashDB(isolated_hash_dir)
        errors = []

        def writer(start, count):
            try:
                for i in range(start, start + count):
                    db.store(f"key_{i}", f"/path/{i}.jpg", f"hash_{i}", f"url_{i}")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(i * 50, 50)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert db.count() == 200

    def test_concurrent_read_write(self, isolated_hash_dir):
        import threading

        db = HashDB(isolated_hash_dir)
        for i in range(100):
            db.store(f"k{i}", f"/p{i}", f"h{i}", f"u{i}")

        errors = []

        def reader():
            try:
                for i in range(100):
                    db.lookup(f"k{i}")
            except Exception as exc:
                errors.append(exc)

        def writer():
            try:
                for i in range(100, 150):
                    db.store(f"k{i}", f"/p{i}", f"h{i}", f"u{i}")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=reader) for _ in range(3)]
        threads.append(threading.Thread(target=writer))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert db.count() == 150


class TestHashDBRealHash:
    """Test using real MD5 hashes as the application does."""

    def test_md5_url_hash(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        url = "https://kemono.cr/data/12/34/1234abcd.jpg"
        url_hash = hashlib.md5(url.encode()).hexdigest()
        db.store(url_hash, "/downloads/file.jpg", "filehash123", url)
        entry = db.lookup(url_hash)
        assert entry is not None
        assert entry["url"] == url
