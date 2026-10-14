import pytest
from PyQt6.QtCore import QSettings, Qt
from app.main_window import MainWindow
from app.translation import Translator
from app.download_task import DownloadTask


@pytest.fixture
def app_window(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "ui_test.ini"), QSettings.Format.IniFormat)
    translator = Translator()
    translator.set_language("en")
    window = MainWindow(translator, settings)
    qtbot.addWidget(window)
    return window


def test_main_window_startup(app_window):
    assert app_window.windowTitle() == "Universal Media Downloader"
    assert app_window.downloads_list is not None
    assert app_window.page_stack.currentIndex() == 0  # Downloads tab


def test_add_link_workflow(app_window, qtbot):
    app_window.url_input.setText("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    qtbot.mouseClick(app_window.btn_add, Qt.MouseButton.LeftButton)

    # Input should be cleared
    assert app_window.url_input.text() == ""
    # A task should be created in download manager
    assert len(app_window.download_manager.tasks) == 1
    task = app_window.download_manager.tasks[0]
    assert "dQw4w9WgXcQ" in task.url
    # Downloads list widget should have 1 item
    assert app_window.downloads_list.count() == 1


def test_tab_switching(app_window, qtbot):
    # Switch to History (index 1)
    qtbot.mouseClick(app_window.btn_history, Qt.MouseButton.LeftButton)
    assert app_window.page_stack.currentIndex() == 1

    # Switch to Settings (index 2)
    qtbot.mouseClick(app_window.btn_settings, Qt.MouseButton.LeftButton)
    assert app_window.page_stack.currentIndex() == 2

    # Switch to About (index 3)
    qtbot.mouseClick(app_window.btn_about, Qt.MouseButton.LeftButton)
    assert app_window.page_stack.currentIndex() == 3

    # Switch back to Downloads (index 0)
    qtbot.mouseClick(app_window.btn_downloads, Qt.MouseButton.LeftButton)
    assert app_window.page_stack.currentIndex() == 0


def test_language_switch_workflow(app_window):
    # Switch to Russian (index 1)
    app_window.language_combo.setCurrentIndex(1)
    assert app_window.translator.current_language == "ru"
    assert app_window.btn_downloads.text() == "Загрузки"

    # Switch to Ukrainian (index 2)
    app_window.language_combo.setCurrentIndex(2)
    assert app_window.translator.current_language == "uk"
    assert app_window.btn_downloads.text() == "Завантаження"

    # Switch back to English (index 0)
    app_window.language_combo.setCurrentIndex(0)
    assert app_window.translator.current_language == "en"
    assert app_window.btn_downloads.text() == "Downloads"
