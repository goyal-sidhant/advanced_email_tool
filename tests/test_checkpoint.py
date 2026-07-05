"""
Tests for CheckpointManager resume correctness.

The checkpoint must track the actual Excel row indexes planned for the
session (a send can target a subset of rows), survive a cancel as
resumable, and keep the original index space across repeated
interruptions so resume never re-sends already-sent rows.
"""

import pytest

from data.checkpoint import CheckpointManager


@pytest.fixture
def manager(tmp_path):
    m = CheckpointManager()
    m.checkpoints_dir = tmp_path
    m.checkpoint_file = tmp_path / "send_checkpoint.json"
    return m


def test_remaining_indices_use_planned_row_indexes(manager):
    manager.start_session([5, 17, 30])

    manager.record_success(5)
    manager.record_failure(17, reason="boom")

    assert manager.get_remaining_indices() == [30]


def test_suspend_keeps_session_resumable(manager):
    manager.start_session([1, 2, 3])
    manager.record_success(1)

    manager.suspend_session()

    assert manager.has_incomplete_session()
    ok, msg, remaining = manager.resume_session()
    assert ok, msg
    assert remaining == [2, 3]


def test_second_interruption_keeps_original_index_space(manager):
    manager.start_session([10, 20, 30])
    manager.record_success(10)
    manager.suspend_session()

    ok, _, remaining = manager.resume_session()
    assert ok
    assert remaining == [20, 30]

    manager.record_success(20)
    manager.suspend_session()

    ok, _, remaining = manager.resume_session()
    assert ok
    # Regression: a resume used to restart the session with re-based
    # indices, making 10 and 20 look unsent (duplicate emails).
    assert remaining == [30]


def test_completed_session_is_not_resumable(manager):
    manager.start_session([0, 1])
    manager.record_success(0)
    manager.record_success(1)
    manager.complete_session(success=True)

    assert not manager.has_incomplete_session()
    ok, _, _ = manager.resume_session()
    assert not ok


def test_legacy_int_total_still_works(manager):
    # Old call style / old checkpoint files: a bare count means rows 0..n-1
    manager.start_session(3)
    manager.record_success(0)

    assert manager.get_remaining_indices() == [1, 2]
