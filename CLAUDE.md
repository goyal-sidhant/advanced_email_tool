# Project: Advanced Email Tool

---

## About Me
I am a CA/GST consultant, not a programmer. I build tools through
conversation with AI. Explain technical decisions in plain English.
Ask before making architectural choices. Never assume I understand
technical jargon — explain it on first use.

## Tech Stack
- **Language:** Python 3 — the default for every app (Standard 12 says when
  another language is allowed)
- **Window toolkit:** PyQt5 (an existing app kept as it is) — `PyQt5>=5.15.0` in
  `requirements.txt`. Not PySide6: this app predates that rule and stays on PyQt5.
- **Other libraries (what the code really imports):** `openpyxl` (reads the
  recipient workbook read-only, from an in-memory copy; writes only new files —
  the blank Excel template and the match report — never the user's workbook);
  `pywin32` (`win32com.client` and `pythoncom`: drives classic Outlook through
  COM); `python-docx` (imported as `docx`, only by Compose › Import File; optional).
  Windows parts of the standard library: `winreg` (theme, New Outlook check) and
  `subprocess` (`tasklist`, `explorer`). The tests use `pytest`, which is not in
  `requirements.txt`. Excel through COM and Power Query are not used.
- **Mail:** classic Outlook for Windows (desktop), driven through COM; emails go
  out from the user's own Outlook mailboxes. New Outlook cannot be automated: the
  app detects it and explains how to switch back.
- **Shared portable Python (nothing installed on staff PCs):** NO — on hold.
  Only I change this to YES, once the shared Python is set up (MASTER_GUIDE A1).
- **Runtime:** while NO, the Python installed on each staff PC plus this app's
  packages from `requirements.txt` (versions not pinned). Which Python version the
  office PCs run is not recorded in the repo (README says 3.10+) — an open question
  in the Brief. Standard 13 covers both settings; moving this app onto it (Python
  3.14 with the py launcher, a windowless `.bat` launcher) is a change I approve first.
- **Shared apps folder:** not recorded — where the app's folder lives today is an
  open question in the Brief.
- **How users start it:** today `python main.py` from the app's folder (README and
  QUICKSTART). The repo has no `Run Advanced Email Tool.bat` and no shortcut set-up.
  *(How staff actually start it is unconfirmed — open question in the Brief.)*
- **User data:** `.app_data\` inside the app's own folder (`config.py:24`): sessions,
  templates, recipient lists, the send checkpoint, preferences and the log (which
  contains client email addresses). Git ignores it; never commit it.

## Reference Documents
- `.build-docs/PROJECT_AUDIT_advanced_email_tool.md` — Full audit of the app as it is
  at adoption (v1.8.0, 03-11-2026): features F1–F25, rules R1–R46, gaps G1–G41
- `.build-docs/REBUILD_BRIEF_advanced_email_tool.md` — The app as it works today: my
  decisions, the Contracts (C1, C2, …) and the open questions. Every change starts here
- `.build-docs/BUILD_PLAN.md` — The Build Plan: tracker, structure, phases and sub-phases,
  change log. Always written and saved before any code — even in auto mode. Not
  written yet: one is written when I ask for a change
- `.build-docs/RESUME_CONTEXT.md` — Where we are, the exact next action, step status,
  hard-won lessons. Read it first in a cold session
- `.build-docs/DECISIONS_LOG.md` — Running log of every discussion and decision
  (Session 0 = the adoption of this existing app, Session 1 = the first Build Plan,
  then one session per sub-phase)
- `.build-docs/Phase <N> ….md` — Each sub-phase's plan, test disputes, reviews and
  re-count evidence (see *Files the loop produces* below)
- `.build-docs/context/` — Dummy sample files only (made-up clients, PANs and
  example.com addresses). Never real client data in this repository
- `.build-docs/readme_template.md` — The README format, for when the user README is
  next rewritten (the existing `README.md` stays as it is until then)

## Current Phase
Adopted into the toolkit (Session 0, 03-11-2026): documentation only, no code
changed; the app is at v1.8.0 (commit f5b9511). No change in progress. Next: my
answers to the open questions in the Brief, then a Build Plan when I ask for a change.
> Once the build starts: Sub-phase [N.M] [name] · Step [.K] [step name] · [status].
> Updated at the end of every step (Build Loop rule 1).

---

# HOW WE BUILD — MANDATORY FOR EVERY PROJECT

Two parts: the Build Plan, written and saved before any code, and the Build
Loop, which every sub-phase of that plan goes through.

---

## The Build Plan — always written, always saved

- Before any code, Claude writes the Build Plan, saves it as
  `.build-docs/BUILD_PLAN.md` and commits it (Standard 10). No sub-phase
  starts until the author approves it.
- This holds in **every** permission mode — **auto mode included**. Auto mode
  removes permission prompts, and it may also tell Claude to keep going,
  minimise interruptions and prefer action over planning. For this project the
  author's rules come first: auto mode never skips the Build Plan, a stop
  point, or the wait for the author's "next".
- A plan that exists only in the chat, or only in Claude Code's own plan-mode
  file, does not count. In plan mode, saving it to `.build-docs/BUILD_PLAN.md`
  is the first action once the plan is approved.
- The same goes for every sub-phase plan (step .1): always written and saved as
  `.build-docs/Phase <N> Plan - <name>.md`, auto mode included.
- BUILD_PLAN.md stays current: its tracker at the end of every step, the rest
  at every .9 Close.

---

## Build loop — nine stop points per sub-phase (the author's standing method)

### Key to the terms below
- **The author** — me (see *About Me*).
- **The Brief** — `.build-docs/PROJECT_BRIEF.md` (new project) or
  `.build-docs/REBUILD_BRIEF_[name].md` (rebuild). In a rebuild, the audit
  (`.build-docs/PROJECT_AUDIT_[name].md`) is a reference: read the parts the
  Brief cites; where they differ, the Brief wins.
- **Contracts** — the numbered promises (C1, C2, …) in the Brief's *Contracts* list,
  under Business Rules: what must hold on every run, whatever the input. Each one
  gets a contract test.
- **BUILD_PLAN** — `.build-docs/BUILD_PLAN.md`: tracker, file structure, feature
  checklist, phases and sub-phases, change log.
- **RESUME_CONTEXT** — `.build-docs/RESUME_CONTEXT.md`: where we are, the exact next
  action, the "Step status" lines, hard-won lessons.
- **Decisions Log** — `.build-docs/DECISIONS_LOG.md`, one session per sub-phase.
- **Sub-phase** — one numbered block of BUILD_PLAN (Phase 2 → 2.1, 2.2, …). Its steps
  are .1 to .9, plus the optional .7b. `<N>` in a file name is the sub-phase number
  (e.g. `Phase 2.1 Plan - Excel reader.md`); in test file names `<phase>` uses an
  underscore instead of the dot (`2_1`), because a dot breaks Python imports.
- **P-flags** — technical choices Claude made without asking, numbered across the
  whole project (P1, P2, …).
- **Lettered assumptions** — assumptions about technical choices, labelled A, B,
  C…, that stand unless the author objects ("silence = consent"). Business
  questions are never settled this way (rule 3).
- **The reference notes** — the files in `.build-docs/context/`.
- **Where files go** — every `Phase <N> …` file lives in `.build-docs/`; every test
  file lives in `tests/`.

### Roles
- **Opus** (the strongest Claude coding model) plans, codes and answers reviews. It keeps the Decisions Log,
  RESUME_CONTEXT and the git commits, and runs every multi-agent workflow.
- **Fable** (the second Claude model) writes the tests **before** any code exists and settles every disagreement.
  A different model writes the tests, so a misreading the coder shares gets caught. Keep its role narrow:
  it costs more and hits usage limits sooner.
- **Codex** (ChatGPT, on the author's OpenAI quota) checks each plan, writes the break-it tests and reviews the code.
  - It must run the model and effort set in `~/.codex/config.toml`. **Never pass `--model` or `--effort`.**
    If Codex reports any other model or effort, the break-it tests go back to Fable.
  - Drive Codex **from Bash through the codex-companion script** (or through the codex-rescue agent with its
    model set to Opus). Never through a Sonnet wrapper. Of the Claude models, only Opus and Fable are used,
    sub-agents included.
  - **Never rush Codex.** Run it in the background with no time limit, and poll
    `status <job> --wait --timeout-ms 540000` until it ends. The 9-minute poll is only a tool limit,
    never a limit on Codex. Fetch the output with `result <job>`.
  - Verify the model and effort Codex actually used from its session log (`~/.codex/sessions/**/rollout-*.jsonl`
    or `~/.codex/logs_2.sqlite`), and record it.
  - **Word Codex briefs plainly** ("damaged or unusual files", not "hostile", "attack" or "zip bomb"),
    or OpenAI's content filter may stop the run. If it does stop, resume the same session once.
- **Opus may never edit, skip, weaken or delete a Fable or Codex test.** If it believes a test is wrong,
  it leaves the test red, logs a dispute, and Fable decides.

### Rules for every step
1. **One step per "next".** Each step ends with: a checkpoint commit (Standard 10; the commit guarded so it never
   runs if the status update failed, e.g. PowerShell `if ($LASTEXITCODE -ne 0) { exit 1 }`); one status line in
   RESUME_CONTEXT ("Step status"), CLAUDE.md *Current Phase*, the Decisions Log session and the BUILD_PLAN tracker;
   a plain-English report; then STOP until the author says "next".
2. **Empty steps skip themselves** (.4 with no disputes, .7 with no findings, .8 with nothing to settle).
3. **Business questions** (anything that changes what the app does with client work) are asked one at a time, in
   plain English, with a recommended default, before the plan depends on them. **Technical choices** are made,
   logged as P-flags or lettered assumptions ("silence = consent") and reported. Never decide a business question
   in code.
4. **Phase plans are never trimmed for size.** Precision wins over length; no context lost, nothing left to guesswork.
5. **Same conversation.** "Start afresh" means a new usage window, never a new conversation. Never tell the author
   to open one; the conversation compacts itself. RESUME_CONTEXT and CLAUDE.md must still let a cold session pick up.
6. **If a usage limit stops a run:** finished files stay on disk. Resume with "finish, do not restart" prompts,
   reusing cached agents where possible. Never redo finished work.
7. **Real data:** never treat a folder as a reference without asking the author what it is and how it was made.
   When real files are needed, name exactly which (company, export, period) in a checklist file with Done / Notes /
   Answer columns, and the author downloads them by hand.
8. **Heavy steps may be split** (e.g. .3a code to green, .3b real-data gate), with a commit and a stop between.
9. Before reporting "done", run the suite yourself and show the exact count. Never claim a pass you did not see.

### The nine steps

| Step | Who | What happens | Output (done when) | Skips when |
|---|---|---|---|---|
| **.1 Plan + plan check** | Opus → Codex → Opus | Ask any business question first. Read to the last line: CLAUDE.md, the Brief, the newest Decisions Log session, RESUME_CONTEXT, BUILD_PLAN's block for this sub-phase, and the reference notes. Optionally, read-only fact-gatherers first check the code, the rules and the real files. Opus writes `.build-docs/Phase <N> Plan - <name>.md`: proof of reading; plain-English context (and what it is NOT); prerequisites, spikes and questions; the Brief contracts it relies on; the edge cases it owns, each with a test; the **locked `file ← test_file` order**; for each file the exact public API (signatures, return shapes, codes, exact texts, constants), its rules and edge cases; contract tests; test data; the real-data gate; the exit gate; open flags and P-flags (numbered on from the last used). Codex checks it read-only. Opus verifies each Codex point, then fixes it or rebuts it with evidence, and appends an answers table. | Plan status "approved for tests"; every Codex point fixed or answered; commit | — |
| **.2 Tests first** | Fable | Writes every test file from the approved plan and the Brief, in the locked order, before any code. Imports modules under test **lazily inside fixtures**, so a missing module fails only its own tests and never breaks collection of the suite. Synthetic files go in temp folders; real fixtures are read-only and the test SKIPS when the data is absent. A coverage pass checks every plan rule has a test, removes over-specification and duplicates, and checks the test files agree with each other. | New tests red **for the right reason only** (the code is missing); every earlier test still green; commit | — |
| **.3 Code** | Opus (Fable for the real-data gate) | Codes in the locked order, each file's tests green before the next, to every coding standard in CLAUDE.md. A test Opus believes wrong is left red and logged in `.build-docs/Phase <N> test disputes.md` (what it asserts, why it is wrong, exact quotes, the code as built, the change if Fable rules for the test). Technical choices made while coding are saved verbatim at the end of the plan. **Real-data gate**, if the plan has one: (1) the app runs in print/preview mode; (2) Fable re-counts independently with its own script, without reading the app's code; (3) every discrepancy is investigated file by file (a fault in the re-count is fixed; a fault in the app goes to Opus; never freeze a wrong number); (4) Fable freezes the anchors in its own test; (5) the gate passes in hard-assert mode, timed. The evidence goes in an evidence file, and the re-count script is preserved. | Suite green except logged disputes; gate passed; commit | — |
| **.4 Disputes** | Fable | Rules on each dispute from primary evidence (the spec, the real files, library source): "test is wrong" (Fable corrects its own test, minimally, keeping the guard's purpose) or "test stands" (Opus changes the code). The ruling is appended to the disputes file. | Every dispute ruled; suite green; commit | No disputes |
| **.5 Break-it tests** | Codex | Writes **new files only** (`tests/test_breakit_<phase>_*.py`), asking "how could this fail silently?" against the Brief's edge cases and contracts. Plan-silent cases are marked `# SPEC-SILENT`. Opus then runs the suite (Codex's sandbox may not be able to run tests) and classifies every failure: real defect, spec-silent, or test error. | New tests added; failures classified; commit | — |
| **.6 Fixes + code review** | Opus → Codex | Opus fixes the real defects. Spec-silent failures are either hardened (refusing an ambiguous input rather than guessing is usually right) or disputed for .8. Profile anything slow before blaming the disk. Then Codex reviews all the sub-phase's code, read-only, with no time limit; the findings ([BLOCKING] / [should-fix] / [minor]) are saved verbatim in `.build-docs/Phase <N> Codex code review.md`. **Ask the author** whether a second review in adversarial mode is wanted (step .7b). | Fixes in; review saved; commit | — |
| **.7 Answers** | Opus | Reproduces each finding first, then either fixes it test-first (a regression test in `tests/test_regressions_<phase>.py` that fails on the old code and passes on the new), rebuts it with evidence, or hands it to Fable when the fix belongs in Fable's or Codex's test files. An independent Opus checker rebuilds each scenario and confirms each fix on the old and the new code. An answers table is appended to the review file. Any change to what the app does with client work goes to the author as a question. | Every finding fixed, rebutted or handed on; suite re-run; commit | Codex found nothing |
| **.7b Adversarial review** (optional, the author's call) | Codex → Opus | Codex's adversarial-review mode (`adversarial-review --background --base <ref> "<plain focus text; known deferred items excluded>"`), over this sub-phase or over several together. Saved verbatim; Opus answers as in .7, with an independent checker. When a fix overturns a plan rule, the plan is rewritten in place, and tests pinned to the old rule become disputes for .8. | Findings answered; commit | Author declines |
| **.8 Settle** | Fable | Settles every rebuttal and every remaining dispute from primary evidence, and applies the review items handed to it. Opus applies any ruling that goes against the code. | Suite fully green; rulings logged; commit | Nothing to settle |
| **.9 Close** | Opus (+ author if a live sitting) | The live sitting first, if the sub-phase has one. Then a read-only gate check with evidence (suite, real-data gate timed, contract tests, fixture tests ran and did not skip). In parallel, on separate files: (a) the Decisions Log session entry (built; decisions; P-flags from the plan and the coders' saved choices; assumptions; disputes; break-it, review and adversarial outcomes; superseded items; open items; status with the suite count and version); (b) small tidy-ups the checkers listed; (c) BUILD_PLAN (tracker, the sub-phase's status, carry-forwards into later blocks, change log) **and the next sub-phase broken into its nine steps, not started**; (d) RESUME_CONTEXT (where we are, the exact next action, new hard-won lessons) and CLAUDE.md *Current Phase*. A cross-document consistency critic then hunts contradictions; a fixer applies the real ones. Bump the version if the author can now see or run something new. | Sub-phase closed; commit; the author pauses before the next sub-phase | — |

### Files the loop produces (per sub-phase)
`Phase <N> Plan - <name>.md` · `Phase <N> test disputes.md` · `Phase <N> Codex code review.md` ·
(optional) `Phase <N> Codex adversarial review.md` · (if a real-data gate) `Phase <N> <gate> re-count.md` plus the
preserved re-count script · `tests/test_breakit_<phase>_*.py` · `tests/test_regressions_<phase>.py` ·
one Decisions Log session per sub-phase · RESUME_CONTEXT "Step status" lines.

---

# THIS IS AN EXISTING APP

This is an existing app. The coding standards apply to new code and to the parts a change touches. Existing code is never rewritten just to meet them: ask me first.

---

# CODING STANDARDS — MANDATORY FOR ALL CODE

These standards apply to EVERY file and EVERY function in this project.
No exceptions. No shortcuts. These exist so that a non-programmer can
read the code six months later and understand what everything does,
why it exists, how it connects to everything else, and what assumptions
were made.

---

## Standard 1: Modular Folder Structure From Day One

NEVER build in a single file. NEVER start flat and split later.
Always use folder-based structure from the very first line of code:

```
my-tool/
├── Run My Tool.bat              ← What the desktop shortcut runs (Standard 13)
├── main.py                      ← Entry point ONLY. Started by the .bat, never by users.
│
├── config/                      ← All settings, constants, mappings
│   ├── __init__.py
│   ├── settings.py              ← Paths, thresholds, environment config
│   ├── constants.py             ← Fixed values (tax rates, state codes, limits)
│   └── mappings.py              ← Lookup tables (state code → name, HSN → rate)
│
├── core/                        ← Business logic, one file per domain area
│   ├── __init__.py
│   ├── gstin_validator.py
│   ├── tax_calculator.py
│   ├── invoice_validator.py
│   └── return_classifier.py
│
├── models/                      ← Data structures / object definitions
│   ├── __init__.py
│   ├── invoice.py               ← What an Invoice object looks like
│   ├── error_entry.py           ← What an Error record looks like
│   └── client.py                ← What a Client record looks like
│
├── readers/                     ← Input handling, one file per format
│   ├── __init__.py
│   ├── excel_reader.py
│   ├── csv_reader.py
│   └── json_reader.py
│
├── writers/                     ← Output generation, one file per type
│   ├── __init__.py
│   ├── excel_writer.py
│   ├── report_writer.py
│   └── json_writer.py
│
├── gui/                         ← Interface, one file per screen/dialog
│   ├── __init__.py
│   ├── main_window.py
│   ├── settings_dialog.py
│   ├── error_viewer.py
│   └── progress_bar.py
│
└── utils/                       ← Shared helpers, split by concern
    ├── __init__.py
    ├── file_helpers.py
    └── format_helpers.py
```

Not every project needs every folder. Propose only what's relevant.
But NEVER combine responsibilities into one file.

Each file does ONE thing. If you can't describe its purpose in one
sentence, split it. Before creating any new file or reorganising
the structure, tell me and get approval.

---

## Standard 2: Naming Conventions

### Files and Folders
- All lowercase with underscores: `gstin_validator.py`, `excel_reader.py`
- Folder names short and descriptive: `core/`, `gui/`, `config/`
- NO abbreviations unless universally known: `gst` is fine, `inv_val` is not

### Functions and Variables
- snake_case: `validate_gstin()`, `tax_rate`, `input_file_path`
- Function names start with a VERB: `validate_`, `calculate_`, `read_`,
  `write_`, `export_`, `parse_`, `format_`, `check_`, `get_`, `set_`
- Booleans start with `is_` or `has_`: `is_valid`, `has_errors`
- NEVER single-letter variables except `i`, `j` in short loops
- NEVER vague names: `data`, `result`, `temp`, `info`
  Instead: `invoice_data`, `validation_result`, `temp_file_path`

### Classes
- PascalCase: `InvoiceValidator`, `ExcelReader`, `MainWindow`

### Constants
- ALL_UPPERCASE: `MAX_FILE_SIZE`, `GST_RATES`, `STATE_CODES`
- ALL constants live in `config/constants.py` — NEVER hardcode values
  directly in logic files

---

## Standard 3: File-Level Documentation

Every Python file must start with this header:

```python
"""
FILE: core/gstin_validator.py

PURPOSE: Validates GSTIN format, structure, and check digit.

CONTAINS:
- validate_gstin()     — Main validation, returns valid/invalid with details
- extract_components() — Breaks GSTIN into state, PAN, entity, check digit
- verify_checksum()    — Runs government check digit algorithm

DEPENDS ON:
- config/constants.py  → STATE_CODES, GSTIN_LENGTH, CHECKSUM_CHARS
- utils/format_helpers.py → clean_string()

USED BY:
- core/invoice_validator.py → calls validate_gstin() for each row
- gui/error_viewer.py → displays validation error messages

CHANGE LOG:
| Date       | Change                              | Why                            |
|------------|-------------------------------------|--------------------------------|
| DD-MM-YYYY | Created — initial validation rules  | Section 25 CGST Act            |
| DD-MM-YYYY | Added state code "00" handling      | Client data had code "00"      |
"""
```

---

## Standard 4: Function-Level Documentation

Every function MUST have ALL of these fields:

```python
def validate_gstin(gstin_string: str, strict_mode: bool = False) -> dict:
    """
    WHAT:
        Validates a GSTIN string against format rules and checksum.
        Returns result with valid/invalid status and extracted components.

    WHY ADDED:
        Clients submit invoices with malformed GSTINs — wrong length,
        invalid state codes, PAN typos. Catches errors before Portal upload.
        Legal basis: Section 25 CGST Act, Rule 10 CGST Rules.

    CALLED BY:
        → core/invoice_validator.py → validate_invoice_row()
        → gui/main_window.py → on_single_gstin_check()

    CALLS:
        → config/constants.py → STATE_CODES, GSTIN_LENGTH
        → utils/format_helpers.py → clean_string()
        → self → verify_checksum()

    EDGE CASES HANDLED:
        - None or empty input → invalid, "GSTIN is empty"
        - Leading/trailing spaces → auto-trimmed
        - Lowercase → auto-uppercased
        - Old state code "00" → "use state-specific code"
        - Valid format, wrong check digit → specific error
        - Non-string input (int, float) → converted to string first

    ASSUMPTIONS:
        - State codes current as of [date]. New codes need
          config/constants.py update.
        - Check digit uses government spec v1.0.
        *** strict_mode defaults False — most client data has minor
            issues that should be auto-corrected. Decided Session 2. ***

    PARAMETERS:
        gstin_string (str): GSTIN to validate. May be messy.
        strict_mode (bool): If True, rejects instead of auto-fixing.

    RETURNS:
        dict: {"valid": bool, "error": str|None, "state_code": str,
               "state_name": str, "pan": str, "entity_type": str}
    """
```

For small helpers (under 5 lines), shortened format:

```python
def clean_string(text: str) -> str:
    """
    WHAT: Strips whitespace, converts to uppercase.
    CALLED BY: core/gstin_validator.py, core/invoice_validator.py
    RETURNS: Cleaned string, or "" if input is None.
    """
```

---

## Standard 5: In-Line Code Comments

```python
# GOOD — explains WHY
# GST Portal rejects amounts beyond 2 decimal places
amount = round(amount, 2)

# GOOD — cites legal basis
# LEGAL(Section 37 / GSTR-1 Table 5): B2CL threshold ₹2,50,000
if amount > B2CL_THRESHOLD and not recipient_gstin:
    table = "B2CL"

# BAD — describes WHAT (obvious from code)
# increment counter
counter += 1
```

### Special Comment Tags:
```python
# TODO(Sidhant, DD-MM-YYYY): Add GSTR-2B support. Deferred Phase 2.
# FIXME(DD-MM-YYYY): Breaks with merged Excel headers.
# HACK(DD-MM-YYYY): String date comparison — openpyxl mixed types.
# ASSUMPTION(DD-MM-YYYY): All files UTF-8. Revisit if errors appear.
# LEGAL(Section 16(2)): ITC only if supplier filed GSTR-1.
```

---

## Standard 6: No Magic Numbers

```python
# BAD
if amount > 250000:
    table = "B2CL"

# GOOD — in config/constants.py:
B2CL_THRESHOLD = 250000  # ₹2,50,000 — Section 37 / GSTR-1 Table 5

# GOOD — in core/return_classifier.py:
from config.constants import B2CL_THRESHOLD
if amount > B2CL_THRESHOLD:
    table = "B2CL"
```

ALL values in config/. Tax rates, thresholds, limits, column names,
date formats, state codes — everything.

---

## Standard 7: Consistent Error Handling

```python
def read_excel_file(file_path: str) -> dict:
    # --- Input validation first ---
    if not file_path:
        return {"success": False, "error": "No file path provided", "data": None}
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}", "data": None}

    # --- Main logic in try/except ---
    try:
        workbook = openpyxl.load_workbook(file_path)
        return {"success": True, "error": None, "data": processed_data}
    except PermissionError:
        return {"success": False,
                "error": f"File may be open in Excel: {file_path}", "data": None}
    except Exception as e:
        return {"success": False,
                "error": f"Unexpected error reading {file_path}: {str(e)}", "data": None}
```

Rules:
- NEVER let exceptions crash the app
- ALWAYS return: `{"success": bool, "error": str|None, "data": ...}`
- Validate inputs FIRST
- Catch specific exceptions first, then general Exception
- Error messages in PLAIN ENGLISH

---

## Standard 8: Type Hints

```python
def validate_gstin(gstin_string: str, strict_mode: bool = False) -> dict:
def calculate_tax(amount: float, rate: float, is_interstate: bool) -> dict:
def get_state_name(state_code: str) -> str | None:
```

---

## Standard 9: Import Organisation

```python
# Group 1: Python standard library
import os
from datetime import datetime

# Group 2: Third-party libraries
import openpyxl
from PySide6.QtWidgets import QMainWindow

# Group 3: This project's modules
from config.constants import STATE_CODES, B2CL_THRESHOLD
from core.gstin_validator import validate_gstin
```

NEVER use `from module import *`. NEVER use relative imports.

---

## Standard 10: Git Commit Messages

```
[TYPE] Short description

WHY: Why this change was made
AFFECTS: Which files/features
EDGE CASES: New edge cases handled (if any)
DECIDED: Session/decision reference (if any)
```

Types: [FEATURE], [FIX], [REFACTOR], [CONFIG], [DOCS], [STYLE]

---

## Standard 11: Assumptions Must Be Visible

If Claude Code makes ANY assumption, it MUST appear in THREE places:
1. In the code (ASSUMPTIONS field or `# ASSUMPTION()` comment)
2. In the DECISIONS_LOG entry
3. Verbally in the chat: "I'm assuming X because Y. Correct?"

No silent assumptions. Ever.

---

## Standard 12: Choosing the Language and Libraries

Python is the default for every app: in a Microsoft study, AI agents did better
in Python than in C#; the leading open-source GST tool (India Compliance) is
mostly Python; and Python covers every task below except the few marked. Use
another language only where this table says so, and only after asking me: a
different language changes how the app is started, tested and maintained.

| Task | Use | Watch out for |
|---|---|---|
| Excel/CSV processing and reconciliations (e.g. GSTR-2B vs purchase register), in workbooks that have no Power Query | `openpyxl` (no Excel needed); `rapidfuzz` for fuzzy matching | openpyxl silently drops Power Query queries (tested) and shapes when it saves a workbook; macros survive only with `keep_vba=True` and still cannot be edited. Reading a Power Query workbook with openpyxl is fine: only saving loses the queries |
| Writing into, or refreshing, a workbook that has Power Query queries | Excel itself, driven through COM with `pywin32` | Follow "Excel through COM" below |
| GST portal JSON files (create or read) | Python's built-in `json` | — |
| Text PDFs (invoices, notices) | `pdfplumber` (MIT licence) | Not PyMuPDF: its licence is AGPL (or paid) |
| Scanned PDFs (OCR) | `OCRmyPDF` with Tesseract, or Windows' built-in OCR through `winrt-Windows.Media.Ocr` | Tesseract must be installed on each PC — ask me first. Windows OCR needs the language pack, and Microsoft supports it only for packaged apps |
| Word letters and replies | `python-docx`, with `docxtpl` for templates (no Word needed) | Word-to-PDF (`docx2pdf`) needs Word installed and a logged-in user — never a scheduled job |
| Desktop windows and animations | PySide6 (the `PySide6-Essentials` package, Qt 6) | Pin it to 6.12.x while any PC runs Windows 10 (Qt 6.12 is the last Qt for Windows 10) |
| Tally Prime | XML over HTTP to port 9000 (TallyPrime running, company loaded) | JSON only where every PC runs TallyPrime 7.0 or later; ODBC is read-only |
| Email (reading mail, saving attachments, sending) | Python talking to the mail server itself, so it works whichever mail app people use (new Outlook, Thunderbird or webmail): IMAP to read (`imaplib`), SMTP to send (`smtplib`), or Microsoft Graph for Microsoft 365 mailboxes | Follow "Email" below |
| GST portal downloads | Do not automate: the app works on files a person downloads | Login needs a CAPTCHA and an OTP, and the portal's terms forbid scraping; automated access is only through GSP/ASP APIs |
| Other websites | Playwright for Python, driving the installed Edge (`channel="msedge"`) | Officially supports Windows 11, not Windows 10 |
| Data that several people change | Ask me first | Never an SQLite file in the shared folder used from several PCs at once (it can corrupt); SQLite is fine for one user on one PC |
| Scheduled jobs | Windows Task Scheduler, under the user's own account (no admin needed) | A job that reads the shared folder must "Run only when user is logged on" |
| Summaries and dashboards | An Excel report written with `openpyxl` (charts included), or charts in the app's own window | Nothing that needs a web server kept running. Qt's chart module is not in PySide6-Essentials: it needs PySide6-Addons (about 105 MB more in the shared runtime), so ask me first, or prefer an Excel report |
| Tools that must live inside Excel | VBA — only after asking me | Macros are blocked in files on an untrusted shared folder and in downloaded or emailed files; Python in Excel runs in Microsoft's cloud and cannot reach local files or Tally |
| Small helper scripts | Python | PowerShell `.ps1` scripts are blocked by default on Windows 10/11 |

### Excel through COM

- Use it only for a workbook with Power Query queries that the app writes into
  or refreshes. Before saving with openpyxl into a workbook the app did not
  create, check it for Power Query (a `customXml/item*.xml` part containing
  `DataMashup`). If one is found, use COM, or stop and tell the user. Never let
  openpyxl save over such a workbook.
- Start a separate, hidden Excel and switch off its prompts (tested):
  `excel = win32com.client.DispatchEx("Excel.Application")`, then
  `excel.Visible = False` and `excel.DisplayAlerts = False`. Never take over the
  user's own open Excel. Without `DisplayAlerts = False`, `Quit()` can wait
  forever on an invisible "save changes?" prompt.
- Always call `excel.Quit()` in a `finally` block, even after an error.
- Open the workbook with `IgnoreReadOnlyRecommended=True`. If `workbook.ReadOnly`
  is then true, someone else has it open: close it, and ask the user to close the
  workbook in Excel first.
- To refresh: set `BackgroundQuery = False` on each of the workbook's
  connections, call `workbook.RefreshAll()`, then
  `excel.CalculateUntilAsyncQueriesDone()`, and only then save. Tested on a
  query loaded to a sheet: this saved all 60,000 new rows, while a plain
  `RefreshAll()` followed at once by a save stored the old 2 rows, because the
  refresh was still running. Before saving, check that no connection's
  `Refreshing` is still true. A connection's `RefreshDate` stayed empty, so
  never use it as proof of a refresh.
- Adding a query through COM works (`workbook.Queries.Add`), but loading it
  into a new Excel table failed here (`ListObjects.Add`: "invalid argument",
  in hidden and in visible Excel). If an app needs a new query loaded into a
  table, ask me first.
- In a worker thread, call `pythoncom.CoInitialize()` first (tested: without
  it, COM calls fail), do the Excel work in a separate function, and call
  `pythoncom.CoUninitialize()` after that function returns, so no Excel object
  is still held.
- Excel must be installed on every PC that runs the app, and it needs a
  logged-in user: never a scheduled job.

### Email

- **Microsoft 365:** Microsoft Graph `sendMail` with delegated sign-in (the
  sender signs in once through MSAL; permission `Mail.Send`). Ask me first: it
  needs a one-time app registration in Microsoft Entra, which I do in the admin
  centre. Password sign-in for sending (SMTP AUTH) is switched off by default
  from the end of December 2026. Attachments over 3 MB need a draft plus an
  upload session. Use app-only sending only with `Mail.Send` limited to that one
  mailbox.
- **Other providers (IMAP and SMTP):** which provider, and how it signs in (app
  password or OAuth), is a question for me. After sending over SMTP, save a copy
  in the Sent folder with IMAP `APPEND`, unless the provider does that itself
  (Gmail does); otherwise there is no record of what went to clients.
- **Mail programs:** classic Outlook can be automated through `pywin32`, with the
  same limits as Excel above. The new Outlook for Windows cannot be automated at
  all (no COM, no VBA). Thunderbird can be automated only through a JavaScript
  add-on — ask me first.
- Passwords and sign-in tokens: Standard 13.

---

## Standard 13: How Users Start the App (No Console Window)

The people who use these apps never run code. They double-click a desktop
shortcut, the app's window opens, and no black console window appears. The
launcher and the `main.py` lines below were tested on Windows 11: started
through a Run: Minimized desktop shortcut from a network path, including a
crash, an error in a worker thread, and a missing shared Python.

### Which Python runs the app: YES or NO

The Tech Stack's *Shared portable Python* line decides it. It is **NO** for now.

**NO: the Python installed on each staff PC, as the office's apps run today.**

- Each staff PC has Python 3.14 from python.org, with its py launcher, and the
  packages in the app's `requirements.txt`, installed on that PC with
  `py -3.14 -m pip install -r requirements.txt`. Installing anything on a staff
  PC is my job: tell me exactly what each PC needs.
- The app's folder still sits in the shared apps folder. The desktop shortcut
  (see *The desktop shortcut* below), the `main.py` lines and the rules for the
  app itself stay the same. The parts about `_runtime` do not apply.
- Tests run with `py -3.14 -m pytest` from the project folder, with the same
  `pytest.ini`. After a release, compile from the app's folder with
  `py -3.14 -m compileall -q .`.
- A new package, or a new Python version, must be on every staff PC before the
  app version that needs it is released.

The launcher, `Run [App Name].bat` in the app's own folder:

~~~bat
@echo off
rem Starts GSTR-2B Reconciler with no console window, using the Python installed on this PC.
rem Desktop shortcut: point it at this file and set "Run" to "Minimized".
set "PYVER=3.14"
py -%PYVER% -c "" >nul 2>&1 || (
  powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [void][System.Windows.MessageBox]::Show('GSTR-2B Reconciler could not start: Python %PYVER% is not installed on this PC. Please tell the office in-charge.', 'GSTR-2B Reconciler')"
  exit /b 1
)
start "" /D "%~dp0" pyw -%PYVER% -B "%~dp0main.py"
~~~

It names the Python version on purpose: a bare `pyw` takes the PC's default
Python, which can be a different build (on the development PC the default is
the experimental free-threaded 3.14t). It has no `-s`, because a PC's packages
may be installed for its user only. Tested from a network path: it started the
app with the installed `pythonw.exe` 3.14, with `-B` in effect and nothing
written into the app's folder, and it showed the message box when that Python
version was missing.

**YES: the shared portable Python.** Everything below applies as written.

### Where everything lives (YES)

~~~text
\\server\share\Apps\                  ← the office shared apps folder (example name)
├── _runtime\
│   ├── python\                       ← ONE portable Python for every app: python.org's
│   │                                    official "embeddable package" plus the packages
│   └── requirements.txt              ← the Python version, then every package with its exact version
├── GSTR-2B Reconciler\               ← one released app
│   ├── Run GSTR-2B Reconciler.bat    ← what the desktop shortcut runs
│   ├── main.py
│   ├── requirements.txt              ← the packages this app imports, with exact versions
│   └── config\  core\  gui\  ...
└── [the next app]\
~~~

- Nothing is installed on users' PCs. Every app shares the one `_runtime` folder.
- The shared apps folder sits on a server share that OneDrive does not sync:
  OneDrive would upload the runtime's 4,000 files and keep them in sync.
- The shared Python is for PCs in the office. Tested from outside the office,
  over a VPN (Tailscale, 74 ms ping): loading Python and Qt from the shared
  folder took 50–100 seconds, against 1–2 seconds from a local copy. Ask me
  before giving an app to someone who works outside the office.
- All testing used Python 3.14. Move `_runtime` to a newer Python only after
  checking that every package listed has a Windows wheel for it — ask me first.
- Packages go into `_runtime` with
  `pip install --target _runtime\python\Lib\site-packages <package>==<version>`,
  run by a Python of exactly the same X.Y version as the runtime (tested). Then
  import each new package with `_runtime\python\python.exe -s` before calling it ready.
- Each app keeps its own `requirements.txt` with the exact versions of the
  packages it imports (not pytest). When releasing, install any that are missing
  from the shared `_runtime` and add them to `_runtime\requirements.txt`. Never
  upgrade or remove a package already there without asking me: every app uses it.
- Claude builds each app in a local apps folder outside OneDrive (for example
  `C:\Apps-dev\`), laid out the same way: a copy of the shared `_runtime` (plus
  `pytest`) next to the project folders.
- Tests run from the project folder with `..\_runtime\python\python.exe -s -m pytest`.
  The project root has a `pytest.ini` with `[pytest]`, `pythonpath = .` and
  `testpaths = tests`, because the portable Python never adds the project folder
  itself (tested).
- Releasing an app means copying its folder into the shared apps folder without
  `.build-docs`, `tests` and `.git`, then compiling it (see Updating below).

### The launcher with YES: `Run [App Name].bat`, in the app's own folder

~~~bat
@echo off
rem Starts GSTR-2B Reconciler with no console window, from the shared folder or a local copy.
rem Desktop shortcut: point it at this file and set "Run" to "Minimized".
set "PYW=%~dp0..\_runtime\python\pythonw.exe"
if not exist "%PYW%" (
  powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [void][System.Windows.MessageBox]::Show('GSTR-2B Reconciler could not start: the shared Python folder was not found. Please tell the office in-charge.', 'GSTR-2B Reconciler')"
  exit /b 1
)
start "" /D "%~dp0" "%PYW%" -B -s "%~dp0main.py"
~~~

Why each part is there (each one was tested):
- `start "" /D "%~dp0"` with full paths built from `%~dp0` works from a network
  path. Never `pushd` + a relative path + `popd`: from a network path the app
  silently fails to start.
- `pythonw.exe` opens no console. `-B` stops users' PCs writing files into the
  shared folder. `-s` stops packages from a person's own Python folder (in their
  user profile) leaking into the shared Python — without it, a developer PC's own
  packages showed up, so an app could work there and fail on every intern's PC.
- The message box replaces a silent failure when the shared Python is missing.
- Never a `.vbs` launcher (Microsoft is switching VBScript off, around 2027) and
  never a `.ps1` launcher (blocked by default).

**The desktop shortcut:** right-click the .bat → Send to → Desktop (create
shortcut); rename it to the app's name; in its Properties set **Run** to
**Minimized**. Tested: no console window appears, and the app's own window
opens normally (not minimized).

### Rules for the app itself

~~~python
# main.py — right after the file header (Standard 3), before any other code (tested).
import ctypes
import os
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path
from types import TracebackType

APP_DIR = Path(__file__).resolve().parent
APP_NAME = APP_DIR.name                      # the app's folder is named after the app
LOG_DIR = Path(os.environ["LOCALAPPDATA"]) / APP_NAME / "logs"
MESSAGE_BOX_ERROR_ICON = 0x10                # Windows MB_ICONERROR


def report_fatal_error(exc_type: type[BaseException], exc_value: BaseException,
                       exc_traceback: TracebackType | None) -> None:
    """
    WHAT: Writes the full error to a log file and shows a plain-English message box.
    CALLED BY: Python itself, for any error nothing else caught (sys.excepthook),
               and report_thread_error() for errors in worker threads.
    RETURNS: Nothing.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"error_{datetime.now():%Y-%m-%d_%H%M%S}.txt"
    log_file.write_text("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)), encoding="utf-8")
    ctypes.windll.user32.MessageBoxW(None, f"Something went wrong in {APP_NAME}.\n\nPlease send this file to the office in-charge:\n{log_file}", APP_NAME, MESSAGE_BOX_ERROR_ICON)


def report_thread_error(args: threading.ExceptHookArgs) -> None:
    """
    WHAT: Passes an uncaught error from a worker thread to report_fatal_error().
    CALLED BY: Python itself (threading.excepthook).
    RETURNS: Nothing.
    """
    report_fatal_error(args.exc_type, args.exc_value, args.exc_traceback)


sys.excepthook = report_fatal_error
threading.excepthook = report_thread_error
sys.path.insert(0, str(APP_DIR))             # the shared portable Python does not add the app's folder itself

# Only now import PySide6 and this project's own modules (config, core, gui, ...).
~~~

- These lines come first, straight after the file header (an exception to
  Standards 2, 6 and 9: these few values stay in `main.py` because `config/`
  cannot be imported yet — never move them into `config/`).
- Find the app's own files from `APP_DIR`, never from the current folder.
- There is no console: `print()` shows nothing. Report problems in the window,
  and log them to files in `%LOCALAPPDATA%\[App Name]\`. Worker threads send
  their errors back to the window; with `concurrent.futures`, always call
  `result()`.
- Settings and logs go in the user's own folder (`%LOCALAPPDATA%\[App Name]\`),
  never in the shared app folder.
- Passwords, app passwords, client secrets and tokens never go in code, in
  `config/` or in the shared folder (another exception to Standard 6). A password
  goes in Windows Credential Manager (the `keyring` package, per user); Microsoft
  sign-in tokens go in an encrypted per-user token cache (`msal-extensions`)
  under `%LOCALAPPDATA%\[App Name]\`. Ask me before any app keeps a password.
- Never keep a database, or any file several people write at the same time, in
  the shared folder (Standard 12).

### Updating

- Add an app's new packages to `_runtime` first — only when nobody has an app
  open, because Windows locks `pythonw.exe` and the Qt files while they run —
  and only then copy in the new app version. After a runtime change, open every
  app once.
- App files can be updated at any time; users get the change the next time they
  open the app.
- After every release or update, compile the app's Python files once, from its
  folder: `..\_runtime\python\python.exe -s -m compileall -q .` — start-up stays fast
  even though users' PCs never write into the shared folder. After changing the
  Python version in `_runtime`, re-run this in every app folder.

---

## Standard 14: Screens Follow the Approved Design and the House Look

The people who use these apps never run code, and some open an app only once
a month, so every screen must explain itself and every app should look like
the others. Screens are designed before the build in Claude Design (a Design
canvas in Claude, started with `/design` in Claude Code), tried, and approved
by me. The approved design is saved in `.build-docs/screens/`: the design's own
files in `source/`, and a PDF of every artboard if I exported one. That copy is
the record: if the live canvas and the copy differ, ask me which one stands. A
screen with no approved design is built from the Brief and the house look, and
the .1 plan says which screens had none.

- Exceptions: an app kept on PyQt5 (Tech Stack), and any screen the Rebuild
  Brief keeps as it is, keep their old look. Rebuild them to match the old
  screens (audit Section 10, and any screenshots in `.build-docs/screens/old/`),
  apply only *Screens for people who never run code*, and ask me before
  restyling them.

### The house look — every design and every app

| What | Use | Why |
|---|---|---|
| Font | Segoe UI: text 14 px, notes 12 px, headings 20 px semibold, at most one 28 px title per window | Every Windows 10 and 11 PC has Segoe UI (Segoe UI Variable is Windows 11 only). Qt's own default is 12 px (tested), smaller than Windows 11's 14 px body text |
| Colours | Light only. Window #F3F3F3; text boxes and tables white; text #1F2328; hints and notes #57606A | #F3F3F3 is the window colour of Qt's Windows 11 look in light mode (tested). Text 13.8:1, hints 5.6:1 or better |
| Main button | One per screen: #0067C0 with white text; #005A9E when pointed at or pressed | #0067C0 is the accent colour Qt's Windows 11 look reported in testing (tested). White text 5.7:1 |
| Status words | Done or Matched #18762F · Check #8A5D00 · Error or Mismatch #C62828 — always a word, never colour alone | Each 4.9:1 or better on Windows 11's #F3F3F3 and Windows 10's #F0F0F0 |
| Sizes | Controls about 30 px tall; corners 4 px; gaps of 4, 8, 12 or 16 px; 16 px from the window's edge | For mouse and keyboard, not 44 px touch targets. At 14 px text, Qt's Windows 11 look draws text boxes, drop-downs and buttons 29 px tall (tested) |
| Window | Opens at 1200 × 600 px (smaller if the Brief's smallest screen needs it), centred in the screen's free area (`QScreen.availableGeometry()`, which leaves out the taskbar) and never larger than it; it may grow, and never needs a phone layout | A 1920 × 1080 screen at 150% scale is 1280 × 720 px; the taskbar (48 px) and the title bar (about 30 px) leave about 640 px |
| Animation | 100–300 ms, only to show that something changed | Nothing waits for an animation |

Contrast figures are worked out with the WCAG formula. Brand colours instead of
these: ask me first, and keep every text colour at 4.5:1 or more.

### Screens for people who never run code

- One obvious main button per screen; every other button plain.
- The interns' own words (GSTIN, ITC, party, voucher, GSTR-2B), never
  programmer words (path, parse, exception, null).
- Nothing is blank before a choice: an empty screen says what to do first, such
  as "Choose this month's GSTR-2B file to start".
- Choosing a file always works through a Browse… button and the standard
  Windows Open dialog. Dropping files onto the window is only ever an extra,
  never instead: if the Brief prefers drag-and-drop, build both, and say so in
  the .1 plan.
- Work that takes more than about a second shows that it is working. Work that
  takes more than about 10 seconds, or any batch of files, shows "File 3 of 15"
  or a percentage, plus a Stop button where stopping is safe (what a stopped
  run leaves behind is a question for me). The work runs in a worker thread
  (Standard 13), so the window, its progress bar and its animations keep moving.
- An error says what happened (naming the file or row), why if known, and what
  to do next, next to the problem (Standard 7). A batch finishes what it can
  and lists every problem at the end, unless the Brief says to stop.
- The done screen shows the counts, the full path of the output, and buttons to
  open the file and its folder.
- Everything works by keyboard, in the order the screen reads, with a visible
  focus outline. A button that cannot be used yet says why, next to it.

### Building a screen from the design

- The design is a picture to match, never part of the app: Claude Design has no
  Qt export, so rebuild each screen in Qt Widgets (PySide6). One `gui/` file per
  screen or dialog (Standard 1), named after its artboard's title
  (`main_window` → `gui/main_window.py`; an artboard titled `main_window-error`
  shows a state of that screen).
- At the .1 Plan of a sub-phase that builds or changes a screen with an
  approved design, read that screen's files in `.build-docs/screens/` and copy
  exactly what they settle: the layout, the order of the steps, which button is
  the main one, every label and message word for word, and every state drawn.
  Take sizes, gaps and colours from the design's own files, not by eye (a CSS
  px is a Qt px), and put them in `config/` as named constants (Standard 6). If
  an artboard still uses rem, % or fr, convert it to px (1 rem = the page's
  root font size, 16 px unless set) and list it in the plan. The plan maps each
  element to a Qt widget and lists, for my approval, every difference users
  would see and what you will build instead — above all anything Qt Widgets
  cannot do simply: shadows on many items, blurred or see-through panels, a
  home-made title bar, a phone layout, pop-up "toast" messages, a chart (it
  needs PySide6-Addons — Standard 12: ask me first). Technical choices users
  would not see are P-flags. Never drop or change part of the design quietly.
- Look: the standard Windows look, in light colours. `main.py` calls
  `apply_house_look(app)` from `gui/theme.py` once, straight after creating the
  `QApplication` and before the first window. It calls
  `app.styleHints().setColorScheme(Qt.ColorScheme.Light)` (without it, a PC in
  Windows dark mode shows a dark window — tested), then sets ONE app-wide style
  sheet, never changed while the app runs. The sheet has one rule that sets
  only the font for every widget (it kept Qt's Windows look on buttons, text
  boxes, drop-downs, tick boxes, tables, tabs and progress bars — tested), and
  full rules for the app's own elements only: the main button, headings, hints
  and notes, panels and status words. Pick each one out by object name, such
  as `QPushButton#mainButton`, `QLabel#hint` or `QFrame#panel`, never by a bare
  type such as `QFrame`, which also matches labels and tables (tested). Full
  means text colour, background, border, corners, padding and font, and for the
  button its look when pointed at, pressed, disabled and focused: a fully
  styled button and label looked the same under Qt's windows11, windowsvista
  and Fusion styles, while a button given only a background colour looked
  different under each (tested). Never restyle ordinary text boxes, drop-downs,
  tick boxes, tables or scroll bars: a partly styled control loses the Windows
  look. Ordinary text keeps the Windows text colour, which the design's #1F2328
  stands in for: adding a colour to the font rule changed how drop-down arrows
  are drawn (tested). Font sizes in the sheet are in pt:
  14 px = 10.5 pt, 12 px = 9 pt, 20 px = 15 pt, 28 px = 21 pt (the same sizes:
  Qt counts 96 px and 72 pt to the inch). With px, Qt's Windows 11 look logs a
  font warning when it sizes a drop-down; 10.5 pt draws the same pixels without
  one (tested). Fill the colour constants into the sheet with Python's
  `string.Template`, not `str.format`, which trips over the sheet's braces.
- Never paste the design's CSS into the style sheet. Qt ignores CSS it does not
  know, such as box-shadow and transition, and a media query such as
  `@media (max-width: 600px)` or a `:root` block makes it stop reading the sheet
  there, so every rule after it is lost (tested). Qt reports both only in its
  message log, which an app without a console never shows, so the exit gate of
  a sub-phase that builds or changes a screen includes a style-sheet test: it
  applies the app's sheet, builds each window and, in each of its states, calls
  `ensurePolished()` on the window and on every widget in
  `window.findChildren(QWidget)`, while catching Qt's messages with
  `qInstallMessageHandler()`, and fails on "Unknown property" or "Could not
  parse". Tested: Qt reports "Could not parse" as soon as a window is built,
  but "Unknown property" only once a widget its rule matches is polished.
  Building the windows alone missed it, and so did a second `ensurePolished()`
  on the window, or a `grab()` of it while shown, after a later state added a
  label; polishing every widget caught it.
- Animations only where the Brief or the design asks for one, built with Qt's
  own `QPropertyAnimation` or `QVariantAnimation`, and skipped when Windows
  asks for less motion: keep the hints object in a variable,
  `hints = app.styleHints()`, then check
  `hints.accessibility().motionPreference() == Qt.MotionPreference.ReducedMotion`
  (Qt 6.12). The one-line `app.styleHints().accessibility().motionPreference()`
  raises RuntimeError in PySide6 6.12.0 (tested). Never make work wait for one.
- A table that can grow past a few hundred rows is a `QTableView` with a model,
  never a `QTableWidget` (tested: 1,000,000 rows painted in 0.07 s; a
  `QTableWidget` took 4.7 s for 50,000 rows).

### Checking the built screens against the design

- A sub-phase that changes how a screen looks (a new window, element or state,
  or a changed layout or wording) has a live sitting at its .9 Close. One that
  only wires logic behind an unchanged screen needs none for this standard, and
  its .9 report says the screens did not change. Before the sitting, check that
  each new or changed window fits the smallest screen in the Brief at its
  Windows scale.
- When the screen has an approved design, do the screen check at the .9 Close,
  just before the live sitting. Open each window the sub-phase changed on the
  real Windows platform (never `-platform offscreen`, which draws differently —
  tested), put it in each changed state the design draws, with the design's
  made-up data, and save a picture of each with `QWidget.grab()` in
  `.build-docs/screens/built/`. Compare each picture with its artboard (its
  page of the design PDF, if there is one, and the design's own files for exact
  sizes, colours and wording), and list in plain English every difference a
  person would notice — position, size, colour, wording, a missing or extra
  element — in `.build-docs/Phase <N> screen check.md`. At the live sitting,
  open each pair for me, with the list.
- A change I approve there is made on the canvas too (by you, or by me), and
  the copy of the design's files in `.build-docs/screens/source/` is replaced
  and committed with the code; I export a new PDF only if I want one. Later
  screen changes take the same order: the design first, then the code. A small
  wording or spacing fix may go into the code first, with the canvas updated in
  the same sub-phase. Whenever `source/` is replaced and I export no new PDF,
  add "(out of date)" to the old PDF's file name, so no later screen check
  compares against it. Claude Design has no version history yet, so these
  copies in git are the history.
- Without an approved design, the live sitting shows the built screens on their
  own, and screen changes go straight to a Change Request (Template 2 in the
  pipeline's Part 3), with no design to update first.
- If any office PC still runs Windows 10, ask me to open the app once on one
  before release: there its windows use the older Windows look.
