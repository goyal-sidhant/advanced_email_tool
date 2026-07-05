"""
Tests for recipient table performance and filter-aware selection.

The table used to create a QCheckBox cell-widget per row and fully
rebuild on every search keystroke and every select-all/none/invert.
It now uses checkable items, debounces the search box, updates check
states in place, and scopes Select All/None/Invert to the visible rows
while a filter is active (searching "smith" then Select All no longer
silently selects every client in the file).
"""

import pytest

from PyQt5.QtCore import Qt


@pytest.fixture
def widget(qapp):
    from ui.components.recipient_list import RecipientListWidget

    w = RecipientListWidget()
    w.set_data(
        [
            {"Email": "amit@x.com", "Name": "Amit"},
            {"Email": "bina@x.com", "Name": "Bina"},
            {"Email": "chetan@y.com", "Name": "Chetan"},
            {"Email": "divya@y.com", "Name": "Divya"},
            {"Email": "esha@z.com", "Name": "Esha"},
        ],
        ["Email", "Name"],
        "Email",
        None,
    )
    return w


def _filter(widget, text):
    """Apply a search filter synchronously (bypassing the debounce)."""
    widget.search_input.blockSignals(True)
    widget.search_input.setText(text)
    widget.search_input.blockSignals(False)
    widget._apply_filter()


def test_table_uses_checkable_items_not_cell_widgets(widget):
    assert widget.table.cellWidget(0, 0) is None, "no per-row QCheckBox widgets"
    item = widget.table.item(0, 0)
    assert item is not None
    assert item.flags() & Qt.ItemIsUserCheckable


def test_checking_an_item_updates_selection(widget):
    item = widget.table.item(2, 0)
    item.setCheckState(Qt.Checked)
    assert widget.get_selected_indices() == [2]

    item.setCheckState(Qt.Unchecked)
    assert widget.get_selected_indices() == []


def test_search_is_debounced(widget):
    widget.search_input.setText("y.com")

    # Filter must not run on the keystroke itself
    assert widget.table.rowCount() == 5

    # After the debounce interval it applies
    import time
    from PyQt5.QtWidgets import QApplication

    deadline = time.time() + 2
    while time.time() < deadline and widget.table.rowCount() != 2:
        QApplication.instance().processEvents()
        time.sleep(0.01)

    assert widget.table.rowCount() == 2


def test_select_all_respects_active_filter(widget):
    _filter(widget, "y.com")  # chetan and divya
    widget.select_all()

    assert widget.get_selected_indices() == [2, 3]
    assert "shown" in widget.select_all_btn.text()


def test_select_all_without_filter_selects_everything(widget):
    widget.select_all()
    assert widget.get_selected_indices() == [0, 1, 2, 3, 4]
    assert widget.select_all_btn.text() == "Select All"


def test_select_none_with_filter_clears_only_visible(widget):
    widget.select_all()  # everyone
    _filter(widget, "y.com")
    widget.select_none()

    assert widget.get_selected_indices() == [0, 1, 4]


def test_invert_with_filter_flips_only_visible(widget):
    widget.set_selected_indices([2])
    _filter(widget, "y.com")  # rows 2, 3 visible
    widget.invert_selection()

    assert widget.get_selected_indices() == [3]


def test_selection_ops_do_not_rebuild_the_table(widget, monkeypatch):
    rebuilds = []
    original = widget._rebuild_table
    monkeypatch.setattr(
        widget, "_rebuild_table", lambda: rebuilds.append(1) or original()
    )

    widget.select_all()
    widget.invert_selection()
    widget.select_none()
    widget.set_selected_indices([1, 2])

    assert rebuilds == [], "selection changes must update check states in place"
