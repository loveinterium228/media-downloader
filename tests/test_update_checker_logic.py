import pytest
from packaging import version


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
