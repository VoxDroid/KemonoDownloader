from kemonodownloader.kd_language import translate


def test_extension_manifest_translations():
    assert "chrome_manifest.json" in translate("extension_manifest_text")
    assert "firefox_manifest.json" in translate("extension_manifest_text")
    assert "chrome_manifest.json" in translate("extension_manifest_chrome")
    assert "firefox_manifest.json" in translate("extension_manifest_firefox")
