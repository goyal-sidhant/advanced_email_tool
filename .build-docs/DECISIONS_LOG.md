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
  - The audit (`PROJECT_AUDIT_advanced_email_tool.md`) describes 25 features, 46 rules and 41 gaps.
    The app's 82 tests pass (Linux, Outlook faked). The most serious gaps, each reproduced on dummy
    data: an identifier picks up other clients' files when one is contained in another (G11);
    Resume and Retry send without asking, Resume can hit another file's rows, and a Preview-mode run
    counts as sent (G1-G3); a Universal BCC typed last is ignored (G4); Excel Refresh and session
    restore change the hand-picked recipients (G19, G20); a profile keeps the previous campaign's
    static attachments (G22); some exported workbooks load only their first rows (G25); `{MISSING}`
    can reach clients (G31).
  - Not possible in this cloud session: opening the window, Outlook, Excel or the office share.
    What needs an office PC is listed under *Open*.
- **Decided** (all by the author, in the adoption request):
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
      apply. How staff start the app is still open.
  12. **Q2 answered (author, 03-11-2026):** every PC that sends uses classic Outlook. G37 (New
      Outlook cannot be automated) stays a future risk only. The mailbox provider is still open.
  13. **Q3 answered (author, 03-11-2026):** "the identifiers are selected so that it doesn't hit
      other client's file". So "contains" matching stays as it is and no overlap check is added;
      G11 is an accepted risk, covered by how the office chooses identifiers. Rule R22 and Contract
      C7 unchanged. Not affected by this answer, still open: G12 (AND with one identifier blank),
      G14 (stale results after a Rescan), G15 (statistics in AND mode), G41 (missing client files
      hidden by static files).
  14. **Q4 answered (author, 03-11-2026): "Fix all three"** — Change 1 in the Brief: Resume and
      Retry Failed ask first; Resume goes ahead only when the same Excel file and the same clients
      (checked by email) are loaded; a Preview-mode run never counts as sent. New or extended
      contracts C4, C15, C16 — decided, **not yet built**: it is built only when the author asks for
      the change, through a Change Request and a Build Plan. Until then the proposed safety-net test
      T6 pins today's behaviour; the change replaces those pins with tests of the new rule.
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
- **Proposed (not yet approved) — safety-net tests.** Tests that pin what the app does **today**,
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
    clients (PAN-like IDs, client codes 101 and 1010, names such as "Ram Kumar" and "Shriram
    Traders", an amount of 150000, 1234.56, a date, a percentage, a blank address, a ";" pair and a
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
  - Business questions Q1-Q17 — the full list, with recommended defaults, is at the end of the
    Brief. Asked first, one at a time: Q1-Q4 — answered 03-11-2026 (Decided 11-14).
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
    7. Where the app's folder and its `.app_data` live, and whether several users or OneDrive share
       them (G24, G36).
    8. ~~Whether any sending PC has New Outlook switched on (G37).~~ Answered by the author (Q2):
       classic Outlook on all sending PCs.
    9. A dummy copy of a workbook exported by your other software loads all its rows (G25).
    10. Because the app runs from the shared server folder (Q1): with dummy data only, open it on two
        PCs at once and note what each sees — the "Restore Previous Session?" prompt and the
        "Resume Previous" button may show the *other* person's work (G24).
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

---

## Session 1 — Build Plan (Steps A and B) — [not started: written when the author asks for the first change]

### Step status

(One line when Step A is confirmed; one when BUILD_PLAN.md is saved)

### Exchanges

(Entries will be added automatically below)
