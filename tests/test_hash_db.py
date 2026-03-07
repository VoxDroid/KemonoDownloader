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
        db.store(
            "abc123",
            "/path/to/file.jpg",
            "deadbeef",
            "https://example.com/f.jpg",
            1024,
        )
        entry = db.lookup("abc123")
        assert entry is not None
        assert entry["file_path"] == "/path/to/file.jpg"
        assert entry["file_hash"] == "deadbeef"
        assert entry["url"] == "https://example.com/f.jpg"
        assert entry["file_size"] == 1024

    def test_lookup_missing_key(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        assert db.lookup("nonexistent") is None

    def test_store_replaces_existing(self, isolated_hash_dir):
        db = HashDB(isolated_hash_dir)
        db.store("abc", "/old.jpg", "hash1", "url1", 100)
        db.store("abc", "/new.jpg", "hash2", "url2", 200)
        entry = db.lookup("abc")
        assert entry["file_path"] == "/new.jpg"
        assert entry["file_hash"] == "hash2"
        assert entry["file_size"] == 200
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
        db.store("k1", "/a.jpg", "ha", "ua", 500)
        db.store("k2", "/b.jpg", "hb", "ub", 600)
        entries = db.all_entries()
        assert len(entries) == 2
        assert "k1" in entries
        assert entries["k2"]["file_path"] == "/b.jpg"
        assert entries["k1"]["file_size"] == 500
        assert entries["k2"]["file_size"] == 600


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
        db.store(url_hash, "/downloads/file.jpg", "filehash123", url, 4096)
        entry = db.lookup(url_hash)
        assert entry is not None
        assert entry["url"] == url
        assert entry["file_size"] == 4096


class TestHashDBFileSize:
    """Tests for file_size column (corruption detection)."""

    def test_file_size_defaults_to_zero(self, isolated_hash_dir):
        """When file_size is not specified, it should default to 0."""
        db = HashDB(isolated_hash_dir)
        db.store("k1", "/f.jpg", "h1", "u1")
        entry = db.lookup("k1")
        assert entry is not None
        assert entry["file_size"] == 0

    def test_file_size_stored_and_retrieved(self, isolated_hash_dir):
        """Stored file_size should be retrievable via lookup."""
        db = HashDB(isolated_hash_dir)
        db.store("k1", "/f.jpg", "h1", "u1", 12345)
        entry = db.lookup("k1")
        assert entry["file_size"] == 12345

    def test_file_size_updated_on_replace(self, isolated_hash_dir):
        """Overwriting an entry should update file_size."""
        db = HashDB(isolated_hash_dir)
        db.store("k1", "/f.jpg", "h1", "u1", 100)
        db.store("k1", "/f.jpg", "h2", "u1", 200)
        entry = db.lookup("k1")
        assert entry["file_size"] == 200

    def test_file_size_in_all_entries(self, isolated_hash_dir):
        """all_entries() should return file_size for each entry."""
        db = HashDB(isolated_hash_dir)
        db.store("a", "/a.jpg", "ha", "ua", 111)
        db.store("b", "/b.jpg", "hb", "ub", 222)
        entries = db.all_entries()
        assert entries["a"]["file_size"] == 111
        assert entries["b"]["file_size"] == 222

    def test_corruption_detection_by_size(self, isolated_hash_dir, tmp_path):
        """Simulate corruption detection: actual file size != stored file_size."""
        db = HashDB(isolated_hash_dir)
        # Create a real file with known content
        test_file = tmp_path / "test_image.jpg"
        test_file.write_bytes(b"x" * 1000)
        file_hash = hashlib.md5(b"x" * 1000).hexdigest()

        db.store("k1", str(test_file), file_hash, "http://example.com/img.jpg", 1000)

        # File is intact
        entry = db.lookup("k1")
        assert os.path.getsize(str(test_file)) == entry["file_size"]

        # Simulate corruption by truncating the file
        test_file.write_bytes(b"x" * 500)
        assert os.path.getsize(str(test_file)) != entry["file_size"]

    def test_legacy_entry_has_zero_file_size(self, isolated_hash_dir):
        """Entries migrated from JSON (without file_size) should default to 0."""
        os.makedirs(isolated_hash_dir, exist_ok=True)
        legacy_data = {
            "legacy1": {
                "file_path": "/old/img.png",
                "file_hash": "oldhash",
                "url": "https://example.com/img.png",
            },
        }
        json_path = os.path.join(isolated_hash_dir, "file_hashes.json")
        with open(json_path, "w") as f:
            json.dump(legacy_data, f)

        db = HashDB(isolated_hash_dir)
        entry = db.lookup("legacy1")
        assert entry is not None
        assert entry["file_size"] == 0


class TestHashDBSchemaMigration:
    """Test that existing databases without file_size column get migrated."""

    def test_old_db_gets_file_size_column(self, isolated_hash_dir):
        """A database created without file_size should gain the column on open."""
        import sqlite3

        os.makedirs(isolated_hash_dir, exist_ok=True)
        db_path = os.path.join(isolated_hash_dir, "file_hashes.db")

        # Create an old-style database without file_size
        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            CREATE TABLE file_hashes (
                url_hash   TEXT PRIMARY KEY,
                file_path  TEXT NOT NULL,
                file_hash  TEXT NOT NULL,
                url        TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT INTO file_hashes VALUES (?, ?, ?, ?)",
            ("old_key", "/old/path.jpg", "oldhash", "https://old.url"),
        )
        conn.commit()
        conn.close()

        # Opening with HashDB should migrate the schema
        db = HashDB(isolated_hash_dir)
        entry = db.lookup("old_key")
        assert entry is not None
        assert entry["file_path"] == "/old/path.jpg"
        assert entry["file_size"] == 0  # Default for migrated rows

        # New stores should work with file_size
        db.store("new_key", "/new.jpg", "newhash", "https://new.url", 999)
        entry2 = db.lookup("new_key")
        assert entry2["file_size"] == 999
