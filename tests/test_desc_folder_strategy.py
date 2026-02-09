import os

from kemonodownloader.creator_downloader import CreatorDownloadThread


class DummySettingsTab:
    def __init__(self, strategy="per_post"):
        self._strategy = strategy

    def get_creator_filename_template(self):
        return "{post_id}_{orig_name}"

    def get_creator_folder_strategy(self):
        return self._strategy


class DummySettings:
    def __init__(self, strategy="per_post"):
        self.settings_tab = DummySettingsTab(strategy)


def make_thread(strategy="per_post"):
    settings = DummySettings(strategy)
    t = CreatorDownloadThread(
        service="patreon",
        creator_id="12345",
        download_folder="/downloads",
        selected_posts=["1"],
        files_to_download=[],
        files_to_posts_map={},
        console=None,
        other_files_dir="/tmp/other",
        post_titles_map={},
        auto_rename_enabled=False,
        settings=settings,
        max_concurrent=1,
    )
    t.creator_name = "Creator"
    return t


def test_desc_folder_per_post():
    t = make_thread("per_post")
    creator_folder = os.path.join(t.download_folder, f"{t.creator_id}_{t.creator_name}")
    desc = t.get_desc_folder_for_post(creator_folder, "1", "My Post")
    assert desc.endswith(os.path.join("1_My_Post"))


def test_desc_folder_single_folder():
    t = make_thread("single_folder")
    creator_folder = os.path.join(t.download_folder, f"{t.creator_id}_{t.creator_name}")
    desc = t.get_desc_folder_for_post(creator_folder, "1", "My Post")
    assert desc == os.path.normpath(creator_folder)


def test_desc_folder_by_file_type():
    t = make_thread("by_file_type")
    creator_folder = os.path.join(t.download_folder, f"{t.creator_id}_{t.creator_name}")
    desc = t.get_desc_folder_for_post(creator_folder, "1", "My Post")
    assert desc.endswith(os.path.join("txt"))
