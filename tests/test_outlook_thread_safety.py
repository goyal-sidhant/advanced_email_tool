"""
Tests for COM thread-safety in OutlookSender.

initialize() runs on a worker thread since the deferred-startup change,
so the COM objects it stores belong to that thread's COM apartment and
die when the thread exits. Any later call from the GUI thread that
reused them failed with COM error -2147220995 ('Object is not connected
to server'). Status checks and account queries must therefore open a
fresh, thread-local COM connection every time.
"""

import pytest

from core.outlook_sender import OutlookSender


class DeadCOMObject:
    """Mimics a COM proxy whose apartment (worker thread) is gone."""

    def __getattr__(self, name):
        raise Exception(
            "(-2147220995, 'Object is not connected to server', None, None)"
        )


class FakeAccount:
    DisplayName = "Office"
    SmtpAddress = "office@firm.com"
    AccountType = 0


class FakeAccounts:
    Count = 1

    def Item(self, index):
        assert index == 1
        return FakeAccount()


class FakeNamespace:
    Offline = False
    Accounts = FakeAccounts()


class FakeOutlook:
    def GetNamespace(self, name):
        return FakeNamespace()


@pytest.fixture
def sender(monkeypatch):
    s = OutlookSender()
    s._initialized = True
    # Objects created by the (now finished) init worker thread
    s.outlook = DeadCOMObject()
    s.namespace = DeadCOMObject()
    monkeypatch.setattr(s, "_get_fresh_outlook", lambda: FakeOutlook())
    return s


def test_is_online_does_not_reuse_worker_thread_com_objects(sender):
    online, message = sender.is_online()

    assert online is True, message
    assert "not connected to server" not in message


def test_refresh_accounts_does_not_reuse_worker_thread_com_objects(sender):
    accounts = sender.refresh_accounts()

    assert [a.email for a in accounts] == ["office@firm.com"]
