from PyQt6.QtWidgets import QMessageBox

from kemonodownloader.creator_downloader import CreatorDownloadThread
from kemonodownloader.kd_settings import SettingsTab


def test_template_presets_and_custom(qapp, monkeypatch):
    st = SettingsTab(None)
    try:
        combo = st.creator_filename_combo
        # Basic existence
        assert combo is not None
        # Should have at least the preset entries + custom
        assert combo.count() >= 5
        # First preset data should be the default
        first_data = combo.itemData(0)
        assert first_data == "{post_id}_{orig_name}"

        # Selecting preset should update temp_settings
        combo.setCurrentIndex(1)
        assert st.temp_settings["creator_filename_template"] == combo.itemData(1)

        # Editing text should mark as custom
        combo.setCurrentIndex(combo.count() - 1)
        combo.setEditText("{post_title}-{post_id}")
        assert st.temp_settings["creator_filename_template"] == "{post_title}-{post_id}"

        # Help button should exist and not raise when invoked
        assert hasattr(st, "creator_template_help_btn")
        # Monkeypatch QMessageBox.information to avoid modal blocking
        monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
        # Call the help method - shouldn't raise or block
        st.show_template_help()
    finally:
        st.deleteLater()


def test_invalid_template_falls_back_and_logs(qapp):
    # Create a thread-like object to test formatting
    class DummySettingsTab:
        def get_creator_filename_template(self):
            return "{unknown_field}"

        def get_creator_folder_strategy(self):
            return "per_post"

    class DummySettings:
        def __init__(self):
            self.settings_tab = DummySettingsTab()

    t = CreatorDownloadThread(
        "patreon",
        "creator123",
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
    t.creator_name = "Creator Name"
    # Should not raise even with invalid template
    folder, filename = t.generate_filename_and_folder(
        "https://kemono.cr/media/abc/image.jpg", "/downloads", 0, 1, "1", "My Post"
    )
    # Fallback format uses post_id_orig_name
    assert (
        filename.endswith("-image.jpg")
        or filename.endswith("_image.jpg")
        or "1_" in filename
        or "1-image.jpg" in filename
    )
