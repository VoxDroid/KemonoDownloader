import os

from kemonodownloader.creator_downloader import CreatorDownloadThread


class MockSettingsTab:
    def __init__(
        self, template="{post_title}-{post_id}-{orig_name}", strategy="per_post"
    ):
        self._template = template
        self._strategy = strategy

    def get_creator_filename_template(self):
        return self._template

    def get_creator_folder_strategy(self):
        return self._strategy


class MockThreadSettings:
    def __init__(self, settings_tab=None):
        self.settings_tab = settings_tab


def make_thread(auto_rename=False, template=None, strategy=None):
    settings_tab = MockSettingsTab(
        template if template is not None else "{post_id}_{orig_name}",
        strategy if strategy is not None else "per_post",
    )
    settings = MockThreadSettings(settings_tab)
    # minimal init
    t = CreatorDownloadThread(
        service="patreon",
        creator_id="creator123",
        download_folder="/tmp",
        selected_posts=["1"],
        files_to_download=[],
        files_to_posts_map={},
        console=None,
        other_files_dir="/tmp/other",
        post_titles_map={},
        auto_rename_enabled=auto_rename,
        settings=settings,
        max_concurrent=1,
    )
    # set creator and titles
    t.creator_name = "Creator Name"
    t.post_titles_map[("patreon", "creator123", "1")] = "My Post"
    return t


def test_filename_template_applies_and_sanitizes():
    t = make_thread(auto_rename=False, template="{post_title}-{post_id}-{orig_name}")
    folder, filename = t.generate_filename_and_folder(
        "https://kemono.cr/media/abc/image.jpg", "/downloads", 0, 1, "1", "My Post"
    )
    assert "My_Post-1-image.jpg" == filename
    # per_post should include post folder
    expected = os.path.normpath(
        os.path.join("/downloads", "creator123_Creator Name", "1_My_Post")
    )
    assert expected in os.path.normpath(folder)


def test_auto_rename_prefix_and_counter():
    t = make_thread(auto_rename=True, template="{orig_name}")
    # call twice for same post to get counter increment
    folder1, filename1 = t.generate_filename_and_folder(
        "https://kemono.cr/media/abc/file.png", "/downloads", 0, 2, "1", "My Post"
    )
    folder2, filename2 = t.generate_filename_and_folder(
        "https://kemono.cr/media/abc/file2.png", "/downloads", 1, 2, "1", "My Post"
    )
    assert filename1.startswith("1_")
    assert filename2.startswith("2_")


def test_folder_strategy_single_and_by_type():
    t_single = make_thread(strategy="single_folder")
    folder_s, fn_s = t_single.generate_filename_and_folder(
        "https://kemono.cr/media/abc/file.mp4", "/downloads", 0, 1, "1", "My Post"
    )
    assert folder_s.endswith("creator123_Creator Name")
    assert "/1_My_Post" not in folder_s

    t_type = make_thread(strategy="by_file_type")
    folder_t, fn_t = t_type.generate_filename_and_folder(
        "https://kemono.cr/media/abc/file.mp4", "/downloads", 0, 1, "1", "My Post"
    )
    assert folder_t.endswith(os.path.join("creator123_Creator Name", "mp4"))
