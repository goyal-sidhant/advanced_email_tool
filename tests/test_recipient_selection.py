"""
Tests for recipient selection survival across column-mapping changes.
"""

import pytest


@pytest.fixture
def tab(qapp):
    from ui.tab_recipients import TabRecipients

    return TabRecipients()


def _rows(n):
    return [{"Email": f"user{i}@example.com", "Name": f"User {i}"} for i in range(n)]


COLUMNS = ["Email", "Name"]


def test_mapping_change_preserves_curated_selection(tab):
    tab.set_data(_rows(5), COLUMNS, "Email", None)
    assert tab.get_selected_count() == 5  # initial load selects all

    tab.set_selected_indices([0, 2])

    # Same data re-pushed because the user touched a mapping combo
    tab.set_data(_rows(5), COLUMNS, "Email", "Name", preserve_selection=True)

    assert sorted(tab.get_selected_indices()) == [0, 2]


def test_preserve_selection_keeps_deliberate_empty_selection(tab):
    tab.set_data(_rows(4), COLUMNS, "Email", None)
    tab.set_selected_indices([])

    tab.set_data(_rows(4), COLUMNS, "Email", "Name", preserve_selection=True)

    assert tab.get_selected_indices() == []


def test_preserve_selection_falls_back_to_select_all_when_rows_change(tab):
    tab.set_data(_rows(5), COLUMNS, "Email", None)
    tab.set_selected_indices([1])

    # Row count changed -> old indices are meaningless, select all again
    tab.set_data(_rows(3), COLUMNS, "Email", None, preserve_selection=True)

    assert tab.get_selected_count() == 3


def test_plain_set_data_still_selects_all(tab):
    tab.set_data(_rows(5), COLUMNS, "Email", None)
    tab.set_selected_indices([1])

    tab.set_data(_rows(5), COLUMNS, "Email", None)

    assert tab.get_selected_count() == 5
