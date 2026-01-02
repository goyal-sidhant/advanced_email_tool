# Changelog

All notable changes to Advanced Email Tool are documented here.

## [1.4.0] - 2026-01-02

### Added

#### Dark Mode 🌙
- **Full dark theme** with Microsoft Blue accents
- Three options via View → Theme menu:
  - **System (Auto)** - Follows Windows dark/light setting
  - **Light** - Classic light theme
  - **Dark** - Dark mode for low-light use
- Preference saved and restored on restart
- All UI elements styled for both modes

#### Theme-Aware Validation
- Email validation colors adapt to theme
- Dark mode uses softer red tones for better visibility
- Success/error indicators adjust automatically

### Technical
- New `utils/theme_manager.py` module
- New `resources/style_dark.qss` stylesheet (350+ lines)
- Preferences saved to `preferences.json`
- Windows registry detection for system theme

---

## [1.3.0] - 2026-01-02

### Added

#### UI Styling
- **Professional stylesheet** with Microsoft Blue color scheme
- Clean Windows-like appearance
- Styled tabs, buttons, inputs, tables, progress bars
- Consistent colors throughout the app
- Dark tooltips with better readability

#### Email Validation
- **Auto-validates emails** when Excel is loaded
- Invalid emails highlighted in **red** in preview table
- Validation status indicator: "✓ All emails valid" or "⚠ X invalid"
- Hover tooltip on invalid cells

#### In-App Help (Tooltips)
- Tooltips on all major UI elements
- Detailed explanations for:
  - Column mapping (To, CC, BCC, Identifiers)
  - AND/OR logic
  - Variable syntax `{ColumnName}`
  - Static vs Variable attachments
  - Preview mode
  - Send interval

#### New Outlook Detection
- Detects if New Outlook is running (`olk.exe`)
- Shows clear warning with instructions to switch back
- Checks registry for UseNewOutlook setting

### Changed
- Improved error messages throughout
- Better organized code structure

---

## [1.2.0] - 2026-01-01

### Added

#### Table in Email Body
- **Paste Table** button in Compose toolbar (`Ctrl+Shift+V`)
- Paste directly from Excel, Google Sheets, or any spreadsheet
- Auto-styles first row as header (blue background, white text)
- Clean table formatting with borders and padding

#### Image in Email Body  
- **Insert Image** menu in Compose toolbar
- Three insertion methods:
  - From File (file picker)
  - From Clipboard (screenshots, copied images)
  - Drag & Drop (like Gmail!)
- Images embedded using CID attachments (Outlook-native, most reliable)
- Supported formats: PNG, JPG, GIF, BMP

### Technical
- Added `embedded_images` field to Email dataclass
- Images stored as base64 in editor, converted to CID on send
- Outlook PropertyAccessor used to set Content-ID for inline display

---

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
