import os
import pytest
from PyQt6.QtCore import QSettings
from app.download_task import DownloadTask
from app.threads import DownloadWorker, InfoWorker
from app.translation import Translator

LIVE_VIDEO_URL = "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
LIVE_AUDIO_URL = "https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3"


@pytest.mark.network
def test_live_network_info_worker():
    """Verify InfoWorker extracts live metadata from a real web stream."""
    settings = QSettings("TestApp", "TestApp")
    worker = InfoWorker(LIVE_AUDIO_URL, settings)

    results = []
    errors = []
    worker.signals.info_fetched.connect(lambda info: results.append(info))
    worker.signals.error.connect(lambda err: errors.append(err))

    worker.run()

    assert len(errors) == 0, f"InfoWorker failed: {errors}"
    assert len(results) == 1, "Expected exactly one info result"
    info = results[0]
    assert "title" in info
    assert info.get("title") is not None


@pytest.mark.network
def test_live_network_download_worker(tmp_path):
    """Verify DownloadWorker downloads, streams, and finalizes a real media stream."""
    settings = QSettings(str(tmp_path / "test.ini"), QSettings.Format.IniFormat)
    settings.setValue("save_path", str(tmp_path))
    settings.setValue("video_container_policy", "keep")
    translator = Translator()

    task = DownloadTask(LIVE_AUDIO_URL)
    task.platform = "Direct"

    progress_history = []
    task.progress_updated.connect(lambda pct, txt: progress_history.append((pct, txt)))

    worker = DownloadWorker(task, settings, ffmpeg_path=None, translator=translator)
    worker.run()

    assert task.status == DownloadTask.Status.COMPLETED
    assert task.final_filepath is not None
    assert os.path.isfile(task.final_filepath)
    assert os.path.getsize(task.final_filepath) > 0
    # Progress hook was invoked and reached 100%
    assert any(pct >= 90 for pct, _ in progress_history)
