# PROJECT AUDIT — Advanced Email Tool

> **What this is.** A "Project Archaeology" audit made with `Project_Audit_FINAL.md` from the
> template toolkit, at the time the app was brought under the toolkit (adoption, not a rebuild).
> It describes the app **as it is** on `main` at commit `f5b9511` (version 1.8.0, 5 July 2026).
>
> - **Audited on:** 03-11-2026, in a Linux cloud session. The app's window, Outlook, Excel and the
>   office network were not available there. Everything that needs them is marked
>   *"needs an office PC"*.
> - **Saved in:** `.build-docs/` (the author asked for this place instead of the project root).
> - **How the audit was done.** Every file in the repository was read line by line (63 tracked
>   files, about 17,200 lines, plus `.gitignore`). Every one of the 28 commits was read with
>   `git show`: the 27 later diffs in full, and the first commit's files through today's files plus
>   those diffs (the 9 files never changed since the first commit were read as they are today).
>   Test files and the two style sheets were read once in full; for the commits that added them, only
>   which test arrived when was noted. Where a reading suggested a silent bug, it was **checked by
>   running the real code on dummy data** in a throw-away copy (Python 3.13, PyQt5 5.15.11 with
>   Qt 5.15.14 drawing off-screen, openpyxl 3.1.5, Outlook replaced by a fake). Those findings say
>   **"(verified on dummy data)"**. The app's own test suite ran there too: **82 passed in 3.5 s**.
> - **No HANDOVER.md or FILE_INDEX.md exists** in this repository, so there was no handover
>   document to compare against. The repo's own `README.md`, `QUICKSTART.md`, `CHANGELOG.md` and
>   `ROADMAP.md` were read instead, and their differences from the code are listed (Section 7.9).
> - **Plain-English terms used below:** *COM* = the Windows mechanism a Python program uses to drive
>   Outlook; *worker thread* = a second line of work that runs while the window stays responsive;
>   *substring match* = "the file name contains this text anywhere"; *checkpoint* = the small file
>   that records which emails of a run were already sent, so a run can be resumed; *atomic write* =
>   writing to a temporary file and swapping it in, so a crash never leaves a half-written file;
>   *dead code* = code that nothing ever calls.

---

## SECTION 1: EXECUTIVE SUMMARY

Advanced Email Tool sends personalised bulk emails through **classic Microsoft Outlook** on a Windows
PC. It reads a recipient list from an Excel workbook (`.xlsx` / `.xlsm`), fills `{Column}` variables
from each row into a subject and a rich-text body, and attaches two kinds of files: **static**
attachments that every recipient gets, and **variable** attachments picked per recipient from a
folder because the file name contains that client's identifier (PAN, client code, name …). It is
built for a CA/GST office that mails documents and reminders to many clients at once
(`ROADMAP.md:232-233`: "Target: GST practitioners, tax professionals", "Typical use: ~50-100 emails
every 10 days"). It is written in Python with **PyQt5** for the window, **openpyxl** to read Excel,
**pywin32** (COM) to drive Outlook, and **python-docx** to import Word text. The app is **complete
and in active use** (version 1.8.0): it has a six-step tabbed workflow, session auto-save, a send
checkpoint with resume and retry, profiles, and 82 automated tests; the last burst of work (July 2026,
done with Claude) fixed many "trust bugs". The main risks found are in **who receives what**: the
identifier match is a plain "contains" test, so one client's identifier can pick up another client's
files; Resume and Retry send without asking and without checking that the same Excel file is loaded;
and several settings can silently differ from what the user set up (Section 7).

---

## SECTION 2: PROJECT STRUCTURE MAP

**Entry point:** `main.py` — run with `python main.py` (`README.md:47-50`, `QUICKSTART.md:8`).
There is **no `Run … .bat` launcher** and no desktop-shortcut set-up in the repository.

```
advanced_email_tool/
├── .git/                         [TOOLING]  Git history: 28 commits, branch main (+ an identical session branch)
├── .gitignore                    [CONFIG]   Ignores .app_data/, logs, sessions, checkpoints, venvs, IDE folders, .claude, Office temp files
├── .app_data/  (not in git)      [GENERATED] Created at start-up next to the code: templates/, sessions/, logs/,
│                                            recipient_lists/, checkpoints/, preferences.json (config.py:24-38)
├── README.md                     [DOCS]     User guide (partly out of date — Section 7.9)
├── QUICKSTART.md                 [DOCS]     Short how-to (contains wrong statements — Section 7.9)
├── CHANGELOG.md                  [DOCS]     Version history 1.0.0 → 1.6.0 only (stops before 1.7.0)
├── ROADMAP.md                    [DOCS]     Says "Current Version: 1.8.0"; done/planned items, parking lot
├── requirements.txt              [CONFIG]   PyQt5>=5.15.0, openpyxl>=3.1.0, pywin32>=306, python-docx>=1.1.0 (no pins)
├── config.py                     [CONFIG]   All settings: version, paths, send interval, size limit, typo list, window, theme, log
├── main.py                       [CORE]     Entry point: Qt app, folders, logger, theme, dependency check, main window
│
├── core/                         [CORE]     Business logic (no window code)
│   ├── __init__.py               [CORE]     Re-exports validators and the 5 core classes
│   ├── validators.py             [CORE]     Email-address checks, typo suggestions, other (mostly unused) checks
│   ├── excel_handler.py          [CORE]     Reads a workbook from an in-memory copy; header row/column offset
│   ├── template_engine.py        [CORE]     Replaces {Column} variables in subject/body
│   ├── attachment_matcher.py     [CORE]     Scans a folder, matches file names to identifiers (OR/AND), match report
│   ├── email_builder.py          [CORE]     Builds one Email object per recipient row (To/CC/BCC/subject/body/files)
│   └── outlook_sender.py         [CORE]     Talks to Outlook (COM): accounts, online check, send/display, batch loop
│
├── data/                         [CORE]     Saving and loading the user's own state (JSON files in .app_data)
│   ├── __init__.py               [CORE]     Re-exports the 4 storage classes
│   ├── session_manager.py        [CORE]     Session auto-save / restore; auto-save timer
│   ├── checkpoint.py             [CORE]     Send checkpoint: planned / completed / failed rows; resume
│   ├── template_storage.py       [CORE]     Email templates (subject + body) as JSON files
│   └── recipient_lists.py        [CORE]     Saved recipient selections (by email, with row numbers as fallback)
│
├── ui/                           [UI]       The window (PyQt5)
│   ├── __init__.py               [UI]       Re-exports MainWindow
│   ├── main_window.py            [UI]       Window, menus, tabs, wiring between tabs, session/profile restore
│   ├── tab_excel.py              [UI]       Tab 1: load Excel, sheet, offsets, column mapping, validation, blank template
│   ├── tab_compose.py            [UI]       Tab 2: subject, rich body, templates, import, Universal BCC
│   ├── tab_attachments.py        [UI]       Tab 3: static files, folder scan, statistics, test matching, report
│   ├── tab_recipients.py         [UI]       Tab 4: choose recipients, saved lists
│   ├── tab_preview.py            [UI]       Tab 5: preview each email, attachments, size warning
│   ├── tab_send.py               [UI]       Tab 6: account, interval, preview mode, test, send, cancel, resume, retry
│   └── components/               [UI]       Reusable widgets
│       ├── __init__.py           [UI]       Re-exports dialogs and widgets
│       ├── dialogs.py            [UI]       Message boxes, file/folder pickers that remember the last folder, input dialog
│       ├── file_list.py          [UI]       File list with sizes, drag-in, context menu; matched-files variant
│       ├── progress_log.py       [UI]       Coloured, time-stamped log with progress bar (Send tab)
│       ├── recipient_list.py     [UI]       Recipient table with tick boxes, search, filter-aware select all/none/invert
│       ├── rich_text_editor.py   [UI]       Body editor: formatting, lists, paste Excel table, images, HTML view
│       ├── tab_navigation.py     [UI]       "< Previous" / "Next >" bar at the bottom of each tab
│       └── variable_completer.py [UI]       Pop-up list of column names after typing "{"
│
├── utils/                        [UTIL]     Helpers
│   ├── __init__.py               [UTIL]     Re-exports logger and file helpers
│   ├── logger.py                 [UTIL]     Log to .app_data/logs/app.log (5 MB × 3) and the console
│   ├── file_utils.py             [UTIL]     Atomic JSON write, preferences, long paths, folder scan
│   ├── html_converter.py         [UTIL]     HTML ↔ text helpers (only 1 of 9 functions is used)
│   └── theme_manager.py          [UTIL]     Light/dark/system theme; reads the Windows registry
│
├── resources/                    [CONFIG]   Style sheets
│   ├── style.qss                 [CONFIG]   Light theme (472 lines)
│   └── style_dark.qss            [CONFIG]   Dark theme (529 lines)
│
└── tests/                        [TEST]     82 pytest tests (Qt off-screen, Outlook faked; never touch COM)
    ├── conftest.py               [TEST]     Adds the app folder to the import path; off-screen Qt; qapp and wait_until helpers
    ├── test_attachment_matcher.py [TEST]    Rescan picks up new / drops deleted files
    ├── test_checkpoint.py        [TEST]     Planned rows, suspend/resume, no re-send after two interruptions
    ├── test_compose_debounce.py  [TEST]     Typing is debounced; images extracted only when emails are built
    ├── test_excel_handler.py     [TEST]     File not locked; Refresh re-reads saved changes
    ├── test_new_session_reset.py [TEST]     New Session clears tabs; empty session not offered for restore
    ├── test_outlook_sender_attachments.py [TEST] An attachment failure blocks the send
    ├── test_outlook_thread_safety.py [TEST] Fresh COM connection per thread
    ├── test_persistence.py       [TEST]     Atomic session save; auto-save timer pauses during a send
    ├── test_polish.py            [TEST]     Preferences, drag-and-drop, all-row validation, preview, checkmarks, geometry
    ├── test_recipient_lists.py   [TEST]     Saved lists follow emails after rows move
    ├── test_recipient_selection.py [TEST]   Mapping changes keep a curated selection
    ├── test_recipient_table.py   [TEST]     Tick-box table, debounced search, filter-aware selection
    ├── test_send_batch.py        [TEST]     Instant cancel, in-flight callback, 3-failure stop, friendly errors
    ├── test_send_ux.py           [TEST]     ETA, no-confirmation cancel, retry failed, abort stays resumable
    ├── test_tab_excel_async_load.py [TEST]  Excel loads in a worker thread
    ├── test_tab_excel_mapping.py [TEST]     Identifier 2 and AND/OR survive restore
    ├── test_tab_send_resume.py   [TEST]     Resume continues the same checkpoint; stale list shows an error
    ├── test_tab_send_startup.py  [TEST]     Outlook connects in the background; Refresh reconnects
    └── test_tab_send_test_email.py [TEST]   Test email uses the chosen account, off the window's thread
```

Not present although documents mention them: `resources/icons/`, `resources/default_templates/`
(`README.md:177-179`), a `pytest.ini`, a `.bat` launcher, `HANDOVER.md`, `FILE_INDEX.md`. `.claude/`
is ignored by git (`.gitignore`, added in commit `32ba07c`), so it is not in the repository.

### Dead code (verified by searching every call site)

- **Dead files:** none — every module is imported somewhere.
- **Dead classes:** `ProgressDialog` (`ui/components/dialogs.py:319`, only re-exported),
  `MultiLineInputDialog` (`dialogs.py:414`).
- **Shadowed method:** `ExcelHandler.close()` is defined **twice** (`core/excel_handler.py:35` and
  `:443`). Python keeps the second one, so the first (added in `0c27360`, with its own error
  catching) never runs. The live one also wipes the loaded data — see F1 (verified on dummy data).
- **Dead functions and methods** (defined, never called by the app or its tests):
  - `core/validators.py`: `extract_template_variables`, `validate_identifier`,
    `check_duplicate_identifiers`, `validate_excel_columns`, `validate_file_path`,
    `validate_directory_path`; `check_attachment_size` and `validate_template_variables` are only
    re-exported from `core/__init__.py`.
  - `core/excel_handler.py`: `get_row`, `get_column_values`, `get_unique_values`, `filter_data`,
    `clear_filter`, `sort_data`, `get_row_count` (the "filtered data" feature is unused —
    `filtered_data` is only read by `validate_email_column`).
  - `core/template_engine.py`: `substitute_safe`, `preview_substitution`, `create_sample_data`,
    `substitute_template`; `validate_variables` is used only by the dead `validate_build_config`.
  - `core/attachment_matcher.py`: `match_all_identifiers`, `get_unmatched_files`,
    `get_total_attachment_size`.
  - `core/email_builder.py`: `Email.get_total_recipients`, `Email.get_attachment_count`,
    `Email.to_dict`, `EmailBuilder.build_emails`, `EmailBuilder.validate_build_config`.
  - `core/outlook_sender.py`: `select_account_by_index`, `create_preview_html`.
  - `data/session_manager.py`: `create_state_snapshot`, `export_session`, `import_session`.
  - `data/checkpoint.py`: `clear_checkpoint` (so the checkpoint file is never deleted; a finished
    run is only marked "completed"), `get_progress`.
  - `data/template_storage.py`: `get_template_names`, `rename_template`, `duplicate_template`,
    `export_template`, `import_template`.
  - `data/recipient_lists.py`: `get_list_names`, `rename_list`, `merge_lists`, `get_statistics`
    (`rename_list` and `merge_lists` would also drop the stored emails — harmless only because
    nothing calls them).
  - `utils/logger.py`: `log_exception`, `log_send_event`, `log_matching_event`.
  - `utils/file_utils.py`: `check_network_drive`, `is_valid_path` (both only re-exported),
    `check_path_length`, `get_path_length` (used only by the former), `list_files_with_identifier`
    (and it is **case-sensitive**, unlike the live matcher).
  - `utils/html_converter.py`: `plain_text_to_html`, `wrap_in_html_document`,
    `extract_body_from_html`, `sanitize_html_for_email`, `convert_newlines_to_br`,
    `normalize_html_whitespace`; `escape_html` is used only by the dead `create_preview_html`.
  - `utils/theme_manager.py`: `get_current_theme`.
  - `ui/tab_compose.py`: `is_valid` — the only check that would have refused a template with
    missing columns; nothing calls it.
  - `ui/tab_preview.py`: `validate_all`, `refresh_preview`.
  - `ui/tab_excel.py`: `get_excel_handler`.
  - `ui/components/dialogs.py`: `show_question_cancel`, and the `ProgressDialog` methods.
  - `ui/components/file_list.py`: `add_file`, `remove_file`, `get_file_count`.
  - `ui/components/progress_log.py`: `get_log_text`, `get_entry_count`.
  - `ui/components/rich_text_editor.py`: `set_plain_text`, `get_plain_text`, `insert_text`,
    `insert_html`, `convert_images_to_cid`.
  - `ui/components/tab_navigation.py`: all six `set_previous_* / set_next_*` methods.
- **Dead signals** (emitted, never connected): `TabSend.send_started`, `TabSend.send_completed`,
  `ProgressLog.log_added`, `FileListWidget.file_double_clicked`.
- **Dead constants** in `config.py`: `WINDOW_WIDTH`, `WINDOW_HEIGHT` (`:89-90`),
  `DEFAULT_FONT_FAMILY`, `DEFAULT_FONT_SIZE`, `EDITOR_FONT_FAMILY`, `EDITOR_FONT_SIZE` (`:97-100`),
  `DEFAULT_RECURSIVE_SEARCH`, `ATTACHMENT_FILE_EXTENSIONS` (`:115-118`), `PDF_FILTER` (`:125`),
  `DEFAULT_SUBJECT`, `DEFAULT_BODY` (`:150-157`); `NETWORK_CHECK_TIMEOUT` (`:145`) feeds only the dead
  `check_network_drive`. `README.md:221` documents a `BATCH_SIZE` setting that does not exist.
- **Dead data and parameters:** `Email.body_text` is computed for every email
  (`core/email_builder.py:254-255`) but never used (Outlook receives only `HTMLBody`);
  `check_network_drive(timeout=…)` never uses `timeout`, and its `start_time` is never read;
  `CheckpointManager.start_session(excel_file=…)` is never given a file (both callers,
  `ui/tab_send.py:609` and `:792`, leave it empty); the session-restore prompt reads keys that are
  never written (`selected_indices`, `template_name` — `data/session_manager.py:149,157`);
  unused imports such as `QProgressDialog` in `ui/tab_excel.py:13`.
- **Dead style-sheet rules:** `QPushButton#primaryButton`, `#dangerButton`, `[primary="true"]`,
  `QLabel[heading/subtle/success/warning/error="true"]`, `QLabel#successIndicator/#errorIndicator`
  and `QTableWidget::item[invalid/warning="true"]` (both `.qss` files) — no widget sets those
  names or properties, and Qt cannot apply property selectors to table items anyway.

---

## SECTION 3: FEATURE INVENTORY

Each feature has a worked example ("concrete trace") through the real code. Where the trace showed
something different from what the feature appears to promise, it says **BUG/GAP** and points to
Section 7.

### F1 — Load the recipient Excel file
- **What it does:** reads one worksheet of an `.xlsx`/`.xlsm` file into a list of rows; each row is
  a dictionary *column name → cell value*. The file on disk is never locked or changed.
- **Where:** `ui/tab_excel.py` (`_browse_file` :367, `_load_file` :379, `_start_load` :389,
  `ExcelLoadWorker` :29, `_on_sheet_changed` :465, `_reload_file` :688, `_reload_with_offset` :870,
  drag-and-drop :93-113, `load_file_path` :980); `core/excel_handler.py` (`_open_workbook` :45,
  `load_file` :79, `load_file_with_offset` :184, `_read_data` :132).
- **Input → output:** workbook path, sheet name, header row and first column → column names
  (`tab_excel._columns`) and rows (`tab_excel._data`); a preview of the first 100 rows.
- **User interaction:** Browse…, or drop the file on the tab; Worksheet drop-down; "Data starts at
  Row/Column" + Apply; Refresh.
- **Concrete trace:** the user drops `clients.xlsx` (header in row 1: `Name | Email | PAN`, 3 data
  rows and one blank row) on the tab → `dropEvent` accepts it because the name ends in `.xlsx` →
  `_start_load` disables the buttons and shows "Loading clients.xlsx…" → the worker calls
  `load_file` → the handler first calls `self.close()` (the **second** definition, :443, which also
  empties `data`, `columns` and `file_path`), checks the file exists and ends in `.xlsx/.xlsm`, then
  copies the bytes into memory and opens them with `read_only=True, data_only=True` (formulas give
  their last saved value) → `_read_data(1, 1)` turns row 1 into column names (an empty header cell
  becomes `Column_N`), skips the blank row, turns empty cells into `""` and keeps numbers and dates
  as numbers and dates → 3 rows. On the window thread, `_update_ui_after_load` fills the sheet list,
  `_load_sheet_data` fills the mapping drop-downs (F2), the preview table and the validation label
  (F3), then emits `data_loaded`, so the main window passes the columns to Compose and the rows to
  Recipients (which selects everyone).
- **BUG/GAP found by tracing** (details in Section 7): a sheet chosen in the drop-down is forgotten by
  session restore and profiles (they reload the workbook's *active* sheet, `tab_excel.py:1003`); the
  header-row/column offset is not saved in sessions or profiles and is dropped when switching sheets
  (`:471`); duplicate header names silently lose a column; a workbook whose internal "used range"
  note is wrong loads only part of its rows (verified on dummy data: 1 of 5 rows); a failed load
  empties the handler, after which **Validate Emails** reports every address as valid.
  [Added 03-11-2026, while preparing question Q19: when a workbook was last saved with another sheet
  in view, the Worksheet drop-down shows the first sheet while the sheet in view is read, and Apply
  and Refresh then read the sheet the drop-down shows — G42.]

### F2 — Map columns (To, CC, BCC, Identifier 1, Identifier 2, AND/OR)
- **What it does:** tells the app which column holds the recipient address(es), optional CC and
  BCC, and up to two identifier columns used to find each client's files.
- **Where:** `ui/tab_excel.py` (`_populate_column_combos` :491, `_auto_detect_columns` :520,
  `get_column_mapping` :759, `_restore_column_mapping` :717); `ui/main_window.py`
  (`_on_mapping_changed` :350); `core/email_builder.py` (`set_column_mapping` :136).
- **Input → output:** column names → a mapping `{'to', 'cc', 'bcc', 'identifier', 'identifier2',
  'identifier_logic'}` used by the email builder, the attachment statistics and the recipient table.
- **User interaction:** five drop-downs and two radio buttons; the app pre-selects some on load.
- **Concrete trace:** columns `Name | CC Email | Email | Email ID | PAN` → auto-detection looks for
  "email" first and takes the **first** column whose name contains it → **To = "CC Email"**; for the
  identifier it tries "identifier", then "id" → **Identifier 1 = "Email ID"** (verified on dummy
  data). With no column containing any email word, To stays on the first column (e.g. "Name").
  Every change emits `mapping_changed`; the main window updates the builder, collects every
  distinct identifier value for the Attachments statistics, and re-sends the rows to Recipients
  keeping the current ticks when the row count is unchanged.
- **BUG/GAP:** the auto-detection can pick the wrong columns without saying so (Section 7.4).

### F3 — Check email addresses
- **What it does:** marks invalid addresses red in the preview, counts invalid addresses over all
  rows, and on request lists problems with typo suggestions ("Did you mean …@gmail.com?").
- **Where:** `core/validators.py` (`validate_email_address` :15, `is_valid_email` :48,
  `validate_email_list` :81, `suggest_email_correction` :115); `ui/tab_excel.py`
  (`_populate_preview_table` :548, `_validate_emails` :661); `core/excel_handler.py`
  (`validate_email_column` :404); `config.py:65-83` (typo list).
- **Input → output:** the To column → red cells, "✓ All N emails valid" / "⚠ N invalid email(s)", a
  message listing up to 20 problems.
- **User interaction:** automatic on load; "Validate Emails" button.
- **Concrete trace:** 150 rows, row 121 holds `broken@` → the preview shows rows 1-100 (row 121 is
  not shown) but the count loops over all 150 rows → "⚠ 1 invalid email(s)" and "Showing first 100
  of 150 rows" (pinned by `test_polish.py`). A cell `a@x.com;b@x.com` is valid (each part checked);
  `a@x.com, b@x.com` (comma) is **invalid** (verified). The button's messages say "Row {i+2}",
  which is only the true Excel row when the header is in row 1 and no blank rows were skipped.
- **Note:** validation **never blocks sending**; invalid and blank addresses still go to the Send tab.

### F4 — Export a blank Excel template
- **Where:** `ui/tab_excel.py:893-978`.
- **Trace:** Export Blank Template → Save dialog (default `email_template.xlsx`) → a new workbook with
  sheet "Recipients" (headers Name, Email, CC, Identifier, Custom1, Custom2 in white on blue, two
  example rows with `john@example.com`, `PAN001`…) and an "Instructions" sheet → saved where the user
  chose; message "Template saved to: …".

### F5 — Compose the subject and body with `{Column}` variables
- **What it does:** a subject line and a rich-text (HTML) body in which `{Column Name}` is replaced,
  per recipient, by that row's value.
- **Where:** `ui/tab_compose.py` (subject :113, body editor :145, debounce :52-55 and :310-328,
  variable info :330-354); `ui/components/rich_text_editor.py`; `ui/components/variable_completer.py`;
  `core/template_engine.py` (`substitute` :51).
- **Input → output:** subject text + body HTML → per row: subject and body with values filled in.
- **User interaction:** type; "Insert Variable" drop-downs; type `{` for a pop-up list of columns;
  the line under the editor says "✓ Using N variable(s)" or "⚠ Missing columns: …".
- **Concrete trace:** subject `Reminder for {Client Name}`, row `{'Client Name': 'Shah Traders'}` →
  the pattern `\{([^{}:;]+)\}` finds `Client Name`, it is in the row → "Reminder for Shah Traders".
  `{client name}` (different case) → not found → the email says **"Reminder for {MISSING}"**
  (verified). A value 150000 becomes "150000", 0.18 becomes "0.18", a date becomes
  "2026-04-01 00:00:00", and a computed amount can show as "1234.5600000000002" (all verified).
  Text such as `{ white-space: pre-wrap; }` inside Qt's own HTML is left alone because it contains
  ":" or ";" — the reason column names may not contain ":" or ";".
- **BUG/GAP:** missing or wrongly-cased variables are sent as `{MISSING}` — the warning line is only
  information, nothing stops the send (`TabCompose.is_valid` is dead code); values are not escaped
  for HTML (`A & B <Pvt> Ltd` goes in as raw HTML, verified).

### F6 — Paste an Excel table and insert images in the body
- **Where:** `ui/components/rich_text_editor.py` (`_paste_table_from_clipboard` :501,
  `_extract_and_style_table` :534, `_convert_tsv_to_table` :597, images :637-769, drag-and-drop
  :235-274); `core/outlook_sender.py` (`_process_embedded_images` :370).
- **Trace (image):** the user pastes a screenshot → `_insert_qimage` stores it in the editor as a
  `data:image/png;base64,…` picture. Only when Preview or Send is opened, `_sync_compose_state`
  (`ui/main_window.py:447`) extracts every such picture with a regex and gives it an id
  `image_xxxxxxxx`. At send time each picture is written to a temporary file, attached, given that
  id as its Content-ID, and the `<img>` tag in the body is replaced by `<img src="cid:…" />`, so
  Outlook shows it inline. The temp file is deleted after adding (left behind only if adding fails).
- **Trace (table):** "📋 Table" with cells copied from Excel → the HTML table is stripped of Excel's
  styling and re-styled with a blue header row; tab-separated text is turned into a table instead.

### F7 — Import body text from Word, text or HTML
- **Where:** `ui/tab_compose.py:446-567`.
- **Trace:** Import File… → `letter.docx` → python-docx reads **paragraph text only** (no tables,
  bold or pictures), each non-empty paragraph becomes `<p>…</p>` → Yes = replace the body, No =
  append, Cancel = nothing. A `.txt` is tried as UTF-8, UTF-8-BOM, cp1252, Latin-1. Text is not
  HTML-escaped, so a "<" in the source becomes HTML.

### F8 — Email templates (save / load / delete)
- **Where:** `ui/tab_compose.py:174-280`; `data/template_storage.py`.
- **Trace:** Save As… "GST Reminder" → file `.app_data/templates/GST Reminder.json` with subject,
  body HTML, dates and app version. The file name keeps only letters, digits, space, "-" and "_",
  cut to 50 characters, so "GST/Reminder" and "GSTReminder" are the **same file** (the second save
  asks "Overwrite?" only if that sanitised file exists). Choosing "-- New Template --" and clicking
  Load clears the subject and body without asking.

### F9 — Universal BCC
- **What it does:** one address added as BCC to every email (e.g. a records mailbox).
- **Where:** `ui/tab_compose.py:151-159`, `:404-419`; `ui/main_window.py:391-399`;
  `core/email_builder.py:238-243`.
- **Concrete trace:** the user writes the subject and body, **then** types `records@firm.example` in
  Universal BCC and opens the Send tab → the BCC box has no change signal, and the builder only reads
  it when the subject or body changes → the emails are built **with no BCC** (verified on dummy data:
  `[[], []]`). Any later edit of the subject or body makes it apply. Preview does not show BCC, and
  the test email clears BCC, so the user cannot see this. **BUG** — Section 7.1.

### F10 — Static attachments (same files for everyone)
- **Where:** `ui/tab_attachments.py:97-117`; `ui/components/file_list.py`;
  `core/email_builder.py:260-262`.
- **Trace:** Add Files… (or drag files in) → list with sizes; a missing file shows red; total size
  over 80 % / 100 % of 25 MB shows an orange warning (static files only). Every built email gets the
  full paths. If a file has gone by send time, Outlook cannot attach it → that email fails (F17).

### F11 — Variable attachments matched by identifier
- **What it does:** indexes one folder (optionally with subfolders) and gives each recipient the
  files whose **file name contains** the recipient's identifier text, ignoring case. Two identifier
  columns can be combined with OR (either) or AND (both in the same file name).
- **Where:** `core/attachment_matcher.py` (`scan` :66, `match_identifier` :107,
  `match_multiple_identifiers` :162, `match_identifiers_and` :195, `get_match_statistics` :231,
  `generate_match_report` :342); `core/email_builder.py:264-287`; `ui/tab_attachments.py`
  (browse + auto-scan :259, `ScanWorker` :24, statistics :325, unmatched list :356, Test :375,
  report :392); `utils/file_utils.py` (`scan_directory` :266).
- **Input → output:** folder + identifiers → per recipient a list of file paths; statistics
  "N/M identifiers matched", the list of identifiers with no files, an Excel match report.
- **User interaction:** Browse… (scans immediately), "Include subfolders", Rescan, Test Matching,
  Generate Report.
- **Concrete trace:** folder holds `101_ITR.pdf`, `1010_ITR.pdf`, `C101_GST.pdf`,
  `ABCDE1234F_form16.pdf`, `ram kumar.pdf`, `Shriram Traders.pdf`. Identifier `101` → matches
  **`101_ITR.pdf`, `1010_ITR.pdf` and `C101_GST.pdf`**; identifier `Ram` → matches **`ram kumar.pdf`
  and `Shriram Traders.pdf`** (both verified). With AND and Identifier 2 blank for a row, the builder
  falls back to Identifier 1 alone (`email_builder.py:281`, verified). If the identifier column
  name differs in case from the Excel header, nothing is attached (`email_builder.py:270,276` use
  an exact-case lookup, unlike To/CC/BCC; verified).
- **BUG/GAP:** one client's identifier can pick up other clients' files and nothing warns about a
  file matched by several recipients; in AND mode the statistics count identifiers one by one, not
  the AND result; a Rescan that overlaps a preview or statistics refresh can cache an incomplete
  result (verified: 0 matches cached instead of 2). Section 7.2.

### F12 — Switch static and variable attachments on or off
- **Where:** `ui/tab_attachments.py:74-92`, `:426-463`; `core/email_builder.py:190-199`.
- **Trace:** untick "Enable Dynamic Attachments" → the folder controls grey out → the builder skips
  the matching step → every email goes without client files; the Send tab then warns
  "N recipient(s) have no attachments" (unless static files exist — then everyone "has attachments").

### F13 — Choose recipients
- **Where:** `ui/tab_recipients.py`; `ui/components/recipient_list.py`.
- **Trace:** 5 rows loaded → all ticked. Search "y.com" (applied 250 ms after typing stops) → 2 rows
  shown, buttons read "Select All (2 shown)" → Select None un-ticks only those 2 (pinned by
  `test_recipient_table.py`). Right-click → Copy Selected Emails. The table shows at most 5 columns
  (To and Identifier first).
- **BUG/GAP:** Excel **Refresh** turns a hand-picked selection back into "everyone" (verified:
  `[0, 2]` became `[0, 1, 2, 3]` with the file unchanged). Section 7.3.

### F14 — Saved recipient lists
- **Where:** `ui/tab_recipients.py:111-254`; `data/recipient_lists.py` (`save_list` :54,
  `resolve_selection` :146).
- **Trace:** select A and C → Save Selection… "Mumbai Clients" → `.app_data/recipient_lists/
  Mumbai Clients.json` holds the row numbers **and the emails**. Next month the Excel has a new row on
  top → Load → rows are found again **by email** (case-insensitive), any saved email no longer present
  is listed in a warning (pinned by `test_recipient_lists.py`). Old lists without emails fall back to
  row numbers. The same email on two rows selects both rows.

### F15 — Preview each email
- **Where:** `ui/tab_preview.py`; `core/email_builder.py` (`get_preview_data` :383).
- **Trace:** entering tab 5 → `_update_preview` flushes Compose, extracts images, and passes the rows
  and ticked row numbers → the drop-down lists "1. a@x.com" (or Name (Email), Identifier - Email, or a
  custom `{Name} <{Email}>` format) → for the chosen row it shows Subject, To, the body rendered by Qt
  (not by Outlook), and the attachment list with sizes; over 25 MB shows a warning. Arrow keys move
  between recipients. Re-entering the tab keeps the same recipient.
- **GAP:** the preview never shows CC or BCC (`cc_display` is created but never filled,
  `tab_preview.py:149-151`), and it uses a second copy of the matching code (`get_preview_data`) that
  must be kept identical to `build_email` by hand.

### F16 — Connect to Outlook
- **Where:** `ui/tab_send.py` (`OutlookInitWorker` :100, `start_outlook_init` :370,
  `_on_outlook_init_done` :386, `_refresh_accounts` :412); `core/outlook_sender.py` (`initialize`
  :99, `_get_fresh_outlook` :143, `_load_accounts` :159, `is_online` :255, `detect_new_outlook` :41).
- **Trace:** the window appears first; 0 ms later the init worker starts COM on its own thread and
  connects to `Outlook.Application` (generated wrapper first, plain dispatch as fallback), lists the
  accounts, and selects the **first** account → the Send tab shows "✓ Online" (or "⚠ Outlook is in
  offline mode") and enables Start Sending. On failure it checks for New Outlook (`olk.exe` running, or
  the `UseNewOutlook` registry value) and explains how to switch back; Refresh retries.

### F17 — Send the batch through Outlook
- **Where:** `ui/main_window.py` (`_update_send_tab` :473); `ui/tab_send.py` (`_update_summary` :472,
  `_start_sending` :582, `_launch_send` :616, `SendWorker` :39, `_on_progress` :704, `_on_finished`
  :719); `core/outlook_sender.py` (`send_email` :280, `send_emails_batch` :440).
- **Input → output:** the ticked rows → one Outlook email each, sent (or opened on screen in
  "Preview mode") at the chosen interval; a coloured log, progress bar and time estimate.
- **User interaction:** Send from (account), Delay between emails (1-30 s, default **1 s** because
  `int(1.5)` = 1), Preview mode, ▶ Start Sending (asks "Are you sure you want to send N emails?"),
  ⬛ Cancel (no question).
- **Concrete trace:** 5 rows ticked, row 3 has a locked PDF → entering tab 6 builds 5 Email objects
  (row numbers 0-4) and the summary shows "Recipients: 5, With attachments: 5" → Start → Yes → the
  chosen account is selected, a checkpoint is started for rows [0,1,2,3,4] (without the Excel file
  name) → the worker sends: for each email a fresh Outlook connection, `CreateItem`, the sending
  account set through a raw COM call (if that fails, only a log warning — the email goes from the
  default account), To/CC/BCC joined with "; ", subject, body (images converted), attachments; row 3's
  locked file cannot be attached → that email is **not sent** and is recorded as failed ("Not sent -
  could not attach: …"); the other 4 are sent; 1 s pause between emails, checked every 0.1 s for
  Cancel → "Complete with Errors: Sent 4, Failed 1" and a "↻ Retry 1 Failed" button.
- **BUG/GAP:** "sent" means *handed to Outlook* (it goes to the Outbox; offline Outlook sends later);
  blank or invalid addresses are not stopped before sending, and three blank-address rows in a row
  stop the whole batch with "Outlook may be unavailable" (verified); the account choice is not
  remembered between launches. Section 7.

### F18 — Send a test email to yourself
- **Where:** `ui/tab_send.py:519-580`.
- **Trace:** "📧 Send Test Email First" → the account in the drop-down is selected → "This will send
  the FIRST email to yourself: To: <account address>, Subject: [TEST] …" → Yes → a copy of the first
  ticked email (with that client's attachments) goes to the account's own address with CC and BCC
  removed, from a worker thread. It is optional; nothing requires it before Start Sending.

### F19 — Checkpoint, Resume and Retry failed
- **Where:** `data/checkpoint.py`; `ui/tab_send.py` (`set_emails` :450-470, `_resume_sending` :667,
  `_retry_failed` :777, `_on_finished` :719-775).
- **Trace:** a run of rows [0..99] is cancelled after 40 → checkpoint `status: in_progress`,
  completed [0..39] → the run is "suspended" (resumable) → whenever the Send tab is entered later,
  "Resume Previous" appears with "Found incomplete session: 40/100 sent" → Resume sends **only** the
  rows still pending, continuing the same checkpoint (pinned by tests). Retry Failed starts a new
  checkpoint for the failed rows only.
- **BUG/GAP (verified on dummy data):** Resume and Retry **do not ask for confirmation**, and Resume
  matches by row number only — after loading a *different* Excel file it sent rows 2-4 of the other
  campaign. A run made in Preview mode that is cancelled records the displayed emails as done, so a
  later real-send Resume **skips them** (rows 0-1 never sent). Clicking Start Sending instead of
  Resume after a cancel starts a fresh run that re-sends the first part. Section 7.1.
  [Added 03-11-2026: Resume Previous also comes back while a run is going, and clicking it sends the
  pending emails twice — G43.]

### F20 — Session auto-save and restore; New Session
- **Where:** `data/session_manager.py`; `ui/main_window.py` (`_setup_auto_save` :324,
  `_get_session_state` :490, `_restore_session_state` :509, `_restore_data_dependent_state` :551,
  `_check_restore_session` :563, `_new_session` :617, `closeEvent` :661).
- **Trace:** every 180 s (paused while sending) and on close, the state — Excel path, mapping,
  subject, body, Universal BCC, static files, folder + subfolders flag, toggles, ticked row numbers,
  account — is written atomically to `.app_data/sessions/current_session.json`. Next start: "Restore
  Previous Session? File: clients.xlsx, Template: Custom, Recipients: **0 selected**, Last saved: 2
  hour(s) ago" → Yes → the workbook reloads in the background (its *active* sheet, row 1 headers), then
  the mapping and the ticked **row numbers** are applied.
- **BUG/GAP (verified):** the prompt always says "0 selected" and "Template: Custom" (it reads keys
  that are never written); ticks are restored by row number, so after rows move in Excel they land on
  other clients (`[A, C]` came back as `[NEW, B]`); the account and the sheet are not restored.

### F21 — Profiles (save / load settings to a shareable file)
- **Where:** `ui/main_window.py:691-919`.
- **Trace:** Profile › Save Profile… (Ctrl+Shift+S) → JSON with Excel path + mapping, subject, body,
  BCC, static files, folder, toggles and account. Load Profile… → "This will replace your current
  settings. Continue?" → Yes → the Excel (if found) loads with its mapping; subject/body/BCC are
  replaced; static files are replaced **only if at least one listed file exists**.
- **BUG/GAP (verified):** loading a profile whose static list is empty (or whose files are all
  missing) **keeps the previous campaign's static attachments** (`LAST_MONTH_notice.pdf` stayed);
  a profile without a folder keeps the old folder; the account in the profile is never applied.

### F22 — Remembered preferences
- **Where:** `utils/file_utils.py:32-56`; `ui/components/dialogs.py:107-125`;
  `ui/main_window.py:72-82`, `:681-686`; `utils/theme_manager.py:41-75`.
- **Trace:** after picking a file in Excel's Browse…, its folder is saved under `last_dir/excel` in
  `.app_data/preferences.json`, and the next Browse… opens there; the window's size, place and
  maximised state are saved on close and restored at start.

### F23 — Theme (System / Light / Dark)
- **Where:** `utils/theme_manager.py`; `ui/main_window.py:131-186`; `resources/*.qss`.
- **Trace:** View › Theme › Dark → `style_dark.qss` is applied to the whole app and "dark" saved;
  "System" reads `AppsUseLightTheme` from the Windows registry (light if it cannot be read).

### F24 — Log file
- **Where:** `utils/logger.py`; `config.py:130-134`.
- **Trace:** every start writes "Starting Advanced Email Tool v1.8.0" to `.app_data/logs/app.log`;
  each email's result is logged at DEBUG level by the checkpoint ("Checkpoint: sent #3 to …"), with
  client addresses; the file rolls over at 5 MB, keeping 3 old files. INFO and above also go to the
  console (invisible when started without one).

### F25 — Navigation, shortcuts and step checkmarks
- **Where:** `ui/main_window.py` (`_setup_shortcuts` :245, `_update_step_indicators` :220);
  `ui/components/tab_navigation.py`.
- **Trace:** Ctrl+1…Ctrl+6 jump to a tab, Ctrl+Tab / Ctrl+Shift+Tab move, ← / → change the previewed
  recipient (only on tab 5); "< Previous" / "Next >" at the bottom of each tab; tab titles gain " ✓"
  when Excel has rows, Compose has text, Attachments has files or a folder, and at least one
  recipient is ticked. Ctrl+N new session, Ctrl+S save session, Ctrl+Q quit, Ctrl+Shift+S/O profiles,
  Ctrl+Shift+V paste table, Ctrl+B/I/U formatting.

---

## SECTION 4: DATA FLOW

```
WHERE DATA ENTERS
  Excel workbook (.xlsx/.xlsm, Browse… or drag-drop) ──► read as bytes into memory (file never locked)
  Attachment folder (Browse…) ─────────────────────────► list of (path, file name, size)  [folder files never opened]
  Static files (Add Files… / drag-in) ─────────────────► list of paths
  Subject, body, images, tables, Universal BCC (typed, pasted, imported from .docx/.txt/.html)
  Saved JSON: session, templates, recipient lists, profiles, checkpoint, preferences (.app_data/)

TRANSFORMATIONS
  workbook bytes ─► openpyxl (read-only, saved values) ─► header row → column names; rows → {column: value}
       └─► mapping (To/CC/BCC/Id1/Id2/AND|OR)          (blank rows dropped; empty cells → "")
  rows ─► Recipients tab: ticked row numbers
  folder ─► scan (one level, or all subfolders) ─► file index
  for each ticked row number i (main_window._update_send_tab):
      row ─► To / CC / BCC lists  (split on ";")  + Universal BCC
          ─► subject, body  ({Column} → str(value); unknown → "{MISSING}")
          ─► attachments = static files (if on) + index files whose NAME CONTAINS Id1/Id2 (if on)
          ─► Email(row_index = i)
  Email ─► Outlook COM: CreateItem → sending account → To/CC/BCC → Subject → HTMLBody
          (pictures → temp files → inline attachments with Content-ID) → Attachments.Add
          → Send()  (or Display() in Preview mode)

WHERE DATA EXITS
  ─► Outlook Outbox → the client's mailbox (copy in the sending mailbox's Sent Items — Outlook's own
     behaviour, not checked here)
  ─► Send tab log (on screen only) and .app_data/logs/app.log (addresses and results)
  ─► .app_data/checkpoints/send_checkpoint.json (row numbers sent / failed)
  ─► .app_data/sessions/current_session.json, templates/*.json, recipient_lists/*.json,
     preferences.json
  ─► Files the user asks for: blank Excel template, match report (.xlsx), profile (.json)
  ─► Clipboard: "Copy Selected Emails", "Copy Log", "Copy Path"
```

Two facts matter most for safety: (1) the email list is **built once when the Send tab is opened**
(and again on every later visit), and the send uses that list — changes made on other tabs during a
send do not affect it; (2) every link between a checkpoint, a session or a saved list and the Excel
data is a **row number** (0 = first data row), except saved lists, which also store emails.

---

## SECTION 5: BUSINESS RULES AND DOMAIN LOGIC

### 5.1 Recipients and addresses
| # | Rule | Where |
|---|---|---|
| R1 | An address is valid if it matches `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` after trimming spaces (so no Unicode letters, no "'" in the local part) | `core/validators.py:33` |
| R2 | Several addresses in one cell are separated by **";" only**; a cell is valid only if every part is valid; empty parts are ignored | `core/validators.py:64-74`; `core/email_builder.py:315-332` |
| R3 | Typo suggestions for 17 common misspelt domains (gmial.com → gmail.com, rediffmal.com → rediffmail.com …) | `config.py:65-83`; `core/validators.py:115-136` |
| R4 | Invalid or blank addresses are **shown, never blocked**: they still reach the Send tab | `ui/tab_excel.py:611-620` (count only); `ui/tab_send.py:582-614` (no check) |
| R5 | The To, CC and BCC columns are looked up ignoring case; the identifier columns and the template variables are **case-sensitive** | `core/email_builder.py:104-112, 221-236` vs `:270, :276`; `core/template_engine.py:80` |
| R6 | Universal BCC is added to every email unless the same text is already in that row's BCC list (exact-case comparison) | `core/email_builder.py:238-243` |
| R7 | The test email goes to the selected account's own address, with "[TEST] " before the subject and CC/BCC removed; attachments kept | `ui/tab_send.py:553-559` |

### 5.2 Excel reading
| # | Rule | Where |
|---|---|---|
| R8 | Only `.xlsx` and `.xlsm` (by file-name ending) | `core/excel_handler.py:101-102, :213-214`; `ui/tab_excel.py:111` |
| R9 | The workbook is read from an in-memory copy, read-only, using **saved values** of formulas (a formula never calculated by Excel reads as blank) | `core/excel_handler.py:45-59` |
| R10 | Header row = "Data starts at Row" (1-1000); first column = "Column" (1-100); nothing left of that column is read | `ui/tab_excel.py:179-191`; `core/excel_handler.py:150-168` |
| R11 | An empty header cell becomes `Column_N` (N counted from the first read column); a header of `0` also becomes `Column_N`; numeric headers become text ("2026") | `core/excel_handler.py:160-163` (verified) |
| R12 | A row whose read cells are all empty is skipped; other empty cells become `""` | `core/excel_handler.py:170-177` |
| R13 | Sheet names are matched ignoring case; with no sheet chosen, the workbook's **active** sheet is read | `core/excel_handler.py:61-69, 108-114` |
| R14 | Auto-detected To column: first column whose lower-case name contains `email`, `e-mail`, `mail`, `to`, `recipient` (in that order); Identifier 1: contains `identifier`, `id`, `code`, `pan`, `gstin`, `client` | `ui/tab_excel.py:520-546` |
| R15 | The preview table shows at most 100 rows; validation counts all rows | `ui/tab_excel.py:548, 611-627` |

### 5.3 Templates and variables
| # | Rule | Where |
|---|---|---|
| R16 | A variable is `{` + any text without `{ } : ;` + `}`; text that starts or ends with a space is not a variable | `core/template_engine.py:28, 30-45` |
| R17 | Values are inserted with Python's `str()`: numbers lose Excel's formatting (150000, 0.18), dates show as `YYYY-MM-DD HH:MM:SS`, empty cells as nothing | `core/template_engine.py:80-85` (verified) |
| R18 | An unknown variable is replaced by the literal text `{MISSING}` and logged as a warning | `core/template_engine.py:56, 86-88` |
| R19 | Values are not HTML-escaped when put into the body | `core/template_engine.py:85` (verified) |
| R20 | The same subject/body template applies to every recipient; images and tables are the same for all | `core/email_builder.py:291-292` |
| R21 | Template and list names keep only letters, digits, space, "-", "_", cut to 50 characters | `data/template_storage.py:49-52`; `data/recipient_lists.py:49-52` |

### 5.4 Attachments
| # | Rule | Where |
|---|---|---|
| R22 | A file matches an identifier if the identifier text (trimmed) appears **anywhere in the file name**, ignoring case; the folder name does not count | `core/attachment_matcher.py:122-134` |
| R23 | OR (default): files matching either identifier, each file once; AND: files whose name contains both — **only when the row has both identifiers**, otherwise the one present is used alone | `core/attachment_matcher.py:162-229`; `core/email_builder.py:279-284` |
| R24 | Subfolders are scanned only when "Include subfolders" is ticked (default off); all file types are indexed; unreadable entries are skipped silently | `ui/tab_attachments.py:156-159`; `utils/file_utils.py:266-322` |
| R25 | Static attachments come first, then matched files; each email gets every matching file (no limit) | `core/email_builder.py:257-289` |
| R26 | Size warning threshold 25 MB (`MAX_ATTACHMENT_SIZE_MB`): static total over 80 % / 100 % (Attachments tab), per-recipient total over 100 % (Preview) — a warning only | `config.py:47-50`; `ui/tab_attachments.py:465-480`; `ui/tab_preview.py:428-438` |
| R27 | **An email whose attachment cannot be added is not sent**; it is a failure "Not sent - could not attach: <names> (file may be open, moved, or renamed)" | `core/outlook_sender.py:340-356` |
| R28 | Paths longer than 240 characters get the Windows long-path prefix when scanning | `utils/file_utils.py:59-90` |

### 5.5 Sending
| # | Rule | Where |
|---|---|---|
| R29 | Start Sending asks "Are you sure you want to send N emails?" (or "display"); Resume and Retry Failed **do not ask** | `ui/tab_send.py:592-600` vs `:667-696`, `:777-800` |
| R30 | Default delay 1 s (`int(SEND_INTERVAL=1.5)`), choice 1-30 whole seconds, none after the last email | `config.py:44`; `ui/tab_send.py:224-226`; `core/outlook_sender.py:520-523` |
| R31 | Cancel never asks and takes effect within about 0.1 s (between emails) | `ui/tab_send.py:653-665`; `core/outlook_sender.py:533-542` |
| R32 | The batch stops itself after **3 failures in a row** (`MAX_CONSECUTIVE_FAILURES`), whatever the cause | `core/outlook_sender.py:436-438, 511-518` |
| R33 | A cancelled or self-stopped run stays resumable; a run that reaches the end is marked completed, even with failures | `ui/tab_send.py:728-733` |
| R34 | Resume sends the planned rows not yet marked sent **or failed**; Retry Failed resends only rows marked failed, as a new checkpoint | `data/checkpoint.py:273-292`; `ui/tab_send.py:777-800` |
| R35 | Preview mode opens each email in Outlook instead of sending, and is recorded in the checkpoint exactly like a send | `core/outlook_sender.py:359-361`; `ui/tab_send.py:65-73` |
| R36 | The email goes from the account chosen in "Send from"; at start-up it is the first account Outlook lists; if setting it fails the default account is used with only a log warning | `core/outlook_sender.py:177-179, 309-318` |
| R37 | Friendly messages for Outlook errors: −2147467260 / "operation aborted" → security prompt; RPC / −2147023174 → restart Outlook; "not registered" → not installed; unknown/invalid recipient → address rejected | `core/outlook_sender.py:20-38` |
| R38 | New Outlook is detected by a running `olk.exe` or registry value `HKCU\Software\Microsoft\Office\16.0\Outlook\Preferences\UseNewOutlook = 1` | `core/outlook_sender.py:41-70` |

### 5.6 Saving state
| # | Rule | Where |
|---|---|---|
| R39 | Session auto-save every 180 s, skipped while sending; also on close | `config.py:56`; `ui/main_window.py:324-329, 677-679` |
| R40 | A session is offered for restore only if it has an Excel path, subject, folder, BCC, static files or visible body text | `data/session_manager.py:99-123` |
| R41 | Session, checkpoint, recipient-list and `file_utils` preference writes are atomic (`.tmp` then replace); template files and the theme preference are written directly | `utils/file_utils.py:16-29`; `data/template_storage.py:103-104`; `utils/theme_manager.py:72-73` |
| R42 | All user data lives in `.app_data\` **inside the app's own folder** ("portable app style"), not in the user's profile | `config.py:20-31` |
| R43 | Log: DEBUG and above to `app.log`, 5 MB × 3 backups; INFO and above to the console | `config.py:130-134`; `utils/logger.py:58-76` |

### 5.7 Window and limits
| # | Rule | Where |
|---|---|---|
| R44 | Window opens at 1100 × 750, minimum 900 × 600, then remembers its last geometry | `config.py:91-94`; `ui/main_window.py:66-82` |
| R45 | Default theme follows Windows (light if unknown) | `config.py:103-106`; `utils/theme_manager.py:77-96` |
| R46 | Lists in message boxes are capped: 20 validation issues, 100 unmatched identifiers, 50 recipients without attachments, 10 missing list emails | `ui/tab_excel.py:678`; `ui/tab_attachments.py:363`; `ui/tab_send.py:506`; `ui/tab_recipients.py:158` |

No GST or tax rules are coded in this app: it does not compute any figure; its "domain" is who gets
which document.

---

## SECTION 6: EDGE CASES AND DEFENSIVE CODE

Handled today (each read in the code; many are pinned by the tests in brackets):

- **Excel open in Excel while loaded** — read from an in-memory copy, so Excel can still save, and
  Refresh picks the saved change up (`test_excel_handler.py`).
- **Slow or big workbook / OneDrive file** — loaded in a worker thread with the buttons disabled and
  "Loading …" shown (`test_tab_excel_async_load.py`); a second load while one runs is ignored.
- **Missing file / wrong type / not a valid workbook / no permission** — plain messages ("File not
  found", "File must be .xlsx or .xlsm format", "Invalid Excel file format", "Permission denied -
  file may be open in another program") (`core/excel_handler.py:96-130`).
- **Headers not in row 1 / data not in column A** — offsets (R10). **Empty header cells** →
  `Column_N`. **Blank rows** skipped. **Empty cells** → `""`.
- **Several addresses in a cell** (";"), **typos in common domains**, **invalid addresses beyond the
  preview's 100 rows** (`test_polish.py`).
- **CSS inside the body HTML** is not mistaken for variables (R16) — a bug found on day one
  (`6e824fa`).
- **Attachment cannot be added** (open, moved, renamed) → that email is not sent and is retryable
  (`test_outlook_sender_attachments.py`).
- **Outlook not running / not installed / New Outlook** → the window still opens; Start Sending stays
  disabled; New Outlook explained; Refresh reconnects (`test_tab_send_startup.py`).
- **Outlook objects dying when their thread ends** → a fresh connection per call and per thread
  (`test_outlook_thread_safety.py`).
- **Outlook hangs mid-batch** → stops after 3 failures in a row, resumable (`test_send_batch.py`).
- **Cancel during a long delay** → within 0.1 s (`test_send_batch.py`).
- **Crash or power cut while saving** → atomic writes for session, checkpoint, lists, preferences
  (`test_persistence.py`); a corrupt session file reads as "no session".
- **Interrupted run** → resume continues the same checkpoint, never re-sends rows already marked
  (`test_checkpoint.py`, `test_tab_send_resume.py`); a resume whose rows are not in the current list
  refuses with an explanation.
- **Rows moved in Excel** → saved lists find clients by email (`test_recipient_lists.py`).
- **Filter active** → Select All/None/Invert act on the visible rows only (`test_recipient_table.py`).
- **Folder changed** → Rescan clears the old match results (`test_attachment_matcher.py`).
- **Report file open in Excel** → "Report Not Saved … close it and try again" instead of a false
  success.
- **Long paths (> 240 characters)** → long-path prefix when scanning.
- **Text files in other encodings** → tries UTF-8, UTF-8-BOM, cp1252, Latin-1.
- **python-docx missing** → a warning instead of a crash.
- **Empty session after New Session** → not offered for restore (`test_new_session_reset.py`).
- **Typing lag with pictures in the body** → debounced, pictures extracted only when building
  (`test_compose_debounce.py`).

Error catching: almost every file operation and every Outlook call is wrapped in `try/except`,
logged, and turned into a message or a failed-email result; the four worker threads catch everything
and report back to the window. Exceptions: there is no last-resort handler for an error inside a
button handler (see Section 7.6), several `except: pass` blocks hide errors (`main.py:80`,
`outlook_sender.py:428`, colour lookups in `tab_excel.py:582, 640`), and `scan_directory` returns an
empty result for *any* error (`utils/file_utils.py:317-322`), which looks the same as an empty folder.

**Rating: MODERATE.** The send pipeline itself is now well defended (July 2026 work), but the
inputs that decide *who gets what* — identifier matching, Excel structure, restore/resume
bookkeeping, settings that silently stay from an earlier campaign — are only lightly checked.

---

## SECTION 7: EDGE CASES NOT HANDLED (GAPS AND VULNERABILITIES)

Severity: **HIGH** = a client could get the wrong document, a wrong or missing email, or an email
could go to the wrong person; **MEDIUM** = wrong content, lost work or a misleading message;
**LOW** = cosmetic or unlikely. "Verified" = reproduced by running the app's code on dummy data;
"code reading" = traced in the code but not run.

### 7.1 Who receives what — sending, resuming, copies
| # | Gap | Severity | How confirmed |
|---|---|---|---|
| G1 | **Resume sends to whatever rows sit at the same numbers.** The checkpoint stores only row numbers; the Excel file name is never recorded (`excel_file` left empty, `ui/tab_send.py:609-612`), and Resume compares nothing. After loading another campaign's Excel and clicking Resume Previous, rows 2-4 of the *other* file were sent. | HIGH | Verified |
| G2 | **Resume and Retry Failed send without any confirmation** (`ui/tab_send.py:667-696`, `:777-800`); only Start Sending asks. The Resume button reappears every time the Send tab is opened while an old run is unfinished, even days later. | HIGH | Code reading + verified (no dialog opened) |
| G3 | **Preview mode counts as sent.** A Preview-mode run that is cancelled records the displayed emails as completed; a later Resume with Preview mode off sends only the rest — the displayed ones are **never sent** (rows 0-1 skipped). | HIGH | Verified |
| G4 | **Universal BCC typed last is ignored.** The BCC box has no change signal; the builder reads it only when the subject or body changes (`ui/main_window.py:391-399`; `ui/tab_compose.py:157-159`). Emails were built with no BCC until the subject was edited again. Preview never shows BCC and the test email clears it, so this is invisible. | HIGH (records copy missing) | Verified |
| G5 | **Start Sending after a cancel re-sends the first part.** It starts a fresh checkpoint for all ticked rows; the "N emails" in the confirmation is the full number. | MEDIUM | Code reading (`ui/tab_send.py:582-614`) |
| G6 | **Blank or invalid addresses are not stopped.** Invalid ones reach Outlook; a blank one fails before Outlook is used ("No recipients specified"); **three in a row stop the whole batch** with "Outlook may be unavailable" (verified); a name typed in the email column (e.g. "Ramesh Kumar") is passed to Outlook, which may resolve it against the address book *(inferred — Outlook behaviour, needs an office PC)*. Comma-separated addresses are passed as one string. | MEDIUM | Verified (blank, comma); inferred (name resolution) |
| G7 | **Sending account not remembered.** Saved in sessions and profiles but never restored; each start selects the first Outlook account. If setting the account fails, the email silently goes from the default account (warning in the log only, `core/outlook_sender.py:309-318`). | MEDIUM | Verified (not restored); code reading (fallback) |
| G8 | **"Sent" means handed to Outlook.** Offline Outlook keeps emails in the Outbox; the app still reports success. The online check is shown once, at connection time. | MEDIUM | Code reading |
| G9 | **No duplicate check**: the same address on two ticked rows gets two emails. | LOW | Code reading |
| G10 | **Closing the window during a send** asks "Are you sure?" and then closes while the send thread is still running; Qt normally aborts the process then, and the email in flight may be sent but not recorded (sent again on Resume). | LOW | *Inferred — needs an office PC* |
| G43 | **Resume Previous clicked while a run is still going sends the pending emails twice.** Entering the Send tab calls `set_emails()` (`ui/main_window.py:473-488`), which shows Resume Previous whenever the checkpoint is "in progress" — also during a run (`ui/tab_send.py:463-470`). `_resume_sending` and `_launch_send` (`:667-696`, `:616-651`) start a second sender without checking that one is running, and both send the rows still pending. | HIGH (clients emailed twice) | Verified — a dummy list of 5, fake Outlook, 1-second gap: after 2 sends, Preview and back to Send, then Resume Previous: clients 3-5 each got two emails. Found 03-11-2026 by a consistency check, after the review |

### 7.2 Attachment matching
| # | Gap | Severity | How confirmed |
|---|---|---|---|
| G11 | **One client's identifier can pick up another client's files.** Matching is "file name contains the text": `101` also attaches `1010_ITR.pdf` and `C101_GST.pdf`; `Ram` attaches `Shriram Traders.pdf`. Nothing warns that one file matched several recipients, or that an identifier is a substring of another. Safe in practice only when identifiers are long and unique (e.g. a full PAN or GSTIN). | HIGH (confidentiality) | Verified |
| G12 | **AND with one identifier blank silently becomes "Identifier 1 only"** (`core/email_builder.py:279-284`). | MEDIUM | Verified |
| G13 | **Identifier column lookup is case-sensitive** while To/CC/BCC are not: after a restore or profile where the header's case changed, every recipient gets no matched files. The Send tab warns "N recipient(s) have no attachments" only when no static file is attached (G41). | MEDIUM | Verified |
| G14 | **A Rescan can leave stale "no files" results.** The scan clears the result cache at its start, then fills the file list gradually in a worker thread; any lookup during the scan (Preview, Send tab, statistics after a mapping change) is cached with the partial list and kept after the scan ends. Verified: 0 matches cached where 2 files exist. A recipient could then go with **some** files missing, which the summary does not flag. | HIGH (when it happens) | Verified (simulated timing) |
| G15 | **Statistics ignore AND mode.** "N/M identifiers matched" counts each identifier alone, so it can say "all matched" while AND matching finds nothing for a recipient. | MEDIUM | Code reading |
| G16 | **Unreadable or disconnected folder = empty folder.** `scan_directory` returns nothing on any error, so a dropped network share shows "Found 0 files" rather than an error. | MEDIUM | Code reading (`utils/file_utils.py:317-322`) |
| G17 | **Subfolder tick not applied until Rescan**; the session then saves the ticked state although the index was built without subfolders. | LOW | Code reading |
| G18 | **No per-recipient size block**: emails over 25 MB are only warned about in Preview; the mail server may reject them later. | LOW | Code reading |
| G41 | **Missing client files are hidden by static files.** The Pre-Send Summary counts *any* attachment (`ui/tab_send.py:481-498`), so when a cover letter or other static file is attached, every email "has attachments" and recipients whose own files were not found are not flagged. | HIGH | Code reading |

### 7.3 Selection, sessions and profiles
| # | Gap | Severity | How confirmed |
|---|---|---|---|
| G19 | **Excel Refresh ticks everyone again** (the data-loaded signal selects all after the mapping restore kept the old ticks). A curated selection `[0, 2]` became `[0, 1, 2, 3]` with the file unchanged. | HIGH | Verified |
| G20 | **Session restore ticks row numbers, not clients**: after a row was added on top, `[A, C]` came back as `[NEW, B]`. | HIGH | Verified |
| G21 | **The restore prompt misreports**: "Recipients: 0 selected" and "Template: Custom" always — it reads `selected_indices` and `template_name`, but the session writes `selected_recipients` and no template name (`data/session_manager.py:149,157` vs `ui/main_window.py:494-507`). | MEDIUM | Verified |
| G22 | **Loading a profile keeps the previous campaign's static attachments** when the profile lists none (or all are missing) — `LAST_MONTH_notice.pdf` stayed. Same for the folder. | HIGH | Verified |
| G23 | **Sheet and header offset are not saved** in sessions or profiles; restore reads the workbook's active sheet with headers in row 1. | MEDIUM | Code reading (`ui/tab_excel.py:980-1004`) |
| G24 | **One session and one checkpoint file per app folder.** Two copies of the app open at once, or two users sharing one app folder, overwrite each other's session and checkpoint (a user could be offered, and resume, someone else's run). | HIGH if the app folder is shared — *inferred, depends on how the office runs it* | Code reading |

### 7.4 Excel input
| # | Gap | Severity | How confirmed |
|---|---|---|---|
| G25 | **Some workbooks load only their first rows.** In read-only mode openpyxl trusts the "used range" note stored in the file; a file written by another program with a wrong note loaded **1 of 5 rows** with no warning. Files saved by Excel itself are fine; exports from other software are the risk. | HIGH (silently missing clients) | Verified |
| G26 | **Duplicate header names**: the later column overwrites the earlier one in every row. | MEDIUM | Verified |
| G27 | **Formulas never calculated by Excel read as blank** (saved values only). | MEDIUM | Verified |
| G28 | **Auto-detected mapping can be wrong**: "CC Email" became To and "Email ID" became Identifier 1; with no email-like column, To = the first column. | MEDIUM | Verified |
| G29 | **A failed load leaves the old rows on screen but empties the handler**, so "Validate Emails" then says "All N email addresses are valid!". | LOW | Verified (handler empty) + code reading |
| G30 | `.xls` and `.csv` are not accepted; codes typed as numbers lose leading zeros in Excel itself (00123 → 123, which then also matches 1234…). | LOW | Code reading |
| G42 | **The Worksheet drop-down can name a different sheet from the one read.** Choosing a workbook reads the sheet that was in view when it was last saved in Excel (`load_file` → `workbook.active`), but the drop-down is refilled and shows the first sheet (`ui/tab_excel.py:447-463`). Apply and Refresh read the sheet the drop-down shows (`:694-715`, `:870-890`), so the list changes to another sheet's clients without a message. A session restore or a profile has the same mismatch (`:1003`). | HIGH (another sheet's clients, without warning) | Verified — a dummy workbook saved with its second sheet "Feb" in view: "Jan" in the drop-down while Feb's clients were listed; Apply switched to Jan's. Found 03-11-2026, after the review |

### 7.5 Email content
| # | Gap | Severity | How confirmed |
|---|---|---|---|
| G31 | **`{MISSING}` can be sent to clients**: a variable whose name differs from the column (case, spaces) is replaced by the text `{MISSING}`; the warning under the editor never blocks a send (`TabCompose.is_valid` is never called). | HIGH | Verified |
| G32 | **Amounts, percentages and dates lose Excel formatting**: 150000 (not 1,50,000), 0.18 (not 18 %), 2026-04-01 00:00:00 (not 01-04-2026), and float noise such as 1234.5600000000002. | MEDIUM | Verified |
| G33 | **Values are not HTML-escaped** (`A & B <Pvt> Ltd`): text in angle brackets can vanish or become markup in the body. Imported .docx/.txt text and pasted TSV tables are not escaped either. | LOW-MEDIUM | Verified |
| G34 | Pictures whose HTML uses single quotes, or other formats, are not converted to inline attachments and may not display. | LOW | Code reading |

### 7.6 Crashes, errors and environment
| # | Gap | Severity | How confirmed |
|---|---|---|---|
| G35 | **No last-resort error handler.** With PyQt5 an unhandled error inside a button or signal handler normally ends the app at once; started without a console, nothing is shown or logged. Standard 13's `sys.excepthook` lines are absent. | MEDIUM | Code reading; *the exact crash behaviour needs an office PC* |
| G36 | **User data inside the app folder** (`.app_data`, R42): sessions, templates, lists, checkpoint, preferences and a log with client addresses. If the folder is shared or OneDrive-synced, all users share them and sync can lock files during atomic replaces. Standard 13 puts these in `%LOCALAPPDATA%`. | MEDIUM-HIGH — *depends on how the office runs it* | Code reading |
| G37 | **Classic Outlook only.** New Outlook cannot be automated (detected and explained); the app stops working on any PC moved to New Outlook. | HIGH (business continuity) | Code reading + toolkit Standard 12 |
| G38 | **Unpinned packages** (`>=` in `requirements.txt`): two PCs can run different versions; `pytest` is not listed. | LOW-MEDIUM | Read |
| G39 | **Rotating log shared by several processes** (two instances or users) can fail to roll over on Windows. | LOW | *Inferred* |
| G40 | **Test Email stays clickable during a batch**, so two Outlook sends can overlap. | LOW | Code reading |

### 7.7 Silent-bug scan (Process step 9)
- **Loop-variable capture in lambdas:** none found — `ui/main_window.py:250` uses `lambda idx=i:`
  correctly; the old per-row check-box lambdas were removed in `7446087`.
- **Mutable default arguments:** none (defaults are `None`).
- **Off-by-one:** "Row {i+2}" in validation messages (`core/excel_handler.py:424-439`) is wrong with a
  header offset or skipped blank rows; Preview's "N." numbers are positions, not Excel rows.
- **String vs number:** identifiers and values go through `str()` — floats keep their noise, numbers
  lose leading zeros.
- **`is` vs `==`:** no misuse found.
- **Stale values:** Universal BCC (G4); match cache during a rescan (G14); a profile keeping old
  static files and folder (G22); the shadowed `ExcelHandler.close()` (Section 2).
- **Thread safety:** the attachment matcher is shared by the scan thread and the window without a
  lock (G14); the Excel handler is shared by the load thread and the window (protected only by
  disabling buttons); checkpoint files are written by the send thread and read by the window
  (atomic writes keep this safe).

### 7.8 "What would break if …" (Process scenario analysis)
- **…the app is started from another folder?** Nothing: paths come from the code's own folder
  (`config.py:21`, `utils/theme_manager.py:34`).
- **…a different Windows user runs it?** They share the same `.app_data` if they share the folder
  (G24, G36); preferences and window size are shared too.
- **…the network share drops mid-operation?** A scan reports 0 files (G16); during a send, each
  email whose attachment cannot be read fails and is retryable; three in a row stop the batch.
- **…it runs a second time on the same data?** Everyone is emailed again — only the last run's
  checkpoint is remembered, and only by row number.
- **…two copies run at once?** Shared session and checkpoint files (G24); possible log rollover errors.
- **…another operating system?** The window opens, but there is no Outlook COM: sending is impossible.
- **…a library is upgraded?** PyQt5 is frozen at 5.15 (Qt 5.15 support ended in May 2025 — toolkit
  evidence); openpyxl's read-only behaviour (G25) is long-standing; a corrupt pywin32 wrapper cache is
  handled by the plain-dispatch fallback.
- **…Outlook is set to New Outlook?** Sending stops (G37).

### 7.9 Repository documents that disagree with the code
- `QUICKSTART.md:88-91` table says `pan001_report.pdf` does **not** match `PAN001`; the code and the
  line below it say matching ignores case.
- `QUICKSTART.md:107` says variable names are **case-insensitive**; they are case-sensitive
  (`README.md:203` is right).
- `README.md:211-225` shows `APP_VERSION = "1.1.1"`, `SEND_INTERVAL = 3`, `BATCH_SIZE = 50`; the code
  has 1.8.0, 1.5 (used as 1 s) and no batch size.
- `README.md:177-179` lists `resources/icons/` and `resources/default_templates/` — absent.
- `README.md:29` says Python 3.10+; nothing in the repo records the Python the office actually uses.
- `README.md:198` advises "Run the tool as administrator" for COM errors.
- `CHANGELOG.md` stops at 1.6.0; 1.7.0, 1.7.1 and 1.8.0 are only in commit messages.
- `ROADMAP.md:40-183` still lists styling, error handling, help, New Outlook warning and dark mode as
  "Not started" or "Planned" — all done; its own "Implementation Order" marks them done.
- `README.md` keyboard table omits Ctrl+Q, Ctrl+Shift+S/O (profiles) and Ctrl+Shift+V.
- Commit `bc73127` says "Column name matching works regardless of case" — true for To/CC/BCC, sheets
  and filters, **not** for template variables or identifier columns.

---

## SECTION 8: DESIGN DECISIONS (INFERRED)

| Decision | Likely reason | Confidence |
|---|---|---|
| **Outlook through COM** rather than SMTP or Microsoft Graph | Uses the office's existing Outlook mailboxes with no passwords or app registration, keeps a copy in Sent Items, and lets "Preview mode" open real Outlook drafts. `ROADMAP.md:194` parks "Graph API (New Outlook)" as "Major rewrite, avoid if possible" and `:196` "Gmail/SMTP support" as later | HIGH |
| **PyQt5** for the window | Mature, rich-text editor and tables built in; chosen in January 2026 before the toolkit's PySide6 rule (toolkit D35, Oct 2026), which allows an existing PyQt5 app to stay as it is | HIGH |
| **openpyxl, read-only, from an in-memory copy** | Read-only is fast; the in-memory copy (July 2026, `fe04ce9`) came from a real problem: Excel could not save while the tool held the file (WinError 32) | HIGH |
| **Identifier = "file name contains"** | Client files are named inconsistently (`PAN001_report.pdf`, `2024_PAN001_final.xlsx` in `README.md:116-120`); a contains-test needs no naming convention. Case was ignored from 14 Jan after "CAPS names didn't match Proper case identifiers" (`bc73127`) — so names are used as identifiers in practice | HIGH (reason); MEDIUM (names in use) |
| **Two identifiers with AND/OR** | Some clients need two keys (e.g. PAN + period, or a name + a code) — added the same afternoon as multiple identifiers (`ebcd168`, `1ca0b44`) | MEDIUM |
| **Data in `.app_data` next to the code** ("portable app style") | Moved there on day one from the user's home folder (`9884d2c`, CHANGELOG 1.0.1); most likely so the whole tool can be copied or synced as one folder | MEDIUM |
| **Six numbered tabs in a fixed order** | Mirrors the real job: list → letter → documents → who → check → send; the step checkmarks (v1.8.0) reinforce it | HIGH |
| **Row numbers as the link between checkpoint, session and data** | Simplest at first; saved lists were later upgraded to emails (`0c27360`) after "inserting/deleting/re-sorting rows in Excel silently selected different clients" — sessions and checkpoints were not | HIGH |
| **Atomic JSON writes** | July 2026 hardening (`4a278bf`): "a crash mid-write can no longer destroy state" | HIGH |
| **Fresh Outlook connection for every call** | First added on day one to fix "CreateItem" failures from a stale connection (`6e824fa`, CHANGELOG 1.0.2), extended in July when Outlook objects created in the start-up thread died with that thread (`f5b9511`) | HIGH |
| **Window first, slow work later in worker threads** | July 2026 (`3cb4ca7`, `fe04ce9`): the window used to freeze while Outlook or a big OneDrive workbook loaded | HIGH |
| **Attachment failure blocks the email** | July 2026 (`0c27360`): "an email whose attachment cannot be added is no longer sent and reported as success" — a client must never get the email without the document | HIGH |
| **Cancel without confirmation** | "every second spent reading one is another email going out" (`ui/tab_send.py:656-658`) | HIGH |
| **Stop after 3 failures in a row** | "a wedged Outlook would otherwise grind through every remaining email" (`core/outlook_sender.py:436-437`) | HIGH |
| **Dark mode and a custom blue style** | Owner preference in January 2026 (v1.3–1.4); predates the toolkit's light-only house look, which exempts apps kept on PyQt5 | HIGH |
| **Many unused helper functions** | The first commit (9,432 lines in one go, 1 January 2026) was generated as a complete framework; later work used only part of it | MEDIUM |

**Evident iterations and refactors:** the variable pattern changed three times on day one (`6e824fa`,
`ebcd168`); `TabPreview` was briefly broken by a button wired to a missing method (`fabf464`, fixed 3
minutes later in `32fb053`); `0a61744` imported `is_valid_email` before it existed (fixed 5 minutes
later in `c012def`); the Send Test Email button called a missing method for two days (`ebcd168` →
`55b92ad`); the variable pop-up was rewritten to stop stealing focus (`32ba07c`); the recipient
table was rebuilt for speed (`7446087`). No commented-out code blocks remain.

### Pattern consistency (Process step 8)
| Pattern | Followed by | Broken by |
|---|---|---|
| Case-insensitive column lookup | To/CC/BCC (`email_builder.py:221-236`), sheets and filters (`excel_handler.py`), mapping restore (`tab_excel.py:115-123`), recipient table | Template variables (`template_engine.py:80`), identifier columns (`email_builder.py:270,276`), Preview's To and display formats (`email_builder.py:397`, `tab_preview.py:306-335`) |
| Atomic JSON writes | Session, checkpoint, recipient lists, `file_utils.save_preference` | Template files (`template_storage.py:103`), theme preference (`theme_manager.py:72`), profiles and exports |
| Clients identified by email rather than row number | Saved recipient lists | Session restore, checkpoint/resume, retry |
| Error results as `(ok, message)` tuples | Excel handler, matcher, storage classes, sender | `scan_directory` (silent empty result), some `except: pass` blocks |
| Heavy work in worker threads | Excel load, folder scan, Outlook connection, test send, batch send | Building all emails when entering Preview/Send (window thread) |
| One shared preferences file | `file_utils` helpers and `ThemeManager` both merge keys | `ThemeManager` reads/writes without `encoding=` and non-atomically |
| Windows-only modules imported inside functions with a fallback | `win32com`/`pythoncom` (`outlook_sender.py`), `winreg` (`theme_manager.py`, `detect_new_outlook`), `main._check_dependencies` checks pywin32 only on Windows | `file_list._open_file_location` runs `explorer` without a platform check (fails harmlessly elsewhere) |
| Two copies of the matching logic | `build_email` and `get_preview_data` are identical today | Any change must be made twice |

### Re-export pattern
`core/__init__.py`, `data/__init__.py`, `utils/__init__.py`, `ui/__init__.py` and
`ui/components/__init__.py` re-export names with `__all__` lists. Most code imports from the
sub-modules directly (`from core.excel_handler import ExcelHandler`), so the re-exports mostly keep
dead names alive (Section 2). These files use relative imports (`from .logger import …`), which the
toolkit's Standard 9 forbids for new code.

---

## SECTION 9: DEPENDENCIES AND ENVIRONMENT

| Package | In `requirements.txt` | Imported where | Purpose |
|---|---|---|---|
| PyQt5 | `>=5.15.0` | everywhere in `ui/`, `main.py`, `data/session_manager.py` (QTimer) | Window, widgets, threads, timers. Licence GPL v3 or commercial (toolkit evidence B); fine for an internal tool that is not distributed |
| openpyxl | `>=3.1.0` | `core/excel_handler.py`, `ui/tab_excel.py`, `core/attachment_matcher.py` | Read recipient workbooks (read-only); write the blank template and the match report |
| pywin32 | `>=306` | `core/outlook_sender.py` (`win32com.client`, `pythoncom`), `main.py` (check only) | Drive classic Outlook through COM — Windows only, imported inside functions |
| python-docx | `>=1.1.0` | `ui/tab_compose.py:506` (`import docx`) | Import Word paragraphs; optional (a warning if missing) |
| pytest | **not listed** | `tests/` | Test suite (with off-screen Qt) |
| Standard library | — | `winreg` (theme, New Outlook), `subprocess` (`tasklist`, `explorer`), `tempfile`, `base64`, `uuid`, `json`, `logging`, `re`, `io` | — |

- **Python version:** not recorded. `README.md:29` says 3.10+; the code uses nothing newer than 3.8.
  The tests ran here on 3.13. The toolkit's standard (Python 3.14 with the py launcher) is not yet
  applied to this app — *what the office PCs have needs an office PC*.
- **Operating system:** Windows 10/11 (`README.md:28`). On other systems the window opens but cannot
  send. Windows-only calls: COM, `winreg`, `tasklist`, `explorer`, the `\\?\` long-path prefix.
- **External programs:** classic **Microsoft Outlook (desktop)**, configured with at least one account,
  running or startable; **not** New Outlook. Excel is not needed by the app (only by the user to edit
  files).
- **File-system assumptions:** the app's own folder must be **writable** (it creates `.app_data` at
  start-up); Excel files and attachment folders may be local, OneDrive or network paths; paths are
  stored as typed (absolute), so profiles shared between PCs work only where the same paths exist.
- **Set-up on a fresh PC (as documented today):** install Python (3.10+ per README) → `pip install -r
  requirements.txt` → open Outlook once → `python main.py` (`QUICKSTART.md:5-8`). There is no
  installer, no `.bat` and no desktop-shortcut step.
- **OS-specific import handling:** consistent — every Windows-only module is imported inside a
  function and guarded (Section 8 table), except the harmless `explorer` call.
- **Run the tests:** `python -m pytest` from the project folder (the tests add the folder to the import
  path themselves; there is no `pytest.ini`). Note: the tests create `.app_data/` (logs, templates
  folder) inside the project folder, because only some paths are redirected to temporary folders.

---

## SECTION 10: UI/INTERFACE DOCUMENTATION

**Main window** (`ui/main_window.py`): title "Advanced Email Tool v1.8.0"; menu bar **File** (New
Session Ctrl+N, Save Session Ctrl+S, Exit Ctrl+Q), **Profile** (💾 Save Profile… Ctrl+Shift+S,
📂 Load Profile… Ctrl+Shift+O, ℹ️ Profile Info), **View › 🎨 Theme** (System (Auto), ☀️ Light,
🌙 Dark — tick marks), **Help › About**; six tabs "1. Excel" … "6. Send" that gain " ✓" when done;
a status bar with a hint for each tab. The style is a custom blue-accented "Windows" look (light) or a
dark grey look (dark). Start-up: the window appears, then "Restore Previous Session?" if a meaningful
session exists, while the Send tab connects to Outlook in the background.

**Tab 1 — Excel** (`ui/tab_excel.py`). Top box "Excel File": file name label (grey "No file
selected"), **Browse…**, **Refresh** (disabled until a file is loaded); "Worksheet:" drop-down and a
row count; "Data starts at: Row [1] Column [1] **Apply**" and **Export Blank Template**. Below, side by
side: "Column Mapping" (To Email *, CC, BCC, a line, Identifier 1, Identifier 2, "Match logic: (•) OR
(either) ( ) AND (both)", grey help text, **Validate Emails**) and "Data Preview" (green "✓ All N emails
valid" or red "⚠ N invalid email(s)", "Showing first 100 of N rows", a table with invalid cells in red).
Bottom: **Next >**. Dropping an `.xlsx/.xlsm` anywhere on the tab loads it.

**Tab 2 — Compose** (`ui/tab_compose.py`). Top bar: "Template:" drop-down ("-- New Template --" +
saved names), **Load**, **Save**, **Save As…**, **Delete**, **Import File…**. "Subject Line" box:
text field ("Enter subject with {Variables} from Excel columns..."), an "Insert Variable" drop-down and
**Insert** (disabled with a tooltip until Excel is loaded). "Email Body" box: toolbar (font, size, B,
I, U, A colour, H highlight, • list, 1. list, ← ↔ → alignment, 📋 Table, 🖼️ Image ▾), the editor,
"Insert Variable:" drop-down + **Insert**, **View HTML** toggle (shows the HTML source below; the editor
is read-only while shown). Then "Universal BCC (added to all emails):" field, a small line "✓ Using N
variable(s) …" / "⚠ Missing columns: …" / "No variables used (static email)", and **< Previous /
Next >**. Typing "{" opens a pop-up list of columns.

**Tab 3 — Attachments** (`ui/tab_attachments.py`). Top: ☑ Enable Static Attachments, ☑ Enable Dynamic
Attachments. Left "Static Attachments (sent to all recipients)": a list with sizes (missing files in
red), "N files", "Total: X MB", **Add Files…**, **Remove**, **Clear All**; right-click: Open File
Location, Copy Path, Remove. Right "Variable Attachments (matched by identifier)": Folder (read-only
field) + **Browse…**, ☐ Include subfolders, **Rescan**, a busy bar while scanning, "Found N files (X MB).
Use 'Rescan' to refresh.", "N/M identifiers matched (P%)", **Generate Report**, a red "⚠ N
identifier(s) have NO matching files **View List**" line, and a "Test Matching" box (field + **Test**,
Enter also works, results listed below). An orange size warning at the bottom; **< Previous / Next >**.

**Tab 4 — Recipients** (`ui/tab_recipients.py`). "Saved Lists:" drop-down ("Name (count)"), **Load**,
**Save Selection…**, **Delete**. A search field + column filter; the table (tick box + up to 5 columns);
**Select All / Select None / Invert** (relabelled "(N shown)" while filtering) and "N of M selected";
right-click: Select/Deselect All Visible, Copy Selected Emails; a bold summary "N of M recipients
selected" with a second pair **Select All / Clear Selection**; **< Previous / Next >**.

**Tab 5 — Preview** (`ui/tab_preview.py`). **← Previous**, a recipient drop-down, **Next →**, "3 / 50";
"Display as:" (Email only / Name (Email) / Identifier - Email / Custom… with a format field), **Refresh
Preview**; "Email Preview" (Subject, To, the body as rendered by Qt) beside "Attachments" ("N
attachment(s): S static, M matched", 📎/🔗 list with sizes, an orange size warning); a validation line
(never filled — `validate_all` is unused); **< Previous / Next >**.

**Tab 6 — Send** (`ui/tab_send.py`). "Send Configuration": "Send from:" (address (name)) + **Refresh**;
"Delay between emails: [1] seconds"; ☐ Preview mode (display in Outlook, don't send). "Pre-Send
Summary": Recipients: N · With attachments: N · "⚠ N without attachments" or "✓ All have attachments",
a red line with **View List**, **📧 Send Test Email First**. Status line ("Ready: N emails to send",
"Sending to X (13/200)… — about 12 min left") and the Outlook state ("⏳ Connecting to Outlook…",
"✓ Online", "⚠ Outlook not available — click Refresh to retry"). "Progress": a coloured, time-stamped
log, a progress bar, **Auto-scroll: ON**, **Copy Log**, **Clear**. Bottom: **▶ Start Sending**,
**⬛ Cancel**, **↻ Retry N Failed** (only after failures), **Resume Previous** (only with an unfinished
checkpoint); **< Previous**.

**Dialogs:** standard Windows file/folder pickers (start in the last folder used for that purpose);
Yes/No questions (restore session, new session, overwrite, delete, load profile, send, test email);
information/warning/error boxes; the template/list name input box; the import choice (Yes = replace,
No = append, Cancel).

**Typical workflow:** open the app → (restore the last session or start fresh) → Excel: Browse, check
the mapping and the validation line → Compose: load a template or write one with variables → Attachments:
add common files, choose the client-files folder, read the matched/unmatched figures → Recipients:
untick clients not to be mailed → Preview: step through a few → Send: check the summary, send a test to
yourself, Start Sending, watch the log; Retry failed or Resume if interrupted.

*(No screenshots were possible in this session; the descriptions above come from the layout code.)*

---

## SECTION 11: RECONSTRUCTION BLUEPRINT

> **The author is keeping this app — no rebuild is planned** (adoption, 03-11-2026). This section is
> kept because the audit format requires it. Read item 4 as a menu of possible future **change
> requests**; each one is the author's decision, made through the Brief and a Change Request
> (pipeline Part 3, Template 2), never quietly in code.

1. **Foundation (if ever rebuilt):** Windows 10/11, the office's Python, classic Outlook; folders as
   today (`core/`, `data/`, `ui/`, `utils/`) plus `config/`, `tests/` and a `pytest.ini`; a windowless
   `.bat` launcher (Standard 13); user data in `%LOCALAPPDATA%` (Standard 13) or a per-user area —
   *the author's call* (Section 8 records why the data sits in the app folder today).
2. **Build order:** Excel reader (F1) → mapping (F2) and address checks (F3) → template engine (F5) →
   attachment matcher (F11) → email builder (F9, F10, F12) → Outlook sender (F16, F17) → checkpoint
   (F19) → window tabs in workflow order (F13-F15, F18) → persistence (F8, F14, F20-F22) → polish
   (F4, F6, F7, F23-F25).
3. **Priority:** essential — F1, F2, F5, F9, F10, F11, F16, F17, F19; important — F3, F13, F14, F15,
   F18, F20; nice to have — F4, F6, F7, F8, F12, F21-F25.
4. **Known improvements** (each respects Section 8; none replaces a choice recorded there):
   - *Identifier matching (keeps "contains", chosen for messy file names):* add an **overlap check**
     before sending — list every file matched by more than one recipient and every identifier that is
     contained in another identifier — and offer an optional whole-word match. (G11, G15)
   - *Resume/Retry (keeps the checkpoint):* store each planned row's email and identifier plus the
     Excel file's name and size in the checkpoint, refuse a resume that does not match, ask for
     confirmation, and never count Preview-mode runs as sent. Saved lists already use emails this way.
     (G1-G3, G5)
   - *Selection and restore:* restore sessions and Refresh by email like saved lists; save the sheet,
     header offset and account; make profiles replace or clear every setting they cover; name the sheet actually read in the Worksheet drop-down. (G19-G23, G7, G42)
   - *Pre-send gate:* before Start Sending, block (or ask about) blank/invalid addresses, `{MISSING}`
     variables, recipients with no client files (counted separately from static files), and duplicates;
     show CC/BCC in Preview. (G4, G6, G9, G31, G41)
   - *Excel reading:* call openpyxl's `reset_dimensions()` before reading in read-only mode, refuse
     duplicate headers, warn about blank formula results. (G25-G27)
   - *Value formatting:* use the cell's Excel number format (or a per-column format) for amounts,
     percentages and dates. (G32)
   - *Robustness:* Standard 13's error hook in `main.py`; a scan error shown as an error; pinned
     package versions; `pytest` in a dev list. (G16, G35, G38)
   - *Outlook dependence (Section 8: COM chosen on purpose):* the trade-off is stated honestly — any
     route that survives New Outlook (Graph or SMTP) is the "major rewrite" the roadmap wants to avoid.
     A third option is to keep COM and add an early, clear warning when a PC switches to New Outlook
     (already partly there) and to track Microsoft's dates for classic Outlook. (G37)
5. **Estimated complexity (AI-assisted, per feature):** F1 MODERATE · F2 SIMPLE · F3 SIMPLE ·
   F4 SIMPLE · F5 MODERATE · F6 COMPLEX · F7 SIMPLE · F8 SIMPLE · F9 SIMPLE · F10 SIMPLE ·
   F11 MODERATE · F12 SIMPLE · F13 MODERATE · F14 MODERATE · F15 MODERATE · F16 MODERATE ·
   F17 COMPLEX · F18 SIMPLE · F19 COMPLEX · F20 MODERATE · F21 MODERATE · F22 SIMPLE · F23 SIMPLE ·
   F24 SIMPLE · F25 SIMPLE.
6. **Suggested Skills:** *outlook-com-sending* (fresh connection per thread, block on attachment
   failure, stop after N failures, friendly COM errors); *excel-reading-without-locks* (in-memory
   read-only load, `reset_dimensions()`, header offsets); *identifier-file-matching* (contains-match
   plus an overlap report); *resumable-batch-checkpoint* (identity by email and file fingerprint,
   atomic writes, suspend vs complete); *qt-worker-thread-pattern* (window first, worker reports back,
   controls disabled while busy).

---

## SECTION 12: CHANGELOG ARCHAEOLOGY (FROM GIT HISTORY)

All 28 commits are on **`main`** (the session branch `claude/determined-carson-1sl8q4` points to the
same commit). There are no unmerged branches, no deleted files and no renamed files. Commits from
14 January 2026 on carry "Co-Authored-By: Claude" lines (Opus 4.5, later Fable 5): the app was built
with AI help throughout. Times are India time.

### 12A. Development timeline

**Phase 1 — Initial build and day-one fixes (1 January 2026)**
| Commit | Time | What changed | Why / what it reveals |
|---|---|---|---|
| `d8e17d6` | 13:09 | Initial commit: 34 files, 9,432 lines — the whole architecture (core/data/ui/utils), six tabs, Outlook COM, checkpoint, sessions, templates, lists | Generated as a complete framework in one go; many helpers were never wired in (Section 2). Data then lived in `~/.advanced_email_tool` |
| `6b54a17` | 13:23 | Removed comments from `requirements.txt` | Tidying |
| `9884d2c` | 13:28 | Data folder moved from the home folder to `.app_data` next to the code; file-dialog filters added (`ALL_FILES_FILTER` was missing — CHANGELOG 1.0.1) | "Portable app style" — the start of R42 |
| `252b676` | 13:46 | `.gitignore`: `*.app_data` | Keep user data out of git |
| `6e824fa` | 13:57 | `.gitignore` fixed to `.app_data/`; Outlook `EnsureDispatch` + a fresh connection per email; a stricter variable pattern that skips CSS | Real failures: "CreateItem" on a stale COM connection; Qt's `{ white-space: pre-wrap; }` was being replaced as a variable (CHANGELOG 1.0.2) |
| `fabf464` | 14:39 | Header row/column offset; Import File (.docx/.txt/.html); Preview display formats; Export Blank Template | Real workbooks do not start at A1 |
| `32fb053` | 14:42 | Added the missing `TabPreview._refresh_current` | The previous commit wired a button to a method that did not exist (the tab could not be built) |
| `ebcd168` | 15:26 | Identifier 2 (OR), Pre-Send Summary, unmatched-identifiers warning, keyboard shortcuts, richer restore prompt, Send Test Email; the variable pattern widened to `[^{}:;]+` | Clients need two keys; the restore prompt read `selected_indices`/`template_name`, which were never written (G21 starts here); the test-email button called a method that did not exist yet |
| `1ca0b44` | 15:37 | AND/OR logic | Some files must contain both keys |
| `ac2fb22` | 15:40 | README, QUICKSTART, CHANGELOG; version 1.1.1 | Documentation written when matching was still case-sensitive (Section 7.9 leftovers) |
| `96fa60f` | 16:38 | `python-docx>=1.1.0` added | Imported two hours earlier (`fabf464`); the code tolerates its absence |

**Phase 2 — Rich content, look and comfort (1-4 January 2026)**
| Commit | Date | What changed | Why / what it reveals |
|---|---|---|---|
| `f70dac1` | 1 Jan 22:12 | Paste Excel table, insert images (inline CID attachments), ROADMAP; v1.2.0 | Reminder emails carry tables and screenshots; attachment-add failures were then only logged |
| `0a61744` | 2 Jan 08:57 | Light and dark style sheets, ThemeManager, tooltips, red invalid emails, New Outlook check at start-up; version jumped 1.2.0 → 1.4.0 | Imported `is_valid_email` before it existed (start-up broke until `c012def`); New Outlook already a worry |
| `c012def` | 2 Jan 09:02 | `is_valid_email` added | Fix for the above |
| `55b92ad` | 3 Jan 09:27 | Profiles; ";"-separated addresses valid; `get_selected_account` added (test email had crashed for 2 days); v1.5.0 | Real use: cells with two addresses; colleagues share settings |
| `60e570a` | 4 Jan 07:49 | `{` autocomplete in subject, body and custom preview format; v1.6.0 | Typos in variable names were a problem |
| `32ba07c` | 4 Jan 17:44 | Pop-up no longer steals focus (`Qt.Tool`, QObject base); `.claude` in `.gitignore` | The first version's event filter could not work; Claude Code in use from now on |

**Phase 3 — Fixes from real use (14 January 2026)**
| Commit | Time | What changed | Why / what it reveals |
|---|---|---|---|
| `bc73127` | 14 Jan 14:36 | Case-insensitive file matching, sheet names, To/CC/BCC columns, filters | "CAPS names didn't match Proper case identifiers" — client **names** are used as identifiers. Variables and identifier columns were left case-sensitive (G13, G31) |
| `a56ea66` | 14 Jan 15:05 | `pythoncom.CoInitialize()` in `initialize` and `_get_fresh_outlook` | COM failed in the send thread |

**Phase 4 — Workflow comfort (3 February 2026)**
| Commit | Time | What changed | Why / what it reveals |
|---|---|---|---|
| `0e2be04` | 3 Feb 08:33 | Previous/Next bars, static/dynamic toggles, auto-scan + "Rescan", Excel "Refresh" keeping the mapping, closing the workbook before reload, status-bar hints; v1.7.0 | File-locking complaints began (properly fixed in July) |

**Phase 5 — Trust and robustness overhaul with tests (5 July 2026, eight commits in ten hours)**
| Commit | Time | What changed | Why / what it reveals |
|---|---|---|---|
| `0c27360` | 11:36 | "8 trust bugs" + the first 32 tests: rescan clears the cache; mapping changes keep the selection; checkpoint tracks real row numbers, cancel stays resumable, resume continues instead of restarting (duplicates); attachment failure blocks the email; restore keeps Identifier 2 and AND/OR; New Session really resets; test email uses the chosen account in a thread; saved lists store emails; v1.7.1 | Each was a real "the tool lied to me" moment. The added `ExcelHandler.close()` is shadowed by the older one |
| `fe04ce9` | 11:45 | Workbook read from an in-memory copy; all loads in a worker thread; restore applies mapping/selection after the data arrives; missing Excel explained | Excel could not save while the tool held the file (WinError 32); OneDrive workbooks froze the window |
| `3cb4ca7` | 16:04 | Window first; Outlook connects in a worker; New Outlook detection moved after a failed connect; Refresh re-queries / reconnects; restore prompt after first paint | Start-up froze, and the COM probe could launch Outlook |
| `4a278bf` | 20:46 | Instant cancel (no question, sliced sleep), in-flight recipient + ETA, stop after 3 failures, Retry Failed, friendly COM errors, atomic writes, in-memory checkpoint, QTimer auto-save paused while sending | Cancel could take 30 s; a stuck Outlook ground through every email; the old auto-save read the window from another thread |
| `1c2e18c` | 20:49 | Debounced typing (300 ms); pictures extracted only when building | Typing lagged with pasted images |
| `7446087` | 20:53 | Recipient table with tick items; debounced search; Select All/None/Invert act on the visible rows | Searching "smith" then Select All used to select every client |
| `63c6697` | 21:08 | Remembered folders and window; drag-and-drop; tab checkmarks; preview keeps its place; real size warning; validation over all rows; inline test matching; honest report errors; fewer pop-ups; docs say case-insensitive; v1.8.0 | Polish after the fixes; the docs were only partly corrected (Section 7.9) |
| `f5b9511` | 21:13 | `is_online` and account loading use a fresh per-thread connection; the init worker CoInitializes | The threaded start-up made "Error checking status" appear (COM objects died with their thread) |

### 12B. File evolution map
| File | Created | Changed in | How its role changed |
|---|---|---|---|
| `ui/main_window.py` | `d8e17d6` | 13 later commits (most of all) | Grew from tab host to the hub of all cross-tab wiring, sessions, profiles, shortcuts, theme and checkmarks |
| `ui/tab_excel.py` | `d8e17d6` | `fabf464` `ebcd168` `1ca0b44` `0a61744` `bc73127` `0e2be04` `0c27360` `fe04ce9` `63c6697` | + offsets, export, Identifier 2, AND/OR, validation colours, refresh with mapping restore, worker-thread loads, drag-drop |
| `ui/tab_compose.py` | `d8e17d6` | `fabf464` `f70dac1` `0a61744` `60e570a` `0e2be04` `0c27360` `1c2e18c` `63c6697` | + import, images, autocomplete, reset, debounce |
| `ui/tab_send.py` | `d8e17d6` | `ebcd168` `0a61744` `0e2be04` `0c27360` `3cb4ca7` `4a278bf` `f5b9511` | + summary, test email, resume rewrite, init worker, retry, ETA, circuit-breaker handling |
| `core/outlook_sender.py` | `d8e17d6` | `6e824fa` `f70dac1` `55b92ad` `a56ea66` `0c27360` `3cb4ca7` `4a278bf` `f5b9511` | From a plain sender to a hardened one: fresh connections, images, blocking attachment failures, New Outlook check, batch safety |
| `config.py` | `d8e17d6` | `9884d2c` `ac2fb22` `f70dac1` `0a61744` `55b92ad` `60e570a` `63c6697` | Data folder moved; version bumps; theme settings |
| `core/email_builder.py` | `d8e17d6` | `ebcd168` `1ca0b44` `f70dac1` `bc73127` `0e2be04` `63c6697` | + second identifier, AND, images, case-insensitive To/CC/BCC, toggles, sizes |
| `core/excel_handler.py` | `d8e17d6` | `fabf464` `bc73127` `0e2be04` `0c27360` `fe04ce9` | + offsets, case-insensitive sheets, close before reload, in-memory loading |
| `core/attachment_matcher.py` | `d8e17d6` | `ebcd168` `1ca0b44` `bc73127` `0c27360` `63c6697` | + OR/AND, case-insensitive, cache cleared on scan, honest report result |
| `ui/tab_preview.py` | `d8e17d6` | `fabf464` `32fb053` `60e570a` `0e2be04` `63c6697` | + display formats, autocomplete, keeps place, real size warning |
| `ui/tab_attachments.py` | `d8e17d6` | `ebcd168` `0a61744` `0e2be04` `0c27360` `63c6697` | + unmatched warning, toggles, auto-scan, reset, inline test |
| `ui/components/recipient_list.py` | `d8e17d6` | `bc73127` `0c27360` `7446087` | Rebuilt for speed and filter-aware selection |
| `data/checkpoint.py` | `d8e17d6` | `0c27360` `4a278bf` | From a count to real row numbers, suspend, in-memory cache, atomic |
| `data/session_manager.py` | `d8e17d6` | `ebcd168` `0c27360` `4a278bf` | + prompt info, empty-session guard, atomic save, QTimer auto-save |
| `data/recipient_lists.py` | `d8e17d6` | `0c27360` `4a278bf` | + emails and resolve-by-email, atomic save |
| `ui/components/rich_text_editor.py` | `d8e17d6` | `f70dac1` `60e570a` `63c6697` | + tables, images, autocomplete, remembered folder |
| `core/validators.py` | `d8e17d6` | `c012def` `55b92ad` | + `is_valid_email` with ";" lists |
| `core/template_engine.py` | `d8e17d6` | `6e824fa` `ebcd168` | Variable pattern changed twice on day one, then stable |
| `utils/file_utils.py` | `d8e17d6` | `4a278bf` `63c6697` | + atomic JSON, preferences |
| `main.py` | `d8e17d6` | `0a61744` `3cb4ca7` `63c6697` | New Outlook check added, then moved out; background start |
| `ui/components/dialogs.py`, `file_list.py` | `d8e17d6` | `63c6697` | Remembered folders; drag-in |
| `ui/components/variable_completer.py` | `60e570a` | `32ba07c` | Focus fix |
| `ui/components/tab_navigation.py` | `0e2be04` | — | — |
| `utils/theme_manager.py`, `resources/*.qss` | `0a61744` | — | — |
| **Never changed since `d8e17d6`:** `core/__init__.py`, `data/__init__.py`, `data/template_storage.py`, `ui/__init__.py`, `ui/components/__init__.py`, `ui/components/progress_log.py`, `utils/__init__.py`, `utils/html_converter.py`, `utils/logger.py` | | | Verified: none of them imports anything added later (e.g. `utils/__init__.py` does not re-export the later `write_json_atomic` or preference helpers, which are imported from `utils.file_utils` directly) |

### 12C. Logic and rule evolution
- **Variable pattern:** `\{([^}]+)\}` (everything, CSS included) → letters/digits/_/space only (13:57)
  → anything except `{ } : ;` (15:26). Discovered in real use; never made case-insensitive.
- **Matching:** one identifier, case-sensitive → two identifiers OR → AND option (all on 1 Jan) →
  case-insensitive (14 Jan). Always "contains".
- **Addresses:** single address → ";" lists (3 Jan).
- **Attachment failure:** logged and sent anyway → email blocked and retryable (5 Jul).
- **Checkpoint:** count-based → real row numbers; cancel "interrupted" → resumable; resume restarted a
  new session (duplicates) → continues the same one (5 Jul). Never tied to a file or to emails.
- **Selection:** every data push selected all → mapping changes keep the selection (5 Jul); Select
  All with a filter selected everyone → visible rows only (5 Jul).
- **Saving:** direct writes → atomic for most files; auto-save on a background timer → window-thread
  timer, paused while sending (5 Jul).
- **Outlook:** `Dispatch` once → `EnsureDispatch` + fresh per email (day 1) → CoInitialize per call
  (14 Jan) → fresh per thread for every call (5 Jul).
- **Data folder:** home folder → app folder (day 1, never revisited).

### 12D. Edge cases discovered in production (bug-fix commits)
| Commit | What broke | Fix | Patch or proper? | Similar cases still open |
|---|---|---|---|---|
| `6e824fa` | CSS blocks replaced as variables; CreateItem failing on a stale connection | Stricter pattern; fresh connection per email | Proper | Column names with ":" or ";" cannot be variables |
| `32fb053`, `c012def`, `55b92ad` | Crashes from methods/functions called before they existed | Added them | Patch | No automated tests existed until July |
| `55b92ad` | "a@x;b@x" flagged invalid | ";" lists | Proper | Commas still invalid (G6) |
| `bc73127` | CAPS vs Proper-case identifiers didn't match | Case-insensitive | Proper for files and To/CC/BCC | Variables and identifier columns still case-sensitive (G13, G31) |
| `a56ea66`, `f5b9511` | COM errors in worker threads | CoInitialize; fresh per-thread connection | Proper | `CoUninitialize` is never called (harmless here) |
| `0e2be04`, `fe04ce9` | Excel could not save while loaded | In-memory copy | Proper | — |
| `0c27360` | Stale match cache; selection wiped; duplicate sends on resume; silent missing attachments; Identifier 2 lost on restore; New Session not resetting; test email account; lists after rows move | Eight targeted fixes + tests | Mostly proper | The email-based identity used for lists was not applied to sessions or checkpoints (G1, G20); the cache can still go stale *during* a scan (G14) |
| `3cb4ca7` | Start-up freezes | Worker thread | Proper | Building emails still happens on the window thread |
| `4a278bf` | Slow cancel; stuck Outlook; crash mid-save; off-thread widget reads | Sliced sleep; circuit breaker; atomic writes; QTimer | Proper | Templates and the theme file are not atomic; the breaker also trips on bad data (G6) |
| `1c2e18c` | Typing lag | Debounce | Proper | The BCC box was never connected (G4) — older than the debounce |
| `7446087` | Select All with a filter selected everyone | Visible rows only | Proper | Refresh still re-selects everyone (G19) |
| `63c6697` | Validation counted only 100 rows; false "report saved"; size warning was a stub | Fixed | Proper | Docs partly corrected (Section 7.9) |

### 12E. Abandoned approaches and reversals
- Data in the user's home folder → app folder (`9884d2c`).
- Strict variable pattern (letters only) → permissive pattern (`ebcd168`): special characters in
  headers were common.
- New Outlook / Outlook probe in `main.py` before the window (`0a61744`) → removed in favour of a
  background connection (`3cb4ca7`): the probe could launch Outlook and froze start-up.
- `threading.Timer` auto-save → `QTimer` (`4a278bf`).
- Per-row `QCheckBox` widgets → checkable items (`7446087`).
- Pop-up as `Qt.Popup` → `Qt.Tool` that never takes focus (`32ba07c`).
- Cancel confirmation dialog → none (`4a278bf`).
- Resume by filtering `self._emails` and restarting the send (re-based row numbers → duplicate
  emails) → continue the same checkpoint (`0c27360`).
- Success pop-ups → status-bar messages (`fe04ce9`, `63c6697`).
- **Remnants still in the code:** the shadowed first `ExcelHandler.close()` (`0c27360`); the large set
  of never-wired helpers from the first commit (Section 2); `TabCompose.is_valid` and
  `TabPreview.validate_all`, validation hooks that were never connected.

### 12F. Dependency evolution
- `d8e17d6`: PyQt5>=5.15.0, openpyxl>=3.1.0, pywin32>=306 (with comments), `pyinstaller` commented
  out as optional. `6b54a17`: comments removed. `96fa60f`: python-docx>=1.1.0 added — two hours
  after the code first imported it (`fabf464`). No change since 1 January.
- No version is pinned; no Python version is recorded.
- **Used but not listed:** `pytest` (tests since `0c27360`). Windows-only `pywin32` has no platform
  marker, so `pip install -r requirements.txt` on another OS fails at that line.
- PyInstaller (.exe) was planned and then **parked by the user** (`ROADMAP.md:222`).

---

## SELF-CONSISTENCY REVIEW

Done after all twelve sections were written; the document was re-read from Section 1 to Section 12.

1. **Cross-section contradictions** — checked:
   - Section 8 vs 11: Outlook COM (HIGH) is not replaced in Section 11; the trade-off is stated.
     "Contains" matching (HIGH) is kept; Section 11 adds an overlap check instead of exact matching.
     The app-folder data location (MEDIUM) is left to the author.
   - Section 3 vs 7: every feature whose trace showed a problem says **BUG/GAP** and points to a
     numbered gap; no feature is described as fully working where a gap was verified.
   - Section 12B vs Sections 3-5: the nine "never changed" files were checked against their imports.
   - Section 2 vs the rest: dead code (`TabCompose.is_valid`, `validate_all`, the shadowed `close()`)
     is consistent with F5, F15 and F1.
2. **All features traced** — F1-F25 each have a concrete trace; the risky ones were run on dummy data.
3. **Shared state, write path vs read path:**
   - *Session file:* written by `_get_session_state` (`selected_recipients`, no `template_name`), read
     by `get_session_info` (`selected_indices`, `template_name`) → **mismatch** (G21).
   - *Checkpoint:* row numbers written by the send thread (`record_success/failure`) and read by
     resume — consistent; `excel_file` written empty and never compared (G1).
   - *Preferences:* two writers (`file_utils` and `ThemeManager`) merge keys; both write plain-ASCII
     JSON, so `ThemeManager` reading without `encoding=` is harmless; keys `theme`, `window_geometry`,
     `last_dir/<purpose>` match between writers and readers.
   - *Templates, lists, profiles:* written and read as UTF-8 JSON with the same keys — consistent
     (lists also keep `recipient_emails`).
   - *Match cache:* written by lookups from two threads without a lock (G14).
4. **Patterns** — every pattern in Section 8 was checked across all files (table "Pattern consistency").
5. **Corrections made during the review:**
   - [Corrected during self-review — Section 2 originally said `clear_checkpoint` was used by "the
     tests' helpers"; the call-site search shows nothing calls it at all.]
   - [Corrected during self-review — G13 originally relied on the Send tab's "without attachments"
     warning as a safety net; F12 and `ui/tab_send.py:481-498` show that warning counts static files
     too, so it stays silent whenever any static file is attached. Added as G41.]
   - [Added after the review, 03-11-2026 — while preparing question Q19, a dummy workbook saved with its
     second sheet in view listed that sheet's clients while the Worksheet drop-down named the first
     sheet, and Apply then switched to the first sheet's clients. Added as G42.]
   - [Added after the review, 03-11-2026 — an independent consistency check found, and Claude reproduced,
     a second sender started by Resume Previous during a run (the emails still pending sent twice).
     Added as G43.]
