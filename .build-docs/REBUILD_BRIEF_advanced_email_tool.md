# Rebuild Brief: Advanced Email Tool
# Date: 03-11-2026
# Author: Adv. Sidhant Goyal

---

> **What kind of Brief this is.** An **adoption** Brief, not a rebuild: the app is kept and every
> future change happens in this repository. It records the app **as it works today** (v1.8.0, commit
> `f5b9511`), so that any change is made on purpose. Every later change starts by updating this Brief
> (pipeline Part 3, Template 2 — Change Request).
>
> **How it was filled.** Claude drafted it from the code, the repository's own documents, the git
> history and test runs on dummy data (`PROJECT_AUDIT_advanced_email_tool.md`, cited as "audit").
> The decisions are yours: check every line.
>
> **Marking.** Everything **not** marked *(inferred)* was read in the code, the repository's
> documents or the git history, or was checked by running the code on dummy data. *(inferred)* marks
> my reading of intent or of how the office uses the app — please confirm or correct it.
>
> Numbers used below: features **F1–F25** (audit Section 3), rules **R1–R46** (audit Section 5), gaps
> **G1–G41** (audit Section 7), Contracts **C1–C16** (Section 5 below; C15-C16 decided, not yet
> built), questions **Q1–Q17** (end).

---

## 1. WHAT THIS TOOL DOES (in my own words)

*Draft from the code — please rewrite it in your own words; any difference from your understanding
is worth noting.*

The tool sends one personalised email per client through classic Outlook. It takes the client list
from an Excel sheet, fills the client's details (name, period, amounts …) into a saved subject and
letter, attaches the common documents plus each client's own files — found in a folder because the
file name contains the client's PAN, code or name — and sends them one by one from the office
mailbox, keeping track so an interrupted run can continue.

---

## 2. WHO USES THIS AND HOW

- **Primary user:** *(inferred)* you and your office staff. `ROADMAP.md:232` says "Target: GST
  practitioners, tax professionals".
- **Technical comfort:** *(inferred)* non-coders. They start the app from a desktop shortcut
  (your answer to Q1a), not by typing a command; README and QUICKSTART still say `python main.py`.
- **Frequency of use:** "~50-100 emails every 10 days" (`ROADMAP.md:233`).
- **Environment:** Windows 10/11 with classic Outlook desktop (`README.md:28-30`). Recipient
  workbooks and attachment folders on local disks, OneDrive *(inferred from commit messages
  `fe04ce9`, `4a278bf`)* and network shares *(inferred from the network-path code)*.
- **Where the app runs (your answer to Q1, 03-11-2026):** from **a shared folder on the office
  server**. So every user shares the one `.app_data` folder inside it — the session, the send
  checkpoint, templates, saved lists, preferences and the log. Sharing it has **never been tested**
  (gaps G24, G36).
- **How staff start it (your answer to Q1a, 03-11-2026):** from **a desktop shortcut** on each PC.
  What the shortcut runs — `python.exe` or `pythonw.exe` with `main.py` — is not recorded (office-PC
  check 11).
- **Mail program (your answer to Q2, 03-11-2026):** every PC that sends uses **classic Outlook**.
  The mailboxes are **a mix**: some on Microsoft 365, some on other providers (your answer to Q2a,
  03-11-2026). Today this changes nothing (the app sends through Outlook whatever the service); it
  would matter only if Outlook had to be replaced — Microsoft Graph for the Microsoft 365
  mailboxes, the provider's own mail server (SMTP) for the others (Standard 12).

---

## 3. FEATURE DECISIONS

Every feature is **KEEP AS-IS** for now — the adoption default, not a decision you have made —
except where your answers decided a change (marked KEEP BUT IMPROVE, with the Change number). The
notes name the gaps that are still candidates; each needs your decision.

| Feature | Audit Ref | Decision | Notes |
|---------|-----------|----------|-------|
| Load the recipient Excel file | F1 | KEEP AS-IS | Never locks or changes the file. Gaps: G23, G25-G27, G29 |
| Map columns (To, CC, BCC, Identifier 1/2, AND/OR) | F2 | KEEP AS-IS | Gap: G28 (auto-detection can pick the wrong column) |
| Check email addresses | F3 | KEEP AS-IS | Shows problems, never blocks (Q10) |
| Export a blank Excel template | F4 | KEEP AS-IS | — |
| Compose with `{Column}` variables | F5 | KEEP AS-IS | Gaps: G31 (`{MISSING}` can be sent), G32 (number/date formats), G33 |
| Paste Excel tables, insert images | F6 | KEEP AS-IS | Gap: G34 |
| Import body from .docx/.txt/.html | F7 | KEEP AS-IS | Paragraph text only |
| Email templates | F8 | KEEP AS-IS | Names that differ only in symbols share one file |
| Universal BCC | F9 | KEEP BUT IMPROVE | **Decided (Q6): Change 3** — whatever is in the BCC box applies (G4). Not yet built |
| Static attachments | F10 | KEEP AS-IS | — |
| Variable attachments by identifier | F11 | KEEP AS-IS | "Contains" matching kept by your decision (Q3): identifiers are chosen so none hits another client's file (G11 accepted). Still open: G12-G17 |
| Attachment on/off switches | F12 | KEEP AS-IS | Gap: G41 |
| Choose recipients | F13 | KEEP BUT IMPROVE | **Decided (Q5): Change 2** — Excel Refresh keeps the hand-picked clients ticked, matched by email (G19). Not yet built |
| Saved recipient lists | F14 | KEEP AS-IS | Follow clients by email (C9) |
| Preview each email | F15 | KEEP BUT IMPROVE | **Decided (Q6): Change 3** — Preview shows each email's CC and BCC. Not yet built |
| Connect to Outlook | F16 | KEEP AS-IS | Classic Outlook only (G37, Q2) |
| Send the batch | F17 | KEEP AS-IS | Gaps: G5-G10, G41 |
| Test email to yourself | F18 | KEEP AS-IS | Clears CC/BCC, so it cannot show the BCC |
| Checkpoint, Resume, Retry failed | F19 | KEEP BUT IMPROVE | **Decided (Q4): Change 1** — Resume/Retry ask first; Resume only on the same file and clients (by email); Preview mode never counts as sent (G1-G3). Not yet built |
| Session auto-save and restore | F20 | KEEP AS-IS | G20 (ticks restored by row number) kept by your decision (Q5); still open: G21, G23, G24 |
| Profiles | F21 | KEEP AS-IS | **G22: keeps the previous campaign's static files** (Q7) |
| Remembered folders and window | F22 | KEEP AS-IS | — |
| Theme (system / light / dark) | F23 | KEEP AS-IS | Old look kept (Standard 14 exception for apps kept on PyQt5) |
| Log file | F24 | KEEP AS-IS | Contains client addresses; lives in the app folder (G36) |
| Navigation, shortcuts, checkmarks | F25 | KEEP AS-IS | — |

---

## 4. NEW FEATURES TO ADD

None requested at adoption.

| New Feature | What it should do | Why I need it | Priority |
|-------------|-------------------|---------------|----------|
| — | — | — | — |

---

## 5. BUSINESS RULES — KEEP / CHANGE / ADD

### Rules to KEEP exactly as-is:
Every rule below is how the code works today; nothing has been changed. Rules flagged ⚠ have a gap
whose fix would change them — whether to change them is a question at the end.

**Recipients and addresses**
- R1 — An address must match `name@domain.tld` (letters, digits and `._%+-` before "@"; a dot and at
  least two letters at the end) — (Audit: `core/validators.py`, line 33)
- R2 — Several addresses in one cell are separated by ";" only; each part must be valid — (Audit:
  `core/validators.py`, lines 64-74; `core/email_builder.py`, lines 315-332)
- R3 — Typo suggestions for 17 common misspelt domains (gmial.com → gmail.com …) — (Audit:
  `config.py`, lines 65-83)
- ⚠ R4 — Invalid or blank addresses are shown but never blocked (G6, Q10) — (Audit:
  `ui/tab_excel.py`, lines 611-620; `ui/tab_send.py`, lines 582-614)
- ⚠ R5 — To, CC and BCC column names are matched ignoring case; identifier columns and `{variables}`
  are case-sensitive (G13, G31, Q8) — (Audit: `core/email_builder.py`, lines 221-236 and 270-276;
  `core/template_engine.py`, line 80)
- ⚠ R6 — Universal BCC is added to every email unless already in that row's BCC — but an address
  typed in the box after the subject and body is ignored (G4) — **to change: Change 3 (Q6)** — (Audit:
  `core/email_builder.py`, lines 238-243)
- R7 — The test email goes to the sending account's own address, subject "[TEST] …", CC and BCC
  removed, attachments kept — (Audit: `ui/tab_send.py`, lines 553-559)

**Excel**
- R8 — Only `.xlsx` and `.xlsm` — (Audit: `core/excel_handler.py`, lines 101-102)
- R9 — Read from an in-memory copy, read-only, using the values Excel last saved — (Audit:
  `core/excel_handler.py`, lines 45-59)
- R10 — Headers in "Data starts at Row" (default 1), data from "Column" (default 1) — (Audit:
  `core/excel_handler.py`, lines 150-168)
- R11 — Empty header → `Column_N`; blank rows skipped; empty cells → blank — (Audit:
  `core/excel_handler.py`, lines 160-177)
- R13 — Sheets matched ignoring case; without a choice, the workbook's active sheet — (Audit:
  `core/excel_handler.py`, lines 61-69, 108-114)
- ⚠ R14 — Auto-detection: To = first column containing "email"/"e-mail"/"mail"/"to"/"recipient";
  Identifier 1 = first containing "identifier"/"id"/"code"/"pan"/"gstin"/"client" (G28) — (Audit:
  `ui/tab_excel.py`, lines 520-546)

**Templates**
- R16 — A variable is `{` + text without `{ } : ;` + `}` — (Audit: `core/template_engine.py`, line 28)
- ⚠ R17 — Values are inserted as plain text of the stored value: 150000, 0.18, 2026-04-01 00:00:00
  (G32, Q9) — (Audit: `core/template_engine.py`, lines 80-85)
- ⚠ R18 — An unknown variable becomes the text `{MISSING}` and the email still goes (G31, Q8) —
  (Audit: `core/template_engine.py`, lines 56 and 86-88)
- R21 — Template and list names keep only letters, digits, space, "-", "_" (50 characters) — (Audit:
  `data/template_storage.py`, lines 49-52)

**Attachments**
- R22 — A file belongs to a client if its **file name contains** the identifier, ignoring case; the
  folder name does not count. **Kept by your decision (Q3, 03-11-2026):** identifiers are chosen so
  that none can hit another client's file; no overlap check (G11 accepted). The identifiers are
  **client codes** (Q3a), so the safeguard holds as long as no code sits inside another (`101`
  inside `1010`) — for example codes all of the same length — (Audit:
  `core/attachment_matcher.py`, lines 122-134)
- ⚠ R23 — OR by default; AND (both in one name) only when the row has both identifiers, otherwise
  the one present is used (G12) — (Audit: `core/email_builder.py`, lines 279-284)
- R24 — Subfolders only when ticked; all file types — (Audit: `utils/file_utils.py`, lines 266-322)
- R25 — Static files first, then every matching file — (Audit: `core/email_builder.py`, lines 257-289)
- R26 — Size warning at 25 MB (warning only) — (Audit: `config.py`, line 47)
- R27 — An email whose attachment cannot be added is not sent — (Audit: `core/outlook_sender.py`,
  lines 340-356)

**Sending**
- ⚠ R29 — Start Sending asks for confirmation; Resume and Retry Failed do not (G2) — **to change:
  Change 1 (Q4)** — (Audit: `ui/tab_send.py`, lines 592-600, 667-696, 777-800)
- R30 — Delay between emails: default 1 s, choice 1-30 s — (Audit: `ui/tab_send.py`, lines 224-226)
- R31 — Cancel never asks; stops within about 0.1 s — (Audit: `ui/tab_send.py`, lines 653-665)
- R32 — The batch stops after 3 failures in a row — (Audit: `core/outlook_sender.py`, line 438)
- R33 — A cancelled or self-stopped run stays resumable; a finished run is closed even with
  failures — (Audit: `ui/tab_send.py`, lines 728-733)
- ⚠ R34 — Resume sends planned rows not marked sent or failed, matched **by row number** (G1);
  Retry resends only failed rows — **to change: Change 1 (Q4)** — (Audit: `data/checkpoint.py`,
  lines 273-292)
- ⚠ R35 — Preview mode opens each email in Outlook and is recorded as if sent (G3) — **to change:
  Change 1 (Q4)** — (Audit: `ui/tab_send.py`, lines 65-73)
- ⚠ R36 — Sends from the account chosen in "Send from"; at each start the first Outlook account; if
  setting it fails, the default account is used with only a log warning (G7, Q11) — (Audit:
  `core/outlook_sender.py`, lines 177-179 and 309-318)

**Saving state**
- R39 — Auto-save every 3 minutes (not while sending) and on close — (Audit: `config.py`, line 56)
- R41 — Session, checkpoint, lists and preferences are written atomically — (Audit:
  `utils/file_utils.py`, lines 16-29)
- ⚠ R42 — All user data in `.app_data` inside the app's folder (G24, G36, Q1, Q12) — (Audit:
  `config.py`, lines 20-31)

The full list (R1-R46, including window sizes and message limits) is in audit Section 5.

### Rules to CHANGE:
**Decided — not yet built** (built only when you ask for the change; the Build Plan comes then):

- **Change 1 — Resume and Retry made safe** (your answer to Q4, 03-11-2026: "Fix all three")
  - **Old rule:** Start Sending asks for confirmation, but Resume Previous and Retry Failed send at
    once (R29); Resume picks the remaining emails by **row number** only, so after another Excel file
    is loaded it sends to that file's rows (R34); a Preview-mode run is recorded as sent, so a later
    real Resume skips those clients for good (R35).
  - **New rule:** (a) Resume and Retry Failed show the number of emails and ask before anything is
    sent, like Start Sending; (b) Resume goes ahead only when the same Excel file and the same
    clients — checked by email address, not row number — are loaded, and otherwise refuses and says
    why; (c) a Preview-mode run never counts as sent: its clients stay pending for a real send.
  - **Why:** gaps G1-G3, each reproduced on dummy data — another file's clients emailed, clients never
    emailed, and no chance to stop.

- **Change 2 — Excel Refresh keeps your hand-picked recipients** (your answers to Q5 and its
  follow-up, 03-11-2026: "Only fix Refresh", "By email address")
  - **Old rule:** clicking Refresh on the Excel tab ticks every recipient again, even when the file did
    not change (G19).
  - **New rule:** after Refresh the same clients stay ticked, found again **by email address** wherever
    their rows moved (as saved lists do); anyone ticked who is no longer in the file is listed for you.
    Session restore at start-up is **not** changed: it still re-ticks by row number (G20, kept by your
    decision).
  - **Why:** G19 reproduced on dummy data — clients you had unticked came back into the send.

- **Change 3 — The Universal BCC always applies, and Preview shows CC and BCC** (your answer to Q6,
  03-11-2026: "Fix both")
  - **Old rule:** the Universal BCC box is read only when the subject or body changes, so an address
    typed there last is ignored (G4); the Preview tab never shows CC or BCC, and the test email
    removes them, so the missing copy cannot be seen.
  - **New rule:** whatever is in the Universal BCC box when the emails are built goes on every email
    (unless that row's own BCC already has it), and the Preview tab shows each email's To, CC and BCC
    exactly as they will be sent.
  - **Why:** G4 reproduced on dummy data — emails were built with no BCC copy.

The other candidate changes are the remaining ⚠ rules above; each one is a question at the end.

### Rules to ADD (not in original):
None decided yet.

### Contracts — promises the rebuild must always keep:
Numbered promises that hold on every run, whatever the input. Each one gets
a contract test, and every sub-phase plan names the contracts it relies on.

*For this app: the promises the code keeps **today**, taken from what it does. A change may alter a
contract only after you approve it here first.*

- **C1** — An email whose attachment cannot be added is never sent: it is reported as failed, naming
  the files, and can be retried. (`core/outlook_sender.py:340-356`; test
  `test_outlook_sender_attachments.py`)
- **C2** — The app only reads the user's Excel workbook and attachment files: it never changes,
  locks, moves, renames or deletes them. The only files it deletes are its own (`.app_data` entries
  it manages, its temporary image files). (`core/excel_handler.py:45-59`; every `os.remove`,
  `os.unlink` and `os.replace` call targets `.app_data` or a temporary file; test
  `test_excel_handler.py` for "not locked")
- **C3** — Within one run each selected row gets at most one email, and Resume never sends a row the
  checkpoint has marked sent or failed, even after several interruptions. (`data/checkpoint.py:273-292`;
  tests `test_checkpoint.py`, `test_tab_send_resume.py`)
- **C4** — Start Sending shows the number of emails and asks for confirmation before anything is sent
  or displayed. (`ui/tab_send.py:589-600`; no test yet) — *Resume and Retry Failed do not ask today
  (G2); Q4 decided they must: see "C4 (extended)" below.*
- **C5** — Cancel never asks, takes effect before the next email (within about 0.1 s of a pause), and
  a cancelled or self-stopped run stays resumable. (`ui/tab_send.py:653-665, 728-733`; tests
  `test_send_batch.py`, `test_send_ux.py`, `test_tab_send_resume.py`)
- **C6** — The batch stops itself after 3 failures in a row and says why. (`core/outlook_sender.py:436-438,
  511-518`; test `test_send_batch.py`)
- **C7** — A recipient's attachments are exactly: the static files (when switched on) plus every
  indexed file whose **name contains** the recipient's identifier, ignoring case — OR across the two
  identifiers, AND only when the row has both. Nothing else is attached. (`core/attachment_matcher.py:107-229`;
  `core/email_builder.py:257-289`; no end-to-end test yet) — *Q3: "contains" stays; identifiers
  are chosen so that none hits another client's file.*
- **C8** — The session, the send checkpoint, saved recipient lists and preferences are written so a
  crash never leaves them half-written. (`utils/file_utils.py:16-29`; test `test_persistence.py`)
- **C9** — A saved recipient list selects the same clients by email after rows move in Excel, and
  lists any saved client no longer in the file. (`data/recipient_lists.py:146-189`; test
  `test_recipient_lists.py`)
- **C10** — Address checking covers every row, not only the 100 shown, and never drops a row.
  (`ui/tab_excel.py:611-620`; test `test_polish.py`)
- **C11** — Slow work never freezes the window: Excel loading, folder scanning, the Outlook
  connection, the test email and the batch run in worker threads. (tests
  `test_tab_excel_async_load.py`, `test_tab_send_startup.py`, `test_tab_send_test_email.py`)
- **C12** — Restoring a session or a profile brings back the whole column mapping, including
  Identifier 2 and AND/OR. (`ui/tab_excel.py:717-791`; test `test_tab_excel_mapping.py`)
- **C13** — Changing a column mapping never changes a hand-picked selection while the rows are the
  same. (`ui/tab_recipients.py:292-296`; test `test_recipient_selection.py`) — *Excel Refresh does
  re-select everyone today (G19); Change 2 (Q5) keeps the ticks: see C17.*
- **C14** — The test email goes only to the sending account's own address, from the account chosen in
  "Send from", with CC and BCC removed. (`ui/tab_send.py:519-567`; test `test_tab_send_test_email.py`)

**Decided, not yet built** (the Changes above). They take effect with the change that builds them;
until then the safety-net tests pin today's behaviour, and the Change Request replaces those tests:
- **C4 (extended)** — Start Sending, Resume Previous and Retry Failed all show the number of emails and
  ask before anything is sent or displayed.
- **C15** — Resume sends only when the Excel file and the clients (checked by email address) match the
  interrupted run; otherwise it sends nothing and says why.
- **C16** — A Preview-mode run never counts as sent: every client it only displayed stays pending for a
  real send. *(C4 extended, C15, C16: Change 1.)*
- **C17** — Excel Refresh never changes which clients are ticked: the same clients stay ticked, matched
  by email address, and any ticked client no longer in the file is listed. *(Change 2.)*
- **C18** — Every email carries the Universal BCC exactly as it stands in the box when the emails are
  built (unless that row's own BCC already has it). *(Change 3.)*
- **C19** — Preview shows each email's To, CC and BCC exactly as they will be sent. *(Change 3.)*

---

## 6. EDGE CASES — LESSONS FROM THE AUDIT

Reference audit Sections 6 and 7.

### Must handle (were handled in original — keep):
- The workbook open in Excel while the tool reads it; Refresh picks up saved changes.
- Big or slow (OneDrive, network) workbooks and folders: worker threads, controls disabled meanwhile.
- Missing, wrong-type, damaged or locked workbook: plain-English message.
- Headers not in row 1 / data not in column A; empty header cells; blank rows; empty cells.
- Several addresses in one cell (";"); typos in common domains; invalid addresses beyond row 100.
- Qt's own CSS in the body is never treated as a variable.
- Attachment that cannot be added (open, moved, renamed): that email is not sent, retryable.
- Outlook not running, not installed, or New Outlook: the window still opens; clear message; Refresh
  reconnects.
- Outlook objects dying with their thread: fresh connection per call and per thread.
- Outlook stuck mid-batch: stop after 3 failures in a row, resumable.
- Cancel during a long pause: within 0.1 s.
- Crash or power cut while saving: atomic writes (session, checkpoint, lists, preferences).
- Interrupted run: resume continues the same checkpoint without re-sending.
- Rows moved in Excel: saved lists follow clients by email.
- Search filter active: Select All / None / Invert act on the visible rows only.
- Folder content changed: Rescan clears old results.
- Report file open in Excel: honest "not saved" message.
- Long paths (over 240 characters) in attachment folders.
- Text files in UTF-8, UTF-8-BOM, cp1252 or Latin-1.

### Must handle (were NOT handled — gaps from Section 7 that bit you):
*Which of these have actually happened is question Q16. Found by the audit (HIGH first):*
- G1-G3 — Resume/Retry without confirmation; Resume can hit another file's rows; Preview mode
  counts as sent — **decided: Change 1 (Q4)**, not yet built.
- G4 — Universal BCC typed last is ignored — **decided: Change 3 (Q6)**, not yet built.
- G14, G41 — stale "no files" after a Rescan; missing client files hidden by static files.
- G19 — Refresh re-selects everyone — **decided: Change 2 (Q5)**, not yet built.
- G22 — a profile keeps the previous campaign's static files.
- G25 — some exported workbooks load only their first rows.
- G31 — `{MISSING}` sent to clients.
- G24, G36 — shared `.app_data`: **known to apply** (the app runs from a shared server folder, Q1).
- G37 — classic Outlook only: every sending PC uses it today (Q2), so this is a future risk — it
  would bite only if a PC moved to New Outlook.

### Not worth handling (over-engineering for my use case):
- **G11 — identifiers contained in other identifiers** (`101` inside `1010`): decided not worth a
  check (Q3, 03-11-2026) — "the identifiers are selected so that it doesn't hit other client's file".
- **G20 — session restore re-ticks rows by number**: kept as it is (Q5, 03-11-2026).

*Still for you to decide.* Candidates: G9 (duplicate addresses), G17 (subfolder tick needs a
Rescan), G30 (`.xls`/`.csv`), G34 (unusual picture formats), G39 (shared log rollover), G40 (test
email during a batch).

---

## 7. DESIGN PREFERENCES

- **Framework:** Keep PyQt5 as it is.
- **Interface style:** one window with six numbered tabs in workflow order (Excel → Compose →
  Attachments → Recipients → Preview → Send), Previous/Next at the bottom, checkmarks on finished
  steps — as today.
- **Output format:** emails in classic Outlook (sent, or opened on screen in Preview mode); optional
  Excel match report; JSON profiles and templates.
- **File handling:** Browse… everywhere; drag-and-drop as an extra for the Excel file and static
  attachments — already both, as Standard 14 requires.
- **Error display:** message boxes for errors and confirmations, the status bar for routine
  successes, a coloured log on the Send tab — as today.

### Screens (Claude draws the new ones in Claude Design before the build)
- **Old screens:** all six tabs and their dialogs **kept as they are**, with their old look (light and
  dark themes) — Standard 14's exception for an app kept on PyQt5. Audit Section 10 describes them.
- **Screens:** unchanged — 1. Excel (Browse…), 2. Compose (Save), 3. Attachments (Browse… for the
  folder), 4. Recipients (Select All), 5. Preview (Next →), 6. Send (▶ Start Sending).
- **States to draw:** none (no new design).
- **Words:** the app's own words — Identifier, Static / Variable attachments, Recipients, Profile,
  Resume Previous, Retry Failed.
- **PCs:** *(unknown — Q14)*; the window needs at least 900 × 600 and opens at 1100 × 750.
- **Sample data for the design:** dummy data only, in `.build-docs/context/`.
- **Animations:** none.
- **Approved design:** Screens unchanged: no design.

---

## 8. WHAT I LEARNED (from reading the audit)

*[For you to write after reading the audit — 3 to 5 sentences.]* Suggested reading order: audit
Section 1, then Section 7 (G1-G4, G11, G14, G19-G22, G25, G31, G41 first), then Section 5.

---

## 9. PARKING LOT

Ideas already parked in the app's own `ROADMAP.md` (lines 185-196 and 222), carried over unchanged.

| Idea | When it came up | Priority | Status |
|------|----------------|----------|--------|
| Create a standalone .exe (PyInstaller) | January 2026 (`ROADMAP.md:131-151`) | — | Parked by you (`ROADMAP.md:222`) |
| Dynamic images per recipient | January 2026 | Maybe someday | "No current use case" |
| Merge several Excel sheets | January 2026 | Maybe someday | "Not requested" |
| Email scheduling (send later) | January 2026 | Maybe someday | Parked |
| CC/BCC from a separate file | January 2026 | Maybe someday | Parked |
| Signature management | January 2026 | Maybe someday | "Usually handled by Outlook" |
| Graph API (New Outlook) | January 2026 | Maybe someday | "Major rewrite, avoid if possible" — see G37, Q2. The mailboxes are a mix (Q2a), so a replacement would need Graph *and* SMTP |
| Mac support | January 2026 | Maybe someday | Parked |
| Gmail/SMTP support | January 2026 | Maybe someday | Parked |

---

## 10. QUESTIONS ONLY YOU CAN ANSWER

Business questions are asked one at a time, in plain English, with a recommended default (Build Loop
rule 3). Each answer is written back into this Brief — as a rule, a contract or an edge case — and
into the Decisions Log. **Asked first:** Q1-Q4 — answered on 03-11-2026.

| # | Question | Why it matters | Recommended default |
|---|---|---|---|
| Q1 | Where does the app's folder live, and how do staff start it today — each PC's own copy, one shared office folder, OneDrive, or only your PC? | All users of one folder share `.app_data` (sessions, the send checkpoint, templates, the log) — G24, G36; it also decides the launcher later (Standard 13) | **Answered 03-11-2026:** a shared folder on the office server; sharing of the app data never tested. **Q1a (03-11-2026):** staff start it from a desktop shortcut. |
| Q2 | Do all PCs that send use **classic** Outlook? Any on New Outlook? Are the mailboxes Microsoft 365 or another provider? | The app cannot work with New Outlook (G37) | **Answered 03-11-2026:** classic Outlook on all sending PCs. **Q2a (03-11-2026):** the mailboxes are a mix of Microsoft 365 and other providers. |
| Q3 | What do your identifiers look like (full PAN/GSTIN, numeric client codes, client names)? Should a future change stop before sending when one file matches more than one selected client? | "Contains" matching lets `101` pick up `1010_…` and `Ram` pick up `Shriram …` — another client's documents (G11) | **Answered 03-11-2026:** leave as is — "the identifiers are selected so that it doesn't hit other client's file". No overlap check. G11 is an accepted risk, covered by how identifiers are chosen. **Q3a (03-11-2026):** the identifiers are client codes. |
| Q4 | Should Resume and Retry Failed ask before sending, refuse when the Excel file or recipients differ from the interrupted run, and never treat Preview mode as sent? | Today they send at once, by row number, and Preview-mode emails count as sent (G1-G3) | **Answered 03-11-2026:** fix all three → Change 1 (Section 5), contracts C4 (extended), C15, C16. Not yet built |
| Q5 | When you click Excel Refresh, or restore a session, should your hand-picked selection be kept by client (email), like saved lists? | Today Refresh ticks everyone again and restore ticks by row number (G19, G20) | **Answered 03-11-2026:** only fix Refresh, matching by email address → Change 2, contract C17. Session restore stays as it is (G20). Not yet built |
| Q6 | Should the Universal BCC always apply exactly as typed, and should Preview show CC and BCC? | A BCC typed last is silently ignored (G4) | **Answered 03-11-2026:** fix both → Change 3, contracts C18, C19. Not yet built |
| Q7 | When you load a profile, should it replace every setting it covers — clearing static files and the folder when the profile has none? | Today the previous campaign's static files stay (G22) | Yes, replace everything |
| Q8 | Should Start Sending be blocked while any email still contains `{MISSING}`? Should `{name}` match a column "Name" (ignore case)? | Clients can receive `{MISSING}` (G31) | Block; ignore case |
| Q9 | Do your templates use amounts, percentages or dates? How should they appear (e.g. 1,50,000.00; 18%; 01-04-2026)? | Today: 150000, 0.18, 2026-04-01 00:00:00 (G32) | Show values as formatted in Excel |
| Q10 | Rows with a blank or invalid address: list them before sending and leave them out, or send anyway? | Today they reach Outlook; three blank rows in a row stop the batch (G6) | List them and leave them out unless you confirm |
| Q11 | Should the app remember the last "Send from" account, and stop (rather than use the default account) if Outlook refuses it? | Today each start picks the first account; a refused account falls back silently (G7) | Remember it; stop if refused |
| Q12 | Keep user data in `.app_data` inside the app's folder, or move it to each user's own folder (Standard 13)? | The folder is shared (Q1), so all users share one session, checkpoint and log (G24, G36) | Move it to each user's own folder (Standard 13), keeping shared templates only if you want them shared |
| Q13 | Are the recipient workbooks always saved by Excel itself, or exported from other software (Tally, the portal, a bank, a CRM)? | Some exported files load only their first rows (G25) | — (a fact) |
| Q14 | Which Windows version, Python version and screen size/scale do the sending PCs have? | Tests, launcher and window size | — (a fact) |
| Q15 | May a future `[DOCS]` change correct `README.md`, `QUICKSTART.md`, `CHANGELOG.md` and `ROADMAP.md` (audit 7.9)? | They contradict the code in places | Yes |
| Q16 | Which of the audit's gaps have actually happened to you? | Goes into Section 6 above | — (a fact) |
| Q17 | Approve the proposed safety-net tests (Decisions Log, Session 0, Proposed) so they are written before the first change? | They pin today's behaviour so a change cannot alter it unnoticed | Approve; write them as the first step of the first change |
