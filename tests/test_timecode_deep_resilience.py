import math
import pytest
from app.timecode import parse_timecode, format_timecode, validate_range


def test_parse_timecode_rejects_nan_and_inf():
    """Verify that NaN and Infinity inputs in any form raise ValueError."""
    for bad_input in ("nan", "NaN", "NAN", "inf", "-inf", "Infinity", "+inf"):
        with pytest.raises(ValueError, match="некорректное время"):
            parse_timecode(bad_input)


def test_parse_timecode_rejects_negative_numbers():
    """Verify that negative timestamps are strictly rejected."""
    for negative in ("-1", "-0.1", "1:-30", "-1:00:00"):
        with pytest.raises(ValueError):
            parse_timecode(negative)


def test_parse_timecode_valid_variations():
    """Verify standard and edge-case valid timecodes."""
    assert parse_timecode("0") == 0.0
    assert parse_timecode("00:00") == 0.0
    assert parse_timecode("00:00:00") == 0.0
    assert parse_timecode("1:30") == 90.0
    assert parse_timecode("01:30") == 90.0
    assert parse_timecode("1:00:00") == 3600.0
    assert parse_timecode("1:30:15.5") == 5415.5
    # Comma used as decimal separator
    assert parse_timecode("1:30,5") == 90.5
    # Empty parts
    assert parse_timecode("1::30") == 3630.0
    # Values above 60 minutes
    assert parse_timecode("90:00") == 5400.0


def test_parse_timecode_empty_and_none():
    assert parse_timecode(None) is None
    assert parse_timecode("") is None
    assert parse_timecode("   ") is None


def test_format_timecode_handles_nan_and_inf():
    """Verify that NaN, Inf, and overflow values format safely to empty string without crashing."""
    assert format_timecode(float("nan")) == ""
    assert format_timecode(float("inf")) == ""
    assert format_timecode(float("-inf")) == ""
    assert format_timecode(None) == ""
    assert format_timecode("invalid") == ""


def test_format_timecode_output_formatting():
    assert format_timecode(0) == "0:00"
    assert format_timecode(45) == "0:45"
    assert format_timecode(90) == "1:30"
    assert format_timecode(3665) == "1:01:05"
    assert format_timecode(7322.4) == "2:02:02"


def test_validate_range_boundaries():
    # End before start
    assert validate_range(10.0, 5.0) == "end_before_start"
    assert validate_range(10.0, 10.0) == "end_before_start"

    # Valid within duration
    assert validate_range(0.0, 10.0, duration=100.0) is None
    assert validate_range(None, 50.0, duration=100.0) is None
    assert validate_range(50.0, None, duration=100.0) is None

    # Exceeding duration
    assert validate_range(100.0, 120.0, duration=100.0) == "start_after_end_of_video"
    assert validate_range(10.0, 102.0, duration=100.0) == "end_after_end_of_video"

    # Safe handling of None or negative duration
    assert validate_range(10.0, 20.0, duration=None) is None
    assert validate_range(10.0, 20.0, duration=-10.0) is None
    assert validate_range(10.0, 20.0, duration=0.0) is None
