"""
Tests for column-mapping restore on the Excel tab.

Session/profile restore goes through set_column_mapping; it must round-trip
everything get_column_mapping saves — including Identifier 2 and the
AND/OR logic — or a two-identifier AND setup silently degrades after a
restart and wrong attachments can match.
"""

import pytest


COLUMNS = ["Email", "PAN", "GST"]


@pytest.fixture
def tab(qapp):
    from ui.tab_excel import TabExcel

    t = TabExcel()
    t._columns = list(COLUMNS)
    t.to_combo.addItems(COLUMNS)
    for combo in (t.cc_combo, t.bcc_combo, t.identifier_combo, t.identifier2_combo):
        combo.addItems(COLUMNS)
    return t


def test_set_column_mapping_round_trips_all_fields(tab):
    saved = {
        "to": "Email",
        "cc": None,
        "bcc": None,
        "identifier": "PAN",
        "identifier2": "GST",
        "identifier_logic": "AND",
    }

    tab.set_column_mapping(saved)
    restored = tab.get_column_mapping()

    assert restored["to"] == "Email"
    assert restored["identifier"] == "PAN"
    assert restored["identifier2"] == "GST"
    assert restored["identifier_logic"] == "AND"


def test_set_column_mapping_defaults_to_or_logic(tab):
    tab.set_column_mapping({"to": "Email", "identifier": "PAN"})

    assert tab.get_column_mapping()["identifier_logic"] == "OR"
