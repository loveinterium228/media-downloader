import threading
import time
from PyQt6.QtCore import QThreadPool, QSettings
from app.download_manager import DownloadManager
from app.download_task import DownloadTask
from app.translation import Translator


class MockWorker:
    def __init__(self, task):
        self.task = task
        self.signals = type("Signals", (), {
            "finished": type("Signal", (), {"connect": lambda self, cb: None})(),
            "error": type("Signal", (), {"connect": lambda self, cb: None})(),
        })()

    def cancel(self):
        self.task.request_stop()


def test_concurrency_stress_queue_tracking(tmp_path):
    """Verify queue invariants under high-throughput concurrent completion events."""
    settings = QSettings(str(tmp_path / "test.ini"), QSettings.Format.IniFormat)
    settings.setValue("parallel_downloads", 4)
    thread_pool = QThreadPool()
    thread_pool.setMaxThreadCount(16)
    translator = Translator()

    dm = DownloadManager(settings, ffmpeg_path=None, thread_pool=thread_pool, translator=translator)

    # Populate 30 tasks
    tasks = [DownloadTask(f"https://example.com/video_{i}") for i in range(30)]
    for t in tasks:
        t.set_status(DownloadTask.Status.PENDING)
    dm.tasks = tasks

    # Simulate start_all
    dm.is_downloading_active = True

    # Register active workers up to limit
    for task in tasks[:4]:
        dm.active_downloads += 1
        task.set_status(DownloadTask.Status.DOWNLOADING)
        dm._workers[task] = MockWorker(task)

    assert dm.active_downloads == 4

    # Run concurrent completion threads simulating worker signals
    errors = []

    def complete_task(task_to_finish):
        try:
            # Simulate worker completion
            task_to_finish.set_completed("/path/file.mp4")
            dm.on_task_finished(task_to_finish)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=complete_task, args=(t,)) for t in list(dm._workers.keys())]
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    assert len(errors) == 0
    # Invariant: active_downloads must never become negative
    assert dm.active_downloads >= 0
    assert dm.active_downloads <= 4


def test_concurrency_rapid_start_stop_cycles(tmp_path):
    """Verify rapid start and stop cycling does not produce deadlocks or corrupted state."""
    settings = QSettings(str(tmp_path / "test.ini"), QSettings.Format.IniFormat)
    settings.setValue("parallel_downloads", 2)
    thread_pool = QThreadPool()
    translator = Translator()

    dm = DownloadManager(settings, ffmpeg_path=None, thread_pool=thread_pool, translator=translator)

    for i in range(10):
        t = DownloadTask(f"https://example.com/item_{i}")
        t.set_status(DownloadTask.Status.PENDING)
        dm.tasks.append(t)

    for cycle in range(5):
        dm.is_downloading_active = False
        dm.active_downloads = 0
        # Register workers
        for t in dm.tasks[:2]:
            dm.active_downloads += 1
            dm._workers[t] = MockWorker(t)
            t.set_status(DownloadTask.Status.DOWNLOADING)

        dm.stop_all()
        assert dm.is_downloading_active is False
        for t in dm.tasks[:2]:
            assert t.is_stop_requested() is True
