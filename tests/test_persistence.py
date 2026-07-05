"""
Tests for crash-safe persistence and the Qt-based auto-save.
"""

import json

import pytest

from data.session_manager import SessionManager, AutoSaveManager


@pytest.fixture
def manager(tmp_path):
    m = SessionManager()
    m.session_file = tmp_path / "current_session.json"
    return m


def test_save_session_is_atomic_no_tmp_left_behind(manager, tmp_path):
    ok = manager.save_session({"excel_file_path": "C:/clients.xlsx"})
    assert ok

    state = manager.load_session()
    assert state["excel_file_path"] == "C:/clients.xlsx"
    # No temp artifacts left next to the session file
    assert list(tmp_path.glob("*.tmp")) == []


def test_save_session_survives_existing_corrupt_file(manager):
    manager.session_file.write_text("{ this is not json", encoding="utf-8")
    assert manager.load_session() is None  # corrupt reads as no session

    ok = manager.save_session({"excel_file_path": "C:/x.xlsx"})
    assert ok
    assert manager.load_session()["excel_file_path"] == "C:/x.xlsx"


def test_autosave_runs_on_qtimer_and_respects_pause(qapp, manager, wait_until):
    auto = AutoSaveManager(manager)

    paused = {"value": True}
    saves = []
    auto.set_state_getter(lambda: {"excel_file_path": f"save{len(saves)}"})
    auto.set_pause_check(lambda: paused["value"])

    original_save = manager.save_session

    def counting_save(state):
        saves.append(state)
        return original_save(state)

    manager.save_session = counting_save

    auto.start(interval=0.05)  # 50ms for the test
    try:
        # Paused: spin some event loop time, nothing may save
        import time

        deadline = time.time() + 0.3
        while time.time() < deadline:
            qapp.processEvents()
            time.sleep(0.01)
        assert saves == []

        paused["value"] = False
        wait_until(lambda: len(saves) >= 2, message="periodic auto-save")
    finally:
        auto.stop()
