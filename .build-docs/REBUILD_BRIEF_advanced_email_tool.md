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
> **G1–G42** (audit Section 7; G42 was added on 03-11-2026), Contracts **C1–C28** (Section 5 below;
> "C4 extended" and C15-C28 are decided, not yet built), questions **Q1–Q20** (end).

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
  03-11-2026), Gmail among them (Q16). Today this changes nothing (the app sends through Outlook whatever the service); it
  would matter only if Outlook had to be replaced — Microsoft Graph for the Microsoft 365
  mailboxes, the provider's own mail server (SMTP) for the others (Standard 12).
- **The sending PCs (your answer to Q14, 03-11-2026):** Windows 11 (26H2), Python 3.14.9, 1080p screens.
- **The recipient lists (your answers to Q13, 03-11-2026):** made in Excel by staff; a list that comes
  from another program or a download is re-saved in Excel only *sometimes*; some columns used in
  emails hold **formulas**; some lists have **two columns with the same heading**, and some have their
  **headings below row 1**.

---

## 3. FEATURE DECISIONS

Every feature is **KEEP AS-IS** for now — the adoption default, not a decision you have made —
except where your answers decided a change (marked KEEP BUT IMPROVE, with the Change number). The
notes name the gaps that are still candidates; each needs your decision.

| Feature | Audit Ref | Decision | Notes |
|---------|-----------|----------|-------|
| Load the recipient Excel file | F1 | KEEP BUT IMPROVE | Never locks or changes the file. **Decided (Q18): Change 10** — a repeated heading keeps both columns, the later one renamed "(2)" (G26). **Decided (Q19): Change 11** — the sheet and the heading row are remembered by sessions and profiles and kept when switching sheets (G23). **Decided (Q20): Change 12** — a newly chosen workbook opens on its first sheet, and the drop-down always shows the sheet read (G42). Not yet built. Possible: G25, G27, G29 |
| Map columns (To, CC, BCC, Identifier 1/2, AND/OR) | F2 | KEEP AS-IS | Gap: G28 (auto-detection can pick the wrong column) |
| Check email addresses | F3 | KEEP BUT IMPROVE | **Decided (Q10): Change 7** — blank and invalid addresses listed before sending and left out unless you confirm (G6). Not yet built |
| Export a blank Excel template | F4 | KEEP AS-IS | — |
| Compose with `{Column}` variables | F5 | KEEP BUT IMPROVE | **Decided (Q8): Change 5** — nothing is sent while `{MISSING}` remains; variable names ignore capitals (G31). **Decided (Q9): Change 6** — numbers and dates as Excel shows them (G32). Both not yet built. Still open: G33 |
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
| Send the batch | F17 | KEEP BUT IMPROVE | **Decided: Change 7 (Q10)** — blank rows never stop the batch; **Change 8 (Q11)** — the chosen account is remembered and never swapped (G6, G7). Not yet built. Still open: G5, G8-G10, G41 |
| Test email to yourself | F18 | KEEP AS-IS | Clears CC/BCC, so it cannot show the BCC |
| Checkpoint, Resume, Retry failed | F19 | KEEP BUT IMPROVE | **Decided (Q4): Change 1** — Resume/Retry ask first; Resume only on the same file and clients (by email); Preview mode never counts as sent (G1-G3). Not yet built |
| Session auto-save and restore | F20 | KEEP BUT IMPROVE | G20 (ticks restored by row number) kept by your decision (Q5); the session moves to each computer — **Change 9 (Q12)**, not yet built (G24); the sheet and heading row are remembered — **Change 11 (Q19)**, not yet built (G23); still open: G21 |
| Profiles | F21 | KEEP BUT IMPROVE | **Decided (Q7): Change 4** — a profile replaces everything it covers (G22). **Decided (Q19): Change 11** — a profile also remembers the sheet and the heading row (G23). Not yet built |
| Remembered folders and window | F22 | KEEP BUT IMPROVE | Preferences move to each computer — **Change 9 (Q12)**; the Send from account is remembered too — **Change 8 (Q11)**. Not yet built |
| Theme (system / light / dark) | F23 | KEEP AS-IS | Old look kept (Standard 14 exception for apps kept on PyQt5) |
| Log file | F24 | KEEP BUT IMPROVE | Contains client addresses; moves out of the shared folder to each computer — **Change 9 (Q12)** (G36). Not yet built |
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
- ⚠ R4 — Invalid or blank addresses are shown but never blocked (G6) — **to change: Change 7
  (Q10)** — (Audit:
  `ui/tab_excel.py`, lines 611-620; `ui/tab_send.py`, lines 582-614)
- ⚠ R5 — To, CC and BCC column names are matched ignoring case; identifier columns and `{variables}`
  are case-sensitive (G13, G31) — **`{variables}` to change: Change 5 (Q8)**; identifier columns stay
  case-sensitive for now (G13) — (Audit: `core/email_builder.py`, lines 221-236 and 270-276;
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
- ⚠ R10 — Headers in "Data starts at Row" (default 1), data from "Column" (default 1). Only Apply and
  Refresh use these boxes: choosing a file, switching sheets, a restore and a profile read from row 1
  of the sheet, even while the boxes show another row (G23) — **to change: Change 11 (Q19)** —
  (Audit: `core/excel_handler.py`, lines 150-168; `ui/tab_excel.py`, lines 387, 471, 694-715, 870-890,
  1003)
- R11 — Empty header → `Column_N`; blank rows skipped; empty cells → blank — (Audit:
  `core/excel_handler.py`, lines 160-177)
- ⚠ R11 (repeated headings) — when two columns share a heading, each row keeps only the right-hand
  column's value, with no message (G26) — **to change: Change 10 (Q18)** — (Audit:
  `core/excel_handler.py`, lines 158-177)
- ⚠ R13 — Sheets matched ignoring case; without a choice, the workbook's active sheet (the one in view
  when it was last saved in Excel), while the Worksheet drop-down shows the first sheet; Apply and
  Refresh then read the sheet the drop-down shows (G42) — **to change: Change 12 (Q20)** — (Audit:
  `core/excel_handler.py`, lines 61-69, 108-114; `ui/tab_excel.py`, lines 447-463)
- ⚠ R14 — Auto-detection: To = first column containing "email"/"e-mail"/"mail"/"to"/"recipient";
  Identifier 1 = first containing "identifier"/"id"/"code"/"pan"/"gstin"/"client" (G28) — (Audit:
  `ui/tab_excel.py`, lines 520-546)

**Templates**
- R16 — A variable is `{` + text without `{ } : ;` + `}` — (Audit: `core/template_engine.py`, line 28)
- ⚠ R17 — Values are inserted as plain text of the stored value: 150000, 0.18, 2026-04-01 00:00:00
  (G32) — **to change: Change 6 (Q9)** — (Audit: `core/template_engine.py`, lines 80-85)
- ⚠ R18 — An unknown variable becomes the text `{MISSING}` and the email still goes (G31) — **to
  change: Change 5 (Q8)** — (Audit: `core/template_engine.py`, lines 56 and 86-88)
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
- R32 — The batch stops after 3 failures in a row; blank addresses will no longer count (Change 7) —
  (Audit: `core/outlook_sender.py`, line 438)
- R33 — A cancelled or self-stopped run stays resumable; a finished run is closed even with
  failures — (Audit: `ui/tab_send.py`, lines 728-733)
- ⚠ R34 — Resume sends planned rows not marked sent or failed, matched **by row number** (G1);
  Retry resends only failed rows — **to change: Change 1 (Q4)** — (Audit: `data/checkpoint.py`,
  lines 273-292)
- ⚠ R35 — Preview mode opens each email in Outlook and is recorded as if sent (G3) — **to change:
  Change 1 (Q4)** — (Audit: `ui/tab_send.py`, lines 65-73)
- ⚠ R36 — Sends from the account chosen in "Send from"; at each start the first Outlook account; if
  setting it fails, the default account is used with only a log warning (G7) — **to change: Change 8
  (Q11)** — (Audit:
  `core/outlook_sender.py`, lines 177-179 and 309-318)

**Saving state**
- R39 — Auto-save every 3 minutes (not while sending) and on close — (Audit: `config.py`, line 56)
- R41 — Session, checkpoint, lists and preferences are written atomically — (Audit:
  `utils/file_utils.py`, lines 16-29)
- ⚠ R42 — All user data in `.app_data` inside the app's folder (G24, G36, Q1) — **to change: Change 9
  (Q12)** — (Audit:
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

- **Change 4 — Loading a profile replaces everything it covers** (your answer to Q7, 03-11-2026:
  "Replace everything")
  - **Old rule:** a profile replaces the static attachments only if at least one of its files still
    exists, and the attachments folder only if it has one, so the previous campaign's files and folder
    stay behind (G22); the sending account saved in a profile is never applied (G7).
  - **New rule:** a profile replaces every setting it covers: no static files in the profile empties the
    list, no folder clears the folder, and every listed file that is missing is shown to you; the other
    settings it covers (mapping, subject, body, BCC, switches, account) come from the profile too.
    *To confirm when the change is planned: what happens when the profile names no Excel file.*
  - **Why:** G22 reproduced on dummy data — last month's notice stayed attached for every recipient.

- **Change 5 — No `{MISSING}` ever reaches a client; variable names ignore capitals** (your answer
  to Q8, 03-11-2026: "Block, ignore case")
  - **Old rules:** a `{variable}` must match its column name exactly, capitals included (R5); an
    unmatched one is sent as the text `{MISSING}`, and the warning line under the editor never stops
    the send (R18, G31).
  - **New rules:** `{name}` matches a column "Name" — capital letters are ignored, as they already are
    for the To/CC/BCC columns; and while any email would still contain `{MISSING}`, nothing goes to
    clients — Start Sending, Resume and Retry are blocked, with the emails and variables listed.
    *To confirm when the change is planned: the test email to yourself stays allowed, so you can see
    the problem.*
  - **Why:** G31 reproduced on dummy data — "Dear {MISSING}".

- **Change 6 — Numbers and dates appear as Excel shows them** (your answer to Q9, 03-11-2026:
  "As shown in Excel")
  - **Old rule:** a `{Column}` holding a number or date is inserted as its raw stored value — 150000,
    0.18, 2026-04-01 00:00:00, even 1234.5600000000002 (R17, G32).
  - **New rule:** every value appears exactly as its cell displays it in Excel — 1,50,000.00 · 18% ·
    01-04-2026 — so the look is set in the workbook. *To settle when the change is planned (a technical
    detail): a cell format the app cannot reproduce exactly is listed for you to decide, never guessed.*
  - **Why:** G32 reproduced on dummy data.

- **Change 7 — Blank or invalid addresses are listed before sending and left out** (Q10: you took the
  recommended answer, 03-11-2026)
  - **Old rules:** invalid and blank addresses are only marked on the Excel tab and still go to Outlook
    (R4); three blank ones in a row stop the whole batch with "Outlook may be unavailable" (R32, G6);
    "a@x.com, b@x.com" (a comma instead of ";") goes to Outlook as one address.
  - **New rule:** before a run (Start, Resume, Retry), every selected row with a blank or invalid
    address — commas instead of ";" included — is listed; those rows are left out of the run unless you
    confirm them; a blank address never counts towards the "3 failures in a row" stop.
  - **Why:** G6 reproduced on dummy data.

- **Change 8 — The "Send from" account is remembered and never silently swapped** (Q11: you took the
  recommended answer, 03-11-2026)
  - **Old rule:** each start selects the first Outlook account; if Outlook refuses the chosen account,
    the email goes from the default account with only a note in the log (R36, G7).
  - **New rule:** the app remembers the last "Send from" account and selects it at start; if Outlook
    refuses the chosen account, that email is not sent and fails with a clear message — it is never
    sent from another account.
  - **Why:** G7 — a client could get the email from the wrong mailbox without anyone noticing.

- **Change 9 — The app's own data moves to each computer: `C:\Users\Public\Advanced Email Tool\`**
  (your answer to Q12, 03-11-2026)
  - **Old rule:** sessions, the send checkpoint, templates, saved lists, preferences and the log live in
    `.app_data` inside the app's folder — the shared server folder — so every user shares them, never
    tested (R42, G24, G36).
  - **New rule:** the app keeps them in `C:\Users\Public\Advanced Email Tool\` on each computer — a folder
    every Windows user of that PC can reach — and no longer writes them into the shared server folder.
    *To confirm when the change is planned: (a) whether templates and saved recipient lists move too
    (each PC then has its own) or stay shared in the server folder; (b) what happens to the data
    already in `.app_data`.*
  - **Note:** Standard 13's default is each Windows user's own folder (`%LOCALAPPDATA%`); your choice
    is one folder per computer, so people who share a PC also share its session and checkpoint.
  - **Why:** G24, G36 — the shared data was never tested, and one user could be offered another
    user's run to resume.

- **Change 10 — A repeated heading keeps both columns** (your answer to Q18, 03-11-2026: "Keep both,
  rename one")
  - **Old rule:** when two columns have the same heading, each row keeps only the right-hand column's
    value under it; the left-hand column's values vanish, although the drop-downs offer the heading
    twice, and nothing is said (R11, G26 — on a dummy list with two "Amount" columns, `{Amount}`
    gave the right-hand 2700, never the left-hand 15000).
  - **New rule:** every column is kept. The first (left-most) keeps its heading; each later repeat is
    renamed with a number — "Amount (2)", "Amount (3)" — and when the list loads a message lists
    every renamed heading and its column. `{Amount}` and the drop-downs then mean the left-most
    column — a change from today, and the message says so. This includes To, CC and BCC: if a list
    ever has two "Email" columns, the emails go to the left-most one's addresses.
    *To confirm when the change is planned: (a) whether headings that differ only in capitals or
    spaces ("Amount", "amount ") count as repeats — `{variables}` will ignore capitals (Change 5);
    (b) what a saved session, profile or template that names a repeated heading should do.*
  - **Why:** G26 — a whole column of client data could vanish without anyone noticing.

- **Change 11 — The heading row and the sheet are remembered, and the boxes always tell the truth**
  (your answer to Q19, 03-11-2026: "Remember, keep on switch" — the recommended answer)
  - **Old rule:** only Apply and Refresh use the "Data starts at Row / Column" boxes. Choosing a file,
    switching sheets, restoring a session and loading a profile read the headings from row 1 (a
    restore or a profile also goes back to the workbook's active sheet), while the boxes can still
    show another row (R10, R13, G23 — verified on a dummy list with headings in row 3).
  - **New rule:** sessions and profiles remember the sheet and the "Data starts at" row and column,
    and a restore or a profile reads the list with them. Switching sheets keeps the row and column.
    A newly chosen file starts at row 1, column 1, as today. The boxes always show the row and column
    the list was actually read from.
    *To confirm when the change is planned: what a restore or a profile does when its remembered
    sheet is no longer in the workbook.*
  - **Why:** G23 — after a restore, a profile or a sheet switch, the list could be read from the
    wrong row or sheet while the boxes showed something else.

- **Change 12 — A newly chosen workbook opens on its first sheet, and the drop-down always names the
  sheet read** (your answer to Q20, 03-11-2026: "Always the first sheet"; the recommended answer was
  the sheet in view)
  - **Old rule:** choosing a workbook reads the sheet that was in view when it was last saved in Excel,
    but the Worksheet drop-down shows the first sheet; Apply and Refresh then read the sheet the
    drop-down shows, so the list changes to another sheet's clients without a message (R13, G42 —
    verified on a dummy workbook saved with its second sheet "Feb" in view: the drop-down said "Jan"
    while Feb's clients were listed, and Apply switched to Jan's).
  - **New rule:** a newly chosen workbook (Browse…, or dropped on the tab) always opens on its first
    (left-most) sheet, whatever was in view in Excel, and the drop-down shows it. The drop-down always
    names the sheet actually read (stated on the question card as a plain fix), so Apply and Refresh
    never change sheets. A restore or a profile opens the sheet it remembered (Change 11).
  - **Why:** G42 — the list could change to another sheet's clients without a word, while the
    drop-down named a different sheet.

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
- **C20** — After a profile is loaded, the static attachments and the attachments folder are exactly
  the profile's (an empty list or no folder clears them); nothing is kept from the previous campaign,
  and missing files are listed. *(Change 4.)*
- **C21** — No email goes to a client while any email of the run would contain `{MISSING}`; a
  `{variable}` matches its column whatever the capital letters. *(Change 5.)*
- **C22** — Every number, percentage and date inserted into an email appears as its cell displays it in
  Excel. *(Change 6.)*
- **C23** — Before a run, every selected row with a blank or invalid address is listed and left out
  unless you confirm it; a blank address never stops the batch. *(Change 7.)*
- **C24** — Every email goes from the "Send from" account chosen for the run, or is not sent at all; the
  last choice is remembered. *(Change 8.)*
- **C25** — Sessions, the send checkpoint, preferences and the log are kept only in
  `C:\Users\Public\Advanced Email Tool\` on each computer — never in the shared server folder
  (templates and saved lists: as settled when the change is planned). *(Change 9.)*
- **C26** — No column of a list is ever dropped: when headings repeat, the first keeps its name, each
  later one is renamed "(2)", "(3)", …, and the renamed headings are listed when the list loads.
  *(Change 10.)*
- **C27** — The list on screen is always read with the sheet, row and column the Excel tab shows —
  after choosing a file, switching sheets, Apply, Refresh, a restore or a profile — and sessions and
  profiles bring back the sheet, row and column they saved. *(Change 11.)*
- **C28** — A newly chosen workbook opens on its first (left-most) sheet, and Apply and Refresh never
  change the sheet. *(Change 12; C27 covers the drop-down always naming the sheet read.)*

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
*Found by the audit (HIGH first). Asked which have actually happened (Q16, 03-11-2026, four cards
of three problems each): none that anyone has noticed. Several of them fail silently (G14, G22,
G26, G41), so "not noticed" does not prove "never happened". The one problem seen in use is new:
see "Seen in use" after this list.*
- G1-G3 — Resume/Retry without confirmation; Resume can hit another file's rows; Preview mode
  counts as sent — **decided: Change 1 (Q4)**, not yet built.
- G4 — Universal BCC typed last is ignored — **decided: Change 3 (Q6)**, not yet built.
- G14, G41 — stale "no files" after a Rescan; missing client files hidden by static files.
- G19 — Refresh re-selects everyone — **decided: Change 2 (Q5)**, not yet built.
- G22 — a profile keeps the previous campaign's static files — **decided: Change 4 (Q7)**, not yet
  built.
- G26 — two columns with the same heading: the earlier one's values vanish — **known to apply**
  (Q13), though no missing column has been noticed (Q16) — **decided: Change 10 (Q18)**, not yet
  built.
- G23 — the heading row ("Data starts at Row") and the sheet are not remembered by sessions and
  profiles — **known to apply** (Q13) — **decided: Change 11 (Q19)**, not yet built.
- G42 — the Worksheet drop-down can name a different sheet from the one read, and Apply and Refresh
  then switch to another sheet's clients without a word (found 03-11-2026 while checking Q19) —
  **decided: Change 12 (Q20)**, not yet built.
- G25, G27 — a list that was never saved by Excel can load only its first rows, and its formulas read
  as blank: possible, because such lists are re-saved in Excel only sometimes (Q13).
- G31 — `{MISSING}` sent to clients — **decided: Change 5 (Q8)**, not yet built.
- G32 — numbers and dates lose Excel's formatting — **decided: Change 6 (Q9)**, not yet built.
- G24, G36 — shared `.app_data`: known to apply (Q1), though no one has yet been offered another
  person's work (Q16) — **decided: Change 9 (Q12)**, not yet built.
- G6 — blank or invalid addresses reach Outlook — **decided: Change 7 (Q10)**, not yet built.
- G7 — the Send from account forgotten or silently swapped — **decided: Change 8 (Q11)**, not yet
  built.
- G37 — classic Outlook only: every sending PC uses it today (Q2), so this is a future risk — it
  would bite only if a PC moved to New Outlook.

*Seen in use (Q16, 03-11-2026) — not one of the audit's gaps, and probably not the app:*
- **Emails sent with client files show twice in Sent.** A "2" appears beside each one, and opening
  it shows two identical copies, although the Outbox held it once. No client has ever said they got
  two. Gmail is one of the accounts set up in classic Outlook. The app hands each email to Outlook
  once: one `Send()` per email; it goes again only when someone runs the batch again — Start
  Sending after a cancel, Resume or Retry (G1-G3, G5). Code read: `core/outlook_sender.py`, line
  363; checked with a fake Outlook on 03-11-2026 — 3 emails, 3 items created, 3 sends.
  *(inferred, not confirmed)* The likely causes, most likely first: Outlook and
  the Gmail account each keep a copy (Gmail's server files every email it sends in "Sent Mail",
  and classic Outlook can upload its own copy to the same folder); a Universal BCC or CC to the
  sending mailbox itself, which Gmail shows in the same conversation; or Outlook's conversation
  view counting two items. Office-PC check 13 (Decisions Log, Session 0) settles it. If the app
  turns out to be the cause, it comes back to you as a question.

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
- **PCs:** Windows 11 (26H2) with 1080p (1920 × 1080) screens (your answer to Q14); the Windows display
  scale was not stated. The window needs at least 900 × 600 and opens at 1100 × 750 — at 150 % scale
  a 1080p screen leaves only about 640 px of height, so check that the whole window fits (office-PC
  check 12).
- **Sample data for the design:** dummy data only, in `.build-docs/context/`.
- **Animations:** none.
- **Approved design:** Screens unchanged: no design.

---

## 8. WHAT I LEARNED (from reading the audit)

*[For you to write after reading the audit — 3 to 5 sentences.]* Suggested reading order: audit
Section 1, then Section 7 (G1-G4, G11, G14, G19-G22, G25, G31, G41 first), then Section 5.

---

## 9. PARKING LOT

Ideas already parked in the app's own `ROADMAP.md` (lines 185-196 and 222), carried over unchanged, and
the ideas you have parked since.

| Idea | When it came up | Priority | Status |
|------|----------------|----------|--------|
| Correct `README.md`, `QUICKSTART.md`, `CHANGELOG.md`, `ROADMAP.md` (audit 7.9) | 03-11-2026 (Q15) | — | **Approved** — a `[DOCS]` change, done when you ask |
| Create a standalone .exe (PyInstaller) | January 2026 (`ROADMAP.md:131-151`) | — | Parked by you (`ROADMAP.md:222`) |
| Dynamic images per recipient | January 2026 | Maybe someday | "No current use case" |
| Merge several Excel sheets | January 2026 | Maybe someday | "Not requested" |
| Email scheduling (send later) | January 2026 | Maybe someday | Parked |
| CC/BCC from a separate file | January 2026 | Maybe someday | Parked |
| Signature management | January 2026 | Maybe someday | "Usually handled by Outlook" |
| Graph API (New Outlook) | January 2026 | Maybe someday | "Major rewrite, avoid if possible" — see G37, Q2. The mailboxes are a mix (Q2a), so a replacement would need Graph *and* SMTP |
| Mac support | January 2026 | Maybe someday | Parked |
| Gmail/SMTP support | January 2026 | Maybe someday | Parked |
| Send emails by signing in to the mail service itself (OAuth), as a setting, instead of only through Outlook | 03-11-2026 (you) | — (not set) | Parked by you. Today every email goes through classic Outlook, which signs in by itself; the app never handles a password or a sign-in. **When picked up** (Standard 12, Email; Standard 13): the Microsoft 365 mailboxes through Microsoft Graph, which needs a one-time app registration in Microsoft Entra that you do; the Gmail mailboxes through Google's own sign-in, which needs a Google Cloud project and possibly Google's review of the app *(to check then)*; sign-in tokens kept per Windows user, encrypted, under `%LOCALAPPDATA%` — never in the shared folder or in `C:\Users\Public` (Change 9); a copy of every email in Sent. It would also free the app from classic Outlook (G37). *Questions then: which mailboxes first; does Outlook stay as the other choice; are the Gmail mailboxes company (Google Workspace) or personal accounts?* Joins the "Graph API (New Outlook)" and "Gmail/SMTP support" ideas above |
| Export the app's settings to a file to share with a colleague or friend, and import such a file | 03-11-2026 (you) | — (not set) | Parked by you. **Partly there today:** Profile › Save Profile… already writes a file you can share — the Excel file's location and column mapping, subject, body, Universal BCC, static files, attachments folder, the on/off switches and the Send-from account (saved, but not brought back on load: G7) — and Load Profile… reads it (F21; Change 4: loading replaces everything). Not in a profile: the saved email templates, the saved recipient lists and the preferences. **When picked up:** what goes in the file; what happens on import when a template or list of the same name exists (replace, keep both, ask); locations that do not exist on the other PC; client data — saved recipient lists hold client email addresses (recommended then: leave them out unless chosen, above all for someone outside the office); never a password or sign-in token (Standard 13). It would also be the way to copy templates and lists between PCs if Change 9 gives each PC its own |

---

## 10. QUESTIONS ONLY YOU CAN ANSWER

Business questions are asked one at a time, in plain English, with a recommended default (Build Loop
rule 3). Each answer is written back into this Brief — as a rule, a contract or an edge case — and
into the Decisions Log. **Asked first:** Q1-Q4 — answered on 03-11-2026; Q5-Q20 were answered the
same day (Q18 and Q19 came from the answer to Q13; Q20 was found while checking Q19). **No question
is open.** The points marked "to confirm when planned" in Section 5 are asked when that change is
planned.

| # | Question | Why it matters | Recommended default |
|---|---|---|---|
| Q1 | Where does the app's folder live, and how do staff start it today — each PC's own copy, one shared office folder, OneDrive, or only your PC? | All users of one folder share `.app_data` (sessions, the send checkpoint, templates, the log) — G24, G36; it also decides the launcher later (Standard 13) | **Answered 03-11-2026:** a shared folder on the office server; sharing of the app data never tested. **Q1a (03-11-2026):** staff start it from a desktop shortcut. |
| Q2 | Do all PCs that send use **classic** Outlook? Any on New Outlook? Are the mailboxes Microsoft 365 or another provider? | The app cannot work with New Outlook (G37) | **Answered 03-11-2026:** classic Outlook on all sending PCs. **Q2a (03-11-2026):** the mailboxes are a mix of Microsoft 365 and other providers. |
| Q3 | What do your identifiers look like (full PAN/GSTIN, numeric client codes, client names)? Should a future change stop before sending when one file matches more than one selected client? | "Contains" matching lets `101` pick up `1010_…` and `Ram` pick up `Shriram …` — another client's documents (G11) | **Answered 03-11-2026:** leave as is — "the identifiers are selected so that it doesn't hit other client's file". No overlap check. G11 is an accepted risk, covered by how identifiers are chosen. **Q3a (03-11-2026):** the identifiers are client codes. |
| Q4 | Should Resume and Retry Failed ask before sending, refuse when the Excel file or recipients differ from the interrupted run, and never treat Preview mode as sent? | Today they send at once, by row number, and Preview-mode emails count as sent (G1-G3) | **Answered 03-11-2026:** fix all three → Change 1 (Section 5), contracts C4 (extended), C15, C16. Not yet built |
| Q5 | When you click Excel Refresh, or restore a session, should your hand-picked selection be kept by client (email), like saved lists? | Today Refresh ticks everyone again and restore ticks by row number (G19, G20) | **Answered 03-11-2026:** only fix Refresh, matching by email address → Change 2, contract C17. Session restore stays as it is (G20). Not yet built |
| Q6 | Should the Universal BCC always apply exactly as typed, and should Preview show CC and BCC? | A BCC typed last is silently ignored (G4) | **Answered 03-11-2026:** fix both → Change 3, contracts C18, C19. Not yet built |
| Q7 | When you load a profile, should it replace every setting it covers — clearing static files and the folder when the profile has none? | Today the previous campaign's static files stay (G22) | **Answered 03-11-2026:** replace everything → Change 4, contract C20. Not yet built |
| Q8 | Should Start Sending be blocked while any email still contains `{MISSING}`? Should `{name}` match a column "Name" (ignore case)? | Clients can receive `{MISSING}` (G31) | **Answered 03-11-2026:** block, ignore case → Change 5, contract C21. Not yet built |
| Q9 | Do your templates use amounts, percentages or dates? How should they appear (e.g. 1,50,000.00; 18%; 01-04-2026)? | Today: 150000, 0.18, 2026-04-01 00:00:00 (G32) | **Answered 03-11-2026:** as shown in Excel → Change 6, contract C22. Not yet built |
| Q10 | Rows with a blank or invalid address: list them before sending and leave them out, or send anyway? | Today they reach Outlook; three blank rows in a row stop the batch (G6) | **Answered 03-11-2026 (recommended answer taken):** list them and leave them out unless you confirm → Change 7, contract C23. Not yet built |
| Q11 | Should the app remember the last "Send from" account, and stop (rather than use the default account) if Outlook refuses it? | Today each start picks the first account; a refused account falls back silently (G7) | **Answered 03-11-2026 (recommended answer taken):** remember it; stop if refused → Change 8, contract C24. Not yet built |
| Q12 | Keep user data in `.app_data` inside the app's folder, or move it to each user's own folder (Standard 13)? | The folder is shared (Q1), so all users share one session, checkpoint and log (G24, G36) | **Answered 03-11-2026:** move it to `C:\Users\Public\Advanced Email Tool` on each computer → Change 9, contract C25. Not yet built. *To confirm when planned: templates and saved lists; the data already in `.app_data`* |
| Q13 | Are the recipient workbooks always saved by Excel itself, or exported from other software (Tally, the portal, a bank, a CRM)? | Some exported files load only their first rows (G25) | **Answered 03-11-2026:** made in Excel by staff; lists from other programs re-saved in Excel only sometimes; some formulas; duplicate headings and headings below row 1 both happen → G26 and G23 apply (new questions Q18, Q19); G25 and G27 stay possible |
| Q14 | Which Windows version, Python version and screen size/scale do the sending PCs have? | Tests, launcher and window size | **Answered 03-11-2026:** Windows 11 (26H2), Python 3.14.9, 1080p screens. *The Windows display scale was not stated (office-PC check 12)* |
| Q15 | May a future `[DOCS]` change correct `README.md`, `QUICKSTART.md`, `CHANGELOG.md` and `ROADMAP.md` (audit 7.9)? | They contradict the code in places | **Answered 03-11-2026 (recommended answer taken):** yes — a `[DOCS]` change, done when you ask (Parking Lot) |
| Q16 | Which of the audit's gaps have actually happened to you? | Goes into Section 6 above | **Answered 03-11-2026 (four cards):** none of the twelve problems listed has been noticed. One new problem seen: emails sent with client files show twice in Sent, though no client has reported two → Section 6, *Seen in use*; office-PC check 13. The app sends each email once *(checked with a fake Outlook)*; the second copy is probably Outlook and Gmail each keeping one *(inferred)* |
| Q17 | Approve the proposed safety-net tests (Decisions Log, Session 0, Proposed) so they are written before the first change? | They pin today's behaviour so a change cannot alter it unnoticed | **Answered 03-11-2026 (recommended answer taken):** approved — written as the first step of the first change |
| Q18 | Some lists have two columns with the same heading (Q13). Today the app silently keeps only the later column. What should happen? | A whole column of client data can vanish without notice (G26) | Recommended: refuse such a list and name the repeated heading. **Answered 03-11-2026:** keep both, rename one — each later repeat becomes "Amount (2)", and a message lists the renamed headings → Change 10, contract C26. Not yet built |
| Q19 | Some lists have their headings below row 1 (Q13). Should sessions and profiles remember the sheet and the "Data starts at Row / Column" setting, and should switching sheets keep it? | Today a restore or a profile reads the active sheet with headings in row 1 (G23) | Recommended: yes — remember both, and keep the setting when switching sheets. **Answered 03-11-2026 (recommended answer):** remember them; switching sheets keeps the row and column; a newly chosen file starts at row 1, column 1; the boxes always show what was read → Change 11, contract C27. Not yet built |
| Q20 | Which sheet should a newly chosen workbook open on? (Found while checking Q19.) | Today the app reads the sheet that was in view when the workbook was last saved, but the drop-down shows the first sheet; Apply and Refresh then switch to it (G42) | Recommended: the sheet in view, shown in the drop-down. **Answered 03-11-2026:** always the first sheet; the drop-down always names the sheet read → Change 12, contract C28. Not yet built |
