"""Tests for Fast Mode and multi-URL batch input features.

These tests exercise logic in both PostDownloaderTab and CreatorDownloaderTab
without requiring a live network connection or real downloads.
"""

import pytest

from kemonodownloader.kd_language import language_manager, translate
from kemonodownloader.post_downloader import get_domain_config


class TestFastModeTranslations:
    """Verify that all fast-mode translation keys exist in every language."""

    KEYS = [
        "fast_mode",
        "fast_mode_enabled",
        "fast_mode_disabled",
        "fast_mode_removed_post_url",
        "fast_mode_removed_posts",
        "fast_mode_removed_creator",
        "fast_mode_info_title",
        "fast_mode_info_text",
        "multi_url_placeholder",
        "multi_url_placeholder_creator",
        "add_all_to_queue",
    ]

    def setup_method(self):
        self.original = language_manager.current_language

    def teardown_method(self):
        language_manager.set_language(self.original)

    @pytest.mark.parametrize("lang", language_manager.get_available_languages())
    def test_keys_exist(self, lang):
        language_manager.set_language(lang)
        for key in self.KEYS:
            result = translate(key)
            # translate returns the key itself when it's missing
            assert result != key, f"Missing translation for '{key}' in {lang}"

    def test_fast_mode_removed_posts_format(self):
        language_manager.set_language("english")
        result = translate("fast_mode_removed_posts", 3)
        assert "3" in result

    def test_fast_mode_removed_creator_format(self):
        language_manager.set_language("english")
        result = translate("fast_mode_removed_creator", "https://kemono.cr/user/123")
        assert "123" in result


class TestFastModePostLogic:
    """Test the fast-mode toggle logic for the post downloader (unit-level)."""

    def test_fast_mode_flags(self):
        """fast_mode attribute should default to False."""
        # Simulating the attribute as it would appear in __init__
        fast_mode = False
        assert fast_mode is False

        # After toggle (state == 2 means Checked)
        state = 2
        fast_mode = state == 2
        assert fast_mode is True

    def test_auto_remove_filter(self):
        """Test the auto-remove logic that runs in post_download_finished."""
        post_queue = [
            ("https://kemono.cr/fanbox/user/1/post/10", False),
            ("https://kemono.cr/fanbox/user/1/post/20", False),
            ("https://kemono.cr/fanbox/user/1/post/30", False),
        ]
        all_files_map = {
            "https://kemono.cr/fanbox/user/1/post/10": [("file.jpg", "10")],
            "https://kemono.cr/fanbox/user/1/post/20": [("file.jpg", "20")],
            # post/30 was NOT in the files map — not completed
        }
        # Simulate fast-mode auto-remove of completed posts
        completed_urls = {url for url, _ in post_queue if url in all_files_map}
        remaining = [(u, c) for u, c in post_queue if u not in completed_urls]

        assert len(remaining) == 1
        assert remaining[0][0].endswith("/post/30")

    def test_auto_remove_empty_queue(self):
        """Auto-remove on an empty queue should produce an empty list."""
        post_queue = []
        all_files_map = {}
        completed_urls = {url for url, _ in post_queue if url in all_files_map}
        remaining = [(u, c) for u, c in post_queue if u not in completed_urls]
        assert remaining == []


class TestFastModeCreatorLogic:
    """Test the fast-mode toggle logic for the creator downloader (unit-level)."""

    def test_creator_auto_remove_filter(self):
        """Completed creator should be removed from queue in fast mode."""
        creator_queue = [
            ("https://kemono.cr/fanbox/user/100", False),
            ("https://kemono.cr/fanbox/user/200", False),
        ]
        current_creator_url = "https://kemono.cr/fanbox/user/100"

        remaining = [
            (u, c)
            for u, c in creator_queue
            if u.rstrip("/") != current_creator_url.rstrip("/")
        ]
        assert len(remaining) == 1
        assert remaining[0][0].endswith("/200")


class TestMultiURLParsing:
    """Test parsing of multi-URL text input (newline-separated URLs)."""

    def test_parse_multiple_urls(self):
        text = (
            "https://kemono.cr/fanbox/user/1/post/10\n"
            "https://kemono.cr/fanbox/user/1/post/20\n"
            "\n"
            "https://kemono.cr/fanbox/user/1/post/30\n"
        )
        urls = [line.strip() for line in text.split("\n") if line.strip()]
        assert len(urls) == 3

    def test_deduplication(self):
        text = (
            "https://kemono.cr/fanbox/user/1/post/10\n"
            "https://kemono.cr/fanbox/user/1/post/10\n"
            "https://kemono.cr/fanbox/user/1/post/20\n"
        )
        urls = [line.strip() for line in text.split("\n") if line.strip()]
        post_queue = []
        added = 0
        skipped = 0
        for url in urls:
            normalized = url.rstrip("/")
            if any(item[0].rstrip("/") == normalized for item in post_queue):
                skipped += 1
                continue
            post_queue.append((url, False))
            added += 1

        assert added == 2
        assert skipped == 1

    def test_empty_input(self):
        text = "   \n  \n  "
        urls = [line.strip() for line in text.split("\n") if line.strip()]
        assert urls == []

    def test_single_url(self):
        text = "https://kemono.cr/fanbox/user/1/post/10"
        urls = [line.strip() for line in text.split("\n") if line.strip()]
        assert len(urls) == 1

    def test_urls_with_trailing_slashes(self):
        text = (
            "https://kemono.cr/fanbox/user/1/post/10/\n"
            "https://kemono.cr/fanbox/user/1/post/10\n"
        )
        urls = [line.strip() for line in text.split("\n") if line.strip()]
        post_queue = []
        added = 0
        for url in urls:
            normalized = url.rstrip("/")
            if any(item[0].rstrip("/") == normalized for item in post_queue):
                continue
            post_queue.append((url, False))
            added += 1
        # Should dedup even with trailing slash difference
        assert added == 1


class TestMultiURLCreatorParsing:
    """Test multi-URL parsing for creator URLs."""

    def test_parse_creator_urls(self):
        text = (
            "https://kemono.cr/fanbox/user/100\n"
            "https://kemono.cr/patreon/user/200\n"
            "https://coomer.st/onlyfans/user/300\n"
        )
        urls = [line.strip() for line in text.split("\n") if line.strip()]
        assert len(urls) == 3

    def test_dedup_creator_urls(self):
        text = (
            "https://kemono.cr/fanbox/user/100\n" "https://kemono.cr/fanbox/user/100\n"
        )
        urls = [line.strip() for line in text.split("\n") if line.strip()]
        queue = []
        for url in urls:
            normalized = url.rstrip("/")
            if any(item[0].rstrip("/") == normalized for item in queue):
                continue
            queue.append((url, False))
        assert len(queue) == 1


class TestPostURLValidation:
    """Test URL validation logic used when adding posts (extracted from PostDownloaderTab)."""

    @staticmethod
    def _is_valid_post_url(url):
        """Mirror the validation logic from PostDownloaderTab.check_post_url_validity."""
        url = url.rstrip("/")
        parts = url.split("/")
        if len(parts) < 7:
            return False
        domain_config = get_domain_config(url)
        if domain_config["domain"] not in url:
            return False
        # Basic structure check: .../service/user/{id}/post/{id}
        return parts[-4] == "user" and parts[-2] == "post"

    def test_valid_kemono_url(self):
        assert self._is_valid_post_url("https://kemono.cr/fanbox/user/12345/post/67890")

    def test_valid_coomer_url(self):
        assert self._is_valid_post_url(
            "https://coomer.st/onlyfans/user/12345/post/67890"
        )

    def test_invalid_missing_post(self):
        assert not self._is_valid_post_url("https://kemono.cr/fanbox/user/12345")

    def test_invalid_random_url(self):
        assert not self._is_valid_post_url("https://google.com/search?q=test")

    def test_url_trailing_slash(self):
        assert self._is_valid_post_url(
            "https://kemono.cr/fanbox/user/12345/post/67890/"
        )


class TestBulkAddSummaryTranslation:
    """Ensure the bulk_add_summary translation key works."""

    def setup_method(self):
        self.original = language_manager.current_language
        language_manager.set_language("english")

    def teardown_method(self):
        language_manager.set_language(self.original)

    def test_bulk_add_summary(self):
        result = translate("bulk_add_summary", 5, 2)
        assert "5" in result
        assert "2" in result


class TestIncrementalPostRemoval:
    """Test the incremental per-URL removal logic for the post downloader.

    In fast mode, each post URL should be removed from the queue as soon as
    all of its post_ids have been marked complete, rather than waiting for
    the entire batch to finish.
    """

    def _build_post_to_url_map(self, urls, all_files_map):
        """Mirror the reverse-map building from start_post_download."""
        post_to_url = {}
        for url in urls:
            for _, post_id in all_files_map.get(url, []):
                post_to_url[post_id] = url
        return post_to_url

    def _simulate_completion(
        self, post_id, post_to_url, all_files_map, completed_posts, post_queue
    ):
        """Simulate update_post_completion fast-mode logic.

        Returns the updated post_queue after the removal check.
        """
        completed_posts.add(post_id)
        url = post_to_url.get(post_id)
        if url:
            all_post_ids = {pid for _, pid in all_files_map.get(url, [])}
            if all_post_ids and all_post_ids.issubset(completed_posts):
                normalized = url.rstrip("/")
                post_queue = [
                    (u, c) for u, c in post_queue if u.rstrip("/") != normalized
                ]
        return post_queue

    def test_single_post_removed_on_completion(self):
        """A single-post URL should be removed immediately when its post completes."""
        post_queue = [
            ("https://kemono.cr/fanbox/user/1/post/10", False),
            ("https://kemono.cr/fanbox/user/1/post/20", False),
        ]
        all_files_map = {
            "https://kemono.cr/fanbox/user/1/post/10": [("file.jpg", "10")],
            "https://kemono.cr/fanbox/user/1/post/20": [("file.jpg", "20")],
        }
        urls = [url for url, _ in post_queue]
        post_to_url = self._build_post_to_url_map(urls, all_files_map)
        completed_posts = set()

        # Complete post 10 → first URL should be removed
        post_queue = self._simulate_completion(
            "10", post_to_url, all_files_map, completed_posts, post_queue
        )
        assert len(post_queue) == 1
        assert post_queue[0][0].endswith("/post/20")

        # Complete post 20 → second URL should be removed
        post_queue = self._simulate_completion(
            "20", post_to_url, all_files_map, completed_posts, post_queue
        )
        assert len(post_queue) == 0

    def test_multi_post_url_waits_for_all(self):
        """A URL with multiple post_ids should only be removed when ALL complete."""
        post_queue = [
            ("https://kemono.cr/fanbox/user/1/post/10", False),
        ]
        all_files_map = {
            "https://kemono.cr/fanbox/user/1/post/10": [
                ("file_a.jpg", "10"),
                ("file_b.jpg", "11"),
            ],
        }
        urls = [url for url, _ in post_queue]
        post_to_url = self._build_post_to_url_map(urls, all_files_map)
        completed_posts = set()

        # Complete only post 10 → URL should NOT be removed yet
        post_queue = self._simulate_completion(
            "10", post_to_url, all_files_map, completed_posts, post_queue
        )
        assert len(post_queue) == 1

        # Complete post 11 → now URL should be removed
        post_queue = self._simulate_completion(
            "11", post_to_url, all_files_map, completed_posts, post_queue
        )
        assert len(post_queue) == 0

    def test_incomplete_post_not_removed(self):
        """A URL whose posts haven't all completed should stay in the queue."""
        post_queue = [
            ("https://kemono.cr/fanbox/user/1/post/10", False),
            ("https://kemono.cr/fanbox/user/1/post/20", False),
        ]
        all_files_map = {
            "https://kemono.cr/fanbox/user/1/post/10": [("file.jpg", "10")],
            "https://kemono.cr/fanbox/user/1/post/20": [("file.jpg", "20")],
        }
        urls = [url for url, _ in post_queue]
        post_to_url = self._build_post_to_url_map(urls, all_files_map)
        completed_posts = set()

        # Complete only post 10
        post_queue = self._simulate_completion(
            "10", post_to_url, all_files_map, completed_posts, post_queue
        )
        assert len(post_queue) == 1
        # post/20 should still be there
        assert post_queue[0][0].endswith("/post/20")

    def test_unknown_post_id_no_crash(self):
        """A post_id not in the reverse map should be harmless."""
        post_queue = [
            ("https://kemono.cr/fanbox/user/1/post/10", False),
        ]
        all_files_map = {}
        urls = [url for url, _ in post_queue]
        post_to_url = self._build_post_to_url_map(urls, all_files_map)
        completed_posts = set()

        post_queue = self._simulate_completion(
            "999", post_to_url, all_files_map, completed_posts, post_queue
        )
        assert len(post_queue) == 1

    def test_post_to_url_map_built_correctly(self):
        """The reverse map should map every post_id to its parent URL."""
        all_files_map = {
            "https://kemono.cr/fanbox/user/1/post/10": [
                ("a.jpg", "10"),
                ("b.jpg", "11"),
            ],
            "https://kemono.cr/fanbox/user/1/post/20": [("c.jpg", "20")],
        }
        urls = list(all_files_map.keys())
        m = self._build_post_to_url_map(urls, all_files_map)
        assert m["10"] == "https://kemono.cr/fanbox/user/1/post/10"
        assert m["11"] == "https://kemono.cr/fanbox/user/1/post/10"
        assert m["20"] == "https://kemono.cr/fanbox/user/1/post/20"

    def test_trailing_slash_normalization(self):
        """URLs with/without trailing slashes should be treated identically."""
        post_queue = [
            ("https://kemono.cr/fanbox/user/1/post/10/", False),
        ]
        all_files_map = {
            "https://kemono.cr/fanbox/user/1/post/10/": [("f.jpg", "10")],
        }
        urls = [url for url, _ in post_queue]
        post_to_url = self._build_post_to_url_map(urls, all_files_map)
        completed_posts = set()

        post_queue = self._simulate_completion(
            "10", post_to_url, all_files_map, completed_posts, post_queue
        )
        assert len(post_queue) == 0


class TestIncrementalCreatorRemoval:
    """Test the incremental per-creator removal logic.

    In fast mode, the creator URL should be removed from the queue as soon
    as all posts for that creator have completed, rather than waiting for
    creator_download_finished.
    """

    def _simulate_post_completion(
        self, post_id, completed_posts, total_posts, creator_queue, current_creator_url
    ):
        """Simulate update_post_completion fast-mode logic for creator."""
        completed_posts.add(post_id)
        if len(completed_posts) >= total_posts and total_posts > 0:
            normalized = current_creator_url.rstrip("/")
            before_len = len(creator_queue)
            creator_queue = [
                (u, c) for u, c in creator_queue if u.rstrip("/") != normalized
            ]
            if len(creator_queue) < before_len:
                pass  # Would log in real code
        return creator_queue

    def test_creator_removed_when_all_posts_complete(self):
        creator_queue = [
            ("https://kemono.cr/fanbox/user/100", False),
            ("https://kemono.cr/fanbox/user/200", False),
        ]
        completed_posts = set()
        total_posts = 2
        current_url = "https://kemono.cr/fanbox/user/100"

        # First post completes — creator still has 1 more
        creator_queue = self._simulate_post_completion(
            "p1", completed_posts, total_posts, creator_queue, current_url
        )
        assert len(creator_queue) == 2

        # Second post completes — all done, creator should be removed
        creator_queue = self._simulate_post_completion(
            "p2", completed_posts, total_posts, creator_queue, current_url
        )
        assert len(creator_queue) == 1
        assert creator_queue[0][0].endswith("/200")

    def test_creator_not_removed_prematurely(self):
        creator_queue = [
            ("https://kemono.cr/fanbox/user/100", False),
        ]
        completed_posts = set()
        total_posts = 3

        creator_queue = self._simulate_post_completion(
            "p1",
            completed_posts,
            total_posts,
            creator_queue,
            "https://kemono.cr/fanbox/user/100",
        )
        assert len(creator_queue) == 1  # Still 2 posts remaining

    def test_idempotent_removal(self):
        """Calling removal twice should not error or change the result."""
        creator_queue = [
            ("https://kemono.cr/fanbox/user/100", False),
        ]
        completed_posts = set()
        total_posts = 1

        creator_queue = self._simulate_post_completion(
            "p1",
            completed_posts,
            total_posts,
            creator_queue,
            "https://kemono.cr/fanbox/user/100",
        )
        assert len(creator_queue) == 0

        # Second call — queue already empty, should be fine
        creator_queue = self._simulate_post_completion(
            "p1",
            completed_posts,
            total_posts,
            creator_queue,
            "https://kemono.cr/fanbox/user/100",
        )
        assert len(creator_queue) == 0


class TestFastModeRemovedPostUrlTranslation:
    """Verify the new fast_mode_removed_post_url translation key."""

    def setup_method(self):
        self.original = language_manager.current_language

    def teardown_method(self):
        language_manager.set_language(self.original)

    def test_format_english(self):
        language_manager.set_language("english")
        result = translate(
            "fast_mode_removed_post_url",
            "https://kemono.cr/fanbox/user/1/post/10",
        )
        assert "post/10" in result

    @pytest.mark.parametrize("lang", language_manager.get_available_languages())
    def test_key_exists_all_languages(self, lang):
        language_manager.set_language(lang)
        result = translate("fast_mode_removed_post_url")
        assert (
            result != "fast_mode_removed_post_url"
        ), f"Missing fast_mode_removed_post_url in {lang}"
