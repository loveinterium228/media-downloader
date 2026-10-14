import pytest
from PyQt6.QtCore import QSettings, QThreadPool
from app.download_manager import DownloadManager
from app.download_task import DownloadTask
from app.translation import Translator


@pytest.fixture
def manager(qtbot, tmp_path, monkeypatch):
    settings = QSettings(str(tmp_path / "test_settings.ini"), QSettings.Format.IniFormat)
    settings.setValue("parallel_downloads", 2)
    thread_pool = QThreadPool()
    monkeypatch.setattr(thread_pool, "start", lambda r: None)
    translator = Translator()
    mgr = DownloadManager(settings, None, thread_pool, translator)
    return mgr


def test_url_normalization(manager):
    raw_kick = "https://kick.com/streamer_name/videos/12345678-abcd-ef01-2345-6789abcdef01"
    normalized = manager._normalize_url(raw_kick)
    assert normalized == "https://kick.com/video/12345678-abcd-ef01-2345-6789abcdef01"

    normal_yt = "https://www.youtube.com/watch?v=123"
    assert manager._normalize_url(normal_yt) == normal_yt


def test_task_concurrency_error_handling(manager):
    task = DownloadTask("https://example.com/test")
    task.set_status(DownloadTask.Status.PENDING)
    manager.tasks.append(task)

    # Simulate start_task
    manager.active_downloads = 1
    manager._workers[task] = None

    # Simulate on_task_error
    manager.on_task_error(task, "Test failure")

    # In the current implementation:
    # on_task_error calls on_task_finished(task), which decrements active_downloads to 0.
    # But when DownloadWorker.run() executes its finally block, it emits worker.signals.finished,
    # which calls on_task_finished(task) a second time!
    # If on_task_finished runs again:
    manager.on_task_finished(task)

    # If it was called twice, active_downloads was decremented twice or miscounted!
    assert manager.active_downloads >= 0
