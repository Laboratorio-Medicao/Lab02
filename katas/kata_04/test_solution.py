import pytest

from .solution import mark_text


def test_keeps_markers_as_separate_tokens():
    assert mark_text("ab -> cd", ["->"]) == ["ab", "->", "cd"]


def test_supports_multiple_markers():
    assert mark_text("left|middle:right", ["|", ":"]) == ["left", "|", "middle", ":", "right"]


def test_prefers_longer_overlapping_marker():
    assert mark_text("a===b", ["=", "==", "==="]) == ["a", "===", "b"]


def test_discards_whitespace_only_parts():
    assert mark_text("  a   |   b  ", ["|"]) == ["a", "|", "b"]


@pytest.mark.parametrize("text,markers", [("", ["|"]), ("abc", [""])])
def test_rejects_empty_arguments(text, markers):
    with pytest.raises(ValueError):
        mark_text(text, markers)