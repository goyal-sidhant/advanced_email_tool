"""
Tests for AttachmentMatcher scan/cache behavior.
"""

import pytest

from core.attachment_matcher import AttachmentMatcher


@pytest.fixture
def matcher(tmp_path):
    m = AttachmentMatcher()
    ok, error = m.set_directory(str(tmp_path))
    assert ok, error
    return m


def test_rescan_picks_up_new_files_for_previously_unmatched_identifier(matcher, tmp_path):
    matcher.scan()
    assert matcher.match_identifier("PAN001") == []

    (tmp_path / "PAN001_report.pdf").write_bytes(b"x" * 10)
    matcher.scan()

    matched_names = [name for _, name, _ in matcher.match_identifier("PAN001")]
    assert matched_names == ["PAN001_report.pdf"]


def test_rescan_drops_deleted_files_from_matches(matcher, tmp_path):
    target = tmp_path / "PAN002_form.pdf"
    target.write_bytes(b"x" * 10)
    matcher.scan()
    assert len(matcher.match_identifier("PAN002")) == 1

    target.unlink()
    matcher.scan()

    assert matcher.match_identifier("PAN002") == []
