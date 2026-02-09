from kemonodownloader.creator_downloader import CreatorDownloadThread


class DummySettingsTab:
    def get_creator_filename_template(self):
        return "{post_id}_{orig_name}"

    def get_creator_folder_strategy(self):
        return "per_post"


class DummySettings:
    def __init__(self):
        self.settings_tab = DummySettingsTab()


def test_stress_run_reduced_concurrency_does_not_crash(tmp_path):
    # This is a lightweight stress test that launches the download thread with
    # multiple workers but avoids network by giving no files. It ensures run() does
    # not crash immediately under threaded asyncio execution.
    t = CreatorDownloadThread(
        service="patreon",
        creator_id="stress",
        download_folder=str(tmp_path),
        selected_posts=["1", "2", "3"],
        files_to_download=[],
        files_to_posts_map={},
        console=None,
        other_files_dir=str(tmp_path),
        post_titles_map={},
        auto_rename_enabled=False,
        settings=DummySettings(),
        max_concurrent=2,
    )
    try:
        # Prevent network activity in the test run
        t.fetch_creator_and_post_info = lambda: None
        t.start()
        # Wait a bit for thread to finish gracefully
        finished = t.wait(2000)
        assert finished is True
    finally:
        t.stop()
        t.quit()
        t.wait(2000)
