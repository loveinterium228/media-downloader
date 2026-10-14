import pytest
from PyQt6.QtCore import QSettings
from app.theme_manager import ThemeManager, DARK, LIGHT


def test_theme_manager_palettes():
    assert "bg" in DARK
    assert "text" in DARK
    assert "accent" in DARK
    assert "bg" in LIGHT
    assert "text" in LIGHT

    # Check distinct contrast
    assert DARK["bg"] != DARK["text"]
    assert LIGHT["bg"] != LIGHT["text"]


def test_qss_generation(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / "theme_test.ini"), QSettings.Format.IniFormat)
    tm = ThemeManager(settings)

    qss_dark = tm.get_dark_theme()
    assert isinstance(qss_dark, str)
    assert len(qss_dark) > 100
    assert DARK["bg"] in qss_dark

    qss_light = tm.get_light_theme()
    assert isinstance(qss_light, str)
    assert len(qss_light) > 100
    assert LIGHT["bg"] in qss_light
