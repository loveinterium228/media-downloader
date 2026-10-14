import pytest
from app.download_task import DownloadTask


def test_download_task_initialization():
    task = DownloadTask("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert task.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert task.status == DownloadTask.Status.FETCHING_INFO
    assert task.progress == 0
    assert not task.has_clip
    assert not task.is_stop_requested()


def test_compact_formats():
    raw_formats = [
        {"format_id": "1", "vcodec": "none", "height": 1080},  # audio only, should be skipped
        {"format_id": "2", "vcodec": "av01.0.08M.08", "height": 1080, "fps": 60, "ext": "mp4", "filesize": 1000},
        {"format_id": "3", "vcodec": "vp9", "height": 720, "fps": 30, "ext": "webm", "filesize": 500},
        {"format_id": "4", "vcodec": "h264", "height": None, "fps": None},  # no height, skipped
    ]
    compact = DownloadTask._compact_formats(raw_formats)
    assert len(compact) == 2
    assert compact[0]["height"] == 1080
    assert compact[0]["fps"] == 60
    assert compact[1]["height"] == 720


def test_task_status_changes(qtbot):
    task = DownloadTask("https://test.com/video")
    with qtbot.waitSignal(task.status_changed) as blocker:
        task.set_status(DownloadTask.Status.DOWNLOADING)
    assert blocker.args == [DownloadTask.Status.DOWNLOADING]

    task.update_progress(50, "50% | 5MB/s")
    assert task.progress == 50
    assert task.progress_text == "50% | 5MB/s"

    task.request_stop()
    assert task.is_stop_requested()
    assert task.status == DownloadTask.Status.STOPPED
