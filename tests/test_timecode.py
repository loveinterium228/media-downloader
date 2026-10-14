import pytest
from app.timecode import parse_timecode, format_timecode, validate_range


def test_parse_timecode_empty_and_none():
    assert parse_timecode(None) is None
    assert parse_timecode("") is None
    assert parse_timecode("   ") is None


def test_parse_timecode_seconds():
    assert parse_timecode("45") == 45.0
    assert parse_timecode("45.5") == 45.5
    assert parse_timecode("45,5") == 45.5


def test_parse_timecode_minutes_seconds():
    assert parse_timecode("1:30") == 90.0
    assert parse_timecode("01:30") == 90.0
    assert parse_timecode("0:45.5") == 45.5
    assert parse_timecode("90:00") == 5400.0


def test_parse_timecode_hours_minutes_seconds():
    assert parse_timecode("1:02:15") == 3735.0
    assert parse_timecode("01:00:00") == 3600.0


def test_parse_timecode_invalid():
    with pytest.raises(ValueError):
        parse_timecode("1:2:3:4")  # too many parts
    with pytest.raises(ValueError):
        parse_timecode("abc")  # non-digits
    with pytest.raises(ValueError):
        parse_timecode("-10")  # negative
    with pytest.raises(ValueError):
        parse_timecode("::")  # no digits


def test_format_timecode():
    assert format_timecode(None) == ""
    assert format_timecode(0) == "0:00"
    assert format_timecode(45) == "0:45"
    assert format_timecode(90) == "1:30"
    assert format_timecode(3665) == "1:01:05"


def test_validate_range():
    assert validate_range(None, None) is None
    assert validate_range(10, 20) is None
    assert validate_range(20, 10) == "end_before_start"
    assert validate_range(10, 10) == "end_before_start"
    assert validate_range(100, 200, duration=50) == "start_after_end_of_video"
    assert validate_range(10, 200, duration=50) == "end_after_end_of_video"
    assert validate_range(10, 50, duration=50) is None
