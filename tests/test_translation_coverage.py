"""Every translation key the app uses must exist in every language."""

import re
from pathlib import Path

from kemonodownloader import kd_help, kd_history
from kemonodownloader.kd_language import language_manager

SOURCE = Path(__file__).parent.parent / "src" / "kemonodownloader"


def used_keys():
    keys = set()
    for path in SOURCE.glob("*.py"):
        if path.name == "kd_language.py":
            continue
        text = path.read_text(encoding="utf-8")
        keys |= set(re.findall(r"""translate\(\s*["']([a-zA-Z0-9_]+)["']""", text))
    # Keys looked up indirectly, through tables.
    keys |= set(kd_history.HistoryModel.COLUMNS)
    keys |= set(kd_history.FavoritesModel.COLUMNS)
    keys |= set(kd_history._KIND_KEYS.values()) | set(kd_history._STATUS_KEYS.values())
    keys |= {key for pair in kd_help.HELP_SECTIONS for key in pair}
    history_source = (SOURCE / "kd_history.py").read_text(encoding="utf-8")
    keys |= set(re.findall(r'_btn, "([a-z_]+)"\)', history_source))
    keys |= set(re.findall(r'\("([a-z_]+)", "fa5s\.', history_source))
    return keys


def test_every_used_key_is_translated_in_every_language():
    languages = language_manager.get_available_languages()
    problems = []
    for key in sorted(used_keys()):
        entry = language_manager.translations.get(key)
        if entry is None:
            problems.append(f"{key}: not defined")
            continue
        problems += [
            f"{key}: missing {lang}" for lang in languages if not entry.get(lang)
        ]
    assert not problems, problems


def test_placeholders_match_across_languages():
    languages = language_manager.get_available_languages()
    for key, entry in language_manager.translations.items():
        if not key.startswith(("history_", "favorites_", "library_", "bookmark_")):
            continue
        expected = set(re.findall(r"\{\d*\}", entry["english"]))
        for lang in languages:
            assert set(re.findall(r"\{\d*\}", entry[lang])) == expected, (key, lang)
