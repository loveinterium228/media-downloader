import os
import pytest
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow
from app.translation import Translator
from app.download_task import DownloadTask
from app.format_dialog import FormatDialog, format_size, codec_name
from app.trim_dialog import TrimDialog


def test_format_dialog_helpers():
    assert codec_name("avc1.64002a") == "H.264"
    assert codec_name("hev1.1.6.L93.B0") == "H.265"
    assert codec_name("vp09.00.51.08") == "VP9"
    assert codec_name("av01.0.08M.08") == "AV1"
    assert codec_name(None) == "—"
    assert codec_name("") == "—"

    assert format_size(None) == "—"
    assert format_size(0) == "—"
    assert format_size(1048576 * 50) == "50 MB"
    assert format_size(1073741824 * 2.5) == "2.50 GB"


def test_trim_dialog_flow(qapp):
    translator = Translator()
    dialog = TrimDialog(translator, duration=120, start=10, end=30)
    assert dialog.start_input.text() == "0:10"
    assert dialog.end_input.text() == "0:30"

    dialog.on_clear()
    assert dialog.result_start is None
    assert dialog.result_end is None


def test_format_dialog_auto_selection(qapp):
    translator = Translator()
    task = DownloadTask("https://example.com/test")
    task.formats = [
        {"format_id": "137", "height": 1080, "fps": 60, "vcodec": "avc1", "ext": "mp4", "has_audio": True, "filesize": 50000000},
        {"format_id": "136", "height": 720, "fps": 30, "vcodec": "avc1", "ext": "mp4", "has_audio": False, "filesize": 20000000},
    ]
    dialog = FormatDialog(translator, task)
    assert dialog.table.rowCount() == 2

    # Click auto
    dialog.on_auto()
    assert dialog.selected_format is None
    assert dialog.selected_label == ""


def test_main_window_dynamic_card_language_switch(qapp, tmp_path):
    settings = QSettings(str(tmp_path / "test.ini"), QSettings.Format.IniFormat)
    translator = Translator()
    translator.set_language("en")

    window = MainWindow(translator, settings)
    task = DownloadTask("https://example.com/test_video")
    task.title = "Sample Video"
    task.formats = [{"format_id": "1", "height": 720, "fps": 30, "vcodec": "avc1", "has_audio": True, "filesize": 1000}]
    task.set_status(DownloadTask.Status.PENDING)

    window.download_manager.tasks.append(task)
    window.add_download_item_widget(task)

    widget = window.downloads_list.itemWidget(window.downloads_list.item(0))
    assert widget.quality_button.text() == "Quality"
    assert widget.trim_button.text() == "Trim"

    # Switch to Russian
    translator.set_language("ru")
    assert widget.quality_button.text() == "Качество"
    assert widget.trim_button.text() == "Обрезать"

    # Switch to Ukrainian
    translator.set_language("uk")
    assert widget.quality_button.text() == "Якість"
    assert widget.trim_button.text() == "Обрізати"
