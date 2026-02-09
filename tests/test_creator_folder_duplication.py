import os

from kemonodownloader.creator_downloader import CreatorDownloadThread


class DummySettingsTab:
    def get_creator_filename_template(self):
        return "{post_id}_{orig_name}"

    def get_creator_folder_strategy(self):
        return "per_post"


class DummySettings:
    def __init__(self):
        self.settings_tab = DummySettingsTab()


def test_creator_folder_not_duplicated():
    t = CreatorDownloadThread(
        "patreon",
        "17913091",
        "/downloads",
        ["1"],
        [],
        {},
        None,
        "/tmp/other",
        {},
        auto_rename_enabled=False,
        settings=DummySettings(),
        max_concurrent=1,
    )
    t.creator_name = "jtveemo"

    creator_folder_name = f"{t.creator_id}_{t.creator_name}"
    # Simulate run-created creator_folder passed into workers
    creator_folder = os.path.normpath(
        os.path.join(t.download_folder, creator_folder_name)
    )

    # Now call generator with folder already being creator_folder
    target_folder, filename = t.generate_filename_and_folder(
        "https://kemono.cr/media/abc/image.jpg", creator_folder, 0, 1, "1", "My Post"
    )

    # target_folder should not contain duplication
    assert target_folder.count(creator_folder_name) == 1

    # Also check when passing base download folder it still builds correct path
    base_folder = os.path.normpath(t.download_folder)
    target_folder2, filename2 = t.generate_filename_and_folder(
        "https://kemono.cr/media/abc/image2.jpg", base_folder, 0, 1, "1", "My Post"
    )
    assert target_folder2.count(creator_folder_name) == 1
