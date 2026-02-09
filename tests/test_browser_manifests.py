import json
import os


def load_manifest(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_chrome_manifest_is_mv3():
    path = os.path.join("browser-extension", "chrome_manifest.json")
    m = load_manifest(path)
    assert m.get("manifest_version") == 3
    assert "service_worker" in m.get("background", {})


def test_firefox_manifest_is_mv2():
    path = os.path.join("browser-extension", "firefox_manifest.json")
    m = load_manifest(path)
    assert m.get("manifest_version") == 2
    assert "scripts" in m.get("background", {}) or m.get("applications")
