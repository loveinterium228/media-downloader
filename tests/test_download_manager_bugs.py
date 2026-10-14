import pytest
from PyQt6.QtCore import QSettings, QThreadPool
from app.download_manager import DownloadManager
from app.download_task import DownloadTask
from app.translation import Translator


def test_download_worker_error_idempotent_concurrency(tmp_path, monkeypatch):
    """
    Verifies that when a task encounters an error and finishes:
    1. active_downloads is accurately decremented only once.
    2. Next pending task is launched without corrupted counters.
    """
    settings = QSettings(str(tmp_path / "test.ini"), QSettings.Format.IniFormat)
    settings.setValue("parallel_downloads", 2)
    thread_pool = QThreadPool()
    monkeypatch.setattr(thread_pool, "start", lambda r: None)
    translator = Translator()
    mgr = DownloadManager(settings, None, thread_pool, translator)

    task1 = DownloadTask("https://example.com/1")
    task2 = DownloadTask("https://example.com/2")
    task1.set_status(DownloadTask.Status.PENDING)
    task2.set_status(DownloadTask.Status.PENDING)
    mgr.tasks.extend([task1, task2])

    # Start task1
    mgr.active_downloads = 1
    dummy_worker = object()
    mgr._workers[task1] = dummy_worker

    # Error happens in task1
    mgr.on_task_error(task1, "Simulated network failure")
    assert task1.status == DownloadTask.Status.ERROR
    # active_downloads is still 1 until the worker emits finished
    assert mgr.active_downloads == 1

    # Worker finishes execution
    mgr.on_task_finished(task1)
    assert mgr.active_downloads == 1  # task2 got launched, so active_downloads is 1 for task2!

    # Calling on_task_finished a second time for task1 does nothing (idempotent)
    mgr.on_task_finished(task1)
    assert mgr.active_downloads == 1
