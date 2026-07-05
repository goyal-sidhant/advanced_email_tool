"""
Tests for deferred Outlook initialization on the Send tab.

Connecting to Outlook (COM dispatch, account enumeration) used to run
inside TabSend.__init__, freezing app startup for seconds — longer if
Outlook wasn't running. It now runs in a worker thread started
explicitly (by main.py after the window is shown), and the accounts
Refresh button doubles as a reconnect when startup failed.
"""

from types import SimpleNamespace

import pytest


@pytest.fixture
def patched_sender(monkeypatch):
    """Record initialize() calls; never touch COM."""
    from core.outlook_sender import OutlookSender

    calls = []
    result = {"value": (True, "")}

    def fake_initialize(self):
        calls.append("initialize")
        if result["value"][0]:
            self._initialized = True
        return result["value"]

    monkeypatch.setattr(OutlookSender, "initialize", fake_initialize)
    monkeypatch.setattr(
        OutlookSender,
        "get_accounts",
        lambda self: [
            SimpleNamespace(name="Office", email="office@firm.com", index=1)
        ],
    )
    monkeypatch.setattr(OutlookSender, "is_online", lambda self: (True, "Online"))
    # Patch both namespaces — ui.tab_send imports the name directly
    monkeypatch.setattr("core.outlook_sender.detect_new_outlook", lambda: False)
    monkeypatch.setattr("ui.tab_send.detect_new_outlook", lambda: False)
    return calls, result


@pytest.fixture
def tab(qapp, patched_sender, monkeypatch):
    import ui.tab_send as tab_send_module

    monkeypatch.setattr(tab_send_module, "show_info", lambda *a, **k: None)
    monkeypatch.setattr(tab_send_module, "show_warning", lambda *a, **k: None)
    monkeypatch.setattr(tab_send_module, "show_error", lambda *a, **k: None)

    from ui.tab_send import TabSend

    return TabSend()


def test_constructor_never_touches_outlook(tab, patched_sender):
    calls, _ = patched_sender

    assert calls == [], "COM init must not run during construction"
    assert not tab.start_btn.isEnabled()


def test_start_outlook_init_connects_in_background(tab, patched_sender, wait_until):
    calls, _ = patched_sender

    tab.start_outlook_init()

    wait_until(lambda: tab.start_btn.isEnabled(), message="outlook connected")
    assert calls == ["initialize"]
    assert tab.account_combo.count() == 1
    assert "office@firm.com" in tab.account_combo.itemText(0)


def test_failed_init_keeps_start_disabled_and_refresh_reconnects(
    tab, patched_sender, wait_until
):
    calls, result = patched_sender
    result["value"] = (False, "Outlook not running")

    tab.start_outlook_init()
    # Wait for the failure to fully settle (worker done, UI updated)
    wait_until(
        lambda: "Refresh" in tab.online_label.text(), message="first init failed"
    )
    assert calls == ["initialize"]
    assert not tab.start_btn.isEnabled()

    # Outlook got started by the user; Refresh doubles as reconnect
    result["value"] = (True, "")
    tab._refresh_accounts()

    wait_until(lambda: tab.start_btn.isEnabled(), message="reconnect")
    assert calls == ["initialize", "initialize"]
    assert tab.account_combo.count() == 1
