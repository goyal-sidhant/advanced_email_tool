"""
Tests for the Excel tab's threaded, non-blocking file load.

Loading used to run openpyxl synchronously on the UI thread — a big or
slow (OneDrive) workbook froze the window with no feedback. Loads now
run in a worker thread with the controls disabled while in flight, and
session restore defers data-dependent steps to a completion callback.
"""

import time

import openpyxl
import pytest


@pytest.fixture
def excel_file(tmp_path):
    path = tmp_path / "clients.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Clients"
    ws.append(["Email", "Name"])
    ws.append(["a@x.com", "A"])
    ws.append(["b@x.com", "B"])
    wb.save(path)
    wb.close()
    return path


@pytest.fixture
def tab(qapp, monkeypatch):
    import ui.tab_excel as tab_module

    monkeypatch.setattr(tab_module, "show_error", lambda *a, **k: None)
    monkeypatch.setattr(tab_module, "show_info", lambda *a, **k: None)

    from ui.tab_excel import TabExcel

    return TabExcel()


def _loaded(tab):
    return lambda: tab.get_data() and tab.row_count_label.text().startswith("2")


def test_load_populates_ui_via_worker(tab, excel_file, wait_until):
    tab._load_file(str(excel_file))

    wait_until(lambda: len(tab.get_data()) == 2, message="excel data loaded")

    assert tab.get_columns() == ["Email", "Name"]
    assert tab.get_file_path() == str(excel_file)
    assert tab.sheet_combo.isEnabled()
    assert tab.browse_btn.isEnabled()
    assert tab.reload_btn.isEnabled()
    assert tab.preview_table.rowCount() == 2


def test_controls_disabled_while_load_in_flight(tab, excel_file, wait_until, monkeypatch):
    from core.excel_handler import ExcelHandler

    real_load = ExcelHandler.load_file

    def slow_load(self, *args, **kwargs):
        time.sleep(0.3)
        return real_load(self, *args, **kwargs)

    monkeypatch.setattr(ExcelHandler, "load_file", slow_load)

    tab._load_file(str(excel_file))

    # Worker still running: controls must be disabled, label must say so
    assert not tab.browse_btn.isEnabled()
    assert not tab.reload_btn.isEnabled()
    assert "…" in tab.row_count_label.text() or "..." in tab.row_count_label.text()

    wait_until(lambda: tab.browse_btn.isEnabled(), message="load finished")
    assert len(tab.get_data()) == 2


def test_load_file_path_runs_callback_after_data_ready(tab, excel_file, wait_until):
    seen = []

    started = tab.load_file_path(
        str(excel_file), on_loaded=lambda: seen.append(len(tab.get_columns()))
    )

    assert started
    wait_until(lambda: bool(seen), message="on_loaded callback")
    assert seen == [2]  # both columns were available inside the callback


def test_load_file_path_missing_file_returns_false(tab):
    assert tab.load_file_path("C:/nowhere/gone.xlsx") is False
