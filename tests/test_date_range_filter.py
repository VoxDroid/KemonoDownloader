import datetime
import gzip
import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import kemonodownloader.creator_downloader as cd
from kemonodownloader.download_utils import parse_post_datetime, post_in_date_range
from kemonodownloader.kd_language import KDLanguage


def test_parse_post_datetime_accepts_api_formats():
    assert parse_post_datetime("2026-01-07T17:20:52") == datetime.datetime(
        2026, 1, 7, 17, 20, 52
    )
    assert parse_post_datetime("2026-01-07T17:20:52.010211") == datetime.datetime(
        2026, 1, 7, 17, 20, 52, 10211
    )
    assert parse_post_datetime("2026-01-07T17:20:52Z") == datetime.datetime(
        2026, 1, 7, 17, 20, 52
    )
    assert parse_post_datetime(None) is None
    assert parse_post_datetime("not a date") is None


def test_post_in_date_range_is_inclusive():
    post = {"id": "p1", "published": "2026-01-07T17:20:52"}
    start = datetime.date(2026, 1, 1)
    end = datetime.date(2026, 1, 31)

    assert post_in_date_range(post, start, end)
    assert post_in_date_range(post, datetime.date(2026, 1, 7), end)
    assert post_in_date_range(post, start, datetime.date(2026, 1, 7))
    assert not post_in_date_range(post, datetime.date(2026, 1, 8), end)
    assert not post_in_date_range(post, start, datetime.date(2026, 1, 6))
    assert post_in_date_range(post, None, None)
    assert not post_in_date_range({"id": "p2"}, start, end)


def test_post_in_date_range_falls_back_to_added():
    post = {"id": "p3", "added": "2025-12-31T23:59:59"}
    assert post_in_date_range(
        post, datetime.date(2025, 12, 1), datetime.date(2025, 12, 31)
    )


def test_new_date_range_keys_are_translated():
    keys = [
        "date_range_filter",
        "date_range_invalid",
        "date_range_applied",
        "date_range_disabled",
        "date_range_ready",
        "date_range_page_filtered",
        "date_range_summary",
        "date_range_no_posts",
        "tip_date_range_filter",
        "tip_date_range_start",
        "tip_date_range_end",
        "tip_date_range_apply",
    ]
    lang = KDLanguage()
    for key in keys:
        entry = lang.translations[key]
        for language in lang.get_available_languages():
            assert entry[language]


def test_post_detection_filters_by_publish_date(monkeypatch):
    settings = SimpleNamespace(
        creator_posts_max_attempts=1,
        settings_tab=SimpleNamespace(),
        api_request_max_retries=1,
    )
    posts = [
        {"id": "old", "title": "Old", "published": "2025-12-31T10:00:00"},
        {"id": "new", "title": "New", "published": "2026-01-07T17:20:52"},
        {"id": "future", "title": "Future", "published": "2026-02-01T00:00:00"},
    ]
    content = gzip.compress(json.dumps(posts).encode("utf-8"))

    class Resp:
        status_code = 200

    class S:
        def get(self, *a, **k):
            response = Resp()
            response.content = content
            return response

    monkeypatch.setattr(cd, "get_session", lambda st: S())

    thread = cd.PostDetectionThread(
        "https://kemono.cr/artist/user/10",
        {},
        settings,
        date_range=(datetime.date(2026, 1, 1), datetime.date(2026, 1, 31)),
    )
    thread.posts_batch = SimpleNamespace(emit=MagicMock())
    thread.finished = SimpleNamespace(emit=MagicMock())
    thread.log = SimpleNamespace(emit=MagicMock())
    thread.error = SimpleNamespace(emit=MagicMock())

    thread.run()

    detected = thread.finished.emit.call_args.args[0]
    assert [post_id for _, (post_id, _) in detected] == ["new"]
    assert thread._date_filter_skipped == 2
