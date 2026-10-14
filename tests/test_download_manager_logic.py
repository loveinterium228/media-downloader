import pytest
from PyQt6.QtCore import QSettings, QThreadPool
from app.download_manager import DownloadManager
from app.download_task import DownloadTask
from app.translation import Translator


@pytest.fixture
def manager(tmp_path, monkeypatch):
    settings = QSettings(str(tmp_path / "test_settings.ini"), QSettings.Format.IniFormat)
    settings.setValue("parallel_downloads", 2)
    thread_pool = QThreadPool()
    monkeypatch.setattr(thread_pool, "start", lambda runnable: None)
    translator = Translator()
    return DownloadManager(settings, None, thread_pool, translator)


def test_concurrency_queue_throttling(manager):
    """Verify that tasks exceeding parallel_downloads stay PENDING."""
    manager.settings.setValue("parallel_downloads", 2)

    tasks = [DownloadTask(f"https://example.com/{i}") for i in range(5)]
    for t in tasks:
        t.set_status(DownloadTask.Status.PENDING)
    manager.tasks.extend(tasks)

    manager.start_all()

    # Exactly 2 tasks should be actively downloading, 3 should still be pending
    downloading = [t for t in manager.tasks if t.status == DownloadTask.Status.DOWNLOADING]
    pending = [t for t in manager.tasks if t.status == DownloadTask.Status.PENDING]

    assert len(downloading) == 2
    assert len(pending) == 3
    assert manager.active_downloads == 2
    assert manager.is_downloading_active is True


def test_sequential_completion_starts_next(manager):
    """When a task completes, the next pending task should start automatically."""
    manager.settings.setValue("parallel_downloads", 2)

    task1 = DownloadTask("https://example.com/1")
    task2 = DownloadTask("https://example.com/2")
    task3 = DownloadTask("https://example.com/3")

    for t in [task1, task2, task3]:
        t.set_status(DownloadTask.Status.PENDING)
    manager.tasks.extend([task1, task2, task3])

    manager.start_all()
    assert manager.active_downloads == 2
    assert task3.status == DownloadTask.Status.PENDING

    # Finish task1
    task1.set_completed("/path/to/1.mp4")
    manager.on_task_finished(task1)

    # task3 should now be launched!
    assert task3.status == DownloadTask.Status.DOWNLOADING
    assert manager.active_downloads == 2

    # Finish task2
    task2.set_completed("/path/to/2.mp4")
    manager.on_task_finished(task2)
    assert manager.active_downloads == 1

    # Finish task3
    task3.set_completed("/path/to/3.mp4")
    manager.on_task_finished(task3)
    assert manager.active_downloads == 0
    assert manager.is_downloading_active is False


def test_stop_all_cancels_all_active_and_pending(manager):
    """stop_all must request stop for all tasks and workers."""
    tasks = [DownloadTask(f"https://example.com/{i}") for i in range(4)]
    for t in tasks:
        t.set_status(DownloadTask.Status.PENDING)
    manager.tasks.extend(tasks)

    manager.start_all()
    assert manager.is_downloading_active is True

    manager.stop_all()
    assert manager.is_downloading_active is False
    for t in manager.tasks:
        assert t.is_stop_requested()


def test_remove_task_while_downloading(manager):
    """Removing a task stops its worker and updates summary."""
    task = DownloadTask("https://example.com/1")
    task.set_status(DownloadTask.Status.PENDING)
    manager.tasks.append(task)
    manager.start_all()

    assert task in manager.tasks
    manager.remove_task(task)
    assert task not in manager.tasks
    assert task.is_stop_requested()


def test_retry_failed_task(manager):
    """Retrying an errored task puts it back to pending and starts it."""
    task = DownloadTask("https://example.com/retry")
    task.set_error("Network timeout")
    manager.tasks.append(task)

    assert task.status == DownloadTask.Status.ERROR
    manager.start_or_retry_task(task)

    assert task.status == DownloadTask.Status.DOWNLOADING
    assert manager.active_downloads == 1
