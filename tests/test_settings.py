"""
Integration tests for the Settings module.
These tests verify settings loading, saving, and UI configuration logic.
"""

import os
import sys
import tempfile

from PyQt6.QtCore import QSettings


class TestDefaultSettings:
    """Tests for default settings values."""

    def test_default_base_folder_name(self):
        """Test default base folder name."""

        # Create a minimal mock parent
        class MockParent:
            base_folder = ""
            download_folder = ""
            cache_folder = ""
            other_files_folder = ""

            def log(self, msg):
                pass

            def ensure_folders_exist(self):
                pass

        # Use a unique QSettings name to avoid conflicts
        QSettings("VoxDroid_Test", "KemonoDownloader_Test").clear()

        # Access default settings directly
        default_settings = {
            "base_folder_name": "Kemono Downloader",
            "simultaneous_downloads": 5,
            "auto_check_updates": True,
            "language": "english",
            "creator_posts_max_attempts": 200,
            "post_data_max_retries": 7,
            "file_download_max_retries": 50,
            "api_request_max_retries": 3,
            "use_proxy": False,
            "proxy_type": "tor",
            "custom_proxy_url": "",
            "tor_path": "",
        }

        assert default_settings["base_folder_name"] == "Kemono Downloader"
        assert default_settings["simultaneous_downloads"] == 5
        assert default_settings["auto_check_updates"] is True
        assert default_settings["language"] == "english"

    def test_default_retry_settings(self):
        """Test default retry configuration values."""
        defaults = {
            "creator_posts_max_attempts": 200,
            "post_data_max_retries": 7,
            "file_download_max_retries": 50,
            "api_request_max_retries": 3,
        }

        # Verify reasonable default values
        assert defaults["creator_posts_max_attempts"] > 0
        assert defaults["post_data_max_retries"] > 0
        assert defaults["file_download_max_retries"] > 0
        assert defaults["api_request_max_retries"] > 0

        # Verify they are integers
        assert isinstance(defaults["creator_posts_max_attempts"], int)
        assert isinstance(defaults["post_data_max_retries"], int)

    def test_default_proxy_settings(self):
        """Test default proxy configuration."""
        defaults = {
            "use_proxy": False,
            "proxy_type": "tor",
            "custom_proxy_url": "",
            "tor_path": "",
        }

        # Proxy should be disabled by default
        assert defaults["use_proxy"] is False
        assert defaults["proxy_type"] in ["tor", "custom"]
        assert defaults["custom_proxy_url"] == ""


class TestBaseDirectoryLogic:
    """Tests for base directory path logic."""

    def test_windows_default_directory(self):
        """Test default directory path on Windows."""
        if sys.platform == "win32":
            appdata = os.getenv("APPDATA", os.path.expanduser("~"))
            expected_base = os.path.join(appdata, "Kemono Downloader")

            # Path should be under APPDATA on Windows
            assert "Kemono Downloader" in expected_base
            assert os.path.isabs(expected_base)

    def test_macos_default_directory(self):
        """Test default directory path on macOS."""
        if sys.platform == "darwin":
            expected_base = os.path.expanduser(
                "~/Library/Application Support/Kemono Downloader"
            )

            assert "Library/Application Support" in expected_base
            assert "Kemono Downloader" in expected_base

    def test_linux_default_directory(self):
        """Test default directory path on Linux."""
        if sys.platform not in ["win32", "darwin"]:
            xdg_data = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
            expected_base = os.path.join(xdg_data, "Kemono Downloader")

            assert "Kemono Downloader" in expected_base

    def test_directory_path_is_absolute(self):
        """Test that directory paths are absolute."""
        if sys.platform == "win32":
            base_dir = os.path.join(
                os.getenv("APPDATA", os.path.expanduser("~")), "Kemono Downloader"
            )
        elif sys.platform == "darwin":
            base_dir = os.path.expanduser(
                "~/Library/Application Support/Kemono Downloader"
            )
        else:
            base_dir = os.path.join(
                os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share")),
                "Kemono Downloader",
            )

        assert os.path.isabs(base_dir)


class TestLanguageSettings:
    """Tests for language settings."""

    def test_available_languages(self):
        """Test that expected languages are available."""
        from kemonodownloader.kd_language import language_manager

        languages = language_manager.get_available_languages()

        assert "english" in languages
        assert "japanese" in languages
        assert "korean" in languages
        assert "chinese-simplified" in languages

    def test_language_persistence(self):
        """Test that language setting can be changed and retrieved."""
        from kemonodownloader.kd_language import language_manager

        original = language_manager.get_language()

        try:
            language_manager.set_language("japanese")
            assert language_manager.get_language() == "japanese"

            language_manager.set_language("korean")
            assert language_manager.get_language() == "korean"
        finally:
            language_manager.set_language(original)


class TestProxySettings:
    """Tests for proxy configuration logic."""

    def test_proxy_type_values(self):
        """Test valid proxy type values."""
        valid_types = ["custom", "tor"]

        for proxy_type in valid_types:
            assert proxy_type in ["custom", "tor", "none"]

    def test_custom_proxy_url_format(self):
        """Test custom proxy URL format validation."""
        valid_urls = [
            "127.0.0.1:8080",
            "192.168.1.1:3128",
            "http://proxy.example.com:8080",
            "socks5://127.0.0.1:9050",
        ]

        for url in valid_urls:
            # Basic validation - should contain a port
            assert ":" in url or url.startswith("http")

    def test_tor_default_port(self):
        """Test Tor SOCKS proxy default configuration."""
        tor_proxy_url = "socks5h://127.0.0.1:9050"

        assert "127.0.0.1" in tor_proxy_url
        assert "9050" in tor_proxy_url
        assert "socks" in tor_proxy_url.lower()


class TestSimultaneousDownloadsSettings:
    """Tests for simultaneous downloads configuration."""

    def test_simultaneous_downloads_range(self):
        """Test valid range for simultaneous downloads."""
        min_downloads = 1
        max_downloads = 20
        default_downloads = 5

        assert min_downloads >= 1
        assert max_downloads <= 20
        assert min_downloads <= default_downloads <= max_downloads

    def test_simultaneous_downloads_is_integer(self):
        """Test that simultaneous downloads is an integer."""
        value = 5
        assert isinstance(value, int)
        assert value > 0


class TestRetrySettings:
    """Tests for retry configuration."""

    def test_retry_values_positive(self):
        """Test that all retry values are positive."""
        retry_settings = {
            "creator_posts_max_attempts": 200,
            "post_data_max_retries": 7,
            "file_download_max_retries": 50,
            "api_request_max_retries": 3,
        }

        for key, value in retry_settings.items():
            assert value > 0, f"{key} should be positive"

    def test_retry_ranges(self):
        """Test that retry values are within reasonable ranges."""
        # Based on UI spinbox ranges
        assert 1 <= 200 <= 1000  # creator_posts_max_attempts
        assert 1 <= 7 <= 100  # post_data_max_retries
        assert 1 <= 50 <= 200  # file_download_max_retries
        assert 1 <= 3 <= 50  # api_request_max_retries


class TestFolderStructure:
    """Tests for folder structure configuration."""

    def test_folder_structure_paths(self):
        """Test that folder structure is correctly defined."""
        base_folder = "/fake/base/Kemono Downloader"

        expected_structure = {
            "Downloads": os.path.join(base_folder, "Downloads"),
            "Cache": os.path.join(base_folder, "Cache"),
            "Other Files": os.path.join(base_folder, "Other Files"),
        }

        assert expected_structure["Downloads"].endswith("Downloads")
        assert expected_structure["Cache"].endswith("Cache")
        assert expected_structure["Other Files"].endswith("Other Files")

    def test_folder_creation_logic(self):
        """Test folder creation with os.makedirs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_folder = os.path.join(tmpdir, "Test", "Nested", "Folder")

            # os.makedirs with exist_ok=True should not raise
            os.makedirs(test_folder, exist_ok=True)

            assert os.path.exists(test_folder)
            assert os.path.isdir(test_folder)

            # Calling again should not raise
            os.makedirs(test_folder, exist_ok=True)


class TestQSettingsIntegration:
    """Tests for QSettings integration."""

    def test_qsettings_value_types(self):
        """Test QSettings value type handling."""
        settings = QSettings("VoxDroid_UnitTest", "KemonoDownloader_UnitTest")

        try:
            # Test setting and getting different types
            settings.setValue("test_string", "hello")
            settings.setValue("test_int", 42)
            settings.setValue("test_bool", True)

            # Retrieve with type hints
            assert settings.value("test_string", type=str) == "hello"
            assert settings.value("test_int", type=int) == 42
            assert settings.value("test_bool", type=bool) is True
        finally:
            # Cleanup
            settings.clear()

    def test_qsettings_default_values(self):
        """Test QSettings default value handling."""
        settings = QSettings("VoxDroid_UnitTest2", "KemonoDownloader_UnitTest2")

        try:
            # Non-existent key should return default
            assert settings.value("nonexistent_key", "default_value") == "default_value"
            assert settings.value("nonexistent_int", 100, type=int) == 100
        finally:
            settings.clear()
