import os
import shutil
import tempfile
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox

from kemonodownloader.kd_thumbnaildl import (
    ThumbnailDownloaderTab,
    ThumbnailDetectionThread,
    ThumbnailDownloadThread,
    make_thumbnail_url,
    classify_url,
    parse_post_url,
    parse_creator_url,
)
from kemonodownloader.app import KemonoDownloader


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def test_make_thumbnail_url():
    assert make_thumbnail_url("", "kemono.cr") == ""
    assert make_thumbnail_url(None, "kemono.cr") == ""

    # Kemono
    path1 = "/data/1a/42/1a428c2147a822fb85c9df8e9c6564e9319dce937adba9f2e8ab547067f256a0.jpg"
    res1 = make_thumbnail_url(path1, "kemono.cr")
    assert res1 == "https://img.kemono.cr/thumbnail/data/1a/42/1a428c2147a822fb85c9df8e9c6564e9319dce937adba9f2e8ab547067f256a0.jpg"

    # Coomer
    path2 = "/data/f0/40/f0400f17df56a975802e2367b963d45c1ec426a540734c296a7938e4d6478dcb.jpg"
    res2 = make_thumbnail_url(path2, "coomer.st")
    assert res2 == "https://img.coomer.st/thumbnail/data/f0/40/f0400f17df56a975802e2367b963d45c1ec426a540734c296a7938e4d6478dcb.jpg"

    # Pawchive
    path3 = "/data/93/39/9339b8b09047ee78042c154c136923be3bd2a7555bfdccf77392a6442801523a.jpg"
    res3 = make_thumbnail_url(path3, "pawchive.pw")
    assert res3 == "https://img.pawchive.pw/thumbnail/data/93/39/9339b8b09047ee78042c154c136923be3bd2a7555bfdccf77392a6442801523a.jpg"

    # Already full thumbnail URL
    full_thumb = "https://img.kemono.cr/thumbnail/data/1a/42/1a42.jpg"
    assert make_thumbnail_url(full_thumb, "kemono.cr") == full_thumb


def test_classify_url():
    post_url = "https://kemono.cr/patreon/user/12345/post/67890"
    creator_url = "https://coomer.st/onlyfans/user/abc"
    thumb_url = "https://img.pawchive.pw/thumbnail/data/93/39/9339.jpg"
    invalid_url = "not_a_valid_url"

    assert classify_url("") == "invalid"
    assert classify_url(post_url) == "post"
    assert classify_url(creator_url) == "creator"
    assert classify_url(thumb_url) == "thumbnail"
    assert classify_url(invalid_url) == "invalid"


def test_parse_post_and_creator_url():
    post_url = "https://kemono.cr/patreon/user/12345/post/67890"
    parsed_post = parse_post_url(post_url)
    assert parsed_post is not None
    assert parsed_post[1] == "patreon"
    assert parsed_post[2] == "12345"
    assert parsed_post[3] == "67890"

    creator_url = "https://coomer.st/onlyfans/user/abc"
    parsed_creator = parse_creator_url(creator_url)
    assert parsed_creator is not None
    assert parsed_creator[1] == "onlyfans"
    assert parsed_creator[2] == "abc"


def test_thumbnail_downloader_tab_ui_and_queue(qapp, temp_dir):
    mock_main = MagicMock()
    mock_main.base_folder = temp_dir
    mock_main.download_folder = temp_dir
    mock_main.cache_folder = os.path.join(temp_dir, "Cache")
    mock_main.settings_tab.settings = {"simultaneous_downloads": 2}

    tab = ThumbnailDownloaderTab(mock_main)

    assert tab.mode_combo.count() == 2
    assert tab.get_current_mode() == "post"

    # Add valid post URL to queue
    tab.url_input.setText("https://kemono.cr/patreon/user/12345/post/67890")
    tab.add_url_to_queue()
    assert tab.queue_list.count() == 1

    # Duplicate URL check
    tab.url_input.setText("https://kemono.cr/patreon/user/12345/post/67890")
    with patch.object(QMessageBox, "information") as mock_info:
        tab.add_url_to_queue()
        assert mock_info.called
    assert tab.queue_list.count() == 1

    # Try adding creator URL in post mode (should be rejected/warned)
    tab.url_input.setText("https://coomer.st/onlyfans/user/abc")
    with patch.object(QMessageBox, "warning") as mock_warn:
        tab.add_url_to_queue()
        assert mock_warn.called
    assert tab.queue_list.count() == 1

    # Switch mode with non-empty queue (warn & confirm)
    with patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Ok):
        tab.mode_combo.setCurrentIndex(1)
        assert tab.queue_list.count() == 0
        assert tab.get_current_mode() == "creator"

    # Add valid creator URL in creator mode
    tab.url_input.setText("https://coomer.st/onlyfans/user/abc")
    tab.add_url_to_queue()
    assert tab.queue_list.count() == 1

    # Remove selected
    tab.queue_list.setCurrentRow(0)
    tab.remove_selected_from_queue()
    assert tab.queue_list.count() == 0


def test_import_urls_from_file(qapp, temp_dir):
    mock_main = MagicMock()
    mock_main.base_folder = temp_dir
    mock_main.download_folder = temp_dir
    mock_main.cache_folder = os.path.join(temp_dir, "Cache")
    mock_main.settings_tab.settings = {"simultaneous_downloads": 2}

    tab = ThumbnailDownloaderTab(mock_main)

    txt_path = os.path.join(temp_dir, "links.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("https://kemono.cr/patreon/user/11/post/22\n")
        f.write("https://coomer.st/onlyfans/user/invalid_mode\n")
        f.write("invalid_link\n")

    with patch("PyQt6.QtWidgets.QFileDialog.getOpenFileName", return_value=(txt_path, "")):
        with patch.object(QMessageBox, "information") as mock_info:
            tab.import_urls_from_file()
            assert mock_info.called

    assert tab.queue_list.count() == 1
    assert tab.queue_list.item(0).text() == "https://kemono.cr/patreon/user/11/post/22"


def test_thumbnail_detection_thread_post_and_creator(qapp):
    urls = [
        "https://kemono.cr/patreon/user/12345/post/67890",
        "https://coomer.st/onlyfans/user/abc",
        "https://img.pawchive.pw/thumbnail/data/93/39/9339.jpg",
    ]
    thread = ThumbnailDetectionThread(urls=urls, mode="post")

    mock_post_resp = MagicMock()
    mock_post_resp.status_code = 200
    mock_post_resp.json.return_value = {
        "id": "67890",
        "title": "Test Post",
        "service": "patreon",
        "file": {"path": "/data/1a/42/1a42.jpg"},
        "attachments": [{"path": "/data/93/39/9339.jpg"}],
    }

    mock_creator_resp = MagicMock()
    mock_creator_resp.status_code = 200
    mock_creator_resp.json.return_value = [
        {
            "id": "111",
            "title": "Creator Post 1",
            "service": "onlyfans",
            "file": {"path": "/data/aa/bb/aabb.jpg"},
        }
    ]

    detected_results = []
    thread.detection_finished.connect(lambda items: detected_results.extend(items))

    def fake_get(url, **kwargs):
        if "post" in url:
            return mock_post_resp
        elif "user/abc" in url:
            return mock_creator_resp
        return MagicMock(status_code=404)

    with patch("kemonodownloader.kd_thumbnaildl.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_session.get.side_effect = fake_get
        mock_get_session.return_value = mock_session

        thread.run()

    assert len(detected_results) == 3
    # Post thumbnails are now grouped into one entry with 2 URLs
    post_item = detected_results[0]
    assert post_item[1] == "67890"  # post_id
    assert len(post_item[2]) == 2    # two thumbnail URLs
    assert "1a42.jpg" in post_item[2][0]
    assert "9339.jpg" in post_item[2][1]
    assert post_item[3] == "patreon"   # service
    assert post_item[4] == "12345"     # user_id
    # Creator thumbnail
    creator_item = detected_results[1]
    assert "aabb.jpg" in creator_item[2][0]
    assert creator_item[3] == "onlyfans"  # service
    # Direct thumbnail
    assert detected_results[2][1] == "direct"


def test_thumbnail_download_thread_and_hashdb(qapp, temp_dir):
    items = [
        # 6-tuple: (title, post_id, thumb_urls, service, user_id, creator_name)
        (
            "[Patreon] Test Post (ID: 67890) [1 Thumbnails]",
            "67890",
            ["https://img.kemono.cr/thumbnail/data/1a/42/1a42.jpg"],
            "patreon",
            "12345",
            "Test_Creator",
        )
    ]

    mock_settings = MagicMock()
    mock_hashdb = MagicMock()
    mock_settings.hash_db = mock_hashdb

    thread = ThumbnailDownloadThread(
        download_items=items, save_dir=temp_dir, settings_tab=mock_settings
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"content-length": "14"}
    mock_resp.iter_content.return_value = [b"fake_jpeg_data"]

    with patch("kemonodownloader.kd_thumbnaildl.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_session.get.return_value = mock_resp
        mock_get_session.return_value = mock_session

        thread.run()

    # The file lands in a creator subfolder: temp_dir/12345_Test_Creator/
    all_files = []
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            all_files.append(os.path.join(root, f))
    assert len(all_files) == 1
    assert all_files[0].endswith(".jpg")
    assert mock_hashdb.add_hash.called


def test_preview_selected_thumbnail_no_error(qapp, temp_dir):
    mock_main = MagicMock()
    mock_main.base_folder = temp_dir
    mock_main.download_folder = temp_dir
    mock_main.cache_folder = os.path.join(temp_dir, "Cache")
    mock_main.settings_tab.settings = {"simultaneous_downloads": 2}

    tab = ThumbnailDownloaderTab(mock_main)

    # Populate detected list with full 6-tuple format
    tab.on_detection_batch(
        [
            (
                "[Patreon] Test Post (ID: 67890) [1 Thumbnails]",
                "67890",
                ["https://img.kemono.cr/thumbnail/data/1a/42/1a42.jpg"],
                "patreon",
                "12345",
                "Test_Creator",
            )
        ]
    )
    tab.detected_list.setCurrentRow(0)

    with patch("kemonodownloader.kd_thumbnaildl.MediaPreviewModal") as mock_modal_cls:
        mock_modal = MagicMock()
        mock_modal_cls.return_value = mock_modal

        tab.preview_selected_thumbnail()
        assert mock_modal_cls.called
        assert mock_modal.exec.called


def test_filtering_and_selection_controls(qapp, temp_dir):
    mock_main = MagicMock()
    mock_main.base_folder = temp_dir
    mock_main.download_folder = temp_dir
    mock_main.cache_folder = os.path.join(temp_dir, "Cache")

    tab = ThumbnailDownloaderTab(mock_main)

    tab.on_detection_batch([
        ("Alpha Item", "1", ["https://img.kemono.cr/thumbnail/data/1.jpg"]),
        ("Beta Item", "2", ["https://img.kemono.cr/thumbnail/data/2.jpg"]),
    ])

    assert tab.detected_list.count() == 2

    # Filter
    tab.filter_input.setText("alpha")
    assert tab.detected_list.item(0).isHidden() == False
    assert tab.detected_list.item(1).isHidden() == True

    # Check all
    tab.filter_input.clear()
    tab.toggle_check_all(Qt.CheckState.Unchecked.value)
    assert tab.detected_list.item(0).checkState() == Qt.CheckState.Unchecked
    assert tab.detected_list.item(1).checkState() == Qt.CheckState.Unchecked


def test_app_thumbnail_tab_integration(qapp):
    win = KemonoDownloader()
    main_widget = win.setup_main_ui()
    assert hasattr(win, "thumbnail_tab")
    assert win.tabs.count() == 6
    assert win.tabs.tabText(2) == "Thumbnail Downloader"
    win.deleteLater()


def test_thumbnail_download_thread_saves_post_text(qapp, temp_dir):
    items = [
        (
            "[Patreon] Post Title (ID: 67890) [1 Thumbnails]",
            "67890",
            ["https://img.kemono.cr/thumbnail/data/1a/42/1a42.jpg"],
            "patreon",
            "12345",
            "Test_Creator",
            "kemono.cr",
        )
    ]

    mock_settings = MagicMock()
    mock_settings.hash_db = MagicMock()

    thread = ThumbnailDownloadThread(
        download_items=items,
        save_dir=temp_dir,
        settings_tab=mock_settings,
        download_text=True,
        auto_rename=True,
    )

    mock_thumb_resp = MagicMock()
    mock_thumb_resp.status_code = 200
    mock_thumb_resp.headers = {"content-length": "14"}
    mock_thumb_resp.iter_content.return_value = [b"fake_jpeg_data"]

    mock_api_resp = MagicMock()
    mock_api_resp.status_code = 200
    mock_api_resp.json.return_value = {
        "title": "Post Title",
        "content": "<p>This is the post description content.</p>",
    }

    def fake_get(url, **kwargs):
        if "api/v1" in url:
            return mock_api_resp
        return mock_thumb_resp

    with patch("kemonodownloader.kd_thumbnaildl.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_session.get.side_effect = fake_get
        mock_get_session.return_value = mock_session

        thread.run()

    desc_files = []
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            if f.startswith("desc_"):
                desc_files.append(os.path.join(root, f))

    assert len(desc_files) == 1
    with open(desc_files[0], "r", encoding="utf-8") as f:
        text = f.read()
    assert "Post Title" in text
    assert "This is the post description content." in text

