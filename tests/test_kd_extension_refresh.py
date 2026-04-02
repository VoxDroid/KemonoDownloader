from types import SimpleNamespace

from kemonodownloader.kd_extension import ExtensionTab


class DummySignal:
    def connect(self, fn):
        self._fn = fn


def test_extension_refresh_ui_calls_update(qapp):
    settings_tab = SimpleNamespace(
        language_changed=DummySignal(),
        font_changed=DummySignal(),
        get_font=lambda: "Poppins",
    )
    parent = SimpleNamespace(settings_tab=settings_tab)

    tab = ExtensionTab(parent)

    calls = {"count": 0}

    def fake_update():
        calls["count"] += 1

    tab.update_ui_text = fake_update
    tab.refresh_ui()

    assert calls["count"] == 1
