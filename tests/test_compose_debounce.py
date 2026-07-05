"""
Tests for compose-tab keystroke performance.

Every keystroke used to run multiple full toHtml() serializations plus a
regex scan over any base64 images (via template_changed →
main_window._on_template_changed → get_embedded_images), making typing
laggy once an image was pasted. Content changes are now debounced and
embedded images are extracted only when emails are actually built.
"""

import pytest


@pytest.fixture
def compose(qapp):
    from ui.tab_compose import TabCompose

    return TabCompose()


def test_template_changed_is_debounced(compose, wait_until):
    emissions = []
    compose.template_changed.connect(lambda: emissions.append(1))

    compose.subject_input.setText("Hello")

    assert emissions == [], "emission must not happen on the keystroke itself"

    wait_until(lambda: len(emissions) == 1, message="debounced emission")


def test_rapid_typing_coalesces_into_one_emission(compose, wait_until, qapp):
    emissions = []
    compose.template_changed.connect(lambda: emissions.append(1))

    for text in ("H", "He", "Hel", "Hell", "Hello"):
        compose.subject_input.setText(text)

    wait_until(lambda: len(emissions) >= 1, message="debounced emission")
    # Let any stray timers fire
    import time

    deadline = time.time() + 0.5
    while time.time() < deadline:
        qapp.processEvents()
        time.sleep(0.01)

    assert len(emissions) == 1


def test_flush_pending_changes_applies_immediately(compose):
    emissions = []
    compose.template_changed.connect(lambda: emissions.append(1))

    compose.subject_input.setText("Urgent {Name}")
    assert emissions == []

    compose.flush_pending_changes()

    assert emissions == [1]


@pytest.fixture
def window(qapp, tmp_path, monkeypatch):
    from core.outlook_sender import OutlookSender

    monkeypatch.setattr(
        OutlookSender, "initialize", lambda self: (False, "disabled in tests")
    )

    from ui.main_window import MainWindow

    win = MainWindow()
    win.tab_send.checkpoint_manager.checkpoints_dir = tmp_path
    win.tab_send.checkpoint_manager.checkpoint_file = tmp_path / "cp.json"
    yield win
    win.auto_save_manager.stop()


def test_embedded_images_not_extracted_per_keystroke(window, wait_until, monkeypatch):
    calls = []
    monkeypatch.setattr(
        window.tab_compose,
        "get_embedded_images",
        lambda: calls.append(1) or [],
    )

    window.tab_compose.subject_input.setText("Dear {Name}")
    # Let the debounce fire and _on_template_changed run
    wait_until(
        lambda: window.email_builder.subject_template == "Dear {Name}",
        message="template propagated",
    )

    assert calls == [], "keystroke path must not extract embedded images"

    # Building emails (entering Send tab) is where extraction happens
    window._update_send_tab()
    assert calls == [1]


def test_entering_send_tab_flushes_pending_compose_edits(window):
    window.tab_compose.subject_input.setText("Last-second edit {Name}")

    # Immediately switch to the Send tab — before the debounce fires
    window._update_send_tab()

    assert window.email_builder.subject_template == "Last-second edit {Name}"
