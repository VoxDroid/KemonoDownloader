from kemonodownloader.kd_extension import MANIFEST_COMMANDS
from kemonodownloader.kd_language import language_manager, translate


def test_manifest_step_names_both_manifests_in_every_language():
    for language in language_manager.get_available_languages():
        text = language_manager.get_text("ext_step_manifest_text", language)
        assert "chrome_manifest.json" in text, language
        assert "firefox_manifest.json" in text, language
        assert "manifest.json" in text, language


def test_manifest_commands_copy_each_manifest_over_the_placeholder():
    commands = [command for _label, command in MANIFEST_COMMANDS]
    for manifest in ("chrome_manifest.json", "firefox_manifest.json"):
        matching = [c for c in commands if manifest in c]
        assert len(matching) == 2  # PowerShell and macOS/Linux
        assert all(
            c.endswith("manifest.json") or c.endswith("-Force") for c in matching
        )


def test_release_link_text_is_translated():
    assert translate("ext_open_releases")
