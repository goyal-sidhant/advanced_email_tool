"""
Tests for send_emails_batch responsiveness and failure handling.
"""

import time

import pytest

from core.email_builder import Email
from core.outlook_sender import OutlookSender, friendly_send_error


def _emails(n):
    return [
        Email(to=[f"user{i}@example.com"], subject=f"Mail {i}", row_index=i)
        for i in range(n)
    ]


@pytest.fixture
def sender(monkeypatch):
    s = OutlookSender()
    s._initialized = True
    return s


def test_cancel_lands_within_a_sleep_slice_not_the_full_interval(sender, monkeypatch):
    monkeypatch.setattr(sender, "send_email", lambda e, d=False: (True, "sent"))

    cancelled = {"flag": False}

    def progress(current, total, email, success, message):
        cancelled["flag"] = True  # cancel right after the first email

    started = time.monotonic()
    results = sender.send_emails_batch(
        _emails(5),
        interval=30,  # the old code slept this long in one chunk
        progress_callback=progress,
        cancel_check=lambda: cancelled["flag"],
    )
    elapsed = time.monotonic() - started

    assert results["sent"] == 1
    assert results["cancelled"] is True
    assert elapsed < 2, f"cancel took {elapsed:.1f}s — sleep is not sliced"


def test_before_send_callback_reports_in_flight_recipient(sender, monkeypatch):
    monkeypatch.setattr(sender, "send_email", lambda e, d=False: (True, "sent"))

    seen = []
    sender.send_emails_batch(
        _emails(2),
        interval=0,
        before_send_callback=lambda current, total, email: seen.append(
            (current, total, email.to[0])
        ),
    )

    assert seen == [(1, 2, "user0@example.com"), (2, 2, "user1@example.com")]


def test_circuit_breaker_stops_after_three_consecutive_failures(sender, monkeypatch):
    monkeypatch.setattr(sender, "send_email", lambda e, d=False: (False, "boom"))

    results = sender.send_emails_batch(_emails(10), interval=0)

    assert results["failed"] == 3
    assert len(results["details"]) == 3
    assert results.get("aborted_reason"), "batch should abort with a reason"
    assert "3 consecutive" in results["aborted_reason"]


def test_successes_reset_the_failure_streak(sender, monkeypatch):
    outcomes = iter([False, False, True, False, False, True, True])
    monkeypatch.setattr(
        sender,
        "send_email",
        lambda e, d=False: (next(outcomes), "msg"),
    )

    results = sender.send_emails_batch(_emails(7), interval=0)

    assert results["sent"] == 3
    assert results["failed"] == 4
    assert not results.get("aborted_reason")


def test_friendly_send_error_maps_common_com_failures():
    assert "security prompt" in friendly_send_error(
        "(-2147467260, 'Operation aborted', None, None)"
    )
    assert "restart Outlook" in friendly_send_error(
        "The RPC server is unavailable"
    )
    assert "not installed" in friendly_send_error(
        "Invalid class string"
    )
    # Unknown errors pass through with the raw text preserved
    assert "weird failure" in friendly_send_error("weird failure")


def test_send_email_returns_friendly_message_on_com_error(sender, monkeypatch):
    def explode():
        raise Exception("(-2147467260, 'Operation aborted', None, None)")

    monkeypatch.setattr(sender, "_get_fresh_outlook", explode)

    success, message = sender.send_email(_emails(1)[0])

    assert success is False
    assert "security prompt" in message
