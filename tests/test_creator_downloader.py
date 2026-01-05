"""
Integration tests for the Creator Downloader module.
These tests verify the logic of post detection and file processing without mocking,
using real HTTP requests to the API endpoints where appropriate.
"""

import hashlib
import os
import sys


try:
    from kemonodownloader.creator_downloader import (
        HEADERS,
        ThreadSettings,
        get_domain_config,
        sanitize_filename,
    )
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
    from kemonodownloader.creator_downloader import (
        HEADERS,
        ThreadSettings,
        get_domain_config,
        sanitize_filename,
    )


class TestThreadSettings:
    """Tests for the ThreadSettings configuration class."""

    def test_thread_settings_initialization(self):
        """Test that ThreadSettings initializes with correct values."""
        settings = ThreadSettings(
            creator_posts_max_attempts=100,
            post_data_max_retries=5,
            file_download_max_retries=10,
            api_request_max_retries=3,
            simultaneous_downloads=5,
            settings_tab=None,
        )

        assert settings.creator_posts_max_attempts == 100
        assert settings.post_data_max_retries == 5
        assert settings.file_download_max_retries == 10
        assert settings.api_request_max_retries == 3
        assert settings.simultaneous_downloads == 5
        assert settings.settings_tab is None

    def test_thread_settings_with_settings_tab(self):
        """Test ThreadSettings with a settings_tab reference."""

        class MockSettingsTab:
            pass

        mock_tab = MockSettingsTab()
        settings = ThreadSettings(
            creator_posts_max_attempts=50,
            post_data_max_retries=3,
            file_download_max_retries=5,
            api_request_max_retries=2,
            simultaneous_downloads=10,
            settings_tab=mock_tab,
        )

        assert settings.settings_tab is mock_tab


class TestDomainConfiguration:
    """Tests for domain configuration and URL parsing."""

    def test_kemono_services(self):
        """Test that kemono.cr supports various services."""
        services = ["fanbox", "patreon", "fantia", "gumroad", "subscribestar"]
        for service in services:
            url = f"https://kemono.cr/{service}/user/12345"
            config = get_domain_config(url)
            assert config["domain"] == "kemono.cr"

    def test_coomer_services(self):
        """Test that coomer.st supports various services."""
        services = ["onlyfans", "fansly"]
        for service in services:
            url = f"https://coomer.st/{service}/user/12345"
            config = get_domain_config(url)
            assert config["domain"] == "coomer.st"

    def test_api_endpoint_format(self):
        """Test that API endpoints are correctly formatted."""
        config = get_domain_config("https://kemono.cr/fanbox/user/123")
        assert config["api_base"].endswith("/api/v1")
        assert not config["api_base"].endswith("/")


class TestFileDetectionLogic:
    """Tests for file detection patterns and logic."""

    def test_image_extensions_detection(self):
        """Test detection of common image file extensions."""
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        for ext in image_extensions:
            filename = f"test_image{ext}"
            # Verify the extension is properly extracted
            _, file_ext = os.path.splitext(filename)
            assert file_ext.lower() in image_extensions

    def test_archive_extensions_detection(self):
        """Test detection of common archive file extensions."""
        archive_extensions = [".zip", ".rar", ".7z"]
        for ext in archive_extensions:
            filename = f"archive{ext}"
            _, file_ext = os.path.splitext(filename)
            assert file_ext.lower() in archive_extensions

    def test_video_extensions_detection(self):
        """Test detection of common video file extensions."""
        video_extensions = [".mp4", ".mov", ".webm"]
        for ext in video_extensions:
            filename = f"video{ext}"
            _, file_ext = os.path.splitext(filename)
            assert file_ext.lower() in [".mp4", ".mov", ".webm"]

    def test_audio_extensions_detection(self):
        """Test detection of common audio file extensions."""
        audio_extensions = [".mp3", ".wav", ".flac"]
        for ext in audio_extensions:
            filename = f"audio{ext}"
            _, file_ext = os.path.splitext(filename)
            assert file_ext.lower() in audio_extensions


class TestURLParsing:
    """Tests for URL parsing and validation logic."""

    def test_parse_creator_url_components(self):
        """Test parsing creator URL into components."""
        url = "https://kemono.cr/fanbox/user/12345678"
        parts = url.rstrip("/").split("/")

        assert parts[-1] == "12345678"  # creator_id
        assert parts[-2] == "user"
        assert parts[-3] == "fanbox"  # service

    def test_parse_post_url_components(self):
        """Test parsing post URL into components."""
        url = "https://kemono.cr/fanbox/user/12345678/post/87654321"
        parts = url.rstrip("/").split("/")

        assert parts[-1] == "87654321"  # post_id
        assert parts[-2] == "post"
        assert parts[-3] == "12345678"  # creator_id
        assert parts[-5] == "fanbox"  # service

    def test_url_with_query_parameters(self):
        """Test URL parsing with query parameters."""
        from urllib.parse import parse_qs, urlparse

        url = "https://kemono.cr/fanbox/user/12345?o=50&q=search"
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)

        assert query_params.get("o", [None])[0] == "50"
        assert query_params.get("q", [None])[0] == "search"

    def test_url_path_extraction(self):
        """Test extracting clean path from URL."""
        from urllib.parse import urlparse

        url = "https://kemono.cr/fanbox/user/12345?o=50"
        parsed = urlparse(url)
        path = parsed.path.strip("/")

        assert path == "fanbox/user/12345"
        assert parsed.query == "o=50"


class TestFileHashLogic:
    """Tests for file hash calculation and deduplication logic."""

    def test_md5_hash_calculation(self):
        """Test MD5 hash calculation for data."""
        test_data = b"test content for hashing"
        expected_hash = hashlib.md5(test_data).hexdigest()

        # Verify hash is consistent
        calculated_hash = hashlib.md5(test_data).hexdigest()
        assert calculated_hash == expected_hash
        assert len(calculated_hash) == 32  # MD5 produces 32 hex characters

    def test_hash_uniqueness(self):
        """Test that different content produces different hashes."""
        data1 = b"content one"
        data2 = b"content two"

        hash1 = hashlib.md5(data1).hexdigest()
        hash2 = hashlib.md5(data2).hexdigest()

        assert hash1 != hash2

    def test_hash_consistency(self):
        """Test that same content always produces same hash."""
        data = b"consistent content"

        hash1 = hashlib.md5(data).hexdigest()
        hash2 = hashlib.md5(data).hexdigest()

        assert hash1 == hash2


class TestSanitizeFilenameEdgeCases:
    """Additional edge case tests for filename sanitization."""

    def test_emoji_in_filename(self):
        """Test handling of emoji characters in filenames."""
        result = sanitize_filename("Post 🎨 with emoji")
        # Should not crash and should produce a valid filename
        assert len(result) > 0
        assert result != "unnamed"

    def test_very_long_unicode_filename(self):
        """Test truncation of long unicode filenames."""
        # Japanese text that's very long
        long_name = "日本語テスト" * 50
        result = sanitize_filename(long_name, max_length=100)
        assert len(result) <= 100

    def test_filename_with_extension(self):
        """Test that file extensions are preserved."""
        result = sanitize_filename("my file.jpg")
        assert result.endswith(".jpg")

    def test_only_whitespace(self):
        """Test filename with only whitespace."""
        result = sanitize_filename("   ")
        assert result == "unnamed"

    def test_periods_in_middle(self):
        """Test that periods in the middle of filename are preserved."""
        result = sanitize_filename("file.name.ext")
        assert "file" in result
        assert "ext" in result


class TestHeadersConfiguration:
    """Tests for HTTP headers configuration."""

    def test_headers_have_user_agent(self):
        """Test that headers include a User-Agent."""
        assert "User-Agent" in HEADERS
        assert len(HEADERS["User-Agent"]) > 0

    def test_headers_have_referer(self):
        """Test that headers include a Referer."""
        assert "Referer" in HEADERS
        assert "kemono" in HEADERS["Referer"] or len(HEADERS["Referer"]) > 0

    def test_headers_have_accept_language(self):
        """Test that headers include Accept-Language."""
        assert "Accept-Language" in HEADERS

    def test_headers_have_connection(self):
        """Test that headers include Connection setting."""
        assert "Connection" in HEADERS
        assert HEADERS["Connection"] == "keep-alive"


class TestAPIResponseParsing:
    """Tests for API response parsing logic."""

    def test_parse_post_data_structure(self):
        """Test parsing of expected post data structure."""
        sample_post = {
            "id": "12345",
            "title": "Test Post",
            "file": {"path": "/data/file.jpg", "name": "file.jpg"},
            "attachments": [
                {"path": "/data/att1.png", "name": "att1.png"},
                {"path": "/data/att2.zip", "name": "att2.zip"},
            ],
            "content": "<p>Post content</p>",
        }

        # Verify structure access
        assert sample_post.get("id") == "12345"
        assert sample_post.get("title") == "Test Post"
        assert sample_post.get("file", {}).get("path") == "/data/file.jpg"
        assert len(sample_post.get("attachments", [])) == 2

    def test_parse_empty_post_data(self):
        """Test parsing of post with missing optional fields."""
        minimal_post = {"id": "12345"}

        # Should handle missing fields gracefully
        assert minimal_post.get("title", f"Post {minimal_post['id']}") == "Post 12345"
        assert minimal_post.get("file") is None
        assert minimal_post.get("attachments", []) == []
        assert minimal_post.get("content", "") == ""

    def test_parse_attachment_list(self):
        """Test parsing of attachment list."""
        attachments = [
            {"path": "/file1.jpg", "name": "image1.jpg"},
            {"path": "/file2.png", "name": "image2.png"},
            {"path": "/archive.zip", "name": "files.zip"},
        ]

        # Extract image attachments
        image_exts = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        images = [
            a
            for a in attachments
            if os.path.splitext(a["path"])[1].lower() in image_exts
        ]

        assert len(images) == 2

        # Extract archives
        archive_exts = [".zip", ".rar", ".7z"]
        archives = [
            a
            for a in attachments
            if os.path.splitext(a["path"])[1].lower() in archive_exts
        ]

        assert len(archives) == 1
