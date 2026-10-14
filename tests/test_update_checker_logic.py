import pytest
from unittest.mock import MagicMock, patch
from packaging import version
from PyQt6.QtCore import QThreadPool, QSettings
from app.update_checker import UpdateCheckWorker, UpdateWorker, UpdateChecker
from app.translation import Translator


@pytest.mark.parametrize("current,latest,expected", [
    ("2026.7.4", "2026.8.19", True),
    ("2026.8.19", "2026.8.19", False),
    ("2026.8.20", "2026.8.19", False),
    ("1.0.0", "1.0.1", True),
    ("2.1.0", "2.0.9", False),
    ("2026.8.19rc1", "2026.8.19", True),
])
def test_version_comparison_logic(current, latest, expected):
    is_newer = version.parse(latest) > version.parse(current)
    assert is_newer == expected


def test_update_check_worker_update_available(qtbot):
    worker = UpdateCheckWorker()
    available_received = []
    worker.signals.update_available.connect(lambda cur, lat: available_received.append((cur, lat)))

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"info": {"version": "9999.1.1"}}
    mock_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_resp):
        worker.run()

    assert len(available_received) == 1
    assert available_received[0][1] == "9999.1.1"


def test_update_check_worker_no_update_needed(qtbot):
    worker = UpdateCheckWorker()
    no_update_called = []
    worker.signals.no_update_needed.connect(lambda: no_update_called.append(True))

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"info": {"version": "2000.1.1"}}
    mock_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_resp):
        worker.run()

    assert len(no_update_called) == 1


def test_update_check_worker_network_failure(qtbot):
    worker = UpdateCheckWorker()
    failed_msgs = []
    worker.signals.check_failed.connect(lambda msg: failed_msgs.append(msg))

    with patch("requests.get", side_effect=RuntimeError("Network down")):
        worker.run()

    assert len(failed_msgs) == 1
    assert "Network down" in failed_msgs[0]


def test_update_check_worker_teardown_resilience():
    """Verify that if Python GC deletes signals during execution, run() does not crash."""
    worker = UpdateCheckWorker()
    del worker.signals

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"info": {"version": "9999.1.1"}}
    mock_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_resp):
        # Must execute cleanly without raising AttributeError
        worker.run()


def test_update_worker_teardown_resilience():
    """Verify UpdateWorker teardown resilience when attributes are cleared."""
    worker = UpdateWorker()
    del worker.signals

    # Must execute cleanly without raising AttributeError
    worker.run()

