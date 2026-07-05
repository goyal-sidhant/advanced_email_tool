"""
Tests for the Send tab's cancel/resume wiring (no real Outlook involved).
"""

import pytest

from core.email_builder import Email


@pytest.fixture
def tab(qapp, tmp_path, monkeypatch):
    from core.outlook_sender import OutlookSender

    # Never touch COM in tests
    monkeypatch.setattr(
        OutlookSender, "initialize", lambda self: (False, "disabled in tests")
    )

    import ui.tab_send as tab_send_module

    # No modal dialogs under the offscreen test platform
    monkeypatch.setattr(tab_send_module, "show_info", lambda *a, **k: None)
    monkeypatch.setattr(tab_send_module, "show_warning", lambda *a, **k: None)
    monkeypatch.setattr(tab_send_module, "show_error", lambda *a, **k: None)

    from ui.tab_send import TabSend

    t = TabSend()
    t.checkpoint_manager.checkpoints_dir = tmp_path
    t.checkpoint_manager.checkpoint_file = tmp_path / "send_checkpoint.json"
    return t


def _emails(indices):
    return [
        Email(to=[f"user{i}@example.com"], subject=f"Mail {i}", row_index=i)
        for i in indices
    ]


def test_cancel_leaves_checkpoint_resumable(tab):
    tab._emails = _emails([0, 1, 2])
    tab.checkpoint_manager.start_session([0, 1, 2])
    tab.checkpoint_manager.record_success(0)

    tab._on_finished({"sent": 1, "failed": 0, "cancelled": True})

    assert tab.checkpoint_manager.has_incomplete_session()
    assert not tab.resume_btn.isHidden()


def test_full_run_completes_checkpoint(tab):
    tab._emails = _emails([0, 1])
    tab.checkpoint_manager.start_session([0, 1])
    tab.checkpoint_manager.record_success(0)
    tab.checkpoint_manager.record_success(1)

    tab._on_finished({"sent": 2, "failed": 0, "cancelled": False})

    assert not tab.checkpoint_manager.has_incomplete_session()


def test_resume_continues_checkpoint_and_sends_only_remaining(tab, monkeypatch):
    tab._emails = _emails([0, 1, 2])
    tab.checkpoint_manager.start_session([0, 1, 2])
    tab.checkpoint_manager.record_success(0)
    tab.checkpoint_manager.suspend_session()
    original_session = tab.checkpoint_manager.session_id

    launched = []
    monkeypatch.setattr(
        tab, "_launch_send", lambda emails: launched.append(emails)
    )

    tab._resume_sending()

    assert len(launched) == 1
    assert [e.row_index for e in launched[0]] == [1, 2]
    # The original session must keep going — no new checkpoint session
    assert tab.checkpoint_manager.session_id == original_session
    assert tab.checkpoint_manager.completed == [0]
    assert tab.checkpoint_manager.total == 3


def test_resume_with_stale_email_list_shows_error_not_send(tab, monkeypatch):
    # Current emails no longer contain the checkpoint's remaining rows
    tab._emails = _emails([7, 8])
    tab.checkpoint_manager.start_session([0, 1, 2])
    tab.checkpoint_manager.record_success(0)
    tab.checkpoint_manager.suspend_session()

    launched = []
    monkeypatch.setattr(
        tab, "_launch_send", lambda emails: launched.append(emails)
    )
    errors = []
    monkeypatch.setattr(
        "ui.tab_send.show_error", lambda parent, title, msg: errors.append(msg)
    )

    tab._resume_sending()

    assert launched == []
    assert errors, "expected an explanatory error dialog"
