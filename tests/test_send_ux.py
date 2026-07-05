"""
Tests for Send tab UX: ETA text, instant cancel, retry-failed, and
abort-stays-resumable.
"""

import pytest

from core.email_builder import Email


@pytest.fixture
def tab(qapp, tmp_path, monkeypatch):
    from core.outlook_sender import OutlookSender

    monkeypatch.setattr(
        OutlookSender, "initialize", lambda self: (False, "disabled in tests")
    )

    import ui.tab_send as tab_send_module

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


def test_format_eta_estimates_time_remaining():
    from ui.tab_send import format_eta

    # 10 done in 100s -> 10s each -> 40 remaining = 400s ≈ 7 min
    text = format_eta(elapsed_seconds=100, done=10, total=50)
    assert "min" in text

    # Short remainder renders in seconds
    text = format_eta(elapsed_seconds=10, done=5, total=6)
    assert "s" in text

    assert format_eta(elapsed_seconds=0, done=0, total=50) == ""
    assert format_eta(elapsed_seconds=100, done=50, total=50) == ""


def test_cancel_takes_effect_without_confirmation_dialog(tab, monkeypatch):
    class FakeWorker:
        def __init__(self):
            self.cancelled = False

        def cancel(self):
            self.cancelled = True

    # If any dialog opens, fail loudly
    import ui.tab_send as tab_send_module

    def no_dialogs(*a, **k):
        raise AssertionError("cancel must not open a confirmation dialog")

    monkeypatch.setattr(tab_send_module.QMessageBox, "question", no_dialogs)

    tab._send_worker = FakeWorker()
    tab._cancel_sending()

    assert tab._send_worker.cancelled is True


def test_finish_with_failures_offers_retry_of_only_failed_rows(tab, monkeypatch):
    tab._emails = _emails([0, 1, 2, 3])
    tab.checkpoint_manager.start_session([0, 1, 2, 3])
    tab.checkpoint_manager.record_success(0)
    tab.checkpoint_manager.record_failure(1, reason="boom")
    tab.checkpoint_manager.record_success(2)
    tab.checkpoint_manager.record_failure(3, reason="boom")

    tab._on_finished({"sent": 2, "failed": 2, "cancelled": False})

    assert not tab.retry_btn.isHidden()
    assert "2" in tab.retry_btn.text()

    launched = []
    monkeypatch.setattr(tab, "_launch_send", lambda emails: launched.append(emails))

    tab._retry_failed()

    assert len(launched) == 1
    assert [e.row_index for e in launched[0]] == [1, 3]
    # Retry starts a fresh checkpoint session covering only those rows
    assert tab.checkpoint_manager.planned == [1, 3]


def test_aborted_batch_stays_resumable(tab):
    tab._emails = _emails([0, 1, 2, 3, 4])
    tab.checkpoint_manager.start_session([0, 1, 2, 3, 4])
    tab.checkpoint_manager.record_failure(0, reason="x")
    tab.checkpoint_manager.record_failure(1, reason="x")
    tab.checkpoint_manager.record_failure(2, reason="x")

    tab._on_finished(
        {
            "sent": 0,
            "failed": 3,
            "cancelled": False,
            "aborted_reason": "Stopped after 3 consecutive failures",
        }
    )

    # Rows 3 and 4 were never attempted — the session must stay resumable
    assert tab.checkpoint_manager.has_incomplete_session()
    assert not tab.resume_btn.isHidden()
