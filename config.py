"""
Advanced Email Tool - Configuration
====================================
Central configuration file for all app settings, paths, and constants.
"""

import os
from pathlib import Path

# =============================================================================
# APPLICATION INFO
# =============================================================================
APP_NAME = "Advanced Email Tool"
APP_VERSION = "1.1.1"
APP_AUTHOR = "Sidhant"

# =============================================================================
# PATHS
# =============================================================================
# Application directory (where the code is located)
APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Data directory - SAME folder as the code (portable app style)
USER_DATA_DIR = APP_DIR / ".app_data"

# Subdirectories
TEMPLATES_DIR = USER_DATA_DIR / "templates"
SESSIONS_DIR = USER_DATA_DIR / "sessions"
LOGS_DIR = USER_DATA_DIR / "logs"
RECIPIENT_LISTS_DIR = USER_DATA_DIR / "recipient_lists"
CHECKPOINTS_DIR = USER_DATA_DIR / "checkpoints"

# Ensure directories exist
def ensure_directories():
    """Create all required directories if they don't exist."""
    for directory in [USER_DATA_DIR, TEMPLATES_DIR, SESSIONS_DIR, 
                      LOGS_DIR, RECIPIENT_LISTS_DIR, CHECKPOINTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

# =============================================================================
# EMAIL SETTINGS
# =============================================================================
# Time between sending emails (seconds) - prevents spam filter triggers
SEND_INTERVAL = 1.5

# Maximum attachment size warning threshold (MB)
MAX_ATTACHMENT_SIZE_MB = 25

# Convert to bytes for comparison
MAX_ATTACHMENT_SIZE_BYTES = MAX_ATTACHMENT_SIZE_MB * 1024 * 1024

# =============================================================================
# SESSION SETTINGS
# =============================================================================
# Auto-save interval (seconds)
AUTO_SAVE_INTERVAL = 180  # 3 minutes

# Session file name
SESSION_FILE = "current_session.json"

# =============================================================================
# EMAIL VALIDATION
# =============================================================================
# Common email typos and their corrections
EMAIL_TYPO_SUGGESTIONS = {
    "gmial.com": "gmail.com",
    "gmal.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmail.co": "gmail.com",
    "gmail.om": "gmail.com",
    "gmaill.com": "gmail.com",
    "yahooo.com": "yahoo.com",
    "yaho.com": "yahoo.com",
    "yahoo.co": "yahoo.com",
    "hotmal.com": "hotmail.com",
    "hotmai.com": "hotmail.com",
    "hotmail.co": "hotmail.com",
    "outloo.com": "outlook.com",
    "outlok.com": "outlook.com",
    "outlook.co": "outlook.com",
    "rediffmal.com": "rediffmail.com",
    "rediffmail.co": "rediffmail.com",
}

# =============================================================================
# UI SETTINGS
# =============================================================================
# Window dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_DEFAULT_WIDTH = 1100
WINDOW_DEFAULT_HEIGHT = 750
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 600

# Font settings
DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_FONT_SIZE = 10
EDITOR_FONT_FAMILY = "Segoe UI"
EDITOR_FONT_SIZE = 11

# =============================================================================
# FILE MATCHING SETTINGS
# =============================================================================
# Whether to search subfolders by default
DEFAULT_RECURSIVE_SEARCH = False

# File extensions to include in matching (empty = all files)
ATTACHMENT_FILE_EXTENSIONS = []  # e.g., ['.pdf', '.xlsx', '.docx']

# =============================================================================
# FILE DIALOG FILTERS
# =============================================================================
EXCEL_FILTER = "Excel Files (*.xlsx *.xlsm);;All Files (*.*)"
ALL_FILES_FILTER = "All Files (*.*)"
PDF_FILTER = "PDF Files (*.pdf);;All Files (*.*)"

# =============================================================================
# LOGGING SETTINGS
# =============================================================================
LOG_FILE_NAME = "app.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3

# =============================================================================
# CHECKPOINT SETTINGS
# =============================================================================
CHECKPOINT_FILE = "send_checkpoint.json"

# =============================================================================
# NETWORK SETTINGS
# =============================================================================
# Timeout for network drive accessibility check (seconds)
NETWORK_CHECK_TIMEOUT = 5

# =============================================================================
# TEMPLATE DEFAULTS
# =============================================================================
DEFAULT_SUBJECT = "{Subject}"
DEFAULT_BODY = """<p>Dear {Name},</p>

<p>Please find the attached documents for your reference.</p>

<p>Regards,<br>
Your Name</p>
"""
