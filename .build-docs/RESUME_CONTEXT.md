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
- **Answered on 03-11-2026 (Q1-Q4):** the app runs from a shared folder on the office server, and the
  sharing of its `.app_data` was never tested (G24, G36 apply); every sending PC uses classic
  Outlook; identifiers are chosen so that none hits another client's file (no overlap check, G11
  accepted); Resume and Retry: "Fix all three" → **Change 1** in the Brief (contracts C4 extended,
  C15, C16) — **decided, not built**.
- **Also answered on 03-11-2026:** Q1a (desktop shortcut), Q2a (a mix of Microsoft 365 and other
  mailboxes), Q3a (client codes), Q5 (Change 2: Refresh keeps the ticks, by email; session restore
  unchanged), Q6 (Change 3: the Universal BCC always applies; Preview shows CC and BCC) — Decisions
  Log, Decided 15-19.
- **Open:** Q7-Q17 (end of the Brief); office-PC checks (Decisions Log, Session 0, *Open*); the
  proposed safety-net tests T1-T7 await approval (Q17).

## Exact next action

1. Ask Q5-Q17 one at a time whenever the author is ready; write each answer into the Brief and
   Session 0 of the Decisions Log.
2. The author runs the office-PC checks listed in Session 0 and reports what they saw.
3. When the author asks for the first change — Change 1 (Resume and Retry made safe) is the one
   already decided — follow pipeline Part 3, Template 2 (Change Request):
   - first update the Brief (the rule and any contract the change touches);
   - write and commit the approved safety-net tests T1-T7; they must pass on today's code;
   - then write `.build-docs/BUILD_PLAN.md` (Session 1) with the change as its first sub-phase, and run
     it through the Build Loop in CLAUDE.md — one step per "next".

## Step status

- 03-11-2026 | Adoption (Session 0) | done | Audit, CLAUDE.md, Brief, Decisions Log, RESUME_CONTEXT,
  README template copy and `context/` added on `adopt-toolkit`; no code changed; 82 tests passed (Linux).
- 03-11-2026 | Session 0 questions Q1-Q4 | done | Answers recorded in the Brief, CLAUDE.md and the
  Decisions Log; Change 1 (Resume and Retry) decided, not built.

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
