import os
import json
import pytest
from app.translation import Translator
from app import paths


def test_translation_files_valid_json():
    for lang in ("en", "ru", "uk"):
        path = paths.resource_path("assets", f"{lang}.json")
        assert os.path.exists(path), f"Translation file {lang}.json missing"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert len(data) > 0


def test_translation_key_parity():
    """Verify that en, ru, uk have matching keys so no UI text is missing."""
    with open(paths.resource_path("assets", "en.json"), "r", encoding="utf-8") as f:
        en_keys = set(json.load(f).keys())
    with open(paths.resource_path("assets", "ru.json"), "r", encoding="utf-8") as f:
        ru_keys = set(json.load(f).keys())
    with open(paths.resource_path("assets", "uk.json"), "r", encoding="utf-8") as f:
        uk_keys = set(json.load(f).keys())

    missing_in_en = ru_keys - en_keys
    missing_in_ru = en_keys - ru_keys
    missing_in_uk = en_keys - uk_keys

    assert not missing_in_en, f"Keys in ru.json but missing in en.json: {missing_in_en}"
    assert not missing_in_ru, f"Keys in en.json but missing in ru.json: {missing_in_ru}"
    assert not missing_in_uk, f"Keys in en.json but missing in uk.json: {missing_in_uk}"


def test_translator_class(qtbot):
    t = Translator()
    t.set_language("en")
    assert t.current_language == "en"
    assert t.translate("app_title") == "Universal Media Downloader"
    assert t.translate("non_existent_key_12345", fallback="Fallback") == "Fallback"
