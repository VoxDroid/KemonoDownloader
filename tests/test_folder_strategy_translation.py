from kemonodownloader.kd_language import translate
from kemonodownloader.kd_settings import SettingsTab


def test_folder_strategy_labels_translated(qapp):
    st = SettingsTab(None)
    try:
        # Default language is english
        st.update_ui_text()
        combo = st.creator_folder_strategy_combo
        assert combo.count() >= 3
        assert combo.itemText(0) == translate("per_post_folders")
        assert combo.itemText(1) == translate("single_creator_folder")
        assert combo.itemText(2) == translate("subfolders_by_file_type")
    finally:
        st.deleteLater()
