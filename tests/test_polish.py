"""
Tests for the UX polish batch: preferences memory, drag-and-drop,
preview fixes, test-matching ergonomics, full-data validation, and
step-completion indicators.
"""

import json

import pytest

from PyQt5.QtCore import Qt, QMimeData, QUrl, QPointF
from PyQt5.QtGui import QDropEvent


# ---------------------------------------------------------------------------
# Preference helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def prefs_file(tmp_path, monkeypatch):
    import config

    path = tmp_path / "preferences.json"
    monkeypatch.setattr(config, "PREFERENCES_FILE", path)
    return path


def test_preferences_round_trip_and_merge(prefs_file):
    from utils.file_utils import load_preference, save_preference

    prefs_file.write_text(json.dumps({"theme": "dark"}), encoding="utf-8")

    save_preference("last_excel_dir", "D:/clients")

    assert load_preference("last_excel_dir") == "D:/clients"
    assert load_preference("missing", "fallback") == "fallback"
    # Existing keys from other writers (theme manager) survive
    assert json.loads(prefs_file.read_text(encoding="utf-8"))["theme"] == "dark"


# ---------------------------------------------------------------------------
# Excel tab: drag-and-drop + full-data validation
# ---------------------------------------------------------------------------

@pytest.fixture
def excel_tab(qapp, monkeypatch):
    import ui.tab_excel as tab_module

    monkeypatch.setattr(tab_module, "show_error", lambda *a, **k: None)
    from ui.tab_excel import TabExcel

    return TabExcel()


def _drop_event(path):
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(path))])
    event = QDropEvent(
        QPointF(5, 5), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier
    )
    event._mime_keepalive = mime  # QDropEvent does not own the mime data
    return event


def test_dropping_xlsx_loads_it(excel_tab, tmp_path, monkeypatch):
    loaded = []
    monkeypatch.setattr(excel_tab, "_load_file", lambda p: loaded.append(p))

    xlsx = tmp_path / "clients.xlsx"
    xlsx.write_bytes(b"fake")

    assert excel_tab.acceptDrops()
    excel_tab.dropEvent(_drop_event(xlsx))

    import os

    assert [os.path.normpath(p) for p in loaded] == [os.path.normpath(str(xlsx))]


def test_dropping_non_excel_is_ignored(excel_tab, tmp_path, monkeypatch):
    loaded = []
    monkeypatch.setattr(excel_tab, "_load_file", lambda p: loaded.append(p))

    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"fake")

    excel_tab.dropEvent(_drop_event(pdf))

    assert loaded == []


def test_validation_covers_all_rows_not_just_preview(excel_tab):
    rows = [{"Email": f"user{i}@example.com"} for i in range(150)]
    rows[120]["Email"] = "broken@"  # invalid, beyond the 100-row preview

    excel_tab._columns = ["Email"]
    excel_tab._data = rows
    excel_tab.to_combo.blockSignals(True)
    excel_tab.to_combo.addItem("Email")
    excel_tab.to_combo.blockSignals(False)

    excel_tab._populate_preview_table()

    assert "invalid" in excel_tab.validation_label.text().lower()
    assert "150" in excel_tab.preview_count_label.text()


# ---------------------------------------------------------------------------
# Preview tab: keeps place, one refresh button, size warning
# ---------------------------------------------------------------------------

@pytest.fixture
def preview(qapp):
    from core.email_builder import EmailBuilder
    from ui.tab_preview import TabPreview

    tab = TabPreview()
    builder = EmailBuilder()
    builder.set_templates("Hi {Name}", "<p>Dear {Name}</p>")
    builder.set_column_mapping(email_column="Email")
    tab.set_email_builder(builder)
    return tab, builder


def _preview_rows(n):
    return [{"Email": f"user{i}@x.com", "Name": f"User {i}"} for i in range(n)]


def test_preview_keeps_place_when_reentered(preview):
    tab, _ = preview
    rows = _preview_rows(5)

    tab.set_preview_data(rows, list(range(5)), "Email", columns=["Email", "Name"])
    tab._show_preview(3)
    assert tab._current_index == 3

    # Re-entering the tab pushes the same data again
    tab.set_preview_data(rows, list(range(5)), "Email", columns=["Email", "Name"])

    assert tab._current_index == 3


def test_preview_resets_when_selection_changes(preview):
    tab, _ = preview
    rows = _preview_rows(5)

    tab.set_preview_data(rows, list(range(5)), "Email", columns=["Email", "Name"])
    tab._show_preview(4)

    # Recipient 4 is no longer selected — position can't be kept
    tab.set_preview_data(rows, [0, 1], "Email", columns=["Email", "Name"])

    assert tab._current_index == 0


def test_only_one_refresh_preview_button(preview):
    from PyQt5.QtWidgets import QPushButton

    tab, _ = preview
    refreshers = [
        b for b in tab.findChildren(QPushButton) if b.text() == "Refresh Preview"
    ]
    assert len(refreshers) == 1


def test_size_warning_shows_when_attachments_exceed_limit(
    preview, tmp_path, monkeypatch
):
    import config

    tab, builder = preview

    big = tmp_path / "big.pdf"
    big.write_bytes(b"x" * 2048)
    builder.set_static_attachments([str(big)])

    monkeypatch.setattr(config, "MAX_ATTACHMENT_SIZE_BYTES", 1024)

    tab.set_preview_data(_preview_rows(1), [0], "Email", columns=["Email", "Name"])

    assert "exceed" in tab.size_warning.text().lower()


# ---------------------------------------------------------------------------
# Attachments tab: Enter-to-test with inline feedback
# ---------------------------------------------------------------------------

@pytest.fixture
def attachments_tab(qapp, tmp_path, monkeypatch):
    import ui.tab_attachments as tab_module

    def no_modals(*a, **k):
        raise AssertionError("test matching must not open modal dialogs")

    monkeypatch.setattr(tab_module, "show_info", no_modals)
    monkeypatch.setattr(tab_module, "show_error", no_modals)

    from ui.tab_attachments import TabAttachments

    tab = TabAttachments()
    (tmp_path / "PAN001_report.pdf").write_bytes(b"x")
    tab.attachment_matcher.set_directory(str(tmp_path))
    tab.attachment_matcher.scan()
    return tab


def test_enter_key_runs_test_matching_inline(attachments_tab):
    tab = attachments_tab

    tab.test_input.setText("PAN001")
    tab.test_input.returnPressed.emit()

    assert "PAN001" in tab.matched_files_list.title_label.text()


def test_no_match_shows_inline_message_not_modal(attachments_tab):
    tab = attachments_tab

    tab.test_input.setText("MISSING")
    tab.test_input.returnPressed.emit()

    assert "No files match" in tab.matched_files_list.title_label.text()


# ---------------------------------------------------------------------------
# Main window: step checkmarks + geometry memory
# ---------------------------------------------------------------------------

@pytest.fixture
def window(qapp, tmp_path, monkeypatch, prefs_file):
    from core.outlook_sender import OutlookSender

    monkeypatch.setattr(
        OutlookSender, "initialize", lambda self: (False, "disabled in tests")
    )

    from ui.main_window import MainWindow

    win = MainWindow()
    win.session_manager.session_file = tmp_path / "session.json"
    win.tab_send.checkpoint_manager.checkpoints_dir = tmp_path
    win.tab_send.checkpoint_manager.checkpoint_file = tmp_path / "cp.json"
    yield win
    win.auto_save_manager.stop()


def test_completed_steps_get_a_checkmark(window):
    assert "✓" not in window.tab_widget.tabText(0)

    # Simulate the Excel tab having loaded data, then its signal firing
    window.tab_excel._columns = ["Email"]
    window.tab_excel._data = [{"Email": "a@b.com"}]
    window._on_data_loaded(["Email"], [{"Email": "a@b.com"}])

    assert "✓" in window.tab_widget.tabText(0)  # Excel done
    assert "✓" in window.tab_widget.tabText(3)  # Recipients auto-selected


def test_window_geometry_saved_on_close(window, prefs_file):
    window.resize(1024, 700)
    window.close()

    prefs = json.loads(prefs_file.read_text(encoding="utf-8"))
    assert "window_geometry" in prefs
