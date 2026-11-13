# Bug Hunt: Advanced Email Tool

> **What is this file?** The list of defects found when the whole app was read, file by file, on
> 13-11-2026, by Claude and by Codex. It is a list **for fixing**: nothing in the app was changed.
> The app is at v1.8.0 (commit `f5b9511`); no code file has changed since then.
>
> **How it fits with the other documents:** the audit (`PROJECT_AUDIT_advanced_email_tool.md`,
> Section 7) lists the gaps known at adoption, G1 to G43. This file continues that numbering with
> **G44 to G143**. The Brief decides what gets fixed: nothing here is decided until you say so.
>
> **The three files of the hunt:**
> - this file: the summary, the index of every defect, your questions, and a suggested order;
> - `BUG_HUNT_details_advanced_email_tool.md`: the full entry for each defect (what happens, when,
>   how it was confirmed, the repair, where in the code);
> - `BUG_HUNT_codex_reports_advanced_email_tool.md`: Codex's three reports, word for word.

---

## 1. In short

- **100 defects** that the audit does not list: **28 HIGH, 39 MEDIUM, 33 LOW**. Also 3 notes on
  weak tests, and 1 correction to the audit (known gap G13 cannot happen).
- **77 are new.** The other 23 are known gaps that turned out to have a further cause or a worse
  result than the audit recorded.
- **How sure:** 52 were re-checked by an independent checker (50 reproduced on dummy data, 1
  confirmed by reading the code, 1 found only partly true); 21 were reproduced by two or more
  readers working separately; 19 were reproduced by one reader; 8 were read from the code and not
  run. Not one of the 58 claims that went to a checker was refuted.
- **Already decided:** your Changes 1 to 12 would repair 1 of the 100 fully (G61) and 26 partly.
  The other 73 are covered by no decision yet.
- **Your call is needed on 29** (Section 5). The rest need no business choice.
- **Safety:** no email was sent and Outlook was never started. Every experiment ran in a throwaway
  copy of the code with Outlook blocked and made-up clients. The app's own data folder
  (`.app_data`), which holds real addresses, was never opened and was not given to Codex.

**The ones that matter most** (all HIGH, all met in ordinary use now and then):

- **After a run stops, neither button sends everyone.** When the app stops on three failures, or
  you click Cancel, Resume Previous leaves out the clients whose emails failed and then says
  "Successfully sent"; Retry Failed sends those but drops the clients not yet tried (G44, G45).
- **Resume Previous works before Outlook is connected.** Each click marks three waiting clients
  as failed without sending anything, and they are then skipped (G46).
- **An old "Retry N Failed" button sends to the new list.** It survives New Session and a new
  list, and one click emails whoever now sits on the old row numbers (G47).
- **The Send tab keeps the emails it built earlier.** After Load Profile with the Send tab open,
  Start Sending sends the previous campaign again (G48).
- **A {Name} that is partly bold, coloured or resized is never filled in.** Clients receive the
  text "{Name}". The same happens for headings with a colon, a space at either end, a line break
  or & < > (G51, G52).
- **Choosing another worksheet, or pressing Apply, resets the column mapping.** CC, BCC and
  Identifier 2 go back to "None" without a message (G54). The "Data starts at" boxes keep the
  last workbook's numbers, and Refresh then drops clients (G49).
- **Ticks change behind your back.** A search left in the Recipients box decides who is ticked
  after Refresh (G55); a saved list ticks every row that shares an address (G56); lists saved
  before 05-07-2026 tick whoever now sits on the old row numbers (G57); Apply ticks everyone
  again (G58).
- **Wrong files.** A filler such as 0, "-" or "NA" in the identifier cell attaches other clients'
  files (G59). "Remove" on the Test Matching list changes only the display (G60). Loading a
  profile after an earlier folder read leaves clients without their files until Rescan (G50).
- **A Universal BCC that was removed or replaced still gets a copy of every email** (G61).
- **The "View HTML" box can bring back an old body**, and text typed there is ignored until
  "Hide HTML" is clicked (G62).

---

## 2. How the hunt was done

| Step | Who | What |
|---|---|---|
| Read | 10 Claude readers (Fable 5.2) | Seven read one area each, to the last line; three followed flows across files (the right email to the right client, background work, what happens when something fails). 217 findings. |
| Read | Codex (gpt-6-astra, effort ultra), 3 jobs | The engine, the window, and the flows across files plus every test. 60 findings. Model and effort checked in Codex's own session logs. |
| Group | Claude | The 277 findings were grouped into distinct defects. Every code file (58) was read in full by at least one Claude reader and by Codex. |
| Check | 26 independent Claude checkers | Each tried to refute, then re-ran on dummy data, a group of findings: everything Codex reported, and everything only one or two readers had seen. 58 claims: 55 reproduced, 1 confirmed by reading the code, 2 narrower than claimed, none refuted. |
| Write up | 10 Claude writers | One plain-English entry per defect, with its line references checked against the code. |

What the words in the "Confirmed" column mean:

- **re-checked**: an independent checker made it happen again with the app's own code.
- **re-checked (code)**: it could not be run here, but a checker confirmed it by reading the code.
- **re-checked (partly)**: a checker found only part of the claim true; the entry says which part.
- **several readers**: two or more readers or checkers reproduced it separately.
- **one reader**: one reader reproduced it; nobody re-checked it.
- **code only**: read from the code; nobody ran it.

What was **not** checked, and limits what this list can promise:

- **Real Outlook.** Outlook was replaced by a stand-in, as in the app's own tests. Anything that
  depends on how Outlook itself behaves is marked as not confirmed in its entry.
- **An office PC.** Nothing ran from the shared server folder, and no real mouse or screen was
  used: clicks and timing were simulated in a hidden window.
- **Word import.** `python-docx` is not installed on this PC, so that part was read, not run.
- **Your real data.** `.app_data` was never opened, so whether old-style saved lists (G57) still
  exist in the office is not known.
- **"How often" is a judgement**, made from how the screens work, not from watching staff.

The existing tests were run once in a throwaway copy before the hunt: **82 passed** (Windows 11,
Python 3.14.10, PyQt5 5.15.11 off-screen, Outlook blocked). Until now they had run only on Linux.

---

## 3. The list

One line per defect, worst first. The full entry for each is in
`BUG_HUNT_details_advanced_email_tool.md` under the same number.

Columns: **Known gap** names the gap this one extends (blank = new). **Decided change** names
the change of yours that would repair it, fully or partly. **Your call** says whether the repair
needs a decision from you (Section 5).

### HIGH — an email or file can reach the wrong client, an email can be wrong, missing or sent twice, or work can be lost

28 defects, G44 to G71.

| No. | What goes wrong | How often | Confirmed | Known gap | Decided change | Your call |
|---|---|---|---|---|---|---|
| G44 | Resume Previous skips the clients whose emails failed earlier, then says 'Successfully sent' | now and then | re-checked | — | — | yes |
| G45 | 'Retry N Failed' after a stopped or cancelled run drops the clients not yet tried; they are never emailed | now and then | re-checked | — | — | yes |
| G46 | Resume Previous works before Outlook is connected: each click marks three waiting clients as failed | now and then | re-checked | — | — | — |
| G47 | The 'Retry N Failed' button outlives its campaign and sends the new list's rows without asking | now and then | re-checked | G1 | Change 1 (partly) | — |
| G48 | After Load Profile with the Send tab open, Start Sending sends the previous campaign again to its clients | now and then | re-checked | — | — | — |
| G49 | The 'Data starts at' boxes keep the last workbook's numbers; Refresh then silently drops clients | now and then | re-checked | G23 | Change 11 (partly) | — |
| G50 | Loading a profile after an earlier folder read leaves clients without their files until Rescan | now and then | re-checked | G14 | — | — |
| G51 | Bold, colour or size on just the name inside {Name} stops it being filled in: clients get the text {Name} | now and then | several readers | — | — | — |
| G52 | A {variable} for a heading with a colon, a space at either end, a line break or & < > is sent as typed | now and then | re-checked | G31 | — | yes |
| G53 | Workbook not found at restore or in a profile: the saved column choices and ticks are dropped, then erased | now and then | several readers | — | — | yes |
| G54 | Choosing another worksheet or pressing Apply silently resets the Column Mapping to the app's own guess | now and then | re-checked | — | — | yes |
| G55 | A search left in the Recipients box decides who is ticked after Refresh or a new list: the rest are unticked | now and then | several readers | G19 | Change 2 (partly) | — |
| G56 | Loading a saved recipient list ticks every row that shares an address, including rows never in the list | now and then | re-checked | — | — | yes |
| G57 | Saved lists made before 5 July 2026 tick whoever now sits on the old row numbers, with no warning | now and then | re-checked | — | — | yes |
| G58 | Apply, and going to another sheet and back, tick every recipient again - as Refresh does (G19) | now and then | one reader | G19 | Change 2 (partly) | yes |
| G59 | A filler in the identifier cell (0, -, ., NA) attaches other clients' files to that client's email | now and then | several readers | G11 | — | yes |
| G60 | 'Remove' and dropped files on the Test Matching list change only the display, not what is sent | now and then | re-checked | — | — | — |
| G61 | A Universal BCC address that was removed or replaced still gets a copy of every email; the new one gets none | now and then | re-checked | G4 | Change 3 (fully) | — |
| G62 | 'View HTML' box: text typed there is ignored until 'Hide HTML', and closing it can bring back an old body | now and then | re-checked | — | — | — |
| G63 | Choosing another folder during a folder read: the new folder is never read and the old folder's files go out | rarely | re-checked | — | — | — |
| G64 | New Session during a folder read keeps the old folder's files in use although no folder is shown | rarely | several readers | — | — | — |
| G65 | Emails built while the client folder is still being read go out without the clients' own files | rarely | re-checked | G14 | Change 1 (partly) | — |
| G66 | A workbook asked for while another is loading is silently skipped; Load Profile then mixes two campaigns | rarely | re-checked | — | — | — |
| G67 | Headings 'Email' and 'EMAIL' in one list: emails go to the left-hand column, Preview shows the chosen one | rarely | re-checked | — | Change 10 (partly) | yes |
| G68 | Lists not saved by Excel: a blank cell at the end of a row is sent as {MISSING} for that client | rarely | re-checked | G31 | Change 5 (partly) | — |
| G69 | A folder read that fails part-way keeps a part list and shows a normal 'Found N files' line | rarely | re-checked | G16 | — | yes |
| G70 | The session is not saved when a send starts; after a crash, Restore and Resume continue an older campaign | only when something else fails | re-checked | — | Change 1 (partly) | — |
| G71 | A progress save that fails is only logged; sending goes on and Resume later sends the same emails again | only when something else fails | re-checked | G36 | Change 9 (partly) | yes |

### MEDIUM — wrong behaviour that a careful user can notice or work around

39 defects, G72 to G110.

| No. | What goes wrong | How often | Confirmed | Known gap | Decided change | Your call |
|---|---|---|---|---|---|---|
| G72 | After choosing a variable from the pop-up in the Subject box, the cursor jumps back near the start | in ordinary use | re-checked | — | — | — |
| G73 | A Preview-mode run is reported as sent: 'Sent to: ...' and 'Successfully sent N emails!' | in ordinary use | re-checked | G3 | Change 1 (partly) | — |
| G74 | Resume Previous sends only the waiting clients ticked now, then closes the run and drops the rest | now and then | re-checked | — | Change 1 (partly) | yes |
| G75 | Clients whose email failed can be retried only until the app is closed or another run starts | now and then | re-checked | — | — | yes |
| G76 | When only failed emails are left, Resume Previous gives an untrue reason and never goes away | now and then | re-checked | — | Change 7 (partly) | — |
| G77 | A profile whose Excel file cannot be found leaves the previous list in place under the new subject and body | now and then | re-checked | G22 | Change 4 (partly) | yes |
| G78 | Coming back to the Send tab during a batch replaces its list: wrong status line, and Retry can disappear | now and then | re-checked | G43 | — | — |
| G79 | An emoji in the Subject box closes the app; a saved subject with one closes it at every restore or load | now and then | re-checked | — | — | — |
| G80 | An email with a blank subject, an empty body, or both can be sent to every ticked client with no warning | now and then | re-checked | — | — | yes |
| G81 | A saved column choice whose heading has gone is silently swapped for the app's own guess or for 'None' | now and then | re-checked | G23 | Change 11 (partly) | yes |
| G82 | Restored ticks past the end of a shorter list: wrong counts, and Save Selection or Copy closes the app | now and then | several readers | G20 | — | — |
| G83 | A session saved with nobody ticked comes back with everybody ticked | now and then | re-checked | — | — | — |
| G84 | Rows hidden or filtered out in Excel are loaded and ticked like all the others | now and then | several readers | — | — | yes |
| G85 | The second 'Select All' / 'Clear Selection' pair acts only on rows a search shows, and does not say so | now and then | several readers | — | — | yes |
| G86 | Hidden Office lock files (~$...) in the client folder are matched and attached like real documents | now and then | several readers | — | — | — |
| G87 | The 'All N emails valid' line and red cells are not redone when the To Email column changes | now and then | re-checked | — | Change 7 (partly) | — |
| G88 | The address check passes addresses that cannot exist (gmail..com) and marks some valid ones as invalid | now and then | re-checked | — | — | — |
| G89 | CC, BCC and Universal BCC addresses are never checked: no red cell, no warning, sent as typed | now and then | one reader | G6 | Change 7 (partly) | yes |
| G90 | Session restore says nothing when the saved client folder cannot be reached, and the next save forgets it | now and then | several readers | — | — | — |
| G91 | Save on the Compose tab overwrites whichever template the drop-down shows, without asking | now and then | re-checked | — | — | — |
| G92 | Leaving 'Restore Previous Session?' unanswered for 3 minutes wipes the saved session; Yes restores nothing | now and then | re-checked | — | — | — |
| G93 | Answering No to 'Restore Previous Session?' (or Esc, or the X) throws the saved session away for good | now and then | re-checked | — | — | yes |
| G94 | Pictures that arrive by Ctrl+V, by dragging from a browser or by Import File go out as links, not pictures | now and then | re-checked | G34 | — | yes |
| G95 | Opening the Send tab with a large picture in the body freezes the window and uses a great deal of memory | now and then | re-checked | — | — | — |
| G96 | Import File: Notepad 'UTF-16' and 'UTF-8 with BOM' text comes in wrong; Word tables are left out silently | now and then | re-checked (code) | — | — | yes |
| G97 | If a newly chosen folder cannot be opened, the Folder box shows it but the previous folder's files are used | rarely | re-checked | — | Change 4 (partly) | — |
| G98 | New Session while a workbook is still loading: the old list comes back by itself, ticked | rarely | re-checked | — | — | — |
| G99 | Variable pop-up: Enter can replace all the text between the '{' and the cursor, or insert nothing | rarely | several readers | — | — | — |
| G100 | One stray cell far outside the list freezes the window or slows the load, and adds invented columns | rarely | several readers | — | — | — |
| G101 | A client code stored in the workbook as 101.0 instead of 101 never matches its files | rarely | re-checked | — | Change 6 (partly) | — |
| G102 | Very long folder paths: files deep in subfolders may be left out of the scan without a message | rarely | code only | — | — | — |
| G103 | Refresh beside 'Send from' during a run switches the remaining emails to the first Outlook account | rarely | re-checked | G7 | Change 8 (partly) | — |
| G104 | The 'Send from' account is found by its place in Outlook's list; if the list changes, another account sends | rarely | one reader | G7 | Change 8 (partly) | — |
| G105 | Template names: two different names can share one file; a template named '-- New Template --' cannot be used | rarely | re-checked | — | — | yes |
| G106 | Two different saved-list names can be one file; Yes to the overwrite question destroys the other list | rarely | re-checked | — | — | yes |
| G107 | The Table button with plain tab-separated text drops a blank top-left cell; headings shift one column left | rarely | re-checked | — | — | — |
| G108 | A turn of the mouse wheel over a drop-down or number box changes it without a click (Excel tab and others) | rarely | several readers | — | — | — |
| G109 | A save of a template, profile or theme choice that stops part-way destroys the previous version | only when something else fails | re-checked | — | — | — |
| G110 | A body picture that cannot be embedded does not stop the email: it is sent anyway and counted as sent | only when something else fails | re-checked | — | — | yes |

### LOW — cosmetic or minor

33 defects, G111 to G143.

| No. | What goes wrong | How often | Confirmed | Known gap | Decided change | Your call |
|---|---|---|---|---|---|---|
| G111 | After File > New Session, 'Validate Emails' and 'Apply' stay clickable with nothing loaded | in ordinary use | one reader | — | — | — |
| G112 | The log holds more client detail than the audit lists (PANs, file names) and does not say who wrote a line | in ordinary use | code only | G36 | Change 9 (partly) | yes |
| G113 | A table pasted from Excel with the Table button loses its grid lines and cell padding | in ordinary use | one reader | — | — | — |
| G114 | The email body goes out marked 10 point although the size box shows 11; choosing 11 does nothing | in ordinary use | one reader | — | — | yes |
| G115 | An empty body is never seen as empty: '2. Compose' always gets its tick and a blank session is offered | in ordinary use | re-checked | — | — | — |
| G116 | A cancelled or stopped run is logged as 'Completed'; the 'Resuming' and 'Retrying' lines vanish at once | in ordinary use | several readers | — | Change 1 (partly) | — |
| G117 | Both themes: drop-downs show no arrow, the font-size box shows one digit, the open tab's title is cut off | in ordinary use | one reader | — | — | — |
| G118 | Attachments tab statistics and match report keep the previous list's identifiers when none is mapped | now and then | several readers | — | — | — |
| G119 | New Session leaves the old 'NO matching files' warning and both attachment switches as they were | now and then | several readers | — | — | — |
| G120 | A line break inside an Excel cell (Alt+Enter) is not kept in the email; Preview glues the lines together | now and then | one reader | — | — | — |
| G121 | The Worksheet list offers chart sheets and hidden sheets; a chart sheet left in view stops the list loading | now and then | one reader | — | Change 12 (partly) | yes |
| G122 | Saved list: a ticked client with a blank address is never ticked again; the warning shows an empty line | now and then | one reader | — | — | — |
| G123 | 'Open File Location' on a static file probably opens Explorer's default folder, not the file's folder | now and then | code only | — | — | — |
| G124 | Refresh (when already connected) and the 'Online' check can freeze the window while Outlook answers | now and then | code only | — | — | — |
| G125 | Dragging a picture file onto the body types the file's address into the email instead of the picture | now and then | several readers | — | — | — |
| G126 | The bullet and number buttons cannot switch a list off | now and then | one reader | — | — | — |
| G127 | Load on the Compose tab wipes the subject and body without asking while '-- New Template --' is shown | now and then | one reader | — | — | — |
| G128 | Send tab: the 'N without attachments' warning is shown in green once 'All have attachments' has been shown | now and then | several readers | — | — | — |
| G129 | After a Resume, 'Complete with Errors' names a different number from the 'Retry N Failed' button | now and then | one reader | — | — | — |
| G130 | A password-protected or damaged workbook only gets the message 'File is not a zip file' | now and then | several readers | — | — | — |
| G131 | 'Export Blank Template' is not blank: it holds two sample clients that load and are ticked like real ones | now and then | one reader | — | — | — |
| G132 | The box is labelled 'Data starts at: Row' but the number is used as the row of the headings | now and then | code only | — | — | — |
| G133 | Left and Right arrow keys do nothing in tables and on the OR/AND buttons: the window keeps them for Preview | now and then | one reader | — | — | — |
| G134 | Dark theme: the Subject line on the Preview tab and the list that opens after typing '{' cannot be read | now and then | several readers | — | — | — |
| G135 | At the app's default window size the Send tab's Progress log shows one line; on a smaller window, none | now and then | one reader | — | — | — |
| G136 | Shared log reaching 5 MB with two copies of the app open: log lines are lost and older logs deleted | rarely | several readers | G39 | Change 9 (partly) | — |
| G137 | The same picture used twice adds a stray attachment; a body picture with a set size is sent at full size | rarely | re-checked (partly) | — | — | — |
| G138 | Preview: the 'exceeds the 25 MB limit' warning of the last client stays on screen when nobody is ticked | rarely | one reader | — | — | — |
| G139 | If PyQt5 is missing the app fails to start without any message; other missing packages are not named | rarely | code only | — | — | — |
| G140 | The window freezes for about 20 seconds when a saved folder or file is on a server that does not answer | only when something else fails | one reader | — | — | — |
| G141 | No time limit on connecting to Outlook; Refresh looks usable but does nothing while it is connecting | only when something else fails | one reader | — | — | — |
| G142 | When the session cannot be saved, auto-save and closing the app fail without telling the user | only when something else fails | code only | — | Change 9 (partly) | — |
| G143 | The 'crash-safe' save is not forced onto the disk before the swap, and always uses one spare file name | only when something else fails | code only | — | Change 9 (partly) | — |

---

## 4. Weak tests, and one correction to the audit

Three notes on the app's own tests. They are not defects in the app, but they matter before any
repair, because the tests are the safety net:

- **T1 — The tests are not kept away from the app's real data folder: they write into its log and
  read real lists.** Nothing in the test set-up points the app's data folder at a temporary place.
  Every run of the tests creates the .app_data folders next to the code if they are missing, adds
  lines to the same app.log the office uses (159 lines for the whole suite in a copy), and the
  windows the tests build read the real saved recipient lists and templates. Only single files
  (session, send progress, lists, preferences) are redirected, and only after the window or its
  parts have already been built. Nothing real is overwritten today, but nothing prevents a later
  test from doing so.
- **T2 — Eight of the 82 tests cannot fail, or do not test what their names say.** The app behaves
  correctly today in the three cases a checker tried: a save cut off half-way keeps the last good
  session, Cancel during the pause between emails stops within a tenth of a second, and restoring a
  saved set-up switches AND back to OR. But the tests meant to guard these would not notice if they
  broke: when the checker deliberately broke each one in a copy, all 82 tests still passed. Five
  more tests are weak in the same way: the Test Matching test passes when nothing matches, the
  step-tick test never looks at the Compose tab, the 'empty session' test uses a hand-written empty
  body that the real editor never produces (so it passes while the real check fails), the
  column-mapping test never checks CC and BCC, and the 'controls disabled while loading' test really
  checks only the Browse button.
- **T3 — Two tests depend on timing: one fails now and then on a busy PC, the other could freeze a
  test run.** The reconnect test asks for a retry the instant the Send tab says 'Outlook not
  available - click Refresh to retry', a moment before the first connection attempt has completely
  ended; a retry asked in that moment is ignored without a message, and the test then fails after a
  5-second wait. It passed 2,000 times out of 2,000 on an idle PC and failed 8 times in 150 on a
  busy one. The test-email test ends before the window has received the result of the send: today
  nothing comes of it, but if that test ever failed on a PC without one add-on to the test tool and
  another test ran after it, a real 'Test Sent' box would open and the unattended test run would
  freeze instead of reporting a failure.

One correction to the audit:

- **Audit correction: known gap G13 (identifier column and capitals) cannot happen through the
  window.** This is a correction to the audit, not a defect in the app. Known gap G13 says that
  after a session restore or a profile in which a heading's capitals changed (saved as 'pan', now
  'PAN'), every client gets no matched files. Through the screens this does not happen: when a saved
  mapping is put back, the app finds the heading ignoring capitals and selects the workbook's own
  spelling in the drop-down, and the emails are always built from what the drop-down shows, so each
  client still gets their files. The capital-sensitive lookup G13 describes does exist in the part
  of the app that builds the emails, but the window never gives it a wrongly capitalised heading.

---

## 5. Questions only you can answer

29 repairs depend on what you want the app to do. Each question ends with the recommended answer
in brackets. Nothing is decided until you answer; when a change is planned, its questions are
asked again, one at a time.

1. **G44** (HIGH — Resume Previous skips the clients whose emails failed earlier, then says
   'Successfully sent') When you resume a stopped run, should the clients whose emails failed
   earlier be tried again automatically as part of Resume, or be kept on a 'Retry Failed' button
   that stays available - also after closing the app - until they are sent or you dismiss them?
   (Recommended: keep them on 'Retry Failed' and never show 'Complete' while any are left.)
2. **G45** (HIGH — 'Retry N Failed' after a stopped or cancelled run drops the clients not yet
   tried; they are never emailed) After a run stops part-way, should 'Retry Failed' and 'Resume
   Previous' stay two buttons, each keeping the other group of clients waiting, or become one
   'Continue' button that sends to everyone not yet sent - the failed and the not-yet-tried
   together? (Recommended: keep the two buttons, each keeping the other group waiting, to match the
   answer recommended in G44.)
3. **G52** (HIGH — A {variable} for a heading with a colon, a space at either end, a line break or &
   < > is sent as typed) If an email still contains curly-bracket text that the app could not fill
   in - for example {Tax: Due} or {Name } - should sending be blocked in the same way you decided
   for {MISSING} in Change 5? (Recommended: yes - block the run and list the emails and the unfilled
   text, exactly as for {MISSING}.)
4. **G53** (HIGH — Workbook not found at restore or in a profile: the saved column choices and ticks
   are dropped, then erased) After 'Excel File Not Found', when you choose the workbook yourself
   with Browse, should the app also put back the ticks saved with the session, which are remembered
   by row number and so are right only if the list has not changed, or only the column choices?
   (Recommended: put back the column choices and say so; put back the ticks only after asking you,
   and otherwise tick everyone and say that the saved ticks were not used.)
5. **G54** (HIGH — Choosing another worksheet or pressing Apply silently resets the Column Mapping
   to the app's own guess) When you pick another sheet of the same workbook, or press Apply, should
   the app keep your column choices (To Email, CC, BCC, Identifier 1 and 2) wherever the same
   headings exist, and tell you which ones it could not keep? (Recommended: yes, the same 'keep on
   switch' you chose for the heading row in Q19.)
6. **G56** (HIGH — Loading a saved recipient list ticks every row that shares an address, including
   rows never in the list) When several rows share one email address and a saved list held only some
   of them, should loading the list tick only the rows whose Identifier 1 value (for example PAN)
   was saved with the list, and - where it still cannot tell the rows apart - tick none of them and
   list them for you to tick by hand? (Recommended: yes - match on address plus Identifier 1, and
   tick none and list them when it cannot tell.)
7. **G57** (HIGH — Saved lists made before 5 July 2026 tick whoever now sits on the old row numbers,
   with no warning) When a list saved before 5 July 2026 (one that holds only row numbers) is
   loaded, should the app refuse it and ask you to tick the clients again and save a fresh list, or
   show you the names of the clients now on those rows and tick them only after you confirm?
   (Recommended: show the names, tick only after you confirm, then offer to save the list afresh)
8. **G58** (HIGH — Apply, and going to another sheet and back, tick every recipient again - as
   Refresh does (G19)) When you press Apply, or look at another sheet and come back, should the
   clients you had ticked by hand stay ticked (found again by email address, as decided for Refresh
   in Change 2) instead of everyone being ticked again? (Recommended: yes - and when you switch to a
   sheet with other clients, say that your earlier ticks do not apply there)
9. **G59** (HIGH — A filler in the identifier cell (0, -, ., NA) attaches other clients' files to
   that client's email) Which entries in the identifier column should the app treat as 'no code' -
   attaching no client files for that row and listing it before sending? (Recommended: 0, '-', '.',
   'NA', 'N/A', 'NIL' and anything made only of punctuation; add a minimum length only if the
   office's real codes are never that short.)
10. **G67** (HIGH — Headings 'Email' and 'EMAIL' in one list: emails go to the left-hand column,
    Preview shows the chosen one) If a list has two headings that differ only in capital letters,
    such as Email and EMAIL, should the app treat them as a repeated heading (keep the left one,
    rename the right one 'EMAIL (2)' and tell you, as already decided for exact repeats in Change
    10), or keep both as they are and always send to exactly the one chosen in the drop-down?
    (Recommended: treat them as a repeated heading; the plain repair, that the email goes where the
    drop-down and Preview say, does not need to wait for this answer.)
11. **G69** (HIGH — A folder read that fails part-way keeps a part list and shows a normal 'Found N
    files' line) If part of the client-files folder could not be read, should the app refuse to send
    until a complete read succeeds, or show a clear warning naming what was not read and let you
    decide to go on? (Recommended: warn, name the unread folders and ask before sending - a
    sub-folder you are simply not allowed to open would otherwise block every run.)
12. **G71** (HIGH — A progress save that fails is only logged; sending goes on and Resume later
    sends the same emails again) If the app cannot save its progress file while emails are going
    out, should it stop after the email in hand and tell you, or keep sending and only warn you that
    this run must not be resumed? (Recommended: stop after the email in hand and tell you.)
13. **G74** (MEDIUM — Resume Previous sends only the waiting clients ticked now, then closes the run
    and drops the rest) If a client still waiting from an interrupted run is no longer ticked when
    you click Resume Previous, should the app (a) refuse and name the client, (b) send the others
    and keep that client waiting so Resume is offered again, or (c) ask whether to drop that client
    from the run? (Recommended: c - ask, naming the client.)
14. **G75** (MEDIUM — Clients whose email failed can be retried only until the app is closed or
    another run starts) If a run ends with some emails failed and the app is closed, or something
    else is sent, before you retry them, what should the app do next time: offer 'Retry the N
    clients that failed last time' when the same list is loaded, or only show you a list of who
    failed? (Recommended: offer the Retry again when the same list is loaded, and show who failed.)
15. **G77** (MEDIUM — A profile whose Excel file cannot be found leaves the previous list in place
    under the new subject and body) When a profile's Excel file cannot be found or opened, should
    the app stop and change nothing, or load the subject, body and attachments anyway but clear the
    list on screen so that nothing can go to the earlier list? (Recommended: stop and change
    nothing; what a profile that names no Excel file should do is the point already left open under
    Change 4.)
16. **G80** (MEDIUM — An email with a blank subject, an empty body, or both can be sent to every
    ticked client with no warning) If the subject line is blank or the body is empty when someone
    clicks Start Sending or Send Test Email First, should the app refuse to send until it is filled
    in, as you decided for {MISSING}, or only warn once and let them send anyway? (Recommended:
    refuse to send until it is filled in.)
17. **G81** (MEDIUM — A saved column choice whose heading has gone is silently swapped for the app's
    own guess or for 'None') When a saved column choice (To, CC, BCC or an identifier) is no longer
    among the workbook's headings after a restore, a profile load or Refresh, should the app stop
    and make you choose that column again, or carry on with its own guess after showing you a
    message? (Recommended: stop and make you choose that column again.)
18. **G84** (MEDIUM — Rows hidden or filtered out in Excel are loaded and ticked like all the
    others) When rows are hidden or filtered out in the Excel list, should the app leave them out,
    load them unticked, or load and tick them as it does today? (Recommended: load them unticked and
    show a message saying how many rows are hidden in Excel.)
19. **G85** (MEDIUM — The second 'Select All' / 'Clear Selection' pair acts only on rows a search
    shows, and does not say so) While a search is showing only some rows, should the bottom 'Select
    All' / 'Clear Selection' buttons act on every client in the list, or only on the rows shown and
    say so in their captions, like the small buttons under the table? (Recommended: only the rows
    shown, with '(N shown)' in the caption - the rule the Brief already keeps for the small buttons)
20. **G89** (MEDIUM — CC, BCC and Universal BCC addresses are never checked: no red cell, no
    warning, sent as typed) When a row's CC or BCC address is invalid, or the Universal BCC is
    invalid, should the app treat it like an invalid To address under Change 7 - list the row and
    leave it out unless you confirm, and not start a run while the Universal BCC is invalid?
    (Recommended: yes)
21. **G93** (MEDIUM — Answering No to 'Restore Previous Session?' (or Esc, or the X) throws the
    saved session away for good) When you answer No to 'Restore Previous Session?', should the app
    keep that saved session so you can still bring it back later (for example from the File menu)
    until you really start new work, or should No throw it away, as it does today? (Recommended:
    keep it until real new work replaces it.)
22. **G94** (MEDIUM — Pictures that arrive by Ctrl+V, by dragging from a browser or by Import File
    go out as links, not pictures) When the body contains a picture that is only a link (pasted from
    Word, Outlook or a web page, or brought in with an .html file), should the app turn it into a
    real inline picture when the file is on this PC and refuse to send while any picture is still
    only a link, or only warn and let staff send anyway? (Recommended: turn it into a real picture
    automatically and refuse to send while any picture is still only a link, as decided for
    {MISSING} in Change 5.)
23. **G96** (MEDIUM — Import File: Notepad 'UTF-16' and 'UTF-8 with BOM' text comes in wrong; Word
    tables are left out silently) When a Word file you import has a table, should the app bring the
    table into the email body, or keep importing text only but tell you clearly that the table was
    left out? (Recommended: keep importing text only, as the Brief says, but name what was left out
    before importing.)
24. **G105** (MEDIUM — Template names: two different names can share one file; a template named '--
    New Template --' cannot be used) Two template names that differ only in punctuation, or only
    after the 50th character, count as one template today, so saving the second replaces the first:
    should the app keep both as separate templates, or refuse the second name and ask you to type a
    different one? (Recommended: keep both as separate templates.)
25. **G106** (MEDIUM — Two different saved-list names can be one file; Yes to the overwrite question
    destroys the other list) When a new list name differs from an existing one only in punctuation,
    or only after the 50th character, should the app keep both lists separately, or refuse the new
    name and ask for a different one? (Recommended: keep both as separate lists, the same answer as
    for template names)
26. **G110** (MEDIUM — A body picture that cannot be embedded does not stop the email: it is sent
    anyway and counted as sent) If a picture in the email body cannot be put into a client's email,
    should that email be held back and shown as failed so it can be retried, as already happens when
    an attachment cannot be added, or should it still go out without the picture? (Recommended: hold
    it back and show it as failed.)
27. **G112** (LOW — The log holds more client detail than the audit lists (PANs, file names) and
    does not say who wrote a line) Should the log be the office's record of each run - who was sent
    what, and by whom - or only a fault-finding aid holding as little client detail as possible?
    (Recommended: make it the record of each run - keep the client's address, add the subject, the
    files sent and the user's name - and keep it only on each PC, as Change 9 plans.)
28. **G114** (LOW — The email body goes out marked 10 point although the size box shows 11; choosing
    11 does nothing) The size box shows 11 but the body is written into emails as 10 point: should
    the body stay at 10 point with the box corrected to show 10, or should new emails really start
    at 11 point? (Recommended: stay at 10 point, so emails keep the look they have today, and make
    the box show 10.)
29. **G121** (LOW — The Worksheet list offers chart sheets and hidden sheets; a chart sheet left in
    view stops the list loading) Should sheets that are hidden in Excel be left out of the Worksheet
    list, so that a hidden sheet is never read unless it is first shown again in Excel?
    (Recommended: yes - leave hidden sheets out, together with chart sheets, which hold no rows.)

---

## 6. What your decided changes already cover

Changes 1 to 12 are decided in the Brief but not built. Built as they are worded today, they
would repair these defects:

| Decided change | Would repair fully | Would repair only partly |
|---|---|---|
| Change 1 | — | G47, G65, G70, G73, G74, G116 |
| Change 2 | — | G55, G58 |
| Change 3 | G61 | — |
| Change 4 | — | G77, G97 |
| Change 5 | — | G68 |
| Change 6 | — | G101 |
| Change 7 | — | G76, G87, G89 |
| Change 8 | — | G103, G104 |
| Change 9 | — | G71, G112, G136, G142, G143 |
| Change 10 | — | G67 |
| Change 11 | — | G49, G81 |
| Change 12 | — | G121 |

"Partly" means the entry names what would be left over. Several are worth one more sentence in
the change when it is planned, so that the change closes the whole defect.

---

## 7. A suggested order of repair

The defects fall into groups that share a cause, so one repair often closes several:

| Group of repairs | HIGH | MEDIUM | LOW | Defects |
|---|---|---|---|---|
| Start, Resume, Retry and the record of a run | 5 | 3 | 0 | G44, G45, G46, G70, G71, G74, G75, G76 |
| Something from an earlier list, profile, folder or session is still in use | 3 | 2 | 3 | G47, G48, G49, G77, G97, G111, G118, G119 |
| Two jobs overlapping, or work finishing after you moved on | 5 | 2 | 1 | G50, G63, G64, G65, G66, G78, G98, G140 |
| {Variables} in the subject and body | 2 | 4 | 1 | G51, G52, G72, G79, G80, G99, G120 |
| Columns and the column mapping | 4 | 2 | 1 | G53, G54, G67, G68, G81, G100, G121 |
| Ticked recipients and saved lists | 4 | 4 | 1 | G55, G56, G57, G58, G82, G83, G84, G85, G122 |
| Matching client files | 3 | 3 | 1 | G59, G60, G69, G86, G101, G102, G123 |
| Email addresses | 1 | 3 | 0 | G61, G87, G88, G89 |
| The Outlook account | 0 | 2 | 2 | G103, G104, G124, G141 |
| Saving the app's own files | 0 | 7 | 4 | G90, G91, G92, G93, G105, G106, G109, G112, G136, G142, G143 |
| The editor and pictures | 1 | 4 | 5 | G62, G94, G95, G107, G110, G113, G114, G125, G126, G137 |
| Import File | 0 | 1 | 0 | G96 |
| Messages and labels that mislead | 0 | 1 | 10 | G73, G115, G116, G127, G128, G129, G130, G131, G132, G138, G139 |
| The window and the themes | 0 | 1 | 4 | G108, G117, G133, G134, G135 |

A suggested order. It is only a suggestion: the order is yours.

1. **The record of a run** (G44, G45, G46, G70, G71, G74, G75, G76), together with known gaps G1
   to G3, G5 and G43 and your Change 1. This group decides whether every client gets exactly one
   email, and most of it shows up after any ordinary failure. It needs your answers on G44, G45,
   G71, G74 and G75.
2. **Stale campaigns and overlapping jobs** (the second and third groups in the table). One rule
   closes most of them: build the emails afresh at the moment Start, Resume or Retry is clicked,
   from what is on screen then, and ignore any result that arrives from an older job.
3. **{Variables}** (G51, G52, G68, G80), with your Change 5. One check closes most of them:
   anything still in curly brackets blocks sending, exactly as decided for {MISSING}.
4. **Columns, ticks and saved lists**, with your Changes 2, 10, 11 and 12.
5. **Matching client files** (G59, G60, G69, G86), with known gaps G14 and G41.
6. **Addresses and the Outlook account**, with your Changes 3, 7 and 8.
7. **Saving the app's own files**, with your Change 9.
8. **The rest**: the editor and pictures, Import File, misleading messages, the window and themes.

Before any repair: the safety-net tests that you approved come first (Decisions Log, Session 0,
Decided 28). The first of the three test notes in Section 4 should be dealt with at the same
time, so that running the tests can never touch the office's real data folder.

---

## 8. Where the evidence is

- The full entries, with the lines of code: `BUG_HUNT_details_advanced_email_tool.md`.
- Codex's reports, word for word: `BUG_HUNT_codex_reports_advanced_email_tool.md`.
- The small scripts that reproduced the defects are **not** in this repository. They sit in a
  temporary folder of the session that ran the hunt and will be lost with it. Each entry gives
  the exact steps, so a repair's own test can be written from the entry.
