import os
import pytest
from app.history_tab import HistoryManager


def test_history_manager_add_and_get(tmp_path):
    mgr = HistoryManager(str(tmp_path))
    assert mgr.get_all() == []

    entry = mgr.add_entry(
        url="https://youtube.com/watch?v=123",
        title="Test Video",
        platform="YouTube",
        status="completed",
        file_path="/tmp/video.mp4"
    )

    assert entry["id"] == 1
    assert entry["title"] == "Test Video"
    assert len(mgr.get_all()) == 1


def test_history_manager_search(tmp_path):
    mgr = HistoryManager(str(tmp_path))
    mgr.add_entry("https://youtube.com/watch?v=1", "Python Tutorial", "YouTube", "completed")
    mgr.add_entry("https://twitch.tv/streamer", "Gaming Stream", "Twitch", "completed")

    results = mgr.search("python")
    assert len(results) == 1
    assert results[0]["title"] == "Python Tutorial"

    results = mgr.search("twitch")
    assert len(results) == 1
    assert results[0]["platform"] == "Twitch"


def test_history_manager_remove_and_clear(tmp_path):
    mgr = HistoryManager(str(tmp_path))
    e1 = mgr.add_entry("https://url1", "Video 1", "YouTube", "completed")
    e2 = mgr.add_entry("https://url2", "Video 2", "YouTube", "completed")

    mgr.remove_entry(e1["id"])
    all_entries = mgr.get_all()
    assert len(all_entries) == 1
    assert all_entries[0]["id"] == e2["id"]

    mgr.clear()
    assert mgr.get_all() == []


def test_history_manager_remove_entries_bulk(tmp_path):
    mgr = HistoryManager(str(tmp_path))
    e1 = mgr.add_entry("https://url1", "Video 1", "YouTube", "completed")
    e2 = mgr.add_entry("https://url2", "Video 2", "YouTube", "completed")
    e3 = mgr.add_entry("https://url3", "Video 3", "YouTube", "completed")

    mgr.remove_entries([e1["id"], e3["id"]])
    remaining = mgr.get_all()
    assert len(remaining) == 1
    assert remaining[0]["id"] == e2["id"]

