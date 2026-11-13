from unittest.mock import MagicMock

from PyQt6.QtWidgets import QLabel, QPushButton

from kemonodownloader.kd_extension import ExtensionTab


def test_extension_tab_renders_and_download_button(qapp, monkeypatch):
    # Make translations predictable (patch the name imported into the module)
    monkeypatch.setattr(
        "kemonodownloader.kd_extension.translate", lambda s, *a: f"tr:{s}"
    )

    # Patch out opening external URLs
    mock_open = MagicMock()
    monkeypatch.setattr(
        "kemonodownloader.kd_extension.QDesktopServices.openUrl", mock_open
    )

    class MockSettings:
        language_changed = MagicMock()
        font_changed = MagicMock()

        def get_font(self):
            return "Arial"

    class MockParent:
        def __init__(self):
            self.settings_tab = MockSettings()

    parent = MockParent()
    tab = ExtensionTab(parent)
    try:
        labels = tab.findChildren(QLabel)
        assert any("tr:extension_title" in lbl.text() for lbl in labels)

        buttons = tab.findChildren(QPushButton)
        download_buttons = [b for b in buttons if "tr:ext_open_releases" in b.text()]
        assert download_buttons, "release page button not found"

        # Click the download button and ensure openUrl was called
        btn = download_buttons[0]
        btn.click()
        assert mock_open.called

        # Trigger font change handler to exercise update path
        tab._on_font_changed("Times")
    finally:
        tab.deleteLater()
