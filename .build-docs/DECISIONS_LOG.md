# Decisions Log: Advanced Email Tool

> **What is this file?** This is your project's memory. After EVERY message
> exchange during the build, Claude Code appends a 2-3 line summary below.
> When a chat session ends and the history is gone, this file preserves
> what happened — what was discussed, what was decided, and what's still open.
>
> **How it is organised:**
> - **Session 0** — what we decided while discussing the project, before the
>   build. Claude pre-fills it from that discussion.
> - **Session 1** — Steps A and B of the Build Prompt: confirming understanding
>   and writing the Build Plan.
> - **Session 2 onwards** — one session per sub-phase of the Build Plan (the
>   Build Loop in CLAUDE.md), laid out as in *Format for each sub-phase session*
>   below.
>
> **Rules:**
> - Auto-maintained by Claude Code — do not edit manually unless correcting an error
> - Claude Code appends after EVERY response, no exceptions
> - Each new sub-phase gets a new session header — not each new chat or usage window
> - The "Open" field carries forward unresolved questions
> - P-flags (technical choices Claude made without asking) are numbered across the
>   whole project — P1, P2, … — so continue from the last number used in this log
> - Lettered assumptions (A, B, C…) are for technical choices only; they stand
>   unless the author objects — silence = consent. Business questions are always asked.
>
> **For this app:** it is an existing app adopted into the toolkit (no rebuild). Session 0 is the
> adoption; Session 1 is the Build Plan of the first change the author asks for. This repository is
> on GitHub: never write real client names, client email addresses, server names or share paths here.

---

## Format for each sub-phase session

Copy this layout when a sub-phase starts. Add a step status line as each step
ends, an exchange entry after every response, and the session entry at .9 Close.

~~~markdown
## Session [N] — Sub-phase [N.M] [name] — [DATE]

### Step status
- [DATE] | [N.M].[K] [step name] | [done / skipped — why] | [one line]

### Exchanges
#### [DATE] | Session [N] | Message [N]
- **Discussed:** [What we talked about in this exchange]
- **Decided/Built:** [What was decided or what code was written]
- **Open:** [Any unresolved question or next step]

### Session entry (written at [N.M].9 Close)
- **Built:** [What now exists that did not before]
- **Decisions:** [What was decided, and why]
- **P-flags:** [From the plan and the coders' saved choices]
- **Assumptions:** [Lettered — A, B, C…]
- **Disputes:** [Each dispute, with Fable's ruling]
- **Break-it tests:** [What Codex's tests found, and what was done]
- **Code review:** [Codex's findings, and the answers]
- **Adversarial review:** [Findings and answers — or "declined"]
- **Superseded:** [Earlier decisions this sub-phase replaced]
- **Open items:** [Carried forward]
- **Status:** [Suite count, e.g. "412 passed, 3 skipped"] · version [x.y]
~~~

---

## Session 0 — Adoption of the existing app into the toolkit — 03-11-2026

> Pre-filled by Claude from the author's adoption request and the audit, before any change.

- **Discussed:**
  - The author asked to bring this working PyQt5 app, used regularly in the office, under the
    template toolkit so future changes go smoothly — not to rebuild it, and not to make a new
    repository.
  - Claude read the six toolkit files named by the author in full (and the toolkit's own decisions
    index), then every file of this repository (63 tracked files plus `.gitignore`) and all 28
    commits, before writing anything.
  - The audit (`PROJECT_AUDIT_advanced_email_tool.md`) describes 25 features, 46 rules and 41 gaps
    (G42 was added later in this session: Decided 33).
    The app's 82 tests pass (Linux, Outlook faked). The most serious gaps, each reproduced on dummy
    data: an identifier picks up other clients' files when one is contained in another (G11);
    Resume and Retry send without asking, Resume can hit another file's rows, and a Preview-mode run
    counts as sent (G1-G3); a Universal BCC typed last is ignored (G4); Excel Refresh and session
    restore change the hand-picked recipients (G19, G20); a profile keeps the previous campaign's
    static attachments (G22); some exported workbooks load only their first rows (G25); `{MISSING}`
    can reach clients (G31).
  - Not possible in this cloud session: opening the window, Outlook, Excel or the office share.
    What needs an office PC is listed under *Open*.
- **Decided** (all by the author: 1-10 in the adoption request, 11-33 answering Q1-Q20, 34 later):
  1. Keep the app as it is: no rebuild, no new repository; all future changes happen in this one.
  2. This session adds documentation files only: no existing code file is changed, moved,
     reformatted or deleted.
  3. Window toolkit: PyQt5 — an existing app kept as it is.
  4. Shared portable Python: NO.
  5. Before the coding standards, CLAUDE.md carries the author's rule, word for word: "This is an
     existing app. The coding standards apply to new code and to the parts a change touches.
     Existing code is never rewritten just to meet them: ask me first."
  6. *How We Build* and the coding standards are copied word for word from `CLAUDE_TEMPLATE.md`.
  7. No Build Plan now: one is written when the author asks for a change.
  8. `.build-docs/context/` is for dummy sample files only; never real client data in this repository.
  9. Safety-net tests that pin today's behaviour are proposed now (below), written later, and run
     before any future change.
  10. The work is committed on a new branch, `adopt-toolkit`, not on `main`.
  11. **Q1 answered (author, 03-11-2026):** the app's folder is in a shared folder on the office
      server; the sharing of the app data has never been tested. So every user shares one
      `.app_data` (session, send checkpoint, templates, lists, preferences, log): gaps G24 and G36
      apply. How staff start the app: see 15.
  12. **Q2 answered (author, 03-11-2026):** every PC that sends uses classic Outlook. G37 (New
      Outlook cannot be automated) stays a future risk only. Mailbox provider: see 16.
  13. **Q3 answered (author, 03-11-2026):** "the identifiers are selected so that it doesn't hit
      other client's file". So "contains" matching stays as it is and no overlap check is added;
      G11 is an accepted risk, covered by how the office chooses identifiers. Rule R22 and Contract
      C7 unchanged. Not affected by this answer, still open: G12 (AND with one identifier blank),
      G14 (stale results after a Rescan), G15 (statistics in AND mode), G41 (missing client files
      hidden by static files).
  14. **Q4 answered (author, 03-11-2026): "Fix all three"** — Change 1 in the Brief: Resume and
      Retry Failed ask first; each goes ahead only when the same Excel file and the same clients
      (checked by email) are loaded; a Preview-mode run never counts as sent. New or extended
      contracts C4, C15, C16 — decided, **not yet built**: it is built only when the author asks for
      the change, through a Change Request and a Build Plan. Until then the proposed safety-net test
      T6 pins today's behaviour; the change replaces those pins with tests of the new rule.
  15. **Q1a answered (author, 03-11-2026):** staff start the app from a desktop shortcut on each
      PC. What the shortcut runs (`python.exe` or `pythonw.exe` with `main.py`) is not recorded —
      office-PC check 11. Recorded in the Brief (Section 2, Q1) and CLAUDE.md (Tech Stack).
  16. **Q2a answered (author, 03-11-2026):** the Outlook mailboxes are a mix — some on Microsoft
      365, some on other providers. Nothing changes today; if Outlook ever had to be replaced, both
      Microsoft Graph and SMTP would be needed (Standard 12). Recorded in the Brief (Section 2, Q2,
      Parking Lot) and CLAUDE.md (Tech Stack).
  17. **Q3a answered (author, 03-11-2026):** the identifiers are client codes. With codes, the Q3
      safeguard holds only as long as no code appears anywhere in another client's file name — inside
      a longer code (`101` in `1010`) or elsewhere, such as a year: equal length is not enough (`202`
      and `024` both pick up `101_GSTR3B_2024.pdf`, checked on dummy data); recorded
      next to rule R22 in the Brief. Where the audit inferred that client names are used as
      identifiers (Section 8, commit `bc73127`), the Brief now wins: client codes. Safety-net test
      T2 will use dummy client codes.
  18. **Q5 answered (author, 03-11-2026):** "Only fix Refresh"; follow-up: "By email address". Change 2
      in the Brief: after Excel Refresh the same clients stay ticked, matched by email address, and
      ticked clients no longer in the file are listed (contract C17 — decided, **not yet built**).
      Session restore keeps re-ticking by row number (G20 accepted).
  19. **Q6 answered (author, 03-11-2026): "Fix both"** — Change 3 in the Brief: whatever is in the
      Universal BCC box when the emails are built goes on every email, and Preview shows each email's
      To, CC and BCC. Contracts C18, C19 — decided, **not yet built**.
  20. **Q7 answered (author, 03-11-2026): "Replace everything"** — Change 4 in the Brief: a profile
      replaces every setting it covers (no static files → list emptied; no folder → folder cleared;
      missing files listed; account and other settings from the profile). Contract C20 — decided,
      **not yet built**. To confirm when the change is planned: a profile that names no Excel file.
  21. **Q8 answered (author, 03-11-2026): "Block, ignore case"** — Change 5 in the Brief: `{variable}`
      names match columns ignoring capitals, and nothing goes to clients (Start, Resume, Retry) while
      any email would contain `{MISSING}`. Contract C21 — decided, **not yet built**. To confirm when
      the change is planned: the test email to yourself stays allowed.
  22. **Q9 answered (author, 03-11-2026): "As shown in Excel"** — Change 6 in the Brief: every number,
      percentage and date in an email appears as its cell displays it in Excel. Contract C22 —
      decided, **not yet built**. Technical detail for planning: a format the app cannot reproduce
      exactly is listed for the author, never guessed.
  23. **Q10 — the author took the recommended answer (03-11-2026):** Change 7 in the Brief — before a run,
      rows with a blank or invalid address (commas included) are listed and left out unless confirmed;
      blank addresses never stop the batch. Contract C23 — decided, **not yet built**.
  24. **Q11 — the author took the recommended answer (03-11-2026):** Change 8 — the last "Send from"
      account is remembered; if Outlook refuses it, the email is not sent (never sent from another
      account). Contract C24 — decided, **not yet built**.
  25. **Q12 answered (author, 03-11-2026): "Computer's Users/Public/Advanced Email Tool"** — Change 9:
      the app's own data moves from `.app_data` in the shared server folder to
      `C:\Users\Public\Advanced Email Tool\` on each computer. Contract C25 — decided, **not yet
      built**. This differs from Standard 13's per-user default (`%LOCALAPPDATA%`): the author's choice
      is one folder per computer. To confirm when planned: templates and saved lists (move, or stay
      shared on the server?) and the data already in `.app_data`.
  26. **Q14 answered (author, 03-11-2026):** the sending PCs run Windows 11 (26H2) and Python 3.14.9,
      with 1080p screens; the display scale was not stated (office-PC check 12). Recorded in the Brief
      (Sections 2 and 7) and CLAUDE.md (Runtime).
  27. **Q15 — the author took the recommended answer (03-11-2026):** a future `[DOCS]` change may correct
      `README.md`, `QUICKSTART.md`, `CHANGELOG.md` and `ROADMAP.md` (audit 7.9); in the Brief's
      Parking Lot, done when the author asks.
  28. **Q17 — the author took the recommended answer (03-11-2026):** the safety-net tests T1-T7 are
      approved, to be written as the first step of the first change. The `pytest.ini` and a
      development requirements list for `pytest` will be proposed in that Build Plan.
  29. **Q13 answered (author, 03-11-2026, four cards):** the lists are made in Excel by staff; a list from
      another program or a download is re-saved in Excel only sometimes; some columns used in emails
      hold formulas; some lists have duplicate headings, and some have headings below row 1. So G26
      (a duplicate heading's earlier column vanishes) and G23 (the heading row and sheet are not
      remembered by sessions and profiles) apply today — new business questions Q18 and Q19 in the
      Brief; G25 and G27 stay possible for lists not re-saved in Excel.
  30. **Q16 answered (author, 03-11-2026, four cards):** none of the twelve problems listed has been
      noticed — wrong or re-ticked recipients, Resume or Retry mistakes; another client's file, a
      client's own file missing, an old file re-sent; a missing BCC copy, `{MISSING}` or raw values,
      the wrong sender account; missing rows or columns, a crash or freeze, another person's work
      offered. One new problem seen: emails sent with client files show twice in Sent ("2" beside
      each; two identical copies when opened), although the Outbox held each once and no client has
      said they got two; Gmail is set up in classic Outlook. Claude read the send code and ran it
      with a fake Outlook (3 emails → 3 items created, 3 sends): the app hands each email to Outlook
      once. *(inferred)* The second copy most likely comes from Outlook and Gmail each keeping one;
      a Universal BCC or CC to the sending mailbox, or Outlook's conversation view, are the other
      candidates. Office-PC check 13 settles it. Recorded in the Brief (Sections 2 and 6, Q16).
  31. **Q18 answered (author, 03-11-2026): "Keep both, rename one"** — not the recommended answer
      (refuse the list). Change 10 in the Brief: when two columns share a heading, both are kept; each
      later repeat is renamed "Amount (2)", "Amount (3)", and a message lists the renamed headings
      when the list loads. `{Amount}` and the drop-downs then mean the left-most column — a change from
      today, where the right-hand column's values win (G26; verified on a dummy list: `{Amount}` gave
      the right-hand 2700). New contract C26. To confirm when planned: whether headings that differ
      only in capitals or spaces count as repeats; what a saved session, profile or template naming a
      repeated heading should do. For that plan: a repeated To, CC or BCC heading means the emails go
      to the left-most column's addresses after the change. Not built.
  32. **Q19 answered (author, 03-11-2026): "Remember, keep on switch"** (the recommended answer) —
      Change 11 in the Brief: sessions and profiles remember the sheet and the "Data starts at" row and
      column, and a restore or a profile reads the list with them; switching sheets keeps the row and
      column; a newly chosen file starts at row 1, column 1, as today; the boxes always show the row
      and column the list was actually read from (stated on the card as a plain display fix). Today
      only Apply and Refresh use the boxes (G23; verified on a dummy list with headings in row 3).
      New contract C27. To confirm when planned: a remembered sheet that is no longer in the workbook.
      Not built.
  33. **Q20 answered (author, 03-11-2026): "Always the first sheet"** — not the recommended answer (the
      sheet in view). Q20 is new: while checking Q19, Claude found a gap, now G42 in the audit. Choosing
      a workbook reads the sheet that was in view when it was last saved, but the Worksheet drop-down
      shows the first sheet, and Apply and Refresh then read the sheet the drop-down shows — verified
      on a dummy workbook saved with "Feb" in view (the drop-down said "Jan" while Feb's clients
      were listed; Apply switched to Jan's). Change 12 in the Brief: a newly chosen workbook always
      opens on its first sheet, and the drop-down always names the sheet read (stated on the card as
      a plain fix), so Apply and Refresh never change sheets. Rule R13 changes; new contract C28.
      Not built.
  34. **Two ideas parked (author, 03-11-2026):** (1) make the app able to send by signing in to the
      mail service itself (OAuth), as a setting, instead of only through Outlook; (2) export the app's
      settings to a file to share with a colleague or friend, and import such a file. Added to the
      Brief's Parking Lot (Section 9) with what each needs when picked up; nothing decided about how,
      nothing built. Profiles (F21) already cover part of (2): Profile › Save Profile… writes a
      shareable file of the campaign settings. The author then widened (2), the same day: "not only
      profile, even the mail compose subject body and things" — the export also covers the Compose
      tab's subject, body and the like; whether the saved email templates go in too is Claude's
      reading *(inferred — to confirm when picked up)*. (A profile already carries the current
      subject, body and Universal BCC; the saved templates, saved lists and preferences cannot be
      exported today.)
- **Assumptions** (technical only — they stand unless the author objects):
  - A. The project tag in file names is `advanced_email_tool` (the repository's name).
  - B. The audit and the Brief describe `main` at commit `f5b9511` (v1.8.0).
  - C. The audit's checks ran on Linux: Python 3.13, PyQt5 5.15.11 (Qt 5.15.14) drawing off-screen,
    openpyxl 3.1.5, Outlook replaced by a fake. Anything that needs Windows, Outlook or Excel is
    marked "needs an office PC" and listed under *Open*.
  - D. The empty `context/` folder holds one empty `.gitkeep` file, because git does not store
    empty folders.
  - E. `readme_template.md` is copied byte for byte; the app's own `README.md` is left untouched.
  - F. In the Brief every feature is KEEP AS-IS by default, because no change has been requested.
  - G. In CLAUDE.md the author's rule is a short section of its own ("THIS IS AN EXISTING APP")
    directly before "CODING STANDARDS"; the Tech Stack gained "Mail" and "User data" lines; the
    Reference Documents gained the `readme_template.md` line; the `screens/` line was deleted, as the
    template says to when there is no design and no old screenshots.
  - H. Answers to the open questions are recorded in this Session 0 until Session 1 starts.
  - I. Markdown files use LF line endings (toolkit D23).
- **Safety-net tests — approved by the author on 03-11-2026 (Q17, recommended answer taken;
  Decided 28); written as the first step of the first change.** Tests that pin what the app does **today**,
  written before the first change and run on every change. Dummy data only (made-up clients, PANs
  such as `AAAPA1111A`, `example.com` addresses), generated by the tests in temporary folders; the
  same dummy files can also be saved in `.build-docs/context/` for the office-PC checks. Outlook is
  replaced by a recording fake, as in the existing tests. A test that pins a known gap says so ("pins
  today's behaviour — G#; change only through the Brief").
  - **T1 `tests/test_safety_net_contracts.py`** — the Contracts with no test, or only part-tested:
    C2 (the workbook and the attachment files are byte-for-byte unchanged, and nothing outside
    `.app_data` and the temporary folder is deleted, after load, Refresh, scan, build, a fake send
    and a report); C3 end to end (a full fake run cancelled, resumed and retried sends each address
    exactly once — today only the checkpoint pieces are tested); C4 (Start Sending shows the count
    and sends nothing on "No"); C7 (exact attachment lists for OR, AND, the on/off switches and
    static files). C1, C5, C6 and C8-C14 already have tests (Brief Section 5).
  - **T2 `tests/test_safety_net_golden_emails.py`** — a "golden" set: a dummy workbook of about eight
    clients identified by dummy client codes — the kind the office uses (Q3a) — including `101` and
    `1010` to pin today's "contains" matching, an amount of 150000, 1234.56, a date, a percentage, a blank address, a ";" pair and a
    "," pair), a dummy attachments folder, a template with variables (one with the wrong case), a
    Universal BCC and one static file. All emails are built through the main window (off-screen) and
    compared — To, CC, BCC, subject, body text and attachment names — with a stored expected file,
    e.g. `tests/golden/emails_v1_8_0.json`. Pins R2, R5, R17-R19, R22-R25, including G4, G11, G12 and
    G31-G33 as today's behaviour.
  - **T3 `tests/test_safety_net_excel_reading.py`** — header and column offsets, blank rows, empty
    and zero headers, numeric headers, duplicate headers (G26), a formula with no saved value (G27), a
    wrong used-range note (G25), the active sheet on restore (G23), `.xls` refused.
  - **T4 `tests/test_safety_net_matching.py`** — contains-matching ignoring case, folder names
    ignored, the subfolder setting, the AND fallback, statistics in AND mode (G15), the stale cache
    during a rescan (G14).
  - **T5 `tests/test_safety_net_state.py`** — the session prompt's wrong keys (G21), restore by row
    number (G20), account and sheet not restored (G7, G23), a profile keeping static files and folder
    (G22), Refresh re-selecting everyone (G19), template-name clashes (R21), the two preference
    writers keeping each other's keys.
  - **T6 `tests/test_safety_net_send_flow.py`** — Resume and Retry without confirmation (G2), Resume
    onto another file's rows (G1), Preview mode counted as sent (G3), three blank addresses stopping
    the batch (G6), Start after a cancel re-sending (G5), the account fallback logged only as a
    warning (G7).
  - **T7 `tests/test_office_pc_smoke.py`** (Windows only, skipped unless switched on) — connect to
    the real classic Outlook, list the accounts, and *open* (never send) one dummy email with a dummy
    attachment and an inline picture.
  - Possibly with them (each touches a file outside `.build-docs`, so only with the author's
    approval): a `pytest.ini` (`pythonpath = .`, `testpaths = tests`, as Standard 13 expects) and
    `pytest` in a development requirements list.
- **Open:**
  - Business questions — the full list, with recommended defaults, is at the end of the Brief.
    Q1-Q20 answered 03-11-2026 (Decided 11-33): Q18 and Q19 came from the Q13 answer, Q20 from
    checking Q19. No business question is open; the points marked "to confirm when planned" in the
    Brief are asked when their change is planned.
  - **Needs an office PC** (cannot be checked in the cloud):
    1. Run the app's tests there (`py -m pytest` in the app folder; expect 82 passed) and note the
       Windows, Python, PyQt5, pywin32 and openpyxl versions (`py -m pip list`).
    2. Start the app the usual way: Send tab shows "✓ Online"; every mailbox is in "Send from".
    3. With dummy data and Preview mode on, open one email in Outlook and check From, To, CC, BCC
       (type a Universal BCC last — G4), the attachments, the inline picture and the subject; close it
       without sending.
    4. Send the test email to yourself: it arrives, the picture shows, Sent Items has a copy, and it
       came from the chosen account (G7).
    5. On a dummy run to your own address, close Outlook midway: the run stops after 3 failures and
       Resume continues it.
    6. Keep the dummy workbook open in Excel, change and save it, click Refresh: the change appears
       (C2), and note that every recipient is ticked again (G19).
    7. ~~Where the app's folder and its `.app_data` live, and whether several users share them (G24,
       G36).~~ Answered by the author (Q1): a shared folder on the office server, so every user shares
       one `.app_data` (check 10 tests what that does). Still to note: whether OneDrive syncs that
       folder on any PC (G36).
    8. ~~Whether any sending PC has New Outlook switched on (G37).~~ Answered by the author (Q2):
       classic Outlook on all sending PCs.
    9. A dummy copy of a workbook exported by your other software loads all its rows (G25).
    10. Because the app runs from the shared server folder (Q1): with dummy data only, open it on two
        PCs at once and note what each sees — the "Restore Previous Session?" prompt and the
        "Resume Previous" button may show the *other* person's work (G24).
    11. Open one desktop shortcut's Properties and note its Target: `python.exe` (a black window
        stays open beside the app) or `pythonw.exe` (no black window — and then an unexpected error
        closes the app without any message, G35).
    12. Note the Windows display scale on a sending PC (Settings › System › Display › Scale) and
        check that the whole app window fits on the 1080p screen (Q14).
    13. **Two copies in Sent (Q16).** With dummy data, send one app email with one dummy client file
        to a colleague's address, from the usual account, and note: (a) where the "2" shows —
        Outlook's Sent Items, or Gmail in a browser or on a phone; (b) whether the colleague got one
        copy or two (if two, note whether Resume Previous was clicked during the run: G43); (c) whether the Universal BCC or CC holds the sending mailbox's own address;
        (d) whether an email typed by hand in Outlook, with an attachment, from the same account,
        also shows "2"; (e) whether one app email with no attachment, and one from a Microsoft 365
        mailbox, show "2". One copy in (b) and a "2" in (d) mean Outlook and Gmail, not the app.
- **Exchanges:**

#### 03-11-2026 | Session 0 | Message 1
- **Discussed:** The adoption request: audit the existing app, create CLAUDE.md, the Brief, this log,
  RESUME_CONTEXT, the README template copy and `context/`, propose safety-net tests, list the open
  questions, commit on `adopt-toolkit`.
- **Decided/Built:** Audit (12 sections + self-review), CLAUDE.md, Brief with Contracts C1-C14 and
  questions Q1-Q17, this log, RESUME_CONTEXT, `readme_template.md` copy, `context/.gitkeep`. No code
  file changed.
- **Open:** Q1-Q4 asked next, one at a time; the remaining questions and the office-PC checks above.

#### 03-11-2026 | Session 0 | Message 2
- **Discussed:** Q1 — where the app's folder lives.
- **Decided/Built:** Answer recorded (shared folder on the office server; sharing of `.app_data`
  never tested) in the Brief (Section 2, Q1, Q12, Section 6), CLAUDE.md (Tech Stack) and here;
  office-PC check 10 added.
- **Open:** how staff start the app; Q2-Q4 next.

#### 03-11-2026 | Session 0 | Message 3
- **Discussed:** Q2 — which Outlook the sending PCs use.
- **Decided/Built:** Answer recorded (classic Outlook on all sending PCs) in the Brief (Section 2,
  Q2, Section 6), CLAUDE.md (Tech Stack) and here; office-PC check 8 closed.
- **Open:** the mailbox provider; Q3-Q4 next.

#### 03-11-2026 | Session 0 | Message 4
- **Discussed:** Q3 — identifiers that are contained in other identifiers (wrong-client files).
- **Decided/Built:** Leave as is; identifiers are chosen so none hits another client's file. Recorded
  in the Brief (Sections 3, 5 and 6, Q3) and here (Decided 13); G11 moved to "not worth handling".
- **Open:** the kinds of identifier in use; Q4 next.

#### 03-11-2026 | Session 0 | Message 5
- **Discussed:** Q4 — Resume and Retry safety (G1-G3).
- **Decided/Built:** "Fix all three" recorded as Change 1 in the Brief (Section 5, contracts C4
  extended, C15, C16; F19 now KEEP BUT IMPROVE) and here (Decided 14). Not built.
- **Open:** Q5-Q17 when the author is ready; office-PC checks; approval of safety-net tests (Q17).

#### 03-11-2026 | Session 0 | Message 6
- **Discussed:** Q1a — how staff start the app.
- **Decided/Built:** A desktop shortcut on each PC (Decided 15); Brief, CLAUDE.md and office-PC check
  11 updated.
- **Open:** Q2a (mailbox provider) next.

#### 03-11-2026 | Session 0 | Message 7
- **Discussed:** Q2a — which mail service the mailboxes are on.
- **Decided/Built:** A mix of Microsoft 365 and other providers (Decided 16); Brief and CLAUDE.md
  updated.
- **Open:** Q3a (kinds of identifier) next.

#### 03-11-2026 | Session 0 | Message 8
- **Discussed:** Q3a — kinds of identifier.
- **Decided/Built:** Client codes (Decided 17); Brief (R22, Q3) and the T2 test-data note updated.
- **Open:** Q5 next.

#### 03-11-2026 | Session 0 | Message 9
- **Discussed:** Q5 — keeping hand-picked recipients on Refresh and session restore; follow-up on how
  to match the clients.
- **Decided/Built:** Change 2 (Refresh keeps the ticks, by email; C17); restore unchanged (G20
  accepted) — Decided 18.
- **Open:** Q6 next.

#### 03-11-2026 | Session 0 | Message 10
- **Discussed:** Q6 — the Universal BCC typed last is ignored; Preview hides CC/BCC (G4).
- **Decided/Built:** Change 3 (C18, C19) recorded in the Brief and here (Decided 19). Not built.
- **Open:** Q7 next. (The session's worker restarted before this answer; all earlier edits were
  checked and found intact.)

#### 03-11-2026 | Session 0 | Message 11
- **Discussed:** Q7 — a loaded profile keeps the previous campaign's static files and folder (G22).
- **Decided/Built:** Change 4 (C20) recorded in the Brief and here (Decided 20). Not built.
- **Open:** Q8 next.

#### 03-11-2026 | Session 0 | Message 12
- **Discussed:** Q8 — `{MISSING}` reaching clients; case-sensitive variable names (G31).
- **Decided/Built:** Change 5 (C21) recorded in the Brief and here (Decided 21). Not built.
- **Open:** Q9 next.

#### 03-11-2026 | Session 0 | Message 13
- **Discussed:** Q9 — raw numbers and dates in emails (G32).
- **Decided/Built:** Change 6 (C22) recorded in the Brief and here (Decided 22). Not built.
- **Open:** Q10 next.

#### 03-11-2026 | Session 0 | Message 14
- **Discussed:** The author's message: take the recommended answers for Q10, Q11, Q15 and Q17;
  Q12 = the computer's Users/Public/Advanced Email Tool folder; Q14 = Windows 11 (26H2), Python 3.14.9,
  1080p screens; ask Q13 and Q16 in detail as question cards.
- **Decided/Built:** Changes 7-9 (contracts C23-C25), Q14 facts, Q15 docs approval and Q17 test
  approval recorded in the Brief, CLAUDE.md and here (Decided 23-28); office-PC check 12 added.
- **Open:** Q13 and Q16, asked next as detailed cards.

#### 03-11-2026 | Session 0 | Message 15
- **Discussed:** Q13 in detail (sources, re-saving, formulas, headings).
- **Decided/Built:** Answers recorded in the Brief (Sections 2, 3, 6, Q13) and here (Decided 29);
  new questions Q18 (duplicate headings) and Q19 (heading row and sheet remembered) added.
- **Open:** Q16 next, as detailed cards; then Q18 and Q19.

#### 03-11-2026 | Session 0 | Message 16
- **Discussed:** Q16 in detail (four cards: recipients, attachments, content and sender, other). The
  author described emails showing twice in Sent and asked whether Outlook, the app or Gmail causes it.
- **Decided/Built:** Answer recorded in the Brief (Sections 2 and 6, Q16), CLAUDE.md (Tech Stack) and
  here (Decided 30); the send code checked with a fake Outlook (one send per email); office-PC check
  13 added; CLAUDE.md *Current Phase* and RESUME_CONTEXT brought up to date.
- **Open:** Q18 and Q19 (from the Q13 answer); the office-PC checks.

#### 03-11-2026 | Session 0 | Message 17
- **Discussed:** The author's "ask": Q18 and Q19, one card each, after Claude checked both on dummy
  data. Checking Q19 turned up a new gap (G42: the Worksheet drop-down can name another sheet than the
  one read), asked as Q20.
- **Decided/Built:** Q18 → Change 10 (C26), Q19 → Change 11 (C27), Q20 → Change 12 (C28), recorded in
  the Brief and here (Decided 31-33); G42 added to the audit; CLAUDE.md *Current Phase* and
  RESUME_CONTEXT brought up to date. Not built.
- **Open:** the office-PC checks; the "to confirm when planned" points in the Brief.

#### 03-11-2026 | Session 0 | Message 18
- **Discussed:** Two Parking Lot ideas from the author: sending through OAuth sign-in, and exporting
  and importing the settings file.
- **Decided/Built:** Both parked in the Brief (Section 9) with notes, and here (Decided 34); Claude
  checked what a profile already holds (`ui/main_window.py:700-729`). Not planned, not built.
- **Open:** the office-PC checks; the "to confirm when planned" points in the Brief.

#### 03-11-2026 | Session 0 | Message 19
- **Discussed:** The author widened Parking Lot idea (2): "not only profile, even the mail compose
  subject body and things".
- **Decided/Built:** The Parking Lot row and Decided 34 updated: the export covers the Compose tab's
  subject, body and the like (with pasted pictures — to check then), as well as the profile
  settings; whether the saved email templates go in too is Claude's reading *(inferred — to confirm
  when picked up)*. Not planned, not built.
- **Open:** the office-PC checks; the "to confirm when planned" points in the Brief.

#### 03-11-2026 | Session 0 | Consistency check (after Message 19)
- **Discussed:** Claude had the adoption documents read by three independent readers (numbering and
  cross-references; facts against the code; faithfulness to the author's answers), each finding then
  tested by a skeptic: 39 confirmed (several found twice), 14 rejected.
- **Decided/Built:** Fixed in the Brief, this log, RESUME_CONTEXT, CLAUDE.md (lines 1-78 only) and
  the audit. Corrections to what had been recorded: Q4's refusal covers Retry Failed as well as
  Resume (Decided 14, Change 1, C15, F19); the Q3 safeguard needs codes that appear nowhere in
  another client's file name — equal length is not enough (Decided 17, R22, G11); blank addresses
  are not marked on the Excel tab and fail before Outlook (R4, Change 7); Decided 34 and Message 19
  no longer present Claude's reading of "and things" as the author's; RESUME_CONTEXT's next action
  now writes the Build Plan before the safety-net tests (CLAUDE.md: the Build Plan comes before any
  code). New gap G43, reproduced by Claude: Resume Previous clicked during a run sends the emails
  still pending twice (audit 7.1; Brief C3, F19, Section 6). Office-PC check 7 marked answered by
  Q1, except OneDrive.
- **Open:** whether and when to fix G43 (the fix itself needs no business choice); the office-PC
  checks.

---

## Session 1 — Build Plan (Steps A and B) — [not started: written when the author asks for the first change]

### Step status

(One line when Step A is confirmed; one when BUILD_PLAN.md is saved)

### Exchanges

(Entries will be added automatically below)
