"""
Shared pytest fixtures for the Advanced Email Tool test suite.
"""

import os
import sys

# Make the app importable from the tests directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Render Qt widgets offscreen so tests never flash windows
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(scope="session")
def qapp():
    """Single QApplication shared by all widget tests."""
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def wait_until(qapp):
    """Spin the event loop until a condition holds (or fail the test)."""
    import time

    def _wait(condition, timeout_ms=5000, message="condition"):
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            qapp.processEvents()
            if condition():
                return True
            time.sleep(0.01)
        pytest.fail(f"Timed out waiting for: {message}")

    return _wait
