# Changelog

All notable changes to Advanced Email Tool are documented here.

## [1.1.1] - 2026-01-01

### Added
- **AND/OR Logic** for multiple identifier matching
  - OR: File matches if it contains either identifier
  - AND: File matches only if it contains both identifiers
  - Radio button selection in Excel tab

### Changed
- Identifier matching now supports choosing logic type

---

## [1.1.0] - 2026-01-01

### Added

#### UX Improvements
- **Pre-Send Summary Panel** (Send tab)
  - Shows recipient count
  - Shows count with/without attachments
  - Warning for recipients without attachments
  - "View List" button to see details

- **Test Send Button**
  - Send first email to yourself for verification
  - Subject prefixed with `[TEST]`
  - Uses logged-in Outlook account

- **Unmatched Identifiers Warning** (Attachments tab)
  - Shows count of identifiers with no matching files
  - "View List" button to see which ones

- **Keyboard Shortcuts**
  - `Ctrl+1` to `Ctrl+6`: Jump to specific tab
  - `Ctrl+Tab`: Next tab
  - `Ctrl+Shift+Tab`: Previous tab
  - `←` / `→`: Navigate recipients in Preview tab
  - `Ctrl+S`: Save session
  - `Ctrl+N`: New session

- **Improved Session Restore Dialog**
  - Shows filename, template name, recipient count
  - Shows "time ago" format (e.g., "2 hours ago")

- **Multiple Identifiers Support**
  - Identifier 1 + Identifier 2 columns
  - Match files using either identifier

### Fixed
- **Special characters in column names** now work
  - Supports `/`, `()`, `-`, spaces in `{Variable Names}`
  - Regex updated to allow `{Column Name (GST)}`, `{Tax/Rate}`, etc.

---

## [1.0.3] - 2026-01-01

### Added
- **Export Blank Excel Template** (Excel tab)
  - Creates professional template with sample structure
  - Includes Instructions sheet
  - Styled headers

- **Import Word/TXT/HTML** (Compose tab)
  - Import content from .docx, .txt, .html files
  - Option to replace or append to current body

- **Preview Display Format Options** (Preview tab)
  - Email only
  - Name (Email)
  - Identifier - Email
  - Custom format with `{ColumnName}` support

- **Data Offset Support** (Excel tab)
  - Set start row and column for data
  - For Excel files where data doesn't start at A1

### Fixed
- Missing `_refresh_current` method in Preview tab

---

## [1.0.2] - 2026-01-01

### Fixed
- **Outlook CreateItem error**
  - Root cause: COM connection going stale
  - Fix: Use `EnsureDispatch` + fresh connection per email

- **CSS matched as variables**
  - Root cause: Regex `{...}` too greedy, matching CSS blocks
  - Fix: New regex only matches valid variable names (no `:` or `;`)

- **Added `.app_data` to .gitignore**

---

## [1.0.1] - 2026-01-01

### Fixed
- Missing `ALL_FILES_FILTER` constant in config.py
- Log directory now portable (`.app_data/` in project folder)
- Removed duplicate `import os` in email_builder.py

### Changed
- Data directory changed from user home to app directory
  - From: `C:\Users\...\`.advanced_email_tool\`
  - To: `advanced_email_tool\.app_data\`

---

## [1.0.0] - 2026-01-01

### Initial Release

#### Features
- 6-tab workflow: Excel → Compose → Attachments → Recipients → Preview → Send
- Excel data loading with column mapping
- Rich text email composer with variable support
- Template save/load system
- Static attachments (sent to all)
- Variable attachments (matched by identifier)
- Recipient selection and filtering
- Email preview with substitution
- Outlook integration with account selection
- Session auto-save and restore
- Checkpoint/resume for interrupted sends
- Progress logging

#### Technical
- PyQt5 desktop application
- Outlook COM automation via pywin32
- openpyxl for Excel handling
- 32 Python files, ~9,300 lines of code

---

## Version Numbering

- **Major.Minor.Patch** (e.g., 1.1.1)
- **Major**: Breaking changes or major feature additions
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, small improvements
