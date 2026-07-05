"""
Tests for send_email attachment failure handling (fake Outlook, no COM).

An email whose attachment cannot be added must NOT be sent — for this
tool that means a client would receive an email missing their document
while the log shows success.
"""

import pytest

from core.email_builder import Email
from core.outlook_sender import OutlookSender


class FakeAttachments:
    def __init__(self, fail_paths):
        self._fail_paths = set(fail_paths)
        self.added = []

    def Add(self, path):
        if path in self._fail_paths:
            raise OSError("The process cannot access the file")
        self.added.append(path)


class FakeMail:
    def __init__(self, fail_paths):
        self.Attachments = FakeAttachments(fail_paths)
        self.sent = False
        self.displayed = False

    def Send(self):
        self.sent = True

    def Display(self):
        self.displayed = True


class FakeOutlook:
    def __init__(self, mail):
        self._mail = mail

    def GetNamespace(self, name):
        return object()

    def CreateItem(self, kind):
        return self._mail


@pytest.fixture
def sender_and_mail(monkeypatch):
    def _make(fail_paths=()):
        mail = FakeMail(fail_paths)
        sender = OutlookSender()
        sender._initialized = True
        monkeypatch.setattr(
            sender, "_get_fresh_outlook", lambda: FakeOutlook(mail)
        )
        return sender, mail

    return _make


def _email(attachments):
    return Email(
        to=["client@example.com"],
        subject="Your documents",
        body_html="<p>Hi</p>",
        attachments=attachments,
        row_index=0,
    )


def test_attachment_failure_blocks_send_and_reports_failure(sender_and_mail):
    sender, mail = sender_and_mail(fail_paths=["C:/files/PAN001_locked.pdf"])

    success, message = sender.send_email(
        _email(["C:/files/PAN001_ok.pdf", "C:/files/PAN001_locked.pdf"])
    )

    assert success is False
    assert "PAN001_locked.pdf" in message
    assert mail.sent is False, "email must not go out without its attachment"


def test_all_attachments_added_sends_normally(sender_and_mail):
    sender, mail = sender_and_mail()

    success, message = sender.send_email(
        _email(["C:/files/PAN001_ok.pdf", "C:/files/PAN001_extra.pdf"])
    )

    assert success is True
    assert mail.sent is True
    assert mail.Attachments.added == [
        "C:/files/PAN001_ok.pdf",
        "C:/files/PAN001_extra.pdf",
    ]
