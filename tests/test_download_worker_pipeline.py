import os
import pytest
from PyQt6.QtCore import QSettings
from app.download_task import DownloadTask
from app.threads import DownloadWorker
from app.translation import Translator


def test_download_worker_cancel(tmp_path):
    settings = QSettings(str(tmp_path / "test.ini"), QSettings.Format.IniFormat)
    settings.setValue("save_path", str(tmp_path))
    translator = Translator()

    task = DownloadTask("https://example.com/test.mp4")
    worker = DownloadWorker(task, settings, ffmpeg_path=None, translator=translator)

    worker.cancel()
    assert worker._cancel_requested is True
    assert task.is_stop_requested() is True


def test_download_worker_cleanup_incomplete(tmp_path):
    settings = QSettings(str(tmp_path / "test.ini"), QSettings.Format.IniFormat)
    settings.setValue("save_path", str(tmp_path))
    translator = Translator()

    task = DownloadTask("https://example.com/test.mp4")
    task.video_id = "test1234"
    task.save_path = str(tmp_path)

    # Create dummy incomplete files
    part_file = tmp_path / "video [test1234].part"
    part_file.write_text("incomplete data")
    temp_file = tmp_path / "temp [test1234].temp"
    temp_file.write_text("temp data")

    assert part_file.exists()
    assert temp_file.exists()

    worker = DownloadWorker(task, settings, ffmpeg_path=None, translator=translator)
    worker._cleanup_incomplete(str(tmp_path))

    assert not part_file.exists()
    assert not temp_file.exists()


def test_download_worker_format_eta():
    assert DownloadWorker._format_eta(45) == "45s"
    assert DownloadWorker._format_eta(125) == "2m 05s"
    assert DownloadWorker._format_eta(3665) == "1h 01m"
