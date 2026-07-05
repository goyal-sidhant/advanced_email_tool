"""
Tests for saved recipient lists surviving Excel row changes.

Lists used to store only raw row indices; inserting/deleting/re-sorting
rows in Excel silently selected different clients. Lists now also store
the recipient emails and are resolved by email first, indices as legacy
fallback.
"""

import pytest

from data.recipient_lists import RecipientListStorage


@pytest.fixture
def storage(tmp_path):
    s = RecipientListStorage()
    s.lists_dir = tmp_path
    return s


def test_save_list_stores_recipient_emails(storage):
    ok, msg = storage.save_list(
        "GST Clients",
        [0, 2],
        recipient_emails=["a@x.com", "c@x.com"],
    )
    assert ok, msg

    data = storage.load_list("GST Clients")
    assert data["recipient_emails"] == ["a@x.com", "c@x.com"]
    assert data["selected_indices"] == [0, 2]


def test_resolve_selection_matches_by_email_after_rows_shift(storage):
    list_data = {
        "selected_indices": [0, 2],
        "recipient_emails": ["a@x.com", "c@x.com"],
    }
    # A new row was inserted at the top and another in the middle
    current_emails = ["new@x.com", "a@x.com", "b@x.com", "c@x.com"]

    indices, missing = RecipientListStorage.resolve_selection(
        list_data, current_emails
    )

    assert indices == [1, 3]
    assert missing == []


def test_resolve_selection_is_case_insensitive(storage):
    list_data = {
        "selected_indices": [0],
        "recipient_emails": ["Client.One@Example.COM"],
    }
    indices, missing = RecipientListStorage.resolve_selection(
        list_data, ["client.one@example.com"]
    )

    assert indices == [0]
    assert missing == []


def test_resolve_selection_reports_missing_recipients(storage):
    list_data = {
        "selected_indices": [0, 1],
        "recipient_emails": ["a@x.com", "gone@x.com"],
    }
    indices, missing = RecipientListStorage.resolve_selection(
        list_data, ["a@x.com", "b@x.com"]
    )

    assert indices == [0]
    assert missing == ["gone@x.com"]


def test_resolve_selection_legacy_list_falls_back_to_indices(storage):
    list_data = {"selected_indices": [0, 5]}  # saved before emails existed

    indices, missing = RecipientListStorage.resolve_selection(
        list_data, ["a@x.com", "b@x.com", "c@x.com"]
    )

    assert indices == [0]  # 5 is out of range and dropped
    assert missing == []


# ---------------------------------------------------------------------------
# End-to-end through the Recipients tab
# ---------------------------------------------------------------------------

def test_saved_list_selects_same_clients_after_excel_reorder(qapp, tmp_path, monkeypatch):
    import ui.tab_recipients as tab_module
    from ui.tab_recipients import TabRecipients

    monkeypatch.setattr(tab_module, "show_info", lambda *a, **k: None)
    monkeypatch.setattr(tab_module, "show_warning", lambda *a, **k: None)
    monkeypatch.setattr(tab_module, "show_error", lambda *a, **k: None)
    monkeypatch.setattr(
        tab_module.InputDialog,
        "get_text",
        staticmethod(lambda *a, **k: ("Mumbai Clients", True)),
    )

    tab = TabRecipients()
    tab.list_storage.lists_dir = tmp_path

    columns = ["Email", "Name"]
    original = [
        {"Email": "a@x.com", "Name": "A"},
        {"Email": "b@x.com", "Name": "B"},
        {"Email": "c@x.com", "Name": "C"},
    ]
    tab.set_data(original, columns, "Email", None)
    tab.set_selected_indices([0, 2])  # a@x.com and c@x.com

    tab._save_list()

    # Excel edited: new client on top, order shuffled
    reordered = [
        {"Email": "new@x.com", "Name": "N"},
        {"Email": "c@x.com", "Name": "C"},
        {"Email": "b@x.com", "Name": "B"},
        {"Email": "a@x.com", "Name": "A"},
    ]
    tab.set_data(reordered, columns, "Email", None)

    idx = tab.lists_combo.findText("Mumbai Clients (2)")
    assert idx >= 0, "saved list should appear in the dropdown"
    tab.lists_combo.setCurrentIndex(idx)
    tab._load_list()

    selected_emails = sorted(
        row["Email"] for row in tab.get_selected_data()
    )
    assert selected_emails == ["a@x.com", "c@x.com"]
