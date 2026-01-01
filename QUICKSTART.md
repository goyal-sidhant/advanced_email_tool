# Quick Start Guide

## First Time Setup

1. Install Python 3.10+
2. Run: `pip install -r requirements.txt`
3. Open Outlook at least once
4. Run: `python main.py`

---

## 6-Step Workflow

### Step 1: Excel
1. Click **Browse** → Select your Excel file
2. Map columns:
   - **To Email** (required): Column with recipient emails
   - **Identifier**: Column for matching attachments (PAN, Code, etc.)

### Step 2: Compose
1. Enter **Subject**: `Reminder: {ClientName} - Annual Return`
2. Write **Body** using the editor
3. Insert variables: Select from dropdown or type `{ColumnName}`
4. **Save** template for reuse

### Step 3: Attachments
**Static** (sent to all):
- Click **Add Files** → Select common attachments

**Variable** (matched per recipient):
1. Click **Browse** → Select folder with client files
2. Click **Scan Folder**
3. Check match statistics

### Step 4: Recipients
- Select/deselect recipients as needed
- Use **Select All** / **Deselect All**

### Step 5: Preview
- Use **←** / **→** to navigate
- Verify subject, body, attachments look correct

### Step 6: Send
1. Check **Pre-Send Summary**
2. Click **Send Test Email First** (recommended!)
3. Check your inbox
4. Click **Start Sending**

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+1-6` | Jump to tab |
| `Ctrl+Tab` | Next tab |
| `Ctrl+Shift+Tab` | Previous tab |
| `Ctrl+S` | Save session |

---

## Variable Syntax

Use `{ColumnName}` in subject or body:

```
Dear {ClientName},

Your PAN {PAN} has pending compliance.
Amount due: ₹{Amount (INR)}

Regards,
{SenderName}
```

**Supported characters in column names:**
- Spaces: `{Client Name}`
- Slashes: `{Tax/Rate}`
- Parentheses: `{Amount (INR)}`
- Hyphens: `{Client-Code}`

---

## Identifier Matching

Files match if identifier appears **anywhere in filename**.

| Identifier | ✅ Matches | ❌ Doesn't Match |
|------------|-----------|------------------|
| `PAN001` | `PAN001_report.pdf` | `pan001_report.pdf` |
| `ABC` | `ABC_form.xlsx` | `abc_form.xlsx` |

**Case-sensitive!**

### Two Identifiers

**OR mode**: File matches if it contains ID1 *or* ID2
**AND mode**: File must contain *both* ID1 *and* ID2

---

## Common Issues

| Problem | Solution |
|---------|----------|
| "Outlook not available" | Open Outlook desktop app first |
| Variables not replaced | Check exact column name (case-sensitive) |
| Files not matching | Check case, use Test Matching feature |
| Special chars not working | Avoid `:` and `;` in column names |

---

## Tips

1. **Always send test first** - Use "Send Test Email First" button
2. **Save templates** - Reuse for recurring emails
3. **Check unmatched** - Review recipients without attachments
4. **Preview all** - Navigate through each recipient before sending
