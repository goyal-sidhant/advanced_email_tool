# Roadmap

## Current Version: 1.2.0

---

## ✅ Recently Completed

### Table in Email Body ✓
**Status:** COMPLETE (v1.2.0)

- Paste Table button in Compose toolbar
- Copy from Excel → Click Paste Table → Styled HTML table
- First row styled as header
- Keyboard shortcut: `Ctrl+Shift+V`

### Image in Email Body ✓
**Status:** COMPLETE (v1.2.0)

- Insert Image menu with 3 options:
  - From File...
  - From Clipboard
  - Drag & Drop (onto editor)
- CID attachment method (Outlook-native)
- Static images only (same for all recipients)

---

## 🔴 Priority 1 — Next Up

### UI Styling
**Status:** Not started

**Goals:**
- Professional look (not "default Qt")
- Consistent color scheme
- Better spacing and typography
- Custom stylesheet (QSS)

**Elements to Style:**
- Tab bar
- Buttons (primary, secondary, danger)
- Input fields
- Group boxes
- Progress bars
- Status indicators (success/warning/error)
- Tables and lists

**Color Palette (tentative):**
```
Primary:    #0078D4 (Microsoft Blue)
Success:    #28A745
Warning:    #FFC107
Error:      #DC3545
Background: #F5F5F5
Card:       #FFFFFF
Text:       #333333
```

---

### Better Error Handling
**Status:** Not started

**Current Issues:**
- Generic error messages
- Some failures silently ignored
- No recovery suggestions

**Improvements Needed:**

| Scenario | Current | Improved |
|----------|---------|----------|
| Outlook not found | "Outlook not available" | "Outlook Classic not detected. New Outlook is not supported. [Learn More]" |
| Network drive disconnect | Crash | "Lost connection to X. Retry?" |
| File locked | Crash | "File in use by another program. Close it and retry." |
| Invalid email | Sends anyway | "Invalid email format for row 5: 'john@'. Skip or fix?" |
| Excel load fail | Generic error | "Cannot read file. Is it open in Excel? Close and retry." |
| Attachment missing | Silent skip | "Warning: 3 attachments not found. [View List]" |

**New Outlook Detection:**
```python
# Check if New Outlook is running
# Show specific message with instructions to switch back
```

---

### In-App Help (Tooltips)
**Status:** Not started

**Implementation:**
- `?` icon buttons next to complex features
- Hover tooltips on all buttons
- Status bar hints on focus

**Key Areas Needing Help:**
- Identifier column explanation
- AND/OR logic explanation
- Variable syntax `{ColumnName}`
- Template save/load
- Static vs Variable attachments
- Preview mode vs actual send

**Example Tooltips:**
```
[Identifier Column ?]
Tooltip: "Column used to match files. If Identifier is 'PAN001', 
         files containing 'PAN001' in filename will be attached."

[AND/OR Logic ?]  
Tooltip: "OR: Match if file contains ANY identifier
         AND: Match only if file contains ALL identifiers"
```

---

## 🟢 Priority 3 — Nice to Have

### Create .exe (PyInstaller)
**Status:** Not started

**Goal:** Run without Python installation

**Steps:**
1. Create PyInstaller spec file
2. Bundle all dependencies
3. Test on clean Windows machine
4. Document build process

**Command:**
```bash
pyinstaller --onefile --windowed --name "EmailTool" main.py
```

**Considerations:**
- Include assets (icons, templates)
- Handle pywin32 DLLs
- Size optimization

---

### New Outlook Warning
**Status:** Not started

**Implementation:**
```python
def check_outlook_type():
    # Try COM connection
    # If fails, check if "olk.exe" (New Outlook) is running
    # Show specific message:
    #   "New Outlook detected. This app requires Outlook Classic.
    #    To switch: Settings → General → 'Use classic Outlook'
    #    [Open Settings] [Learn More]"
```

---

### Dark Mode
**Status:** Planned for future

**Implementation:**
- QSS stylesheet swap
- System preference detection (Windows dark mode)
- Toggle in settings/menu

**Considerations:**
- Rich text editor styling
- Preview pane styling
- Ensure readability in both modes

---

## 🅿️ Parking Lot — Maybe Someday

| Feature | Notes |
|---------|-------|
| Dynamic images per recipient | No current use case |
| Multiple Excel sheets merge | Not requested |
| Email scheduling | Send later functionality |
| CC/BCC from separate file | Complex recipient management |
| Signature management | Usually handled by Outlook |
| Graph API (New Outlook) | Major rewrite, avoid if possible |
| Mac support | Different mail architecture |
| Gmail/SMTP support | Alternative to Outlook |

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.1.1 | 2026-01-01 | AND/OR identifier logic, documentation |
| 1.1.0 | 2026-01-01 | UX improvements, multiple identifiers |
| 1.0.3 | 2026-01-01 | Import/export features |
| 1.0.2 | 2026-01-01 | Bug fixes (Outlook COM, CSS regex) |
| 1.0.1 | 2026-01-01 | Config fixes |
| 1.0.0 | 2026-01-01 | Initial release |

---

## Implementation Order

```
1. [P1] Table in Email Body       ✅ DONE (v1.2.0)
2. [P1] Image in Email Body       ✅ DONE (v1.2.0)
3. [P2] UI Styling                🔜 NEXT
4. [P2] Better Error Handling     Queued
5. [P2] In-App Help (Tooltips)    Queued
6. [P3] Create .exe               Later
7. [P3] New Outlook Warning       Later
8. [P3] Dark Mode                 Future
```

---

## Notes

- User's workflow is Excel-heavy → Paste from Excel is natural
- Static content only for tables/images in bulk mail context
- New Outlook lacks COM → Must use Classic Outlook
- Target: GST practitioners, tax professionals
- Typical use: ~50-100 emails every 10 days
