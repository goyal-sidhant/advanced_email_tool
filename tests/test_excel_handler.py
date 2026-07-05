"""
Tests for ExcelHandler file-lock behavior.

The app must never hold the Excel file open: users keep the file open in
Excel while the tool runs, and Excel saves by replacing the file — which
fails on Windows if any process holds a handle. Loads therefore read an
in-memory copy and Refresh re-reads from disk.
"""

import os

import openpyxl
import pytest

from core.excel_handler import ExcelHandler


def _write_workbook(path, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Clients"
    for row in rows:
        ws.append(row)
    wb.save(path)
    wb.close()


@pytest.fixture
def excel_file(tmp_path):
    path = tmp_path / "clients.xlsx"
    _write_workbook(
        path,
        [["Email", "Name"], ["a@x.com", "A"], ["b@x.com", "B"]],
    )
    return path


def test_loaded_file_is_not_locked_on_disk(excel_file, tmp_path):
    handler = ExcelHandler()
    ok, error = handler.load_file(str(excel_file))
    assert ok, error

    # Excel saves by replacing the file — a held handle makes this fail
    renamed = tmp_path / "renamed.xlsx"
    os.rename(excel_file, renamed)  # raises PermissionError if locked
    os.rename(renamed, excel_file)

    # Data stays readable from the in-memory copy after the swap
    assert handler.row_count == 2
    assert handler.data[0]["Email"] == "a@x.com"


def test_refresh_rereads_changes_saved_while_loaded(excel_file):
    handler = ExcelHandler()
    ok, error = handler.load_file(str(excel_file))
    assert ok, error
    assert handler.row_count == 2

    # User edits and saves the file in Excel while the tool has it loaded
    _write_workbook(
        excel_file,
        [["Email", "Name"], ["a@x.com", "A"], ["b@x.com", "B"], ["c@x.com", "C"]],
    )

    ok, error = handler.load_file(str(excel_file))
    assert ok, error
    assert handler.row_count == 3
    assert handler.data[2]["Email"] == "c@x.com"


def test_offset_load_does_not_lock_file_either(excel_file, tmp_path):
    handler = ExcelHandler()
    ok, error = handler.load_file_with_offset(str(excel_file), start_row=1, start_col=1)
    assert ok, error

    renamed = tmp_path / "renamed2.xlsx"
    os.rename(excel_file, renamed)
    os.rename(renamed, excel_file)
