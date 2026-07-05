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
