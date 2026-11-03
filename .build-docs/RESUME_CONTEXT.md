# RESUME_CONTEXT — Advanced Email Tool

> Read this first in a cold session, then CLAUDE.md, the Brief and the newest Decisions Log session.

## Where we are

- **Adoption done (Session 0, 03-11-2026).** The existing app (v1.8.0, `main` at `f5b9511`) is now
  under the template toolkit. Documentation only: no code file was changed, moved, reformatted or
  deleted.
- **Added, on branch `adopt-toolkit` (not merged into `main`):** `CLAUDE.md`;
  `.build-docs/PROJECT_AUDIT_advanced_email_tool.md`; `.build-docs/REBUILD_BRIEF_advanced_email_tool.md`;
  `.build-docs/DECISIONS_LOG.md`; this file; `.build-docs/readme_template.md`;
  `.build-docs/context/.gitkeep`.
- **Test suite:** 82 passed (Linux, Python 3.13, PyQt5 5.15.11 off-screen, Outlook faked) on
  03-11-2026. Not yet run on an office PC.
- **No Build Plan** (`.build-docs/BUILD_PLAN.md` does not exist): one is written when the author asks
  for a change.
- **Questions Q1-Q20 answered on 03-11-2026** (Brief Section 10; Decisions Log, Session 0, Decided
  11-33). In short:
  - the app runs from a shared folder on the office server, started from a desktop shortcut on each
    PC; the sharing of its `.app_data` was never tested (G24, G36 apply);
  - every sending PC uses classic Outlook; the mailboxes are a mix of Microsoft 365 and other
    providers, Gmail among them; the PCs run Windows 11 (26H2) and Python 3.14.9, with 1080p screens;
  - identifiers are client codes, chosen so that none hits another client's file (no overlap check:
    G11 accepted); session restore by row number stays as it is (G20 accepted);
  - the recipient lists are made in Excel by staff; some have duplicate headings or headings below
    row 1 (G26 and G23 apply: Changes 10 and 11); checking Q19 found gap G42 (the Worksheet
    drop-down can name another sheet than the one read): Change 12;
  - none of the audit's listed problems has been noticed in use (Q16). One new one has: emails sent
    with client files show twice in Sent. The app sends each email once (checked with a fake
    Outlook), so it is probably Outlook and Gmail each keeping a copy *(inferred — office-PC
    check 13)*;
  - the safety-net tests T1-T7 are approved (Q17); a future `[DOCS]` change may correct the README
    and the other user documents (Q15).
- **Decided, not built — Changes 1-12** (Brief Section 5; contracts C4 extended and C15-C28):
  1. Resume and Retry ask first, refuse another file or other clients, and never count Preview mode
     as sent;
  2. Excel Refresh keeps the hand-picked ticks, by email address;
  3. the Universal BCC always applies, and Preview shows CC and BCC;
  4. loading a profile replaces everything it covers;
  5. sending is blocked while any `{MISSING}` remains, and `{variables}` ignore capitals;
  6. numbers and dates appear as Excel shows them;
  7. blank or invalid addresses are listed before sending and left out unless confirmed;
  8. the "Send from" account is remembered, and a refused account means not sent;
  9. the app's own data moves to `C:\Users\Public\Advanced Email Tool\` on each computer;
  10. a repeated heading keeps both columns: the later one becomes "Amount (2)", and `{Amount}`
      means the left-most column;
  11. sessions and profiles remember the sheet and the heading row; switching sheets keeps the row
      and column; the boxes always show what was read;
  12. a newly chosen workbook opens on its first sheet, and the drop-down always names the sheet
      read.
  The points marked "to confirm when planned" in the Brief are asked at that change's .1 Plan.
- **Parking Lot:** two ideas added by the author on 03-11-2026 — sending by signing in to the mail
  service (OAuth), and exporting and importing the app's settings (Brief Section 9). Not planned.
- **Open:** no business question. The office-PC checks (Decisions Log, Session 0, *Open*: checks
  1-13, check 8 answered), and the "to confirm when planned" points in the Brief, asked when their
  change is planned.

## Exact next action

1. The author runs the office-PC checks listed in Session 0 and reports what they saw; write each
   result into the Brief and Session 0 of the Decisions Log.
2. When the author asks for the first change, follow pipeline Part 3, Template 2 (Change Request):
   - first update the Brief (the rule and any contract the change touches), asking the "to confirm
     when planned" points that belong to that change;
   - write and commit the approved safety-net tests T1-T7; they must pass on today's code;
   - then write `.build-docs/BUILD_PLAN.md` (Session 1) with the change as its first sub-phase, and run
     it through the Build Loop in CLAUDE.md — one step per "next".

## Step status

- 03-11-2026 | Adoption (Session 0) | done | Audit, CLAUDE.md, Brief, Decisions Log, RESUME_CONTEXT,
  README template copy and `context/` added on `adopt-toolkit`; no code changed; 82 tests passed (Linux).
- 03-11-2026 | Session 0 questions Q1-Q4 | done | Answers recorded in the Brief, CLAUDE.md and the
  Decisions Log; Change 1 (Resume and Retry) decided, not built.
- 03-11-2026 | Session 0 questions Q1a-Q3a, Q5, Q6 | done | Answers recorded; Changes 2 and 3
  decided, not built.
- 03-11-2026 | Session 0 questions Q7-Q17 | done | Answers recorded in the Brief, CLAUDE.md and the
  Decisions Log; Changes 4-9 decided, not built; Q18 and Q19 added; office-PC checks 12 and 13 added.
- 03-11-2026 | Session 0 questions Q18-Q20 | done | Answers recorded in the Brief, CLAUDE.md and the
  Decisions Log; Changes 10-12 decided, not built; gap G42 added to the audit.

## Hard-won lessons

From the git history (each was a real failure in use) and from the adoption audit:

1. **Outlook objects belong to the thread that made them.** Open a fresh connection in every thread
   and for every call (`6e824fa`, `a56ea66`, `f5b9511`); reusing one from the start-up thread gave
   "Object is not connected to server".
2. **Never hold the Excel file open.** Read it into memory first; otherwise Excel cannot save
   (WinError 32) while the tool is open (`fe04ce9`).
3. **The window comes first.** Excel loading, folder scanning, the Outlook connection, the test email
   and sending run in worker threads (`3cb4ca7`, `fe04ce9`); never read Qt widgets from another
   thread (the old auto-save did — `4a278bf`).
4. **An email must never go without its document.** A failed attachment blocks that email
   (`0c27360`).
5. **Link saved state to clients by email, not by row number.** Saved lists were fixed this way
   (`0c27360`); sessions and the send checkpoint still use row numbers (gaps G1, G20).
6. **State files are written atomically** (temporary file, then swap — `4a278bf`); templates and the
   theme setting are not yet.
7. **Two copies of the matching code** — `EmailBuilder.build_email` and `get_preview_data` — must be
   changed together.
8. **`ExcelHandler.close()` is defined twice**; Python uses the second one, which also clears the
   loaded data.
9. **openpyxl's read-only mode trusts the file's own "used range" note**: a workbook exported by other
   software can load only its first rows (G25).
10. **Running the tests creates `.app_data/` inside the project folder** (logs, templates). It is
    ignored by git; run them in a copy when the working folder must stay untouched.
11. **This cloud session cannot open the window, Outlook, Excel or the office share.** Anything that
    depends on them is an office-PC check; dummy data only, never real client files.
12. **One `Send()` per email.** `core/outlook_sender.py` hands each email to Outlook once; it goes
    again only when someone runs the batch again — Start Sending after a cancel, Resume or Retry
    (G1-G3, G5). A double copy of every email in Sent therefore starts with office-PC check 13, not
    with the app's code (Q16).
