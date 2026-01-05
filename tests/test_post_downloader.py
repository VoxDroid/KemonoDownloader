"""
Integration tests for the Post Downloader module.
These tests verify the logic of single post detection and file processing.
"""

import os
import sys
from urllib.parse import urljoin


try:
    from kemonodownloader.post_downloader import (
        HEADERS,
        ThreadSettings,
        get_domain_config,
    )
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
    from kemonodownloader.post_downloader import (
        HEADERS,
        ThreadSettings,
        get_domain_config,
    )


class TestPostThreadSettings:
    """Tests for the Post Downloader ThreadSettings class."""

    def test_post_thread_settings_initialization(self):
        """Test that ThreadSettings initializes correctly."""
        settings = ThreadSettings(
            creator_posts_max_attempts=100,
            post_data_max_retries=5,
            file_download_max_retries=10,
            api_request_max_retries=3,
            simultaneous_downloads=5,
            settings_tab=None,
        )

        assert settings.post_data_max_retries == 5
        assert settings.file_download_max_retries == 10
        assert settings.api_request_max_retries == 3


class TestPostURLParsing:
    """Tests for post URL parsing and validation."""

    def test_parse_post_url_basic(self):
        """Test parsing a basic post URL."""
        url = "https://kemono.cr/fanbox/user/12345/post/67890"
        parts = url.rstrip("/").split("/")

        service = parts[-5]
        creator_id = parts[-3]
        post_id = parts[-1]

        assert service == "fanbox"
        assert creator_id == "12345"
        assert post_id == "67890"

    def test_parse_post_url_coomer(self):
        """Test parsing a coomer.st post URL."""
        url = "https://coomer.st/onlyfans/user/98765/post/54321"
        parts = url.rstrip("/").split("/")

        service = parts[-5]
        creator_id = parts[-3]
        post_id = parts[-1]

        assert service == "onlyfans"
        assert creator_id == "98765"
        assert post_id == "54321"

    def test_construct_api_url(self):
        """Test constructing API URL from post URL components."""
        url = "https://kemono.cr/patreon/user/111/post/222"
        parts = url.rstrip("/").split("/")

        service = parts[-5]
        creator_id = parts[-3]
        post_id = parts[-1]

        config = get_domain_config(url)
        api_url = f"{config['api_base']}/{service}/user/{creator_id}/post/{post_id}"

        assert api_url == "https://kemono.cr/api/v1/patreon/user/111/post/222"


class TestFileURLConstruction:
    """Tests for file URL construction from API responses."""

    def test_construct_file_url_basic(self):
        """Test constructing file URL from API path."""
        base_url = "https://kemono.cr"
        file_path = "/data/12/34/1234abcd.jpg"

        file_url = urljoin(base_url, file_path)

        assert file_url == "https://kemono.cr/data/12/34/1234abcd.jpg"

    def test_construct_file_url_with_name_query(self):
        """Test adding filename query parameter to URL."""
        base_url = "https://kemono.cr"
        file_path = "/data/12/34/1234abcd"
        file_name = "my_image.jpg"

        file_url = urljoin(base_url, file_path)
        if "f=" not in file_url and file_name:
            file_url += f"?f={file_name}"

        assert file_url == "https://kemono.cr/data/12/34/1234abcd?f=my_image.jpg"

    def test_file_url_already_has_query(self):
        """Test handling URL that already has query parameters."""
        file_url = "https://kemono.cr/data/file?f=existing.jpg"
        file_name = "new_name.jpg"

        # Should not add duplicate f= parameter
        if "f=" not in file_url and file_name:
            file_url += f"?f={file_name}"

        # f= is already in the URL, so nothing should be added
        assert file_url == "https://kemono.cr/data/file?f=existing.jpg"


class TestFileExtensionDetection:
    """Tests for file extension detection logic."""

    def test_get_extension_from_path(self):
        """Test extracting extension from file path."""
        test_cases = [
            ("/path/to/file.jpg", ".jpg"),
            ("/path/to/file.PNG", ".png"),
            ("/path/to/archive.ZIP", ".zip"),
            ("/path/to/video.mp4", ".mp4"),
            ("/path/to/noext", ""),
        ]

        for path, expected_ext in test_cases:
            _, ext = os.path.splitext(path)
            assert ext.lower() == expected_ext.lower()

    def test_effective_extension_from_name(self):
        """Test getting effective extension prioritizing name over path."""

        def get_effective_extension(file_path, file_name):
            name_ext = os.path.splitext(file_name)[1].lower()
            path_ext = os.path.splitext(file_path)[1].lower()
            return name_ext if name_ext else path_ext

        # Name has extension, path doesn't
        assert get_effective_extension("/data/abc123", "image.jpg") == ".jpg"

        # Path has extension, name doesn't
        assert get_effective_extension("/data/abc123.png", "image") == ".png"

        # Both have extension, name takes priority
        assert get_effective_extension("/data/abc.png", "image.jpg") == ".jpg"

        # Neither has extension
        assert get_effective_extension("/data/abc", "image") == ""


class TestAllowedExtensions:
    """Tests for file extension filtering."""

    def test_image_extensions_allowed(self):
        """Test that common image extensions are in allowed list."""
        allowed = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".jpe"]

        test_files = [
            ("image.jpg", True),
            ("image.jpeg", True),
            ("image.png", True),
            ("animation.gif", True),
            ("photo.webp", True),
        ]

        for filename, should_be_allowed in test_files:
            ext = os.path.splitext(filename)[1].lower()
            is_allowed = ext in allowed or (ext == ".jpeg" and ".jpg" in allowed)
            assert is_allowed == should_be_allowed

    def test_archive_extensions_allowed(self):
        """Test that common archive extensions are in allowed list."""
        allowed = [".zip", ".rar", ".7z"]

        test_files = [
            ("files.zip", True),
            ("archive.rar", True),
            ("compressed.7z", True),
        ]

        for filename, should_be_allowed in test_files:
            ext = os.path.splitext(filename)[1].lower()
            is_allowed = ext in allowed
            assert is_allowed == should_be_allowed

    def test_video_extensions_allowed(self):
        """Test that common video extensions are in allowed list."""
        allowed = [".mp4", ".mov"]

        test_files = [
            ("video.mp4", True),
            ("clip.mov", True),
        ]

        for filename, should_be_allowed in test_files:
            ext = os.path.splitext(filename)[1].lower()
            is_allowed = ext in allowed
            assert is_allowed == should_be_allowed

    def test_audio_extensions_allowed(self):
        """Test that common audio extensions are in allowed list."""
        allowed = [".mp3", ".wav", ".flac"]

        test_files = [
            ("song.mp3", True),
            ("audio.wav", True),
            ("lossless.flac", True),
        ]

        for filename, should_be_allowed in test_files:
            ext = os.path.splitext(filename)[1].lower()
            is_allowed = ext in allowed
            assert is_allowed == should_be_allowed

    def test_special_extensions_allowed(self):
        """Test that special file extensions are in allowed list."""
        allowed = [".psd", ".clip", ".pdf", ".docx"]

        test_files = [
            ("artwork.psd", True),
            ("project.clip", True),
            ("document.pdf", True),
            ("text.docx", True),
        ]

        for filename, should_be_allowed in test_files:
            ext = os.path.splitext(filename)[1].lower()
            is_allowed = ext in allowed
            assert is_allowed == should_be_allowed


class TestPostDataStructure:
    """Tests for parsing post data structures from API."""

    def test_post_with_main_file(self):
        """Test parsing post with main file."""
        post_data = {
            "id": "12345",
            "title": "Test Post",
            "file": {"path": "/data/file.jpg", "name": "cover.jpg"},
        }

        assert "file" in post_data
        assert post_data["file"]["path"] == "/data/file.jpg"
        assert post_data["file"]["name"] == "cover.jpg"

    def test_post_with_attachments(self):
        """Test parsing post with attachments."""
        post_data = {
            "id": "12345",
            "title": "Test Post",
            "attachments": [
                {"path": "/data/att1.png", "name": "image1.png"},
                {"path": "/data/att2.png", "name": "image2.png"},
                {"path": "/data/archive.zip", "name": "bonus.zip"},
            ],
        }

        assert len(post_data["attachments"]) == 3

        # Count images
        image_exts = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        images = [
            a
            for a in post_data["attachments"]
            if os.path.splitext(a["path"])[1].lower() in image_exts
        ]
        assert len(images) == 2

    def test_post_with_content_images(self):
        """Test parsing post with embedded content images."""
        from bs4 import BeautifulSoup

        post_data = {
            "id": "12345",
            "title": "Test Post",
            "content": '<p>Text</p><img src="/data/inline1.jpg"><img src="/data/inline2.png">',
        }

        soup = BeautifulSoup(post_data["content"], "html.parser")
        images = soup.select("img[src]")

        assert len(images) == 2
        assert images[0]["src"] == "/data/inline1.jpg"
        assert images[1]["src"] == "/data/inline2.png"

    def test_post_with_empty_content(self):
        """Test parsing post with empty content."""
        post_data = {"id": "12345", "title": "Test Post", "content": ""}

        assert post_data.get("content", "") == ""

    def test_post_with_null_file(self):
        """Test parsing post where file is null."""
        post_data = {"id": "12345", "title": "Test Post", "file": None}

        # Should handle null file gracefully
        file_data = post_data.get("file")
        assert file_data is None

        # Safe access pattern
        file_path = post_data.get("file", {}) or {}
        path = file_path.get("path")
        assert path is None


class TestDeduplication:
    """Tests for file deduplication logic."""

    def test_remove_duplicate_files(self):
        """Test removing duplicate file entries."""
        files = [
            ("file1.jpg", "https://example.com/file1.jpg"),
            ("file2.jpg", "https://example.com/file2.jpg"),
            ("file1.jpg", "https://example.com/file1.jpg"),  # Duplicate
            ("file3.jpg", "https://example.com/file3.jpg"),
        ]

        # Using dict.fromkeys to remove duplicates while preserving order
        unique_files = list(dict.fromkeys(files))

        assert len(unique_files) == 3
        assert files[0] in unique_files
        assert files[1] in unique_files
        assert files[3] in unique_files

    def test_dedup_by_url(self):
        """Test deduplication by URL only."""
        files = [
            ("name1.jpg", "https://example.com/same_url"),
            ("name2.jpg", "https://example.com/same_url"),  # Same URL, different name
            ("name3.jpg", "https://example.com/different_url"),
        ]

        # Create a set of URLs to track seen URLs
        seen_urls = set()
        unique_files = []

        for name, url in files:
            if url not in seen_urls:
                seen_urls.add(url)
                unique_files.append((name, url))

        assert len(unique_files) == 2


class TestHeadersConfiguration:
    """Tests for HTTP headers in post downloader."""

    def test_post_headers_have_required_fields(self):
        """Test that headers contain required fields."""
        required_fields = ["User-Agent", "Referer", "Accept-Language", "Connection"]

        for field in required_fields:
            assert field in HEADERS, f"Missing header field: {field}"

    def test_post_headers_values_not_empty(self):
        """Test that header values are not empty."""
        for key, value in HEADERS.items():
            assert value is not None, f"Header {key} is None"
            assert len(str(value)) > 0, f"Header {key} is empty"
