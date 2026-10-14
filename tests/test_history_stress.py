import os
import json
import pytest
from app.history_tab import HistoryManager


def test_history_cap_at_500_entries(tmp_path):
    mgr = HistoryManager(str(tmp_path))

    # Add 550 entries
    for i in range(550):
        mgr.add_entry(
            url=f"https://example.com/{i}",
            title=f"Video #{i}",
            platform="YouTube",
            status="completed"
        )

    all_entries = mgr.get_all()
    assert len(all_entries) == 500
    # Newest items are first, so #549 is index 0, and #50 is index 499
    assert all_entries[0]["title"] == "Video #549"
    assert all_entries[-1]["title"] == "Video #50"


def test_corrupted_history_file_graceful_recovery(tmp_path):
    history_file = tmp_path / "history.json"
    with open(history_file, "w", encoding="utf-8") as f:
        f.write("{this is invalid corrupted JSON content!@@#$$%^}")

    # Manager should not crash, but recover with an empty list
    mgr = HistoryManager(str(tmp_path))
    assert mgr.get_all() == []

    # Can still add new entries without error
    mgr.add_entry("https://example.com/ok", "Valid", "YouTube", "completed")
    assert len(mgr.get_all()) == 1


def test_history_unicode_and_special_characters(tmp_path):
    mgr = HistoryManager(str(tmp_path))
    title = "日本語タイトル / Текст с эмодзи 🚀🔥 / Special '\"&<>"
    url = "https://example.com/watch?v=тест&lang=ru#section"

    mgr.add_entry(url, title, "YouTube", "completed", "/path/to/файлик.mp4")

    # Reload fresh instance from disk
    mgr2 = HistoryManager(str(tmp_path))
    loaded = mgr2.get_all()
    assert len(loaded) == 1
    assert loaded[0]["title"] == title
    assert loaded[0]["url"] == url
    assert loaded[0]["file_path"] == "/path/to/файлик.mp4"
