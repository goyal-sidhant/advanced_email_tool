"""
Tests for 'New Session' actually clearing state.

Each data-bearing tab needs a reset() that wipes what the user sees, and
the session manager needs to recognize an empty snapshot so a reset
session is not offered for restore at next launch (the auto-save timer
keeps running after New Session and re-saves whatever state remains).
"""

import pytest

from data.session_manager import SessionManager


# ---------------------------------------------------------------------------
# Tab resets
# ---------------------------------------------------------------------------

def test_tab_excel_reset_clears_loaded_state(qapp):
    from ui.tab_excel import TabExcel

    tab = TabExcel()
    # Simulate a loaded file (signals blocked: no real file behind this state)
    tab._file_path = "C:/clients/list.xlsx"
    tab._columns = ["Email", "PAN"]
    tab._data = [{"Email": "a@b.com", "PAN": "P1"}]
    tab.file_label.setText("list.xlsx")
    tab.reload_btn.setEnabled(True)
    tab.sheet_combo.blockSignals(True)
    tab.sheet_combo.addItems(["Sheet1", "Sheet2"])
    tab.sheet_combo.blockSignals(False)
    tab.sheet_combo.setEnabled(True)
    tab.to_combo.blockSignals(True)
    tab.to_combo.addItems(["Email", "PAN"])
    tab.to_combo.blockSignals(False)
    tab.preview_table.setRowCount(1)
    tab.preview_table.setColumnCount(2)

    tab.reset()

    assert tab.get_file_path() is None
    assert tab.get_data() == []
    assert tab.get_columns() == []
    assert tab.sheet_combo.count() == 0
    assert not tab.sheet_combo.isEnabled()
    assert tab.to_combo.count() == 0
    assert not tab.reload_btn.isEnabled()
    assert tab.preview_table.rowCount() == 0
    assert tab.file_label.text() == "No file selected"


def test_tab_compose_reset_clears_content(qapp):
    from ui.tab_compose import TabCompose

    tab = TabCompose()
    tab.set_subject_template("Reminder for {Name}")
    tab.set_body_template("<p>Dear client, your PAN is ready.</p>")
    tab.universal_bcc_input.setText("audit@example.com")

    tab.reset()

    assert tab.get_subject_template() == ""
    assert "your PAN is ready" not in tab.get_body_template()
    assert tab.get_universal_bcc() is None


def test_tab_attachments_reset_clears_folder_and_files(qapp, tmp_path):
    from ui.tab_attachments import TabAttachments

    f = tmp_path / "static.pdf"
    f.write_bytes(b"x")

    tab = TabAttachments()
    tab.set_static_attachments([str(f)])
    tab.folder_input.setText(str(tmp_path))
    tab.attachment_matcher.set_directory(str(tmp_path))
    tab.attachment_matcher.scan()
    tab.scan_status_label.setText("Found 1 files")

    tab.reset()

    assert tab.get_static_attachments() == []
    assert tab.folder_input.text() == ""
    assert not tab.get_attachment_folder()
    assert tab.attachment_matcher.total_files == 0
    assert tab.scan_status_label.text() == "No folder selected"


# ---------------------------------------------------------------------------
# Empty-session guard
# ---------------------------------------------------------------------------

def test_empty_snapshot_is_not_meaningful():
    empty_state = {
        "excel_file_path": "",
        "subject_template": "",
        "body_template": "<html><head></head><body><p><br/></p></body></html>",
        "universal_bcc": "",
        "static_attachments": [],
        "attachment_folder": "",
        "selected_recipients": [],
    }
    assert not SessionManager.has_meaningful_content(empty_state)
    assert not SessionManager.has_meaningful_content(None)


def test_snapshot_with_data_is_meaningful():
    assert SessionManager.has_meaningful_content(
        {"excel_file_path": "C:/clients/list.xlsx"}
    )
    assert SessionManager.has_meaningful_content(
        {"subject_template": "Reminder for {Name}"}
    )
    assert SessionManager.has_meaningful_content(
        {"body_template": "<html><body><p>Dear {Name}</p></body></html>"}
    )
    assert SessionManager.has_meaningful_content(
        {"static_attachments": ["C:/x.pdf"]}
    )
