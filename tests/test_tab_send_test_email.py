"""
Tests for the Send Test Email flow.

The test email must go out from the account picked in the dropdown (it
used to use whatever account was last applied — the first one on a fresh
start), and must not block the UI thread while sending.
"""

import threading
from types import SimpleNamespace

import pytest

from core.email_builder import Email
from PyQt5.QtWidgets import QMessageBox


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

    t.account_combo.clear()
    t.account_combo.addItem("Personal (a@x.com)", "a@x.com")
    t.account_combo.addItem("Office (office@firm.com)", "office@firm.com")

    t._emails = [
        Email(to=["client@example.com"], subject="Your documents", row_index=0)
    ]
    return t


class FakeMessageBox:
    Yes = QMessageBox.Yes
    No = QMessageBox.No
    answer = QMessageBox.Yes

    @classmethod
    def question(cls, *args, **kwargs):
        return cls.answer

    @classmethod
    def information(cls, *args, **kwargs):
        return cls.Yes


def _patch_confirm(monkeypatch, answer):
    import ui.tab_send as tab_send_module

    FakeMessageBox.answer = answer
    monkeypatch.setattr(tab_send_module, "QMessageBox", FakeMessageBox)


def test_test_send_uses_account_from_dropdown(tab, monkeypatch):
    _patch_confirm(monkeypatch, FakeMessageBox.No)  # abort before sending

    selected = []
    monkeypatch.setattr(
        tab.outlook_sender, "select_account", lambda email: selected.append(email)
    )
    monkeypatch.setattr(
        tab.outlook_sender,
        "get_selected_account",
        lambda: SimpleNamespace(email="office@firm.com"),
    )

    tab.account_combo.setCurrentIndex(1)  # office@firm.com
    tab._send_test_email()

    assert selected == ["office@firm.com"]


def test_test_send_runs_off_the_ui_thread(tab, monkeypatch):
    _patch_confirm(monkeypatch, FakeMessageBox.Yes)

    monkeypatch.setattr(
        tab.outlook_sender,
        "get_selected_account",
        lambda: SimpleNamespace(email="a@x.com"),
    )
    monkeypatch.setattr(tab.outlook_sender, "select_account", lambda email: None)

    calls = []

    def fake_send(email, display_only=False):
        calls.append((threading.current_thread(), email))
        return True, "sent"

    monkeypatch.setattr(tab.outlook_sender, "send_email", fake_send)

    tab.account_combo.setCurrentIndex(0)
    tab._send_test_email()

    worker = getattr(tab, "_test_worker", None)
    assert worker is not None, "test send should run through a worker thread"
    assert worker.wait(5000)

    assert len(calls) == 1
    send_thread, sent_email = calls[0]
    assert send_thread is not threading.main_thread()
    assert sent_email.to == ["a@x.com"]
    assert sent_email.subject.startswith("[TEST]")
    assert sent_email.cc == [] and sent_email.bcc == []
