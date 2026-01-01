# Advanced Email Tool

A PyQt5 desktop application for sending personalized bulk emails through Microsoft Outlook with dynamic attachments.

## Features

### Core Functionality
- **Excel Data Source**: Load recipient data from `.xlsx` / `.xlsm` files
- **Template Variables**: Use `{ColumnName}` placeholders in subject and body
- **Rich Text Editor**: Compose HTML emails with formatting
- **Outlook Integration**: Send via Microsoft Outlook COM automation

### Attachment System
- **Static Attachments**: Files sent to all recipients
- **Variable Attachments**: Auto-match files by identifier (PAN, Client Code, etc.)
- **Multiple Identifiers**: Match by 2 columns with AND/OR logic
- **Folder Scanning**: Index attachment folders for fast matching

### Workflow Features
- **6-Tab Workflow**: Excel → Compose → Attachments → Recipients → Preview → Send
- **Session Auto-Save**: Never lose your work
- **Checkpoint/Resume**: Resume interrupted send operations
- **Test Send**: Send first email to yourself before bulk send

## Installation

### Requirements
- Windows 10/11
- Python 3.10+ 
- Microsoft Outlook (desktop app, not web)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Packages
```
PyQt5>=5.15.0
openpyxl>=3.0.0
pywin32>=300
python-docx>=0.8.11  # Optional, for Word import
```

## Usage

### Quick Start
```bash
python main.py
```

### Workflow

#### 1. Excel Tab
- Load your Excel file with recipient data
- Map columns: To Email, CC, BCC, Identifier(s)
- Data offset: If headers aren't in row 1, column A

#### 2. Compose Tab
- Write subject with variables: `Reminder for {ClientName}`
- Compose body using rich text editor
- Insert variables from dropdown or type `{ColumnName}`
- Save/load templates for reuse
- Import content from Word (.docx) or Text (.txt) files

#### 3. Attachments Tab
- **Static**: Add files sent to everyone
- **Variable**: 
  - Select folder containing client files
  - Scan folder to index files
  - Files matched by identifier in filename (substring match)
  - Use 2 identifiers with AND/OR logic

#### 4. Recipients Tab
- View all recipients from Excel
- Select/deselect individual recipients
- Filter by criteria
- Save recipient lists for reuse

#### 5. Preview Tab
- Navigate through each recipient
- See substituted subject and body
- View matched attachments per recipient
- Customize display format (Email / Name + Email / Custom)

#### 6. Send Tab
- Pre-send summary with warnings
- Send test email to yourself first
- Configure send interval (delay between emails)
- Preview mode (display in Outlook without sending)
- Real-time progress log

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+1` to `Ctrl+6` | Jump to specific tab |
| `Ctrl+Tab` | Next tab |
| `Ctrl+Shift+Tab` | Previous tab |
| `←` / `→` | Navigate recipients (Preview tab) |
| `Ctrl+S` | Save session |
| `Ctrl+N` | New session |

## Column Name Support

Template variables support special characters:
- `{Client Name}` - spaces
- `{Tax/Rate}` - slashes
- `{Amount (INR)}` - parentheses
- `{Client-Code}` - hyphens

## Identifier Matching

### Single Identifier
Files are matched if the identifier appears anywhere in the filename.

Example: Identifier = `PAN001`
- ✅ `PAN001_report.pdf`
- ✅ `2024_PAN001_final.xlsx`
- ❌ `pan001_report.pdf` (case-sensitive!)

### Multiple Identifiers (OR Logic)
File matches if it contains **either** identifier.

Example: ID1 = `ABC123`, ID2 = `PAN001`
- ✅ `ABC123_report.pdf`
- ✅ `PAN001_form.pdf`
- ✅ `ABC123_PAN001_final.pdf`

### Multiple Identifiers (AND Logic)
File matches only if it contains **both** identifiers.

Example: ID1 = `ABC123`, ID2 = `PAN001`
- ❌ `ABC123_report.pdf`
- ❌ `PAN001_form.pdf`
- ✅ `ABC123_PAN001_final.pdf`

## File Structure

```
advanced_email_tool/
├── main.py                 # Entry point
├── config.py               # App configuration
├── requirements.txt        # Dependencies
├── README.md               # This file
├── CHANGELOG.md            # Version history
│
├── core/                   # Business logic
│   ├── email_builder.py    # Email construction
│   ├── excel_handler.py    # Excel file handling
│   ├── template_engine.py  # Variable substitution
│   ├── attachment_matcher.py # File matching
│   ├── outlook_sender.py   # Outlook COM integration
│   └── validators.py       # Email validation
│
├── ui/                     # User interface
│   ├── main_window.py      # Main window
│   ├── tab_excel.py        # Excel tab
│   ├── tab_compose.py      # Compose tab
│   ├── tab_attachments.py  # Attachments tab
│   ├── tab_recipients.py   # Recipients tab
│   ├── tab_preview.py      # Preview tab
│   ├── tab_send.py         # Send tab
│   └── components/         # Reusable UI components
│
├── data/                   # Data management
│   ├── session_manager.py  # Session save/restore
│   ├── template_storage.py # Template persistence
│   ├── checkpoint.py       # Send checkpoint/resume
│   └── recipient_lists.py  # Saved recipient lists
│
├── utils/                  # Utilities
│   ├── logger.py           # Logging
│   ├── file_utils.py       # File operations
│   └── html_converter.py   # HTML utilities
│
├── resources/              # Static resources
│   ├── icons/
│   └── default_templates/
│
└── .app_data/              # Runtime data (gitignored)
    ├── logs/
    ├── templates/
    ├── sessions/
    ├── checkpoints/
    └── recipient_lists/
```

## Troubleshooting

### "Outlook not available"
- Ensure Microsoft Outlook desktop app is installed
- Run Outlook at least once before using this tool
- Check if Outlook is set as default mail client

### "Cannot create mail item"
- Restart Outlook
- Run the tool as administrator
- Check Windows Event Viewer for COM errors

### Special characters in columns not working
- Ensure you're using the exact column name including spaces
- Variable names are case-sensitive
- Avoid `:` and `;` in column names (reserved for CSS)

### Files not matching
- Matching is case-sensitive
- Check identifier exists in filename (not just folder name)
- Use "Test Matching" feature in Attachments tab

## Configuration

Edit `config.py` to customize:

```python
APP_NAME = "Advanced Email Tool"
APP_VERSION = "1.1.1"

# Send settings
SEND_INTERVAL = 3  # Seconds between emails
BATCH_SIZE = 50    # Emails per batch

# Auto-save
AUTO_SAVE_INTERVAL = 180  # Seconds
```

## License

Internal tool - Not for distribution.

## Support

For issues or feature requests, contact the developer.
