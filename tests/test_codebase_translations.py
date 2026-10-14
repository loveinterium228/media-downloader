import re
import os
import json
import pytest
from app import paths


def test_missing_translation_keys_in_code():
    """Find all translate('key') and setProperty(..., 'key') calls in python files and ensure they exist in en.json."""
    app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app")
    with open(paths.resource_path("assets", "en.json"), "r", encoding="utf-8") as f:
        en_keys = set(json.load(f).keys())

    pattern_translate = re.compile(r"translate\(\s*['\"]([a-zA-Z0-9_-]+)['\"]")
    pattern_props = re.compile(r"setProperty\(\s*['\"](?:text_key|title_key)['\"]\s*,\s*['\"]([a-zA-Z0-9_-]+)['\"]")

    missing = {}
    for root, _, files in os.walk(app_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = pattern_translate.findall(content) + pattern_props.findall(content)
                    for k in matches:
                        # Case-insensitive lookup check
                        if k not in en_keys and k.lower() not in en_keys:
                            missing.setdefault(k, []).append(file)

    assert not missing, f"Translation keys used in code but missing from en.json: {missing}"
