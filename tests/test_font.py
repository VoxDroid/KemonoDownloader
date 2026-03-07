"""
Comprehensive tests for the font settings feature.
Tests font defaults, loading, saving, UI, signals, translations, and bundled font files.
"""

import os

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QMessageBox

from kemonodownloader.kd_language import KDLanguage, language_manager, translate
from kemonodownloader.kd_settings import SettingsTab


class MockParent:
    """Minimal mock parent for SettingsTab instantiation."""

    def __init__(self):
        self.base_folder = ""
        self.download_folder = ""
        self.cache_folder = ""
        self.other_files_folder = ""

        class DummyTab:
            pass

        self.post_tab = DummyTab()
        self.creator_tab = DummyTab()

    def ensure_folders_exist(self):
        os.makedirs(self.base_folder, exist_ok=True)

    def log(self, msg):
        pass


# ---------------------------------------------------------------------------
# Font default values
# ---------------------------------------------------------------------------


class TestFontDefaults:
    """Tests for font default settings."""

    def test_default_font_is_jetbrains_mono(self, qapp):
        """Test that the default font is JetBrains Mono."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            assert st.default_settings["font"] == "JetBrains Mono"
        finally:
            st.deleteLater()

    def test_get_font_returns_default(self, qapp):
        """Test that get_font returns the default when no setting is persisted."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            # get_font reads from self.settings which is loaded from QSettings
            assert st.get_font() in ("JetBrains Mono", "Poppins")
        finally:
            st.deleteLater()

    def test_settings_dict_contains_font_key(self, qapp):
        """Test that loaded settings contain the font key."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            assert "font" in st.settings
            assert st.settings["font"] in ("JetBrains Mono", "Poppins")
        finally:
            st.deleteLater()

    def test_temp_settings_contains_font_key(self, qapp):
        """Test that temp_settings contains the font key."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            assert "font" in st.temp_settings
            assert st.temp_settings["font"] in ("JetBrains Mono", "Poppins")
        finally:
            st.deleteLater()


# ---------------------------------------------------------------------------
# Font combo box UI
# ---------------------------------------------------------------------------


class TestFontComboBox:
    """Tests for font selection combo box."""

    def test_font_combo_exists(self, qapp):
        """Test that the font combo box is created."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            assert hasattr(st, "font_combo")
        finally:
            st.deleteLater()

    def test_font_combo_has_two_options(self, qapp):
        """Test that the font combo box has JetBrains Mono and Poppins."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            assert st.font_combo.count() == 2
        finally:
            st.deleteLater()

    def test_font_combo_items(self, qapp):
        """Test that the combo items contain the expected font families."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            items = [st.font_combo.itemData(i) for i in range(st.font_combo.count())]
            assert "JetBrains Mono" in items
            assert "Poppins" in items
        finally:
            st.deleteLater()

    def test_font_combo_display_names(self, qapp):
        """Test that the combo display names match."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            names = [st.font_combo.itemText(i) for i in range(st.font_combo.count())]
            assert "JetBrains Mono" in names
            assert "Poppins" in names
        finally:
            st.deleteLater()


# ---------------------------------------------------------------------------
# update_font / temp_settings
# ---------------------------------------------------------------------------


class TestUpdateFont:
    """Tests for the update_font method."""

    def test_update_font_changes_temp_settings(self, qapp):
        """Test that changing the combo box index updates temp_settings."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            # Find index for Poppins
            poppins_idx = None
            for i in range(st.font_combo.count()):
                if st.font_combo.itemData(i) == "Poppins":
                    poppins_idx = i
                    break
            assert poppins_idx is not None, "Poppins not found in combo"

            st.font_combo.setCurrentIndex(poppins_idx)
            assert st.temp_settings["font"] == "Poppins"
        finally:
            st.deleteLater()

    def test_update_font_to_jetbrains(self, qapp):
        """Test switching font back to JetBrains Mono."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            # Switch to Poppins first
            for i in range(st.font_combo.count()):
                if st.font_combo.itemData(i) == "Poppins":
                    st.font_combo.setCurrentIndex(i)
                    break
            # Switch back to JetBrains Mono
            for i in range(st.font_combo.count()):
                if st.font_combo.itemData(i) == "JetBrains Mono":
                    st.font_combo.setCurrentIndex(i)
                    break
            assert st.temp_settings["font"] == "JetBrains Mono"
        finally:
            st.deleteLater()


# ---------------------------------------------------------------------------
# font_changed signal
# ---------------------------------------------------------------------------


class TestFontChangedSignal:
    """Tests for the font_changed signal."""

    def test_font_changed_signal_exists(self, qapp):
        """Test that SettingsTab has a font_changed signal."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            assert hasattr(st, "font_changed")
        finally:
            st.deleteLater()

    def test_font_changed_signal_emits_on_apply(self, monkeypatch, tmp_path, qapp):
        """Test that font_changed signal is emitted when font changes on apply."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            st.temp_settings["base_directory"] = str(tmp_path)
            st.temp_settings["base_folder_name"] = "Kemono Downloader Test"

            # Change the font in temp settings
            st.temp_settings["font"] = "Poppins"
            # Ensure current settings have a different font
            st.settings["font"] = "JetBrains Mono"

            received = []
            st.font_changed.connect(lambda f: received.append(f))

            # Monkeypatch dialogs
            monkeypatch.setattr(
                QMessageBox,
                "question",
                lambda *a, **k: QMessageBox.StandardButton.Yes,
            )
            monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)

            st.confirm_and_apply_settings()

            assert len(received) == 1
            assert received[0] == "Poppins"
        finally:
            st.deleteLater()

    def test_font_changed_signal_not_emitted_when_same(
        self, monkeypatch, tmp_path, qapp
    ):
        """Test that font_changed signal is NOT emitted when font stays the same."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            st.temp_settings["base_directory"] = str(tmp_path)
            st.temp_settings["base_folder_name"] = "Kemono Downloader Test"

            # Keep the same font in both
            current_font = st.settings.get("font", "JetBrains Mono")
            st.temp_settings["font"] = current_font

            received = []
            st.font_changed.connect(lambda f: received.append(f))

            monkeypatch.setattr(
                QMessageBox,
                "question",
                lambda *a, **k: QMessageBox.StandardButton.Yes,
            )
            monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)

            st.confirm_and_apply_settings()

            assert len(received) == 0
        finally:
            st.deleteLater()


# ---------------------------------------------------------------------------
# Font in confirm / applied dialog messages
# ---------------------------------------------------------------------------


class TestFontInDialogs:
    """Tests for font appearing in settings confirmation and applied messages."""

    def test_settings_applied_message_includes_font(self, monkeypatch, tmp_path, qapp):
        """Test that the applied-settings info dialog mentions the font."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            st.temp_settings["base_directory"] = str(tmp_path)
            st.temp_settings["base_folder_name"] = "Kemono Downloader Test"
            st.temp_settings["font"] = "Poppins"

            monkeypatch.setattr(
                QMessageBox,
                "question",
                lambda *a, **k: QMessageBox.StandardButton.Yes,
            )

            captured = {}

            def fake_info(self_arg, title, message):
                captured["message"] = message

            monkeypatch.setattr(QMessageBox, "information", fake_info)

            st.confirm_and_apply_settings()

            assert "Poppins" in captured.get("message", "")
        finally:
            st.deleteLater()


# ---------------------------------------------------------------------------
# Reset to defaults
# ---------------------------------------------------------------------------


class TestFontReset:
    """Tests for font reset to defaults."""

    def test_reset_restores_default_font(self, monkeypatch, qapp):
        """Test that reset_to_defaults restores JetBrains Mono font."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            # Change font to Poppins first
            for i in range(st.font_combo.count()):
                if st.font_combo.itemData(i) == "Poppins":
                    st.font_combo.setCurrentIndex(i)
                    break

            assert st.temp_settings["font"] == "Poppins"

            # Monkeypatch the information dialog from reset_to_defaults
            monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)

            st.reset_to_defaults()

            assert st.temp_settings["font"] == "JetBrains Mono"
            # Combo box should also reflect the default
            assert (
                st.font_combo.itemData(st.font_combo.currentIndex()) == "JetBrains Mono"
            )
        finally:
            st.deleteLater()


# ---------------------------------------------------------------------------
# Bundled font files
# ---------------------------------------------------------------------------


class TestBundledFontFiles:
    """Tests for bundled font files existence."""

    FONTS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "src",
        "kemonodownloader",
        "resources",
        "fonts",
    )

    def test_fonts_directory_exists(self):
        """Test that the fonts resource directory exists."""
        assert os.path.isdir(self.FONTS_DIR)

    def test_jetbrains_mono_regular_exists(self):
        """Test JetBrainsMono-Regular.ttf is present."""
        assert os.path.isfile(os.path.join(self.FONTS_DIR, "JetBrainsMono-Regular.ttf"))

    def test_jetbrains_mono_bold_exists(self):
        """Test JetBrainsMono-Bold.ttf is present."""
        assert os.path.isfile(os.path.join(self.FONTS_DIR, "JetBrainsMono-Bold.ttf"))

    def test_jetbrains_mono_medium_exists(self):
        """Test JetBrainsMono-Medium.ttf is present."""
        assert os.path.isfile(os.path.join(self.FONTS_DIR, "JetBrainsMono-Medium.ttf"))

    def test_poppins_regular_exists(self):
        """Test Poppins-Regular.ttf is present."""
        assert os.path.isfile(os.path.join(self.FONTS_DIR, "Poppins-Regular.ttf"))

    def test_poppins_bold_exists(self):
        """Test Poppins-Bold.ttf is present."""
        assert os.path.isfile(os.path.join(self.FONTS_DIR, "Poppins-Bold.ttf"))

    def test_poppins_medium_exists(self):
        """Test Poppins-Medium.ttf is present."""
        assert os.path.isfile(os.path.join(self.FONTS_DIR, "Poppins-Medium.ttf"))

    def test_all_bundled_fonts_exist(self):
        """Test that all fonts listed in BUNDLED_FONTS exist on disk."""
        from kemonodownloader.app import BUNDLED_FONTS

        for font_family, font_files in BUNDLED_FONTS.items():
            for font_file in font_files:
                path = os.path.join(self.FONTS_DIR, font_file)
                assert os.path.isfile(path), f"Missing font: {font_file}"


# ---------------------------------------------------------------------------
# load_bundled_fonts
# ---------------------------------------------------------------------------


class TestLoadBundledFonts:
    """Tests for the load_bundled_fonts function."""

    def test_load_bundled_fonts_runs_without_error(self, qapp):
        """Test that load_bundled_fonts does not raise."""
        from kemonodownloader.app import load_bundled_fonts

        # Should not raise even if called multiple times
        load_bundled_fonts()
        load_bundled_fonts()

    def test_bundled_fonts_dict_structure(self):
        """Test that BUNDLED_FONTS has the expected structure."""
        from kemonodownloader.app import BUNDLED_FONTS

        assert isinstance(BUNDLED_FONTS, dict)
        assert "JetBrains Mono" in BUNDLED_FONTS
        assert "Poppins" in BUNDLED_FONTS

        for family, files in BUNDLED_FONTS.items():
            assert isinstance(files, list)
            assert len(files) > 0
            for f in files:
                assert f.endswith(".ttf")


# ---------------------------------------------------------------------------
# Font translation keys
# ---------------------------------------------------------------------------


class TestFontTranslations:
    """Tests for font-related translation keys."""

    def setup_method(self):
        """Store original language before each test."""
        self.original = language_manager.current_language

    def teardown_method(self):
        """Restore original language after each test."""
        language_manager.set_language(self.original)

    def test_font_settings_key_english(self):
        """Test font_settings translation in English."""
        language_manager.set_language("english")
        assert translate("font_settings") == "Font Settings"

    def test_font_key_english(self):
        """Test font translation in English."""
        language_manager.set_language("english")
        assert translate("font") == "Font:"

    def test_font_settings_key_japanese(self):
        """Test font_settings translation in Japanese."""
        language_manager.set_language("japanese")
        text = translate("font_settings")
        assert text != "font_settings"  # Should not return the key itself
        assert len(text) > 0

    def test_font_key_japanese(self):
        """Test font translation in Japanese."""
        language_manager.set_language("japanese")
        text = translate("font")
        assert text != "font"
        assert len(text) > 0

    def test_font_settings_key_korean(self):
        """Test font_settings translation in Korean."""
        language_manager.set_language("korean")
        text = translate("font_settings")
        assert text != "font_settings"
        assert len(text) > 0

    def test_font_key_korean(self):
        """Test font translation in Korean."""
        language_manager.set_language("korean")
        text = translate("font")
        assert text != "font"
        assert len(text) > 0

    def test_font_settings_key_chinese(self):
        """Test font_settings translation in Chinese-Simplified."""
        language_manager.set_language("chinese-simplified")
        text = translate("font_settings")
        assert text != "font_settings"
        assert len(text) > 0

    def test_font_key_chinese(self):
        """Test font translation in Chinese-Simplified."""
        language_manager.set_language("chinese-simplified")
        text = translate("font")
        assert text != "font"
        assert len(text) > 0

    def test_font_translation_keys_in_all_languages(self):
        """Test that font_settings and font keys exist in every language."""
        manager = KDLanguage()
        for key in ("font_settings", "font"):
            assert key in manager.translations
            for lang in ("english", "japanese", "korean", "chinese-simplified"):
                assert (
                    lang in manager.translations[key]
                ), f"Missing {lang} translation for {key}"


# ---------------------------------------------------------------------------
# QSettings persistence
# ---------------------------------------------------------------------------


class TestFontQSettingsPersistence:
    """Tests for font setting persistence via QSettings."""

    def test_font_saved_to_qsettings(self, qapp):
        """Test that font value is saved to QSettings."""
        qs = QSettings("VoxDroid_FontTest", "KemonoDownloader_FontTest")
        try:
            qs.setValue("font", "Poppins")
            assert qs.value("font", type=str) == "Poppins"

            qs.setValue("font", "JetBrains Mono")
            assert qs.value("font", type=str) == "JetBrains Mono"
        finally:
            qs.clear()

    def test_font_default_from_qsettings(self, qapp):
        """Test that QSettings returns default when font key is absent."""
        qs = QSettings("VoxDroid_FontTest2", "KemonoDownloader_FontTest2")
        try:
            value = qs.value("font", "JetBrains Mono", type=str)
            assert value == "JetBrains Mono"
        finally:
            qs.clear()


# ---------------------------------------------------------------------------
# Font group UI elements
# ---------------------------------------------------------------------------


class TestFontGroupUI:
    """Tests for the font settings group box in the UI."""

    def test_font_group_exists(self, qapp):
        """Test that the font group box is created."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            assert hasattr(st, "font_group")
        finally:
            st.deleteLater()

    def test_font_label_exists(self, qapp):
        """Test that the font label is created."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            assert hasattr(st, "font_label")
        finally:
            st.deleteLater()

    def test_available_fonts_list(self, qapp):
        """Test that _available_fonts contains expected entries."""
        parent = MockParent()
        st = SettingsTab(parent)
        try:
            font_families = [fam for _, fam in st._available_fonts]
            assert "JetBrains Mono" in font_families
            assert "Poppins" in font_families
        finally:
            st.deleteLater()
