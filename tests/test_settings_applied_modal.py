import os

from PyQt6.QtWidgets import QMessageBox

from kemonodownloader.kd_language import translate
from kemonodownloader.kd_settings import SettingsTab


class MockParent:
    def __init__(self):
        self.base_folder = ""
        self.download_folder = ""
        self.cache_folder = ""
        self.other_files_folder = ""

        # Minimal post/creator tabs used elsewhere
        class DummyTab:
            pass

        self.post_tab = DummyTab()
        self.creator_tab = DummyTab()

    def ensure_folders_exist(self):
        os.makedirs(self.base_folder, exist_ok=True)

    def log(self, msg):
        pass


def test_settings_applied_message_includes_template_and_strategy(
    monkeypatch, tmp_path, qapp
):
    parent = MockParent()
    st = SettingsTab(parent)
    try:
        # Prepare temp settings with non-empty directory to avoid directory creation warning
        st.temp_settings["base_directory"] = str(tmp_path)
        st.temp_settings["base_folder_name"] = "Kemono Downloader Test"
        st.temp_settings["simultaneous_downloads"] = 3
        st.temp_settings["auto_check_updates"] = True
        st.temp_settings["language"] = "english"
        st.temp_settings["use_proxy"] = False
        st.temp_settings["proxy_type"] = "tor"

        # Set creator-specific settings
        st.temp_settings["creator_filename_template"] = "{post_title}-{post_id}"
        st.temp_settings["creator_folder_strategy"] = "single_folder"

        # Monkeypatch question to behave as if the user clicked Yes
        monkeypatch.setattr(
            QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes
        )

        captured = {}

        def fake_info(self_arg, title, message):
            captured["title"] = title
            captured["message"] = message

        monkeypatch.setattr(QMessageBox, "information", fake_info)

        # Call apply
        st.confirm_and_apply_settings()

        assert "{post_title}-{post_id}" in captured["message"]
        # Folder strategy display uses translate("single_creator_folder")
        assert translate("single_creator_folder") in captured["message"]
    finally:
        st.deleteLater()
