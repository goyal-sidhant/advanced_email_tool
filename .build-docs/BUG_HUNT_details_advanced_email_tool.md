# Bug Hunt, the full entries: Advanced Email Tool

> **What is this file?** The full entry for every defect found by the bug hunt of 13-11-2026:
> G44 to G143, then the three notes on weak tests. The summary, the index, the questions for the
> author and a suggested order of repair are in `BUG_HUNT_advanced_email_tool.md`. Read that first.
>
> The app is at v1.8.0 (commit `f5b9511`); no code file has changed since then, so every line
> number below is for that code. Nothing in the app was changed by the hunt.

**How to read an entry**

- **What happens / When**: in plain English, with the words on the screen.
- **How serious, how often**: HIGH = an email or file can reach the wrong client, an email can be
  wrong, missing or sent twice, or work can be lost. MEDIUM = wrong behaviour that a careful user
  can notice or work around. LOW = cosmetic or minor. "How often" is a judgement from how the
  screens work, not from watching the office.
- **How it was confirmed**: "re-checked" means an independent checker made it happen again with
  the app's own code, on dummy data, with Outlook replaced by a stand-in. "Reproduced by several
  readers" means two or more readers did so separately. "Read from the code only" means nobody ran
  it. Anything that depends on how the real Outlook, Excel or Windows behaves is named as not
  confirmed.
- **Known gap**: the audit gap (G1 to G43) that this entry extends, with what is new.
- **Already decided**: the change in the Brief (Changes 1 to 12, decided, not built) that would
  repair it, and what would be left over.
- **The repair**: what the repair would do, not how to code it. A repair is planned through the
  Brief and the Build Plan like any other change.
- **Your call**: the one question for the author, with the recommended answer in brackets.
- **Where in the code**: files and line numbers, the most decisive first.

---

## HIGH (G44 to G71)

### G44 — Resume Previous skips the clients whose emails failed earlier, then says 'Successfully sent'

- **What happens:** After a run stops or is cancelled with some emails failed, Resume Previous sends
  only the clients not yet tried and leaves out the ones that failed, although the app's own stop
  message says 'Fix the problem, then use Resume to continue'. When the resumed emails go through,
  the app says 'Successfully sent N emails!' and 'Complete: N sent, 0 failed' and closes the run.
  The 'Retry N Failed' button is hidden the moment Resume starts and comes back only if one of the
  resumed emails also fails, and the earlier 'Failed' lines are cleared from the Progress list. The
  clients that failed earlier are never emailed and nothing on screen names them.
- **When:** A run is interrupted after at least one email has failed: the app stops itself after
  three failures in a row (for example Outlook stops answering, or three clients' attachments cannot
  be added), or the user clicks Cancel after a failure. The user then clicks Resume Previous -
  straight away, or after closing and reopening the app, when it is the only button offered - and
  every resumed email goes through.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Four readers reproduced it and Codex reported it
  in all three jobs; the checker reproduced it on the real main window with a simulated Outlook
  (list of 5: the three failed clients never emailed, 'Successfully sent 2 emails!', run closed),
  also with a restart in between and after a Cancel, and two other checkers reproduced it
  independently. The Outlook failures were simulated, not real.
- **The repair:** Never close a run or report plain success while any of its clients is still
  failed: after Resume keep 'Retry N Failed' on offer for every failure of the whole run (also after
  the app is closed) and end with a summary that names every client not sent. Make the stop message
  name the button that really sends the failed emails again.
- **Your call:** When you resume a stopped run, should the clients whose emails failed earlier be
  tried again automatically as part of Resume, or be kept on a 'Retry Failed' button that stays
  available - also after closing the app - until they are sent or you dismiss them? (Recommended:
  keep them on 'Retry Failed' and never show 'Complete' while any are left.)
- **Where in the code:** data/checkpoint.py:288-292; ui/tab_send.py:628-631, 723-733, 755-757,
  767-773; core/outlook_sender.py:511-516, 30-32

### G45 — 'Retry N Failed' after a stopped or cancelled run drops the clients not yet tried; they are never emailed

- **What happens:** When a run stops part-way with some clients failed and others not yet tried, the
  Send tab shows 'Retry N Failed' and 'Resume Previous' side by side. Clicking Retry sends only the
  failed ones and replaces the app's record of the run with a new one that lists just those clients.
  When they go through, the app says 'Successfully sent N emails!', both buttons disappear, and the
  clients not yet tried get nothing and are mentioned nowhere, even after the app is closed and
  reopened. The only button left is Start Sending, which emails every ticked client again, including
  those who already have the email.
- **When:** A run is interrupted - stopped by three failures in a row, or cancelled - while it has
  at least one failed client and at least one client not yet tried, and the user clicks 'Retry N
  Failed' before 'Resume Previous'. If the retried emails fail again instead of going through,
  Resume Previous answers 'The remaining recipients are not in the current email list' and the
  clients not yet tried are lost all the same.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Two readers reproduced it (two more inside their
  G44 findings), Codex reported it in two jobs, and the checker reproduced it on the real main
  window with a simulated Outlook (list of 5: clients 4 and 5 never emailed, progress file left
  'completed' with planned rows [0, 1, 2]), also after a Cancel; two other checkers reproduced it
  independently. The checker's bracketed answer here was one 'Continue' button while its G44 verdict
  recommended keeping Retry: I aligned both questions on the answer that keeps contract C3 and
  Change 1 as worded.
- **The repair:** 'Retry Failed' must work inside the same record of the run, so the clients not yet
  tried stay waiting and 'Resume Previous' is still offered. 'Complete' must never be shown while a
  planned client is neither sent nor given up by the user.
- **Your call:** After a run stops part-way, should 'Retry Failed' and 'Resume Previous' stay two
  buttons, each keeping the other group of clients waiting, or become one 'Continue' button that
  sends to everyone not yet sent - the failed and the not-yet-tried together? (Recommended: keep the
  two buttons, each keeping the other group waiting, to match the answer recommended in G44.)
- **Where in the code:** ui/tab_send.py:791-795, 745-753, 767-773, 730-733;
  data/checkpoint.py:81-101

### G46 — Resume Previous works before Outlook is connected: each click marks three waiting clients as failed

- **What happens:** When an earlier run was left unfinished, the Send tab shows Resume Previous and
  lets it be clicked while the tab still says 'Connecting to Outlook…' or 'Outlook not available';
  only Start Sending is greyed out. A click sends nothing: in about two seconds the next three
  waiting clients are recorded as failed and the run stops with 'Outlook may be unavailable ... use
  Resume to continue', and every further click records three more. Once Outlook is connected, Resume
  sends only the clients not yet recorded and ends with 'Successfully sent N emails!'; the others
  are never emailed (6 of 10 in the re-check). If Outlook finishes connecting in the middle of such
  a run, Start Sending becomes clickable while emails are going out and a second run can be started
  on top of the first.
- **When:** An unfinished run is on record (cancelled, stopped after three failures, or the window
  was closed during a run). The app is started, the same list is back on screen, and Resume Previous
  on the Send tab is clicked while Outlook is still connecting or has failed to connect - for
  example because Outlook was closed and is slow to open. The second-run part also needs Outlook to
  finish connecting within those two seconds.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Four readers reproduced it (two reported it
  inside G44) and Codex did not report it; the checker reproduced it on the real main window with a
  simulated Outlook that does not connect (10 clients: two early clicks marked rows 2-7 failed, the
  later Resume sent 2 and six were never emailed), and also the second overlapping run (extends G43)
  and the too-early Resume leaving from the first mailbox (extends G7). How long a real Outlook
  takes to connect was not measured.
- **The repair:** Offer Resume Previous and Retry Failed only when Start Sending is offered (Outlook
  connected and no run going), and switch Start Sending on in one place that checks both. If Outlook
  is not connected when a run is about to start, stop before the first email and record nothing
  against any client.
- **Where in the code:** ui/tab_send.py:463-470, 667-696, 777-800, 70-73, 391, 736;
  core/outlook_sender.py:295-296, 511-518

### G47 — The 'Retry N Failed' button outlives its campaign and sends the new list's rows without asking

- **What happens:** After a run with failures, the 'Retry N Failed' button stays on the Send tab for
  the rest of the sitting: File > New Session, browsing to another list or loading a profile do not
  remove it, and the old run's lines stay in the Progress list. The button remembers only row
  numbers, so one click sends the subject and body now on screen to whoever sits at those row
  numbers in the list now on screen, at once and without a question, and then says 'Successfully
  sent N emails!'. The clients whose email had really failed get nothing, and the clients emailed by
  the click get a second copy when Start Sending is used.
- **When:** A run ends 'Complete with Errors' and Retry is not clicked. In the same sitting the user
  starts another campaign (File > New Session, Browse… to another list, or Load Profile), opens the
  Send tab and clicks the leftover 'Retry N Failed'. It sends only if rows with the old failed row
  numbers are ticked in the list now loaded; otherwise it says 'Nothing to Retry' and disappears.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Three readers reproduced it and Codex did not
  report it; the checker reproduced three routes on the real main window (New Session then another
  list, New Session then the same list with a draft letter, Browse to another list): each time two
  emails went out with no question and the clients that had really failed got nothing. The Load
  Profile route and the 'Nothing to Retry' branch were read from the code only; severity follows the
  checker (HIGH, readers said MEDIUM) because its runs showed a draft and another campaign's letter
  reaching clients.
- **Known gap:** extends G1. G1 and G2 describe Resume by row number and the missing question; new
  here is that the Retry button, its remembered row numbers and the old Progress lines are never
  cleared, so Retry reaches a later campaign.
- **Already decided:** Change 1: partly - Retry would ask first and refuse when the file or the
  clients differ, but the same list with a different subject and body would still go out after one
  Yes, and nothing decided removes the leftover button, its remembered rows and the old Progress
  lines
- **The repair:** Hide 'Retry N Failed' and forget the failed rows whenever the campaign changes
  (New Session, another Excel file, a loaded profile), keep them across a Refresh of the same list,
  and give the Send tab a reset that New Session uses. With Change 1, tie Retry to the run it
  belongs to.
- **Where in the code:** ui/tab_send.py:777-800, 450-470, 767-773; ui/main_window.py:617-639

### G48 — After Load Profile with the Send tab open, Start Sending sends the previous campaign again to its clients

- **What happens:** The app prepares the batch of emails at the moment the Send tab is opened and
  keeps it until the user goes to another tab and comes back. If a profile is loaded from the menu
  while the Send tab is in front, tabs 1 to 4 change to the new campaign but the Send tab keeps the
  old batch. Start Sending then sends the old campaign (old clients, old letter, old attachments)
  and reports 'Successfully sent N emails!'; if that campaign had just been sent, its clients get it
  a second time and the new campaign's clients get nothing. Send Test Email First, Resume Previous
  and Retry Failed use the same old batch.
- **When:** The Send tab is in front with a campaign built, most naturally straight after sending
  it. Profile > Load Profile... (or Ctrl+Shift+O), choose the next profile, Yes, OK on 'Profile
  loaded successfully!', then Start Sending and Yes without opening another tab first; the only
  hints are the old count in the question and in 'Recipients: N'. Opening any other tab and coming
  back rebuilds the batch correctly. A second, rarer way in (it needs a big list or a slow server
  folder and a quick user): opening the Send tab while a workbook is still loading after Browse...,
  Refresh or Load Profile builds the batch from the list that was on screen before - with a profile,
  the new letter addressed to the old list's clients - and it is not rebuilt when the load ends.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Nine readers and Codex (window-5, flows-5)
  reported it; a checker reproduced it through the real window with a fake Outlook (campaign A's
  three clients emailed twice, campaign B's none) and tried every menu action and shortcut reachable
  from the Send tab - only Load Profile does this - and three checkers reproduced it independently.
  The still-loading route was reproduced only with the workbook load slowed on purpose (a real
  5,000-row list loaded in about 1.1 s from a local disk); real Outlook was not used.
- **The repair:** Build the emails afresh from what the window holds at the moment Start Sending,
  Send Test Email First, Resume Previous or Retry Failed is clicked, and refuse while a workbook is
  still loading or a folder is still being scanned. In addition, take the user back to tab 1 after
  Load Profile, as New Session already does.
- **Where in the code:** ui/main_window.py:443-445 (the batch is built only when the tab changes to
  Send), 473-488 (built and handed to the Send tab), 772-896 (Load Profile neither changes tab nor
  rebuilds; 'Profile loaded successfully!' at 814), 617-639 (New Session is safe because it jumps to
  tab 1, line 637); ui/tab_send.py:450-458 (the batch is kept), 582-614 (Start Sending sends it as
  it stands, line 614), 519-567, 667-696 and 777-800 (the test email, Resume and Retry pick from the
  same batch); ui/tab_excel.py:389-424 (a workbook load finishes later, in a worker thread)

### G49 — The 'Data starts at' boxes keep the last workbook's numbers; Refresh then silently drops clients

- **What happens:** The 'Data starts at' Row and Column boxes keep the last number put into them:
  File > New Session and choosing another workbook do not set them back to 1. The next list is read
  correctly from row 1 while the Row box still shows, say, 3; the first click on Refresh or Apply
  then re-reads that list from row 3 with no message. In the checker's test 6 clients became 4, the
  second client's details became the column headings and the To and Identifier choices changed by
  themselves; with a plain circular every sign stayed green, 4 emails went out with 'Successfully
  sent 4 emails!' and the first two clients got nothing, and with a personalised email the 4 emails
  also carried '{MISSING}' and no client files. A left-over Column number cuts off the first column
  instead: nobody is dropped, but the Name column disappears and every email says {MISSING}.
- **When:** All in one sitting (closing and reopening the app puts the boxes back to 1): a list
  whose headings are below row 1 is read with Row = 3 (or Column = 2) and Apply; then File > New
  Session, or simply Browse... or a drop of another workbook whose headings are in row 1; then
  Refresh (for example to pick up a correction just saved in Excel) or Apply. It is also reached
  with no earlier list, when a number is typed into the Row box, Apply is not pressed, and Refresh
  is clicked later. The office has lists with headings below row 1, so mixed layouts in one sitting
  are ordinary; before sending, the only signs are a lower row count and headings that show one
  client's details.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Two readers reproduced it and Codex reported it
  in all three jobs; a checker reproduced it with the app's real window and buttons and a fake
  Outlook - the New Session route, the plain Browse route, Apply, the Column box, and a control run
  in which Refresh kept all 6 clients. Nothing material is unconfirmed (all runs were off-screen, on
  dummy data).
- **Known gap:** extends G23. G23 and rule R10 record that the boxes can show another row than the
  one read; new is that the left-over number then makes Refresh or Apply silently drop clients from
  a list that had loaded correctly, and that New Session does not reset the boxes.
- **Already decided:** Change 11: partly - a newly chosen file would start at row 1, column 1 with
  the boxes showing what was read, so the left-over number would be gone; the Brief's wording does
  not say what Refresh does with a number changed in a box and never applied, which it uses today
  (Change 5 would block only the '{MISSING}' variant, not the plain-circular one)
- **The repair:** Set both boxes back to 1 on New Session and whenever a workbook is newly chosen,
  dropped, restored or loaded from a profile, and make Refresh re-read the list with the row and
  column it was actually read with, not whatever the boxes hold at that moment. Show a message
  whenever a Refresh changes the headings or loses a chosen column.
- **Where in the code:** ui/tab_excel.py:793-823 (New Session never resets the two boxes), 179-192
  (they are set to 1 only when the tab is built), 379-387 and 1003 (a newly chosen, restored or
  profile workbook is read without them), 696-697 and 708-713 (Refresh uses whatever they hold),
  876-877 (so does Apply); core/excel_handler.py:150-166

### G50 — Loading a profile after an earlier folder read leaves clients without their files until Rescan

- **What happens:** Loading a profile reads the new client list and the new client folder at the
  same time. If a folder was already read earlier in the same sitting, the app works out which
  client has which files the moment the list arrives - while the new folder is still empty or half
  read - remembers those answers, and keeps using them after the folder has been read completely.
  The Attachments tab then shows, for example, 'Found 60 files' beside '0/60 identifiers matched',
  and the emails are built without the clients' own files, or with only one of two documents while
  every count looks right. With a cover letter attached to everyone, the Send tab still says 'All
  have attachments'.
- **When:** (1) Earlier in the same sitting a folder holding at least one file was read: Yes to
  'Restore Previous Session?', a Browse..., or an earlier profile. (2) Profile > Load Profile with a
  profile whose workbook and folder both exist; nothing else is clicked. (3) The folder is still
  being read when the list arrives: with nothing slowed, on a local disk, 1,260 files in 60
  sub-folders went wrong on every load, 600 files in one folder only when the 'Profile loaded
  successfully!' box appeared at once, and 60 files in one folder mostly escaped - so sub-folders,
  thousands of files or a slower server folder are the risky cases. It stays wrong until Rescan,
  choosing the folder again, New Session or a restart; a profile loaded as the very first action of
  a sitting is safe.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Two readers reproduced it; the checker
  reproduced it through the real window with a slowed folder (0/60 matched, 60 emails without their
  file, 'All have attachments' once a cover letter was added) and with nothing slowed on a local
  disk, and a second checker reproduced it independently (9,000 files in sub-folders: all 60 emails
  without any of the client's files). Not confirmed: the time the real 'Profile loaded
  successfully!' box takes to appear (stood in for by a pause of 0 to 150 ms) and the speed of the
  office's server folder; Codex did not report it.
- **Known gap:** extends G14. G14 needs a Rescan plus a look-up at the wrong moment; here one
  ordinary menu action (Load Profile) sets off the same fault with no extra click, because the file
  count left by the earlier folder is not reset.
- **The repair:** Never work out or remember which files belong to a client while a folder is still
  being read: read the folder into a separate list, swap it in when finished, forget the earlier
  answers, then work out the statistics afresh. Reset the file count whenever the folder changes.
- **Where in the code:** core/attachment_matcher.py:57-61 (the file count is not reset when the
  folder changes; it is set only at 94), 124-137 (answers remembered; emptied only at 82, when a
  read starts); ui/tab_attachments.py:491-492; ui/main_window.py:841 and 881 (list load and folder
  read started together), 362-378

### G51 — Bold, colour or size on just the name inside {Name} stops it being filled in: clients get the text {Name}

- **What happens:** In the body, a variable is filled in only when the whole of it, both curly
  brackets included, carries one and the same formatting. If Bold, Underline, a size or a colour is
  put on the name alone (the Italic, font and highlight buttons work the same way), the app no
  longer sees a variable and every client receives the raw text, for example 'Dear {Name}' with Name
  in bold. Nothing turns into {MISSING}, the line under the editor does not warn (it says 'No
  variables used (static email)' or lists only the other variables) and the run ends with
  'Successfully sent'; only the Preview tab shows the unfilled text. If the formatting covers one
  curly bracket but not the other, the client gets {MISSING} instead and the rest of that paragraph
  changes its look.
- **When:** Compose tab, body only (the Subject box has no formatting). The user clicks inside the
  name of a variable, or double-clicks it (a double-click selects the word without its curly
  brackets), or selects one word of a two-word name such as {Client Name}, and then presses B or U
  or picks a size, font or colour; with nothing selected the buttons act on just the word the cursor
  is in. Ctrl+B pressed while typing in the Subject box also acts on the word where the cursor last
  stood in the body (seen by one reader). Selecting the whole variable, both curly brackets
  included, before formatting works. No special data or saved state is needed, and every client in
  the run is affected.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by several readers. Four readers reproduced it independently
  off-screen and a checker reproduced it again as an extra finding (real window, real B button and
  double-click, Start Sending against a fake Outlook: body handed over 'Dear {Name}, your return is
  filed.', no {MISSING}); Codex did not report it and there was no dedicated re-check verdict.
  Cause: _merge_format selects WordUnderCursor, Qt then saves a span tag with a style between the
  two brackets, and the variable pattern at core/template_engine.py:28 cannot match because the
  style text holds ':' and ';'; same family as G31, not run on a visible screen or with real
  Outlook, and the Ctrl+B-in-Subject route was seen by one reader only.
- **The repair:** Look for variables in the text the user sees, not in the saved form of the body,
  so that formatting can no longer split one; the formatting buttons could also take in the whole
  {...} when the cursor or selection touches one. Before sending, stop while any email still shows a
  column name in curly brackets - Change 5 as worded looks only for {MISSING} and would not catch
  this, and whether to block is the question asked under G52.
- **Where in the code:** ui/components/rich_text_editor.py:357-363; core/template_engine.py:28,
  71-90, 126-153; core/email_builder.py:249-251; ui/components/rich_text_editor.py:302-355, 441-448,
  133-140; ui/tab_compose.py:330-354

### G52 — A {variable} for a heading with a colon, a space at either end, a line break or & < > is sent as typed

- **What happens:** The Insert Variable buttons and the '{' pop-up list offer every column, but some
  headings can never be filled in. A variable is left exactly as typed, in the subject and in the
  body, when its heading contains a colon or semicolon (this includes a heading that Excel stores as
  a date or a time) or starts or ends with a space or line break; in the body only, the same happens
  when the heading contains &, <, > or a double quote, or has a line break inside it. Every client
  then receives the raw text, for example {Tax: Due} or {Name }: nothing turns into {MISSING}, the
  line under the editor says 'No variables used (static email)' or shows a green tick that does not
  mention the problem, and the run ends with 'Successfully sent'. For a heading with a space at its
  end, typing {Name} by hand gives {MISSING} instead, so that column cannot be used at all until the
  heading is corrected in Excel.
- **When:** A list with a heading of one of these shapes: 'Tax: Due', 'Mobile No:', 'Amount; Rs',
  'Time 10:30', a heading cell holding a date such as Apr-26 (the app reads it as '2026-04-01
  00:00:00'), 'Name ' with a space after the word, 'Interest & Penalty', 'P&L Amount', or a heading
  typed on two lines with Alt+Enter. The column is put into the subject or body with Insert
  Variable, with the '{' pop-up or by typing, and the batch is sent; no timing or saved state is
  involved and it happens on every run. With an ordinary heading, a space typed just inside the
  curly brackets ({ Name } or {Name }) is sent as typed in the same silent way. Headings with an
  apostrophe, round brackets, a slash, a dot, @, %, the rupee sign or spaces in the middle work.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Four readers reproduced it (a fifth saw the '&'
  and space cases) and Codex found the colon and semicolon case twice by reading; a checker (its
  verdict plus two extra findings) reproduced every heading shape end to end through the real
  window, Preview and Start Sending against a fake Outlook (subject handed over: 'Tax notice {Tax:
  Due}', no {MISSING}). The checker called the colon case 'new, closest to G31' and the edge-space
  case 'extends and corrects G31'; after reading core/template_engine.py:28-45 I filed the merged
  defect as extending G31, and real Outlook was not used.
- **Known gap:** extends G31. G31 covers only variables that turn into {MISSING}; here the column
  exists, the app's own Insert button wrote the variable, nothing becomes {MISSING} and nothing
  warns - and G31 is wrong to say that a name differing by a space becomes {MISSING}: with a space
  at either end it is left as typed.
- **The repair:** Trim headings when the list is read, and recognise a variable by comparing the
  text between the curly brackets with the real headings (in the body, after turning the editor's
  coded forms of & < > and the double quote back into the characters) instead of by a pattern that
  rejects ':' and ';'. Build it together with Change 5, so that its block also stops a run while any
  email still shows a heading in curly brackets that was not filled in.
- **Your call:** If an email still contains curly-bracket text that the app could not fill in - for
  example {Tax: Due} or {Name } - should sending be blocked in the same way you decided for
  {MISSING} in Change 5? (Recommended: yes - block the run and list the emails and the unfilled
  text, exactly as for {MISSING}.)
- **Where in the code:** core/template_engine.py:28, 37-45, 71-90, 139-153;
  core/excel_handler.py:158-163; core/email_builder.py:246-251; ui/tab_compose.py:300-308, 330-354;
  ui/components/rich_text_editor.py:391-395, 441-448

### G53 — Workbook not found at restore or in a profile: the saved column choices and ticks are dropped, then erased

- **What happens:** When the workbook of the saved session cannot be found, the app shows 'Excel
  File Not Found ... Click Browse on the Excel tab to reselect it', brings back the subject, body
  and attachments, and silently drops the saved column choices and ticks. When the user then chooses
  the workbook with Browse, the columns are the app's own guess (CC, BCC and Identifier 2 on None,
  OR instead of AND, in some runs another address column as To Email) and every client is ticked,
  with no message that the saved choices were not put back. The next automatic save (every 3
  minutes) or closing the app writes this state over the saved session, so the saved choices are
  gone for good. A profile whose workbook is not found ('Please load the Excel file manually') loses
  its column choices the same way.
- **When:** A session saved with columns set by hand (a CC column, Identifier 2 with AND, a
  corrected To Email) or with only some clients ticked; before the next start the workbook is
  renamed or moved (a new month's file) or sits on a network drive that is not connected yet; the
  user answers Yes to 'Restore Previous Session?' and then either closes the app or chooses the
  workbook with Browse. The same with Profile > Load Profile... when the profile's workbook is not
  where the profile says.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by several readers. Six readers reproduced it on dummy data
  (after Browse: guessed columns and every row ticked; after the next save the session file held no
  workbook, an empty mapping and no ticks), three of them also for a profile, and a checker
  reproduced it as a side finding with real restarts; Codex did not report it, there was no
  dedicated re-check, and the 'workbook found but fails to open' and 'closed while the restored
  workbook is still loading' variants are from reading the code only. Severity is my call: four
  readers said HIGH, two readers and the checker's side note MEDIUM; HIGH is kept because clients
  who had been unticked come back into the send, the To Email or CC column can change, and the saved
  choices are erased.
- **The repair:** Keep the saved column choices and ticks waiting until a workbook is loaded, put
  the column choices back on the workbook the user then chooses wherever the same headings exist,
  and say plainly what was and was not put back. Do not let the automatic save or closing overwrite
  those parts of the saved session before then; do the same for a profile.
- **Your call:** After 'Excel File Not Found', when you choose the workbook yourself with Browse,
  should the app also put back the ticks saved with the session, which are remembered by row number
  and so are right only if the list has not changed, or only the column choices? (Recommended: put
  back the column choices and say so; put back the ticks only after asking you, and otherwise tick
  everyone and say that the saved ticks were not used.)
- **Where in the code:** ui/main_window.py:513-526 (warning only), 551-561 (saved mapping and ticks
  applied only by the restore's own load), 490-507 with 677-679 (what the automatic save and close
  write), 837-855 (profile); ui/tab_excel.py:379-387 (Browse: plain load with guessed columns),
  413-424 (a failed load returns before the follow-up step), 980-1004 (load_file_path returns False
  for a missing file); ui/tab_recipients.py:292-296 (every load ticks everyone);
  data/session_manager.py:333-343

### G54 — Choosing another worksheet or pressing Apply silently resets the Column Mapping to the app's own guess

- **What happens:** Each time another sheet is picked in the Worksheet list, or Apply is pressed,
  the app starts the Column Mapping panel afresh: CC, BCC and Identifier 2 go back to '-- None --'
  and To Email and Identifier 1 go back to the app's own guess, even when the headings are exactly
  the same. The AND/OR choice stays, so AND with only one identifier left quietly means Identifier 1
  only; no message appears, and Preview does not show CC or BCC. In the checker's runs the next
  batch went out with no CC copy and with January's file added to February's, and where a wrong
  guess for To Email had been corrected by hand, each email went only to the 'CC Email' person and
  the client received nothing. Refresh, by contrast, keeps the choices.
- **When:** A workbook is loaded and at least one column was chosen by hand: any CC, BCC or
  Identifier 2 column, or a To Email or Identifier 1 different from the app's guess. Then any one
  of: pick another sheet in the Worksheet list (even one with the same headings, and even if you
  come straight back); press Apply (even with Row 1 and Column 1 unchanged); or, after Restore
  Previous Session or a profile on a workbook with several sheets, pick the sheet you had been
  working on.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader found and reproduced it; Codex did
  not report it. A checker reproduced it through the real main window with a fake Outlook (a sheet
  switch and Apply lost CC and Identifier 2 with no message, Refresh kept them; the same after a
  session restore) and confirmed HIGH.
- **The repair:** After a sheet switch or Apply, put back every column choice whose heading still
  exists in the list just read, as Refresh already does, and show one message naming any choice that
  could not be kept.
- **Your call:** When you pick another sheet of the same workbook, or press Apply, should the app
  keep your column choices (To Email, CC, BCC, Identifier 1 and 2) wherever the same headings exist,
  and tell you which ones it could not keep? (Recommended: yes, the same 'keep on switch' you chose
  for the heading row in Q19.)
- **Where in the code:** ui/tab_excel.py:465-471 (_on_sheet_changed reloads through _load_sheet_data
  only), 491-518 (_populate_column_combos empties all five drop-downs), 520-546 (auto-detect sets To
  and Identifier 1 only), 870-891 (Apply: after_reload calls _load_sheet_data only); contrast
  688-715 (Refresh saves the mapping at 695 and puts it back at 702)

### G55 — A search left in the Recipients box decides who is ticked after Refresh or a new list: the rest are unticked

- **What happens:** If text is still in the search box on the Recipients tab when the list is read
  again, the app applies that old search to the new rows, and its automatic 'tick everyone' then
  ticks only the rows the search shows. After Refresh on an unchanged file, 12 ticked clients became
  3 while the status bar said 'Refreshed — 12 rows reloaded from file', and the Send tab offered
  only those 3; in another run three hand-picked clients were replaced by one client who had not
  been ticked. With a new workbook that has no matching row, nobody is ticked and the Recipients
  table looks empty. No message appears; the only signs are the counts, such as '3 of 12 selected
  (showing 3)' and 'Ready: 3 emails to send'.
- **When:** Type something in the Recipients search box to look a client up and leave it there;
  then, on the Excel tab, click Refresh or load another workbook (both were run). By reading the
  code the same follows a sheet switch, Apply and Load Profile, because they deliver the rows the
  same way. An empty search box avoids it.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by several readers. Five readers reproduced it independently
  through the real main window (Refresh and a new workbook); Codex did not report it, no checker
  re-ran it, and the sheet-switch, Apply and Load Profile routes are from reading the code. Severity
  is my call: four readers said MEDIUM because the lower count is on screen, one said HIGH; HIGH is
  used because one reader's run ticked a client who had not been ticked and dropped the three
  hand-picked ones, the same harm the audit rates HIGH under G19, plus missing emails.
- **Known gap:** extends G19. G19 says Refresh ticks everyone; with a search left in the box it
  instead ticks only the rows that match the search (or nobody), and the same happens with a newly
  loaded workbook, which G19 does not mention.
- **Already decided:** Change 2: partly - once Refresh keeps the ticks by email address the Refresh
  route goes away; a new workbook, a sheet switch, Apply and Load Profile would still tick only the
  rows the old search shows
- **The repair:** Clear the search box (or ignore it) whenever new rows arrive, and make the
  automatic 'tick everyone' on a newly read list tick every row whatever the search shows.
- **Where in the code:** ui/components/recipient_list.py:132-146 (set_data keeps the search text;
  refilling the column drop-down at 140-143 fires the filter connected at line 78), 262-288
  (_apply_filter), 361-367 (select_all ticks only the shown rows while a search hides rows);
  ui/tab_recipients.py:288-296 (automatic select-all on new rows); ui/main_window.py:331-344

### G56 — Loading a saved recipient list ticks every row that shares an address, including rows never in the list

- **What happens:** A saved recipient list remembers only the email address of each ticked row, not
  which row it was. When the list is loaded, every row in the Excel list that has one of those
  addresses is ticked, so if two rows share an address and only one was ticked when the list was
  saved, both are ticked with no message and the extra row gets its own email with its own
  attachments. The only hint is that the list's name carries the old count, for example 'Demand
  notices (1)', while the tab says '2 of 3 recipients selected'; in the checker's test run a list
  saved with one client sent two emails.
- **When:** Two or more rows have the same To address (capitals and spaces at the ends are ignored)
  - a director with two companies, a family or an accountant with one address, two notices for one
  client. On the Recipients tab only some of those rows are ticked and saved with Save Selection...;
  later, in the same sitting or another day, the list is picked and Load is clicked. A new row with
  the same address added to the workbook after the list was saved is ticked too; it does not happen
  when the cells differ, for example 'a@example.com; b@example.com' against 'a@example.com'.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Two readers reproduced it on the real Recipients
  tab and Codex reported it in all three jobs; a checker reproduced it end to end with the real Save
  Selection, Clear Selection, Load and Start Sending buttons and a fake Outlook, plus variants, and
  a checker reproduced it independently. The audit mentions the behaviour under F14 as a plain fact
  and Codex related it to G9, but it is not among G1-G43, and it goes against contract C9 ('selects
  the same clients').
- **The repair:** Save more than the address for each ticked row - for example the Identifier 1
  value such as PAN - and tick only the rows that match all of it; when rows cannot be told apart,
  say so in a message instead of ticking them silently. Use the same matching for Changes 1 and 2,
  which will also recognise clients by email address and would otherwise carry the same flaw.
- **Your call:** When several rows share one email address and a saved list held only some of them,
  should loading the list tick only the rows whose Identifier 1 value (for example PAN) was saved
  with the list, and - where it still cannot tell the rows apart - tick none of them and list them
  for you to tick by hand? (Recommended: yes - match on address plus Identifier 1, and tick none and
  list them when it cannot tell.)
- **Where in the code:** data/recipient_lists.py:173-189 (every row holding a saved address is
  collected and ticked), ui/tab_recipients.py:215-224 (only the address of each ticked row is
  saved), 143-168 (the rows are ticked; a message appears only for addresses that are missing)

### G57 — Saved lists made before 5 July 2026 tick whoever now sits on the old row numbers, with no warning

- **What happens:** A recipient list saved before the 5 July 2026 update remembers only row numbers,
  not which clients they were. When it is loaded today the app ticks whoever now sits on those rows
  and shows no message, so other clients are ticked and the list's own clients are left out; if the
  file has become shorter, the rows that no longer exist are dropped without a word. Each email that
  goes out is still that row's own email with its own files, so the harm is who is and who is not
  emailed. Saving the list again under its name then stores the wrong clients in it for good.
- **When:** A list that was saved between January and early July 2026 and has not been saved again
  since; meanwhile the workbook's rows have moved (a client added above, a row deleted, the sheet
  sorted) or a different workbook is loaded. Then: Recipients tab > pick the list under 'Saved
  Lists' > Load. Lists saved with today's version are not affected. Whether the office still has
  such old lists was not checked (the app's data folder was off limits); because that folder is
  shared, a colleague's old list counts too.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader found it and Codex did not; a checker
  rebuilt an old-style list with the app's own pre-update code from git and loaded it in today's
  real main window (other clients ticked, no message box, and Start Sending then emailed three
  clients not on the list while the list's own three got nothing), and a checker reproduced the
  silent ticking independently. Not confirmed: whether the office still has such old lists - the
  app's data folder was off limits. The audit records the fallback as plain behaviour (F14), not as
  a gap; contract C9 does not hold for these lists.
- **The repair:** When a list holds no client addresses, never tick silently: say that it was saved
  by row number before July 2026, show which clients those rows are now, and either refuse it or
  tick only after the user confirms; also warn when some of its rows lie beyond the end of the file.
  If Change 9 carries the old list files over to the new data folder, this comes with them.
- **Your call:** When a list saved before 5 July 2026 (one that holds only row numbers) is loaded,
  should the app refuse it and ask you to tick the clients again and save a fresh list, or show you
  the names of the clients now on those rows and tick them only after you confirm? (Recommended:
  show the names, tick only after you confirm, then offer to save the list afresh)
- **Where in the code:** data/recipient_lists.py:166-171 (a list without stored addresses falls back
  to its row numbers and reports nothing missing); ui/tab_recipients.py:143-147, 157-166 (the
  'Partial Load' warning is shown only when something is reported missing);
  ui/tab_recipients.py:213-224 (Save Selection... is the only place that stores addresses);
  tests/test_recipient_lists.py:77-85 (pins today's silent fallback)

### G58 — Apply, and going to another sheet and back, tick every recipient again - as Refresh does (G19)

- **What happens:** After clients have been unticked on the Recipients tab, pressing Apply on the
  Excel tab - even with Row 1 and Column 1 unchanged - or choosing another sheet and coming back
  ticks every client again, with no message. The Send tab then offers the full number, and the
  clients who were meant to be left out are emailed (in the check, two of four ticked became four of
  four and all four were sent). It is the known Refresh problem (G19) reached by two other routes:
  every re-read of the list ends in the same step that ticks everyone.
- **When:** A list is loaded and some clients are unticked by hand on the Recipients tab. Then, on
  the Excel tab, Apply is pressed, or another sheet is picked in the Worksheet drop-down and the
  first sheet is picked again. Nothing else is needed; the only signs are the count on the
  Recipients tab and the number in the question before sending.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by one reader. No reader and not Codex: a checker came across
  it while checking the lost column choices and ran it once on the real main window with a fake
  Outlook (ticks [0, 2] became [0, 1, 2, 3] after Apply and after a sheet round trip, no dialog, all
  four clients reached the fake Outlook); no dedicated re-check. I confirmed the path in the code:
  Apply and a sheet change end in the same list-loaded step as Refresh, which ticks everyone.
- **Known gap:** extends G19. G19 and Change 2 name Refresh only; Apply and a sheet change tick
  everyone again through the same step, so a repair worded for Refresh alone would leave them.
- **Already decided:** Change 2: partly - it is worded for Refresh only; Apply and going to another
  sheet and back would still tick everyone again unless the change covers every re-read of the list
- **The repair:** Treat every re-read of the list the way Change 2 treats Refresh: keep the same
  clients ticked, found again by email address, and list anyone ticked who is no longer shown,
  instead of ticking everyone. Build it with Change 2, and with the repair that keeps the column
  choices on Apply and on a sheet change (G54).
- **Your call:** When you press Apply, or look at another sheet and come back, should the clients
  you had ticked by hand stay ticked (found again by email address, as decided for Refresh in Change
  2) instead of everyone being ticked again? (Recommended: yes - and when you switch to a sheet with
  other clients, say that your earlier ticks do not apply there)
- **Where in the code:** ui/main_window.py:331-344 (the list-loaded step hands the rows to the
  Recipients tab without asking to keep the ticks); ui/tab_recipients.py:292-296 (which then ticks
  everyone); ui/tab_excel.py:465-471 (sheet change), 473-489 (the list-loaded step, emitted at 489),
  870-891 (Apply)

### G59 — A filler in the identifier cell (0, -, ., NA) attaches other clients' files to that client's email

- **What happens:** Any text in the identifier cell is used as that client's code, and a file is
  attached when its name contains that text. So '-' attaches every file with a hyphen in its name,
  '.' every file in the folder, 0 every file with a zero in its name (any year such as 2026), and
  'NA' every file whose name contains those two letters (as in 'Final'). That client is sent other
  clients' documents, and the Attachments tab counts the filler as a matched identifier, so nothing
  looks wrong unless that client's Preview is opened. Only a truly empty cell is skipped.
- **When:** A row's Identifier 1 or Identifier 2 cell holds something that is not a real code: '-',
  '.', 'NA' or the like typed to mean 'no code', or the number 0 - for example a formula pointing at
  an empty cell, which can even look blank in Excel when zeros are hidden. A client-files folder is
  in use and the row is ticked. Seen with one identifier column, and with two under Match logic OR
  (the app's default).
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by several readers. Three readers reproduced it independently
  on dummy files with the real list reader, email builder and file matcher (0 and '-' each picked up
  three other clients' files, '.' every file in the folder, 'NA' one or two); there was no dedicated
  re-check and Codex did not report it. Not run: Match logic AND with a real code in the other cell,
  where by reading core/email_builder.py:281-284 the filler would narrow that client's own files
  instead; how often the office's lists carry such fillers is not known.
- **Known gap:** extends G11. G11 was accepted on the understanding that identifiers are chosen
  client codes that hit no other client's file; here the cell holds no code at all, and a one- or
  two-character filler matches a large part of the folder.
- **The repair:** Treat a cell that is not a usable code as 'no identifier' - attach no client files
  for that row - and list those rows before sending. Also warn before sending when one client
  matches an unusually large share of the folder.
- **Your call:** Which entries in the identifier column should the app treat as 'no code' -
  attaching no client files for that row and listing it before sending? (Recommended: 0, '-', '.',
  'NA', 'N/A', 'NIL' and anything made only of punctuation; add a minimum length only if the
  office's real codes are never that short.)
- **Where in the code:** core/email_builder.py:264-287 (270-272, 275-277: any non-empty text is used
  as an identifier); core/attachment_matcher.py:119-134 (133: name-contains test);
  core/excel_handler.py:177 (a numeric 0 is kept); ui/main_window.py:366-378

### G60 — 'Remove' and dropped files on the Test Matching list change only the display, not what is sent

- **What happens:** On the Attachments tab, the Test Matching box lists the files found for the
  identifier you typed. Right-clicking a file there offers Remove, and a file dragged in from
  Explorer is added to that list; either way the list, its file count and its total size change at
  once, so the change looks accepted. But that list is only a display: a file removed there is still
  attached to that client's email, and a file dropped there is attached to nobody. Nothing warns
  you; only the Preview tab for that client, or pressing Test again, shows the true list.
- **When:** A folder has been scanned. (a) Type an identifier, press Test or Enter, right-click a
  listed file and choose Remove - for example to keep a wrongly matched file away from that client;
  or (b) drag a file from Explorer onto the Matched Files box (this works even before any test, and
  even with 'Enable Dynamic Attachments' unticked). Then send without checking that client on the
  Preview tab.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader (rated LOW) and Codex (flows item 17,
  rated MEDIUM) both found it; the checker reproduced it in the app's real main window with real
  mouse clicks, a fake Outlook and dummy data: after Remove the list showed 1 file while the email
  went out with all 3, and a dropped file appeared in the list but in no email. The checker rated it
  HIGH because Remove looks like the cure for a wrongly matched file (known gap G11) but does
  nothing; a real drag from Windows Explorer could not be performed (the drop was injected and
  routed by Qt).
- **The repair:** Make the Matched Files list view-only: its right-click menu offers only Open File
  Location and Copy Path, and it no longer accepts dropped files. A real way to leave out or add one
  file for one client would be a separate new feature to ask for.
- **Where in the code:** ui/components/file_list.py:157-167; ui/components/file_list.py:193-196;
  ui/components/file_list.py:62-63; ui/components/file_list.py:140-155;
  ui/components/file_list.py:392-399; ui/tab_attachments.py:114; ui/tab_attachments.py:236-237;
  ui/tab_attachments.py:386-387; core/email_builder.py:264-287

### G61 — A Universal BCC address that was removed or replaced still gets a copy of every email; the new one gets none

- **What happens:** The app copies the Universal BCC box into the emails only at the moment the
  subject or body changes. Once an address has been taken in that way, emptying the box or typing a
  different address changes nothing until the subject or body is edited again: every email of the
  run is handed to Outlook with the removed address on BCC, together with that client's own
  documents, and a replacement address gets no copy at all. Nothing shows it: the Preview tab has no
  BCC line, the test email leaves BCC out, the Send tab lists only the To address, and the saved
  session records the box as it reads on screen.
- **When:** (1) In one sitting: type a Universal BCC, then type or edit the subject or body, then
  clear or replace the BCC box - for example to correct a typing mistake in the address - and make
  no further change to the subject or body; open Preview or Send and click Start Sending. (2) The
  everyday route: answer Yes to 'Restore Previous Session?' or use Profile > Load Profile where the
  saved state holds a Universal BCC - the restore itself makes that address live - then empty or
  change only the BCC box and send. It lasts until the subject or body is next changed, a profile is
  loaded, New Session is used or the app is restarted.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Two readers reproduced it and Codex found it
  twice by reading; a checker reproduced it with the real window, the real send run and a fake
  Outlook by three routes (typed then removed or replaced, restored then removed, profile then
  changed): 3 of 3 emails carried the removed address and 0 the new one. Change 3 covers it provided
  the box is read at build time even when empty (contract C18); the route that stays open afterwards
  - a profile loaded while the Send tab is showing - is G48, and real Outlook delivery was not
  tested.
- **Known gap:** extends G4. G4 describes only the opposite direction (an address typed last is
  ignored, so the records copy is missing); here an address the user removed keeps receiving every
  client's email and documents, and the replacement gets nothing.
- **Already decided:** Change 3: fully
- **The repair:** Read the Universal BCC box at the moment the emails are built and treat an empty
  box as 'no BCC' (this is Change 3). Its test should cover an address that was cleared and one that
  was replaced, not only one typed last.
- **Where in the code:** ui/main_window.py:391-399, 447-452, 473-488; ui/tab_compose.py:157-159,
  310-328, 404-407; core/email_builder.py:238-243; core/outlook_sender.py:326-327

### G62 — 'View HTML' box: text typed there is ignored until 'Hide HTML', and closing it can bring back an old body

- **What happens:** The 'View HTML' box under the body is a separate copy of the body, taken when
  the box is opened. Text typed in it is not part of the email until 'Hide HTML' is clicked: Save,
  Save As..., File > Save Session, Preview and Start Sending all carry on with the old wording and
  still report success. The copy is also never refreshed while the box is open, so if a New Session
  is started or another template, profile or file is loaded meanwhile, the next click on 'Hide HTML'
  puts the earlier wording back over the new one - in the test, the emails handed to Outlook had
  template B's subject with template A's wording, and Save then stored A's wording under B's name.
  While the box is open the Insert and Table buttons still change the locked body, and 'Hide HTML'
  throws those changes away without a message.
- **When:** Someone clicks View HTML on the Compose tab. (a) They change the text in the HTML box
  and, without clicking Hide HTML, press Save or Save As..., use File > Save Session, or go to
  Preview or Send. (b) They leave the box open and then use File > New Session, choose another
  template and click Load, use Profile > Load Profile, or Import File... (Replace), and later click
  Hide HTML - after New Session the body cannot be typed in until that click, so the click cannot be
  avoided. (c) With the box open they click Insert or Table and then Hide HTML. It never happens
  while the box is closed.
- **How serious, how often:** HIGH · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Five readers reported it in six findings (all
  reproduced off-screen) and Codex found it twice by reading; a checker reproduced every route with
  the real window and a fake Outlook, including emails handed over with the old wording and template
  B saved with A's body, and a checker reproduced it independently. The dedicated verdict's HIGH and
  occasional are used although a checker rated it MEDIUM and rare (the HTML box must be open); the
  Image and bold or colour buttons with the box open were not run.
- **The repair:** Treat the HTML box and the body as one thing: close the box and unlock the body
  whenever the body is replaced or cleared (New Session, Load, Load Profile, Import File, restore),
  and take in what is typed in the box whenever the body is read (Save, Save Session, Preview,
  Send). While the box is open, switch off the toolbar and Insert buttons; when Change 4 (profiles)
  is built it should reset the box too.
- **Where in the code:** ui/components/rich_text_editor.py:397-414, 432-448, 468-470, 391-395,
  501-524; ui/tab_compose.py:193-220, 247-251, 288-298, 487-491; ui/main_window.py:617-639, 857-861,
  528-531, 490-507

### G63 — Choosing another folder during a folder read: the new folder is never read and the old folder's files go out

- **What happens:** The Folder box shows the newly chosen folder, but the app never reads it: the
  earlier read carries on, and the files it finds after the switch become the list that clients are
  matched against. Clients are then sent the first folder's files (for example last month's notice)
  or no client file at all, and the run ends with 'Successfully sent'. The screen shows an ordinary
  'Found N files' line under the new folder's name; the only clues are an unexpected file count and,
  where the names differ, the file names shown in Test Matching and Preview. Rescan (once the moving
  bar has gone) or choosing the folder again puts it right, but nothing prompts the user to do so,
  and Rescan clicked while the bar is still moving does nothing.
- **When:** On the Attachments tab a folder is still being read ('Scanning...' showing). The read
  was started by Browse..., by answering Yes to 'Restore Previous Session?' or by Load Profile, and
  it lasts several seconds because the folder is very large, 'Include subfolders' is ticked on a big
  folder tree, or the server link is slow. Before it ends, the user picks another folder with
  Browse... (the button stays usable) or loads a profile that names another folder. Wrong files go
  out when the first folder's file names contain the same client codes - normal for monthly work
  with the same PANs; otherwise the clients simply get no client file.
- **How serious, how often:** HIGH · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** re-checked: reproduced. Five readers reproduced it and Codex reported it
  in all three jobs (code reading plus small in-memory checks; Codex filed it under G14, the checker
  classed it as new, in G14's family); the checker reproduced it end to end through the real window
  with a fake Outlook (4 of 6 emails carried folder A's file, 2 none, 0 the chosen folder's), again
  with nothing slowed (20,000 files in 100 subfolders, second pick 0.10 s later) and by the Load
  Profile route, and five other checkers reproduced it independently. Not measured: how long the
  office's server folder takes to read, which decides how easily a person hits it (a local SSD read
  17,000 to 270,000 files a second); one reader alone showed that picking the same folder twice
  during a read leaves a list missing its first part (171 of 200 files).
- **The repair:** Every change of folder must end with a read of the folder now shown: stop, or
  ignore the result of, any read still going, and accept a finished file list only if it belongs to
  the folder on screen. Until that read has ended, hold back Browse... and Rescan (or queue them)
  and keep Preview and Send from using a half-built list.
- **Where in the code:** ui/tab_attachments.py:284-285 (a new read is skipped while one is running),
  259-280, 531-554, 302-315; core/attachment_matcher.py:57-61, 86-94

### G64 — New Session during a folder read keeps the old folder's files in use although no folder is shown

- **What happens:** File > New Session empties the Folder box, but the folder read that was still
  going carries on and the files it finds stay in the app's list. When that read ends, the line
  under the empty box changes from 'No folder selected' to 'Found N files', and Rescan and Generate
  Report become clickable, while the '3. Attachments' tab has no tick. If the next list has a PAN or
  code column (the app picks it as Identifier 1 by itself) and no folder is chosen, every client
  whose code appears in an old file name gets the earlier campaign's files attached. Rescan does not
  clear them (it only says 'No directory set'); choosing a folder does.
- **When:** A folder read lasting several seconds is still going ('Scanning...' showing) - after Yes
  to 'Restore Previous Session?', after Load Profile, or after a Browse... to a very large or slow
  folder - and the user chooses File > New Session > Yes. A new Excel list with a code or PAN column
  is then loaded, and emails are previewed or sent without a client-files folder being chosen: for
  example a circular with only a static file.
- **How serious, how often:** HIGH · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** reproduced by several readers. Three readers reproduced it (two rated it
  HIGH, one MEDIUM), and five checkers reproduced it independently as a side finding while
  re-checking G63, all rating it HIGH (one end to end: 4 of 6 emails sent with the old folder's file
  while no folder was selected); there was no dedicated re-check and Codex did not report this
  route. Every run slowed or paused the folder read to stand in for a slow server folder; a checker
  also notes that Change 4, built as worded (a profile with no folder clears the folder), would open
  the same door from Load Profile.
- **The repair:** New Session must stop, or ignore the result of, any folder read still going, so
  that nothing arrives after the clear. With no folder chosen the app should attach no matched files
  at all, and Rescan should empty the list.
- **Where in the code:** ui/tab_attachments.py:514-529 (reset does not stop the running read),
  302-315; core/attachment_matcher.py:470-478, 86-94, 76-77 (Rescan with no folder returns before
  the list is emptied); core/email_builder.py:265; ui/main_window.py:617-639

### G65 — Emails built while the client folder is still being read go out without the clients' own files

- **What happens:** After 'Restore Previous Session?' > Yes or a profile load, the client folder is
  read in the background, and nothing on the Send tab shows this or holds the user back. The emails
  are made up at the moment the Send tab is opened; if the folder has not been read yet they are
  made up without the clients' own files (or with only those read so far) and are not made up again
  when the reading ends. Start Sending, or Resume Previous (which asks nothing), then sends them
  like that and reports 'Successfully sent'. With a cover letter for everyone the summary says 'All
  have attachments'; without one it does show 'N without attachments'.
- **When:** A saved session or profile whose client folder takes longer to read than the user needs
  to reach the Send tab - about 1.5 seconds or more. Start the app > Restore > Yes (or Load Profile
  > OK), open '6. Send' while the Attachments tab still says 'Scanning...', then Start Sending > Yes
  or Resume Previous. With nothing slowed this needed 24,000 files in sub-folders on a local disk; a
  server folder with sub-folders or a slow link would need far fewer, which could not be measured.
  With a cover letter the wrong result stays until Rescan; without one, leaving the Send tab and
  coming back after the read has ended puts it right.
- **How serious, how often:** HIGH · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** re-checked: reproduced. Two readers reproduced it with a slowed folder
  read; the checker reproduced it through the real window with a fake Outlook (6 of 6 emails without
  the client's file under 'All have attachments'; Resume Previous sent 4 emails with no attachments
  and asked nothing) and once with nothing slowed (24,007 files in 400 sub-folders: 4 of 6 without
  their file). Not confirmed: how long the office's server folder takes to read, which decides how
  easily a person hits it; Codex did not report it.
- **Known gap:** extends G14. G14 is described for a Rescan; this is the same hole on the automatic
  folder read after a restore or a profile load, made worse by a Send list that is never built
  again, and hidden by G41 when a static file is attached (Resume asking nothing is G2).
- **Already decided:** Change 1: partly - Resume Previous would ask before sending, but nothing
  would wait for the folder read or check the attachments, and Start Sending is unchanged
- **The repair:** While the client folder (or the workbook) is still being read, hold back the
  Preview and Send lists and the Start Sending, Resume Previous, Retry Failed and Send Test Email
  buttons, with a visible 'Reading the client folder...' note on the Send tab. Build the Send list
  again when the reading ends.
- **Where in the code:** ui/main_window.py:439-445 and 473-488 (the Send list is built only when the
  Send tab is opened), 406-419 (411 is the only place the email builder is given the file matcher);
  ui/tab_attachments.py:302-315, 531-554; ui/tab_send.py:667-696, 481-498;
  core/email_builder.py:265; core/attachment_matcher.py:86-92, 124-137

### G66 — A workbook asked for while another is loading is silently skipped; Load Profile then mixes two campaigns

- **What happens:** While one workbook is still being read in, a request to load another one is
  ignored without any message. If the request came from Profile > Load Profile, the app skips the
  profile's own workbook and column choices, yet still switches to the profile's subject, body, BCC
  and attachments and says 'Profile loaded successfully!'. A moment later the earlier workbook
  finishes and its clients fill the list, so the window holds one campaign's clients with the other
  campaign's email and files, with a tick on every step; in the checker's test run five clients of
  one campaign were each sent the other campaign's email and covering letter. A second workbook
  dropped onto the Excel tab during a load is ignored in the same way.
- **When:** A workbook is still showing 'Loading ...' on the Excel tab - after Yes to 'Restore
  Previous Session?', after Browse..., or after a file was dropped on the tab - and before it
  finishes the user chooses Profile > Load Profile..., picks a profile whose own Excel file exists
  and answers Yes (or drops a second workbook on the tab; Browse... is greyed out during a load).
  The first load has to outlast the two profile boxes, about 2 seconds at least. Measured on a local
  disk, a list of a few hundred rows loads in about a tenth of a second, so it takes a very large
  list (20,000 rows took about 4 seconds), a workbook with many sheets (1 to 2.5 seconds), a stray
  formatted cell far below the data (up to 7.5 seconds) or a slow link such as a file that must
  first download.
- **How serious, how often:** HIGH · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** re-checked: reproduced. Three readers reproduced it and Codex reported
  it in all three of its jobs; a checker reproduced it through the real window (Browse..., the Load
  Profile menu entry, a fake Outlook; also with an unslowed 20,000-row workbook and with a dropped
  second file), and three checkers saw it again with a slowed load. Not run: the case where the
  earlier workbook then fails to load (code reading only); the audit's Section 6 lists 'a second
  load while one runs is ignored' as handled, without these consequences.
- **The repair:** Never ignore a request to load a workbook without saying so: either let the newest
  request win and throw the older result away when it arrives, or refuse with a clear 'still loading
  - try again' message, for Load Profile and for a dropped file alike. Say 'Profile loaded
  successfully!' only when the profile's own workbook and column choices were really taken; this is
  best done together with Changes 4 and 11, which rework the same steps.
- **Where in the code:** ui/tab_excel.py:398-399 (the second request is dropped without a word),
  1003-1004 (the caller is still told the load started), 97-101 (a dropped file takes the same
  route), 413-424 (the earlier load's result is accepted and runs its own follow-up);
  ui/main_window.py:841-847 (the profile asks for its workbook and ignores the answer), 857-896 (the
  rest of the profile is applied regardless), 812-814 (fixed 'Profile loaded successfully!')

### G67 — Headings 'Email' and 'EMAIL' in one list: emails go to the left-hand column, Preview shows the chosen one

- **What happens:** When a list has two headings that differ only in capital letters (for example
  Email and EMAIL) holding different addresses, the app offers both in every drop-down but sends to
  the left-hand column whichever one is chosen. The Preview tab shows the address from the chosen
  column, so Preview and the email actually sent disagree; CC and BCC behave the same way. The app
  itself picks the right-hand heading as To Email when the list is loaded, so this happens without
  anyone touching the drop-down. Refresh, Restore Previous Session and Load Profile also move such a
  choice to the left-hand heading without a message, and for Identifier 1 or 2 that changes which
  files each client gets.
- **When:** Only with a list that has two headings identical except for capital letters (Email /
  EMAIL, CC / cc, PAN / pan) with different values on the same row. Load it with Browse and leave To
  Email as the app set it (the right-hand one), or choose the right-hand one by hand, then Start
  Sending. Choosing the left-hand one by hand gives the same address in Preview and in the email.
  The address used is always one from the same client's own row; Send Test Email does not reveal it,
  because it goes to your own address.
- **How serious, how often:** HIGH · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** re-checked: reproduced. Three readers reproduced it and Codex reported
  it twice (engine-1, flows-1); a checker reproduced it through the real main window with a fake
  Outlook (3 of 3 emails went to the left-hand address while the To drop-down and Preview showed the
  right-hand one) and also reproduced the silent move of the choice on Refresh, session restore and
  profile load, including different attached files with PAN/pan headings. Whether the office's lists
  ever have headings that differ only in capitals is not known, hence 'rare'.
- **Already decided:** Change 10: partly - it removes the cause only if its open point (a) is
  settled so that headings differing only in capitals count as repeats; Change 3 would make Preview
  show the address really used, but the email would still not go to the column named in the
  drop-down
- **The repair:** Make the email, the Preview, the address check and the put-back of column choices
  all use exactly the heading chosen in the drop-down, ignoring capitals only when no exact heading
  exists. When a list has headings that differ only in capitals, say so when it loads (this can be
  settled together with Change 10).
- **Your call:** If a list has two headings that differ only in capital letters, such as Email and
  EMAIL, should the app treat them as a repeated heading (keep the left one, rename the right one
  'EMAIL (2)' and tell you, as already decided for exact repeats in Change 10), or keep both as they
  are and always send to exactly the one chosen in the drop-down? (Recommended: treat them as a
  repeated heading; the plain repair, that the email goes where the drop-down and Preview say, does
  not need to wait for this answer.)
- **Where in the code:** core/email_builder.py:104-112 (_find_key returns the first heading equal
  ignoring capitals), 220-236 (To, CC and BCC use it), 396-398 (Preview uses the exact heading);
  ui/tab_excel.py:520-534 (auto-detect keeps the later twin, line 522), 717-733 with 115-123
  (Refresh, restore and profile put the choice back on the first twin), 572-575 (the address check
  reads the first twin); core/excel_handler.py:158-177 (both headings kept as separate columns),
  419-420 (Validate Emails reads the exact heading); ui/components/recipient_list.py:46-54

### G68 — Lists not saved by Excel: a blank cell at the end of a row is sent as {MISSING} for that client

- **What happens:** When a list was written by a program that leaves out the workbook's 'used range'
  note and does not store blank cells, the app reads each row only as far as its last filled cell.
  For a client whose last cells are blank, the app then behaves as if those columns did not exist
  for that client, and each {Variable} for them is sent as the text {MISSING} in that client's
  subject or body, where a list saved by Excel gives a blank. Nothing warns: the Excel tab shows the
  cells as blank, the line under the Compose editor stays green, the first client's Preview and the
  test email look right, and the run ends with 'Successfully sent'. Only paging to an affected
  client in Preview shows it.
- **When:** All three together: (1) the workbook was written by another program that leaves out the
  'used range' note and does not store blank cells (reproduced with a list written by a script in
  'streaming' mode and with an ordinary file from which only the note was removed; files saved by
  Excel carry the note, and files written by pandas and XlsxWriter were checked and are not
  affected); (2) for a ticked client, the cell under a column used as a {Variable} is blank and
  every cell to its right in that row is blank too (a blank in the middle of a row is fine); (3)
  nobody pages to that client in Preview before Start Sending. It happens the same way after Browse,
  Refresh and Apply.
- **How serious, how often:** HIGH · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** re-checked: reproduced. Three readers reproduced it and Codex did not
  report it; a checker reproduced it end to end through the real main window with a fake Outlook (2
  of 3 emails contained {MISSING}; the same rows written the ordinary way gave blanks), tested the
  boundaries and rated it HIGH (readers: MEDIUM) because {MISSING} reaches a client. Which of the
  office's outside sources write such files is not known (a Google Sheets download is suspected, not
  tested); the checker also showed that the audit's suggested repair for G25 (openpyxl's
  reset_dimensions()) would by itself cause this in ordinary workbooks.
- **Known gap:** extends G31. G31 is about a variable whose name does not match a heading; here the
  name is right and the cell is simply blank, so the Compose line shows no warning at all (same
  family of files as G25).
- **Already decided:** Change 5: partly - it would stop these emails going out, but it would then
  block the whole run (Start, Resume, Retry) for cells that are merely blank, naming columns that do
  exist; the cause stays
- **The repair:** When reading a list, give every row a value for every heading (blank where the
  cell is absent), so a blank cell is blank whichever program wrote the file. Do this before Change
  5 and before any repair of G25 that makes the app ignore the 'used range' note.
- **Where in the code:** core/excel_handler.py:166-179 (173-177: an entry is made only for the cells
  received), 143 (rows taken as openpyxl returns them); core/template_engine.py:80-88 (a missing
  entry becomes {MISSING})

### G69 — A folder read that fails part-way keeps a part list and shows a normal 'Found N files' line

- **What happens:** When the app cannot read part of the client-files folder, it keeps whatever it
  did read and shows an ordinary 'Found N files' line, with no error. Clients whose papers sit in
  the unread part get their email without those papers, and the run still ends with 'Successfully
  sent'. If such a client has no other file, the usual red 'no matching files' warning appears
  (which reads as 'no file was prepared', not 'the folder could not be read'); if the client has
  another file, or a static file is attached, nothing on any screen shows it.
- **When:** (1) With no fault at all: 'Include subfolders' is ticked and the chosen folder contains
  a sub-folder this Windows user is not allowed to open - it is skipped without a word. (2) With a
  fault: the connection to the folder fails while it is being listed, so the listing stops early;
  with subfolders ticked a short network drop loses the files and sub-folders asked for during it,
  while a plain folder is listed in well under a second, so the chance there is tiny. Then Preview
  and Send as usual.
- **How serious, how often:** HIGH · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** re-checked: reproduced. Two readers reproduced it with simulated listing
  errors (one rated it HIGH, one MEDIUM); the checker reproduced it through the real window with a
  real, unpatched fault (a sub-folder refused by a Windows access rule: 'Found 3 files', '3/3
  identifiers matched', 'All have attachments', and one client sent without two of her three papers)
  and with a simulated network drop (4 of 10 entries listed). Not confirmed: a real network drop,
  and a sub-folder path longer than about 260 characters on a PC where Windows long paths are
  switched off; Codex did not report it, and the recommended answer in the business question is this
  writer's (the checker asked the question without recommending one).
- **Known gap:** extends G16. G16 and audit 7.8 say an unreadable or dropped folder shows 'Found 0
  files'; the result can also be a part list with a normal-looking count, which is far harder to
  notice (audit rule R24 already records that unreadable entries are skipped silently).
- **The repair:** Have the folder read keep a note of everything it could not read (sub-folders
  refused, files it could not size, a listing that stopped early) and show it in red - 'Scan
  incomplete - N folders/files could not be read', with their names - in place of a plain count. An
  incomplete list should never look like a good one.
- **Your call:** If part of the client-files folder could not be read, should the app refuse to send
  until a complete read succeeds, or show a clear warning naming what was not read and let you
  decide to go on? (Recommended: warn, name the unread folders and ask before sending - a sub-folder
  you are simply not allowed to open would otherwise block every run.)
- **Where in the code:** utils/file_utils.py:296 (os.walk without an error handler skips sub-folders
  it cannot list), 303-305 and 314-315 (single files dropped), 317-322 (the listing ends quietly
  after part of it was handed over); core/attachment_matcher.py:86-101

### G70 — The session is not saved when a send starts; after a crash, Restore and Resume continue an older campaign

- **What happens:** The app saves the session (list, subject and body, attachments, ticks) only
  every three minutes, on a normal close and with File > Save Session; it does not save when Start
  Sending is clicked, and the three-minute save is switched off while emails are going out. If the
  PC loses power or the app dies during a run, the next start restores an older state, and Resume
  Previous then carries on from that older state without asking. In the re-check the remaining
  clients got the email with the old due date, two clients ticked at the last minute were never
  emailed and the app said 'Successfully sent 2 emails!'; in a second test last month's clients got
  last month's email again and this month's waiting clients got nothing.
- **When:** Something is changed after the last three-minute auto-save (subject or body,
  attachments, ticks or the list), or Start Sending is clicked within three minutes of opening the
  app while an older session is still saved. The app then ends abnormally while emails are going out
  (power cut, forced restart, End Task, or an unexpected error), and at the next start the user
  answers Yes to 'Restore Previous Session?' and clicks Resume Previous. Closing the window normally
  during a run does save the session, so that path is safe.
- **How serious, how often:** HIGH · it shows up only when something else fails (disk, network,
  another program).
- **How it was confirmed:** re-checked: reproduced. Two readers found it (one simulated the crash,
  one read the restart from the code) and Codex did not report it. The checker reproduced it with
  two program runs on one data folder, the first killed in mid-send (old due date sent, rows 4-5
  never emailed; in a second test last month's list was emailed again), and confirmed that a normal
  close during a run does save the session.
- **Already decided:** Change 1: partly - Resume would ask first and refuse when the restored file
  or clients differ, but an older subject, body, attachments or BCC would still go out after one
  Yes, and nothing decided saves the session when a run starts
- **The repair:** Save the session at the moment a run starts (Start, Resume or Retry) and again
  when it ends, so a restore after a crash is exactly what was being sent. When Resume cannot find
  some waiting clients in the list on screen, name them and keep the run resumable instead of
  closing it (see G74).
- **Where in the code:** ui/main_window.py:324-329, 677-679; data/session_manager.py:333-343;
  ui/tab_send.py:609-614, 637, 675-689, 730-733

### G71 — A progress save that fails is only logged; sending goes on and Resume later sends the same emails again

- **What happens:** After every email the app notes in a small progress file which clients are done;
  when that note cannot be saved (the file is open in another program at that moment, the shared
  folder cannot be reached, or the disk is full), nothing is shown in the window and sending carries
  on. When Resume Previous is clicked later, the app trusts the older file instead of what it knew,
  so every client emailed after the last good save gets the same email, with the same attachments, a
  second time. If the trouble lasts to the end of the run, a run that ended with 'Successfully sent'
  is offered for Resume the next time the Send tab is opened, and one click sends its last part
  again. If the very first save at Start Sending fails, the run's progress is filed under the
  previous run's record or nowhere, and Resume then refuses or follows the older run's list.
- **When:** The save of the progress file must fail for the last emails before the run stops
  (Cancel, the app's own stop after three failures, the window being closed, or the end of the run);
  one failed save followed by a good one repairs itself. It needs a fault: another program holding
  the file for a moment (in the shared folder this could be another PC's copy of the app, a virus
  scanner or a backup tool), the shared folder dropping, or a full disk. Nothing unusual is needed
  in the Excel data.
- **How serious, how often:** HIGH · it shows up only when something else fails (disk, network,
  another program).
- **How it was confirmed:** re-checked: reproduced. Three readers reproduced it with a forced write
  failure and Codex reported it in all three jobs from reading the code; the checker reproduced it
  with a real Windows file lock (clients 3 and 4 emailed twice after Cancel and Resume), with a
  simulated full disk to the end of the run (clients 3-5 emailed twice) and for a failed first save
  at Start. Not tested: a real server outage, a OneDrive-synced folder or a really full disk; with
  nothing holding the file 0 of 1,500 saves failed, so how often it happens in the office is
  unknown.
- **Known gap:** extends G36. G36 says only that a shared or synced folder can lock files while they
  are being saved; new here is that the failed save is hidden, sending continues and Resume then
  sends again or follows an older run's record - so the audit's note in 7.7 that the safe-save
  method prevents this is not fully true.
- **Already decided:** Change 9: partly - with the data on each PC's own disk a server drop or
  another user's lock no longer breaks the save, but a failed save would still be hidden and Resume
  would still trust the older file
- **The repair:** Treat a failed save as a real event: try again for about a second, then show it in
  the window and stop after the email in hand; at Start send nothing unless the first save worked,
  and never write one run's progress into another run's record. For Resume and at the end of a run,
  use what the app already knows (and save it again first) instead of an older file.
- **Your call:** If the app cannot save its progress file while emails are going out, should it stop
  after the email in hand and tell you, or keep sending and only warn you that this run must not be
  resumed? (Recommended: stop after the email in hand and tell you.)
- **Where in the code:** data/checkpoint.py:160-167, 139-158, 101, 195-201, 219-230, 301-316;
  utils/file_utils.py:16-29; ui/tab_send.py:609-614, 730-733

## MEDIUM (G72 to G110)

### G72 — After choosing a variable from the pop-up in the Subject box, the cursor jumps back near the start

- **What happens:** In the Subject box, typing '{' and choosing a column from the pop-up list puts
  the variable in correctly, but the typing cursor then jumps back to near the start of the box
  instead of staying after the variable. Whatever is typed next lands inside the earlier words:
  'Reminder {Name} for March' comes out as 'Remindfor Marcher {Name}'. With a short opening such as
  'Hi {' the cursor lands inside the variable itself and the next words break it, so clients would
  get {MISSING} in the subject. The body is not affected; the Format box of 'Display as: Custom...'
  on the Preview tab has the same fault.
- **When:** An Excel list is loaded, so the pop-up has columns. In the Subject box: type any text,
  type '{', accept an entry (Enter, Down then Enter, or a click) and keep typing. It happens every
  time: the cursor lands as many places from the start of the box as the column name has characters,
  plus two - place 6 for 'Name', 13 for 'Client Name' - wherever the variable was put. It is mildest
  when the variable is the very first thing in the subject (the cursor is one place short).
- **How serious, how often:** MEDIUM · it shows up in ordinary use.
- **How it was confirmed:** re-checked: reproduced. One reader reproduced it with simulated key
  presses and Codex found it by reading with a stand-in control (rated only 'possible'); a checker
  reproduced it in 6 of 6 scenarios with the real Compose tab off-screen and in the Preview tab's
  Custom format box, with the body editor as a clean control. Cause: setText at
  variable_completer.py:255 re-enters _on_text_changed, which resets _trigger_pos to -1 (212-214)
  before line 256 uses it; accepting by mouse click was not verified on a real screen.
- **The repair:** Work out where the cursor must go before the text is replaced, as the Subject
  line's own Insert button already does, so that the cursor stays just after the inserted variable.
- **Where in the code:** ui/components/variable_completer.py:255-258, 201-220, 156;
  ui/tab_compose.py:123-124; ui/tab_preview.py:112

### G73 — A Preview-mode run is reported as sent: 'Sent to: ...' and 'Successfully sent N emails!'

- **What happens:** With 'Preview mode (display in Outlook, don't send)' ticked, the app only opens
  each email in Outlook and sends nothing. Yet it reports the run in the words of a real send: a
  green 'Sent to: ...' line for every client, 'Completed: Email sending (N successful)', the status
  'Complete: N sent, 0 failed' and a box saying 'Successfully sent N emails!'. Only the confirmation
  question ('display N emails') and the first line ('Starting: Displaying emails') show that it was
  a preview. The Preview mode box also stays ticked afterwards, so the next Start Sending in the
  same sitting is another display-only run that again ends with 'Successfully sent'.
- **When:** On the Send tab, tick 'Preview mode', click Start Sending and answer Yes: the wrong
  words appear on every Preview-mode run. A client goes without the email only if someone then
  trusts those words over the Outlook windows that opened - for example after forgetting the box is
  still ticked - and closes them without sending.
- **How serious, how often:** MEDIUM · it shows up in ordinary use.
- **How it was confirmed:** re-checked: reproduced. One reader reproduced it and Codex did not
  report it. The checker reproduced it on the real main window with a simulated Outlook that noted
  Displayed or Sent (really sent 0, opened 3, final box 'Successfully sent 3 emails!', the same box
  as a real send) and saw the log file write 'Batch complete: 3 sent, 0 failed' for the Preview run.
- **Known gap:** extends G3. G3 is about a displayed email being recorded as sent in the progress
  file; this is the same root showing in the words on screen and in the log file.
- **Already decided:** Change 1: partly - a Preview-mode run would no longer count as sent in the
  progress file (contract C16), but the Brief does not say that the words on screen and in the log
  change
- **The repair:** In Preview mode say 'Opened in Outlook (not sent): ...' on each line and
  'Displayed N emails - nothing was sent' in the status line, the summary and the final box, and
  write 'displayed' in the log file. Build it together with Change 1.
- **Where in the code:** ui/tab_send.py:708-709, 743, 755-757;
  ui/components/progress_log.py:266-279; core/outlook_sender.py:359-361

### G74 — Resume Previous sends only the waiting clients ticked now, then closes the run and drops the rest

- **What happens:** Resume Previous sends only the clients who are both still waiting from the
  interrupted run and ticked right now; it refuses only when none of the waiting clients is ticked.
  After sending that part it says 'Successfully sent N emails!' and marks the whole interrupted run
  as finished, so Resume is not offered again even when the other clients are ticked again. The
  waiting clients that were left out are never emailed and nothing on screen mentions them.
- **When:** A run is cancelled or stops part-way, and before Resume Previous is clicked fewer of the
  waiting clients are ticked than when the run started: the user unticked some on the Recipients
  tab, or (rarer) the app ended abnormally during the run and the session restored at the next start
  carries older ticks. At least one waiting client must still be ticked; with none ticked the app
  refuses and keeps the run.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Three readers reproduced it, Codex reported it
  in two jobs, and the checker reproduced it on the real main window (one of two waiting clients
  unticked: 'Successfully sent 1 emails!', run closed, Resume not offered again) and by the restore
  route with no unticking. Where the user removed the tick, leaving that client out is their own
  choice; the defect is the silence and the closed run.
- **Already decided:** Change 1: partly - it cures this only if 'the same clients' (contract C15) is
  built to mean that every client still waiting is in the ticked list; the Brief does not say what
  happens to a waiting client who is loaded but not ticked
- **The repair:** Before resuming, compare the clients still waiting with the ticked list (by email
  address); if any are missing, name them and ask what to do. Never mark the run finished while a
  planned client is neither sent, failed nor dropped by the user.
- **Your call:** If a client still waiting from an interrupted run is no longer ticked when you
  click Resume Previous, should the app (a) refuse and name the client, (b) send the others and keep
  that client waiting so Resume is offered again, or (c) ask whether to drop that client from the
  run? (Recommended: c - ask, naming the client.)
- **Where in the code:** ui/tab_send.py:675-689, 730-733; data/checkpoint.py:195-201

### G75 — Clients whose email failed can be retried only until the app is closed or another run starts

- **What happens:** When a run ends with some emails failed, the app offers 'Retry N Failed', but it
  remembers those clients only while it stays open and only until the next run. After closing and
  reopening the app, the Send tab shows no Retry button, no Resume button and an empty Progress list
  - just 'Ready: N emails to send', and Start Sending would email everyone again. The same happens
  without closing: sending anything else with Start Sending removes the offer. The failed clients'
  row numbers stay in a saved file that nothing reads, and their addresses are only in the app's log
  file.
- **When:** A run reaches its end with one or more failed emails (not three in a row) - for example
  an attachment that was open or moved, or a blank address. The user does not click 'Retry N Failed'
  straight away and then closes the app (nothing warns about the unsent clients) or starts another
  run with Start Sending in the same sitting.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader reproduced it and Codex noted it in
  passing inside its G44 finding (window-9). The checker reproduced it over two program runs (after
  the restart: no Retry, no Resume, 'Ready: 6 emails to send', failed rows [1, 4] still in the
  progress file that nothing reads) and within one sitting, and a second checker reproduced the
  restart part independently.
- **The repair:** Keep the last run's failed clients (by address) on disk and read them back, so
  'Retry the N that failed' is offered again at the next start and after any later run while the
  same list is loaded - or at the least show and save the list of who failed.
- **Your call:** If a run ends with some emails failed and the app is closed, or something else is
  sent, before you retry them, what should the app do next time: offer 'Retry the N clients that
  failed last time' when the same list is loaded, or only show you a list of who failed?
  (Recommended: offer the Retry again when the same list is loaded, and show who failed.)
- **Where in the code:** ui/tab_send.py:767-773, 730-733, 628, 463-470; data/checkpoint.py:84-85,
  239-243

### G76 — When only failed emails are left, Resume Previous gives an untrue reason and never goes away

- **What happens:** The app stops a run after three failures in a row even when the third failure is
  the last email of the run, so it says 'Stopped ... Outlook may be unavailable ... use Resume to
  continue' although nobody is left waiting. Resume Previous then answers 'The remaining recipients
  are not in the current email list. Reload the same Excel file and select the same recipients, then
  try Resume again', which is untrue: the list is the same and those clients simply failed. The run
  stays marked as unfinished, so the Resume button and the line 'Found incomplete session' come back
  on every visit to the Send tab and after every restart (when the Retry button is gone), until some
  other run reaches its end.
- **When:** The last three emails attempted in a run all fail: for example exactly three clients
  fail in a normal run, the user clicks 'Retry 3 Failed' and they fail again because the cause is
  still there; or the last three ticked rows have no email address; or Outlook refuses the last
  three. The user then clicks Resume Previous, as the message says.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader reproduced it and Codex did not
  report it; the checker reproduced four ways in on the real main window (a Retry of three that fail
  again, three blank addresses at the end, Outlook refusing the last three, a run of exactly three)
  and the stuck Resume button after a restart. A second checker reproduced the blank-address route
  independently, where no failure had to be simulated.
- **Already decided:** Change 7: partly - blank or invalid addresses would no longer count towards
  the stop, which closes that way in; the stop on the last email, the untrue Resume message and the
  stuck 'unfinished' mark stay for other failures (address refused by Outlook, attachment that
  cannot be added, Outlook down)
- **The repair:** When the three-failure stop falls on the last email of a run, close the run as
  'complete with N failed' and offer Retry instead of 'stopped - use Resume'. When Resume finds
  nobody waiting, close the unfinished run and say what is true: nothing is left to resume, N
  clients failed, use Retry.
- **Where in the code:** core/outlook_sender.py:511-518; ui/tab_send.py:680-689, 730-731, 749-753,
  463-470; data/checkpoint.py:219-230, 239-243, 288-292

### G77 — A profile whose Excel file cannot be found leaves the previous list in place under the new subject and body

- **What happens:** Loading a profile changes the subject, body, BCC and attachment settings
  straight away, but it replaces the list only if the profile's Excel file can be opened. When that
  file is missing, a warning names it and asks you to load it by hand, and then a second box says
  'Profile loaded successfully!' - while the list already on screen stays exactly as it was, ticks
  included. In the checker's test run the Send tab then held 'GST notice' emails addressed to the
  earlier campaign's audit clients, and Start Sending sent them. If the file is there but damaged,
  the success box comes first and a bare 'Error loading file' second; if the profile names no file,
  the old list stays with no warning at all.
- **When:** A list is already on screen (for example after 'Restore Previous Session', or left from
  the previous campaign), and Profile > Load Profile is used with a profile whose Excel file is not
  at the saved place on this PC (moved, renamed, deleted, or the profile was made on another PC), is
  there but cannot be opened, or was never set. The mixed-up emails go out only if the user then
  goes to Send without loading the right file - in the missing-file case after dismissing a warning
  that tells them to load it. (The same mix when another workbook is still loading is G66.)
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader reproduced it (Codex reported only
  the overlapping-load route, which is G66); a checker reproduced four routes - file missing, file
  damaged, no file named in the profile, another workbook still loading - through the app's own Load
  Profile with a fake Outlook, and a checker reproduced the missing and unnamed cases independently.
  Nothing material is unconfirmed.
- **Known gap:** extends G22. G22 records that a profile keeps the previous campaign's static
  attachments and folder; new is that the previous client list and its ticks also stay when the
  profile's Excel file is missing, cannot be opened or was never set, and that the app still says
  'Profile loaded successfully!'.
- **Already decided:** Change 4: partly - a profile would replace every setting it covers, but the
  Brief leaves open what happens when the profile names no Excel file, and a missing or unreadable
  file, the old list left on screen and the fixed success message are not settled
- **The repair:** Settle it together with Change 4: when the profile's Excel file cannot be found or
  opened, either stop before changing anything, or load the rest but clear the list and ticks on
  screen. Replace the fixed 'Profile loaded successfully!' with a summary of what was and was not
  loaded.
- **Your call:** When a profile's Excel file cannot be found or opened, should the app stop and
  change nothing, or load the subject, body and attachments anyway but clear the list on screen so
  that nothing can go to the earlier list? (Recommended: stop and change nothing; what a profile
  that names no Excel file should do is the point already left open under Change 4.)
- **Where in the code:** ui/main_window.py:837-855 (the list is replaced only when the profile's
  file exists; otherwise a warning at most, and nothing is cleared), 857-861 (subject, body and BCC
  are replaced regardless), 812-814 (fixed 'Profile loaded successfully!'); ui/tab_excel.py:413-420
  (a file that cannot be opened gives only the error box)

### G78 — Coming back to the Send tab during a batch replaces its list: wrong status line, and Retry can disappear

- **What happens:** Each time the Send tab is opened again while a batch is running, the app
  rebuilds that tab's list of emails from whatever is ticked at that moment. The emails already
  queued keep going out unchanged, but the status line reads 'Ready: N emails to send' until the
  next email goes, the Pre-Send Summary shows the new numbers for the rest of the run, and 'Resume
  Previous' appears (the known gap G43). If the ticks were changed meanwhile, the batch ends with
  'Sent: 3, Failed: 1 ... Use 'Retry 1 Failed'' but neither a Retry nor a Resume button is offered,
  even after ticking everyone again: the failed client has to be found in the progress list and sent
  by hand.
- **When:** A batch is running and at least one email in it fails. The user goes to Recipients and
  clears or changes the ticks so that the failed client is no longer ticked (or picks File > New
  Session), then returns to the Send tab before the batch ends. Only visiting another tab and coming
  back, with the ticks unchanged, gives just the wrong status line, the changed summary and the
  Resume Previous button; the Retry button then still appears at the end.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader found and ran it; a checker
  reproduced it with the real window, 4 dummy clients, a 2-second delay and a fake Outlook refusing
  the first email, in three variants (Clear Selection, only the failed client unticked, New
  Session), and in two controls (tab visited with ticks unchanged, tab never left) the Retry button
  did appear. Codex did not report it.
- **Known gap:** extends G43. G43 records only that Resume Previous comes back during a run and
  sends the pending emails twice; the lost Retry button and the wrong status line and summary are
  new consequences of the same cause, the Send tab being rebuilt when it is re-opened during a run.
- **The repair:** While a batch is running, leave the Send tab's list, status line and summary alone
  when the tab is opened again, and decide whether to offer 'Retry N Failed' from the finished
  batch's own failed clients, not from the current ticks. It is the same repair as G43 (nothing is
  rebuilt or restarted during a run), so the two can be done together.
- **Where in the code:** ui/main_window.py:443-445 (the Send tab is rebuilt on every entry, with no
  check that a batch is running), 473-488; ui/tab_send.py:457-458 (the list and the status line are
  replaced), 463-470 (Resume Previous is shown), 767-773 (the Retry list is built from the replaced
  list, line 770); ui/main_window.py:617-639 and 772-822 (New Session and Load Profile do not check
  for a running batch)

### G79 — An emoji in the Subject box closes the app; a saved subject with one closes it at every restore or load

- **What happens:** If a picture-emoji (folded hands, a lamp, a party popper and most other colour
  emoji) is typed or pasted so that it sits at or near the end of the Subject box, the whole app
  closes that instant with no message and nothing in its log; whatever was changed since the last
  3-minute auto-save is lost. An emoji gets in safely only when it is added in front of words
  already in the box, and from then on that subject is a trap: typing or deleting at its end, the
  Subject line's Insert button, loading that template or profile, or answering Yes to 'Restore
  Previous Session?' closes the app every time. Answering No lets the app start, but the saved
  session is then replaced by an empty one. The body is safe (there an emoji only makes the '{'
  pop-up list narrow on the wrong letters), and so are ordinary symbols such as the rupee sign, a
  tick, a star or a heart, and Hindi text.
- **When:** Only characters that are stored as a pair: most colour emoji and the 'fancy font'
  letters copied from web tools (15 of 15 tested closed the app; 18 ordinary symbols did not). In
  the Subject box - and in the Format box of 'Display as: Custom...' on the Preview tab - the app
  closes when such a character is typed (Win + .) or pasted with the cursor at the end, when a whole
  subject holding one is pasted into the empty box, when the user types or presses Backspace at the
  end of a subject that already holds one, and when the box is filled in one go with such a subject:
  Restore Previous Session > Yes, Load on the Compose tab, Profile > Load Profile, or the Subject
  line's Insert button. Because the office shares one saved session, every user who answers Yes is
  closed out. It can also strike during a batch, because the Compose tab stays usable while emails
  are being sent: in the test the run stopped after 3 of 8 emails and was left waiting to be
  resumed.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader found it and Codex did not; a checker
  reproduced it with the app's real classes, one scenario per process (process killed with exit code
  0xC0000409 from an IndexError at variable_completer.py:223; 33 characters and 16 cursor positions
  with no miss; trapped session, template and profile; a mid-batch kill), and a checker reproduced
  it independently. Not confirmed: the real Windows emoji panel (Qt ran off-screen; Ctrl+V paste was
  exercised exactly), what Windows shows when the app closes on an office PC, and whether the email
  in flight at a mid-batch close is delivered; G35 is why it closes silently and G24 why one saved
  subject affects every user.
- **The repair:** Make the pop-up helper count positions the same way as the text it reads, in every
  place that mixes the two counts (the Subject pop-up, the Subject line's Insert button and the body
  pop-up's narrowing); a guard on the one faulty line alone stops the closing but leaves the
  variable landing one character off per emoji. Also add the last-resort safety net (known gap G35),
  so that no error can close the app without a word.
- **Where in the code:** ui/components/variable_completer.py:201-226 (line 223), 242-258, 339-368;
  ui/tab_compose.py:124, 300-308, 409-411; ui/tab_preview.py:112; main.py (no last-resort error
  hook)

### G80 — An email with a blank subject, an empty body, or both can be sent to every ticked client with no warning

- **What happens:** The app never checks that a letter has actually been written. With the client
  list loaded and clients ticked, Start Sending asks only 'Are you sure you want to send N emails?'
  and then hands Outlook one email per client with a blank subject line and an empty body, each with
  that client's own attachments, and finishes with 'Successfully sent N emails!'. The same happens
  when only the subject or only the body was forgotten; the Preview tab shows the blank email
  without comment and the '2. Compose' tab carries its tick the whole time. What real Outlook does
  with a blank subject sent this way was not tested.
- **When:** A client list is loaded, at least one client is ticked, Outlook is connected, and the
  subject box, the body or both are empty: Compose was never filled in; a saved template was picked
  in the Template drop-down but Load was not pressed; File > New Session was used and the list
  loaded again; or only the subject or only the body was forgotten. Then open the Send tab, click
  Start Sending and answer Yes (Send Test Email First behaves the same way).
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader found and ran it; a checker
  reproduced it through the real window with a fake Outlook in four variants (Compose never touched,
  after New Session, only the subject missing, only the body missing) and for a template picked but
  not loaded, and counted 0 calls of the three unused checks. Codex did not report it; what real
  Outlook does with a blank subject sent by a program was not tested.
- **The repair:** Before Start Sending and Send Test Email First (and Resume Previous and Retry
  Failed), look at the emails that were built: if the subject is blank or the body has nothing a
  reader would see, stop or ask, as the office decides, say what is missing and point to the Compose
  tab. This belongs in the same check before sending that Change 5 adds for {MISSING}; a body that
  holds only a picture must count as filled in.
- **Your call:** If the subject line is blank or the body is empty when someone clicks Start Sending
  or Send Test Email First, should the app refuse to send until it is filled in, as you decided for
  {MISSING}, or only warn once and let them send anyway? (Recommended: refuse to send until it is
  filled in.)
- **Where in the code:** ui/tab_send.py:582-600 (the only test is 'no emails at all', line 584; one
  question, 592-597), 519-567 (the test email likewise, line 521); core/outlook_sender.py:295-299,
  330 and 338 (only a missing To address is refused; subject and body are passed on as they are);
  the three checks that know about an empty subject or body have no caller:
  ui/tab_compose.py:421-444, core/email_builder.py:334, ui/tab_preview.py:479;
  ui/components/rich_text_editor.py:472 (the editor's own 'is the body empty' test, which the repair
  should use)

### G81 — A saved column choice whose heading has gone is silently swapped for the app's own guess or for 'None'

- **What happens:** When a session is restored, a profile is loaded or Refresh is clicked, the app
  puts back each column choice only if a heading with that name (capital letters aside) is still in
  the workbook. If the heading was renamed, deleted or merely gained a trailing space, that choice
  is skipped without any message: To and Identifier 1 stay on the app's own guess (the first column
  if no heading looks like an email column), and CC, BCC and Identifier 2 stay on 'None'. The status
  bar still says 'Session restored' or 'Refreshed', and a profile still says 'Profile loaded
  successfully!'. In the checker's test run, emails set to go to the 'Accounts Email' column with a
  copy to 'Partner Email' went to the owner's 'Email' address with no copy; the changed choices do
  show on the Excel tab, but nothing points to them.
- **When:** A column was chosen by hand (To, CC, BCC, Identifier 1 or Identifier 2) and its heading
  is later changed in the workbook - renamed (for example 'Accounts Email' to 'Accounts Mail'),
  deleted, or given or losing a trailing space - followed by Yes to 'Restore Previous Session?' for
  that workbook, Profile > Load Profile naming that workbook, or Refresh. A change of capital
  letters alone does not set it off. Harm needs the lost choice to differ from the app's own guess,
  which is always so for CC, BCC and Identifier 2.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader reproduced it (Codex did not report
  it); a checker reproduced it on all three routes - session restore, Refresh and Load Profile -
  with control runs showing that the changed heading, not timing, causes the fallback, and a checker
  came across it independently on Refresh and a profile. All runs were off-screen on dummy data with
  a fake Outlook.
- **Known gap:** extends G23. G23 and the Brief's note under contract C12 cover only a restore or
  profile that reads the wrong row or sheet; new is that a renamed, deleted or re-spaced heading
  sets off the same silent fallback, and that Refresh does it too.
- **Already decided:** Change 11: partly - it removes the known cause (a restore or profile reading
  the wrong row or sheet), but a renamed, deleted or re-spaced heading, and the Refresh route, would
  still fall back silently; no decided change adds a message
- **The repair:** After a restore, a profile load or Refresh, compare each saved column choice with
  the headings actually read and show one message naming every choice that was not found. Show such
  a field as 'not chosen' instead of keeping the app's guess, and do not send while To is not
  chosen.
- **Your call:** When a saved column choice (To, CC, BCC or an identifier) is no longer among the
  workbook's headings after a restore, a profile load or Refresh, should the app stop and make you
  choose that column again, or carry on with its own guess after showing you a message?
  (Recommended: stop and make you choose that column again.)
- **Where in the code:** ui/tab_excel.py:724-733 (a saved name that is not found is skipped, with no
  message), 495-511 and 520-546 (the drop-downs were refilled and guessed just before), 699-702
  (Refresh), 781-791; ui/main_window.py:553-555 (session restore), 840-846 (profile)

### G82 — Restored ticks past the end of a shorter list: wrong counts, and Save Selection or Copy closes the app

- **What happens:** After Restore Previous Session the app ticks the saved row numbers without
  checking that those rows still exist. If rows were deleted from the workbook since, the Recipients
  tab shows wrong or impossible counts such as '5 of 3 recipients selected', and the extra ticks
  cannot be removed by unticking rows because no row shows them. Sending is safe (the Send tab
  builds emails only for rows that exist), but clicking 'Save Selection...' and typing a name, or
  right-click > 'Copy Selected Emails', closes the app at once with no message, and anything not yet
  saved is lost. Clicking Select All or Clear Selection with the search box empty removes the extra
  ticks.
- **When:** A session is saved with ticks on rows near the end of the list (everyone ticked is
  enough); rows are then deleted from the workbook, for example a pending list that shrinks as
  clients comply; at the next start the user answers Yes to 'Restore Previous Session?' and later
  uses 'Save Selection...' or 'Copy Selected Emails'.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by several readers. Six readers reproduced it and a checker
  reproduced it as a side finding with real restarts; Codex did not report it and there was no
  dedicated re-check. Four of them saw the real click end the program with no message on the
  development PC (Windows exit code 0xC0000409 or 127, PyQt5 5.15.11), which confirms there what G35
  only inferred; the office PCs were not tried.
- **Known gap:** extends G20. G20 (kept by decision) says restore re-ticks by row number; new here
  are the ticks on rows that no longer exist, the wrong counts, and the app closing on 'Save
  Selection...' or 'Copy Selected Emails'.
- **The repair:** On restore, drop saved row numbers that are beyond the loaded list and say how
  many were dropped; make 'Save Selection...' and 'Copy Selected Emails' skip rows that no longer
  exist.
- **Where in the code:** ui/main_window.py:557-559 (saved row numbers passed on unchecked);
  ui/components/recipient_list.py:397-405 (set_selected_indices stores them as given), 407-414
  (get_selected_data), 345-354 (_copy_selected_emails); ui/tab_recipients.py:213-220 (_save_list
  reads the ticked rows after the name is typed), 256-260 and 300-304 (counts); contrast
  ui/tab_recipients.py:150-154 (loading a saved list does check the range)

### G83 — A session saved with nobody ticked comes back with everybody ticked

- **What happens:** If the app is closed with no client ticked, the saved session correctly records
  that nobody is ticked, but after Yes to 'Restore Previous Session?' every row comes back ticked
  ('5 of 5 recipients selected', Send tab 'Ready: 5 emails to send'). Loading the workbook ticks
  everyone first, and the saved ticks are put back only when at least one row was ticked. A saved
  selection with one or more ticks comes back correctly. The restore question gives no clue, because
  it always says 'Recipients: 0 selected' (G21).
- **When:** Workbook loaded; on the Recipients tab click Clear Selection (or untick every row by
  hand), for example to hand-pick clients later or so that nothing can be sent by accident; close
  the app (closing saves the session) or let the 3-minute automatic save run; start the app and
  answer Yes to 'Restore Previous Session?'.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Three readers reproduced it and Codex reported
  it in all three jobs (rated HIGH there); a checker reproduced it with a real restart in two
  separate processes (saved ticks [] came back as [0, 1, 2, 3, 4]; a control with ticks [1, 3] came
  back correctly) and rated it MEDIUM, which is used here.
- **The repair:** On restore, apply the saved selection whenever the session holds one, also when it
  is empty; fall back to everyone ticked only when the session holds no saved selection at all.
- **Where in the code:** ui/main_window.py:557-559 (`if selected:` skips an empty saved list), 505
  (the empty list is saved); ui/tab_recipients.py:292-296 (every load ends in select-all)

### G84 — Rows hidden or filtered out in Excel are loaded and ticked like all the others

- **What happens:** The app reads every row of the sheet and ticks every one, whether or not the row
  is hidden in Excel by a filter or by hand. Staff who filter the list in Excel to, say, the
  'Pending' clients, save it and load it get all the clients, including those the filter hid, all of
  them ticked. Nothing says that hidden rows were included; the only sign is the full count on the
  Recipients tab and in the 'Are you sure you want to send N emails?' question, and if that is
  missed the filtered-out clients get the email too.
- **When:** The list is filtered in Excel (for example Status = Pending), or some rows are hidden by
  hand, the workbook is saved, and it is then loaded or refreshed in the app.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by several readers. Three readers each loaded a dummy
  workbook with a filter and hidden rows and got every row; Codex did not report it and no checker
  re-ran it. A list filtered and saved in Excel itself was not tried, but the app never looks at
  hidden marks at all (the read-only way it opens the workbook does not even supply them); rated
  MEDIUM as two of the three readers did (the third said LOW), because the full count is on screen.
- **The repair:** Settle the rule first; then leave rows that are hidden or filtered out in Excel
  out of the list, or load them unticked, or load them as today, and in every case say how many
  hidden rows there were.
- **Your call:** When rows are hidden or filtered out in the Excel list, should the app leave them
  out, load them unticked, or load and tick them as it does today? (Recommended: load them unticked
  and show a message saying how many rows are hidden in Excel.)
- **Where in the code:** core/excel_handler.py:143 (every row of the sheet is read), 166-171 (only
  completely empty rows are skipped), 55-59 (read-only opening, which gives no row visibility);
  ui/tab_recipients.py:292-296 (every loaded row is ticked)

### G85 — The second 'Select All' / 'Clear Selection' pair acts only on rows a search shows, and does not say so

- **What happens:** The Recipients tab has two pairs of selection buttons. While a search is showing
  only some rows, the small pair under the table changes its captions to 'Select All (2 shown)' /
  'Select None (2 shown)', but the second pair beside the summary line keeps reading 'Select All' /
  'Clear Selection' although it, too, acts only on the rows shown. A user who searches for one
  client, clicks 'Clear Selection' meaning to start from nobody and then ticks that client is left
  with every hidden client still ticked. The counts stay truthful ('9 of 10 recipients selected',
  and the number on the Send tab), so a careful user can see it; a hurried one emails nearly
  everybody.
- **When:** Recipients tab with clients ticked (everyone is ticked after a list loads): type
  something in the search box so that only some rows show, then click 'Clear Selection' or 'Select
  All' at the bottom right, beside the 'N of M recipients selected' line.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by several readers. One reader reproduced it on the
  Recipients tab and a checker, independently, through the real main window (four hidden clients
  stayed ticked and the Send tab offered 5 emails where 1 was meant); Codex did not report it and
  there was no dedicated re-check. Acting only on the rows shown is the intended, tested rule for
  the small buttons (tests/test_recipient_table.py) - the defect is the uncaptioned second pair.
- **The repair:** Give the second pair the same '(N shown)' captions while a search is active, or
  make it always act on every client in the list, or remove the duplicate pair.
- **Your call:** While a search is showing only some rows, should the bottom 'Select All' / 'Clear
  Selection' buttons act on every client in the list, or only on the rows shown and say so in their
  captions, like the small buttons under the table? (Recommended: only the rows shown, with '(N
  shown)' in the caption - the rule the Brief already keeps for the small buttons)
- **Where in the code:** ui/tab_recipients.py:95-101 (the second pair is wired to the same
  search-aware actions as the small pair); ui/components/recipient_list.py:290-300 (only the table's
  own three buttons get the '(N shown)' caption), 361-375 (select_all / select_none act on the shown
  rows while a search is active)

### G86 — Hidden Office lock files (~$...) in the client folder are matched and attached like real documents

- **What happens:** When the folder is read, the app lists every file in it, including hidden ones:
  the small lock file that Excel or Word keeps beside an open document
  ('~$AAAPA1111A_statement.xlsx'), temporary files, Thumbs.db and desktop.ini. A lock file's name
  contains the client's code, so it is matched and added to that client's email beside the real
  file. What follows was not tested with Outlook: either the client receives a stray hidden file
  that holds the staff member's user name, or Outlook cannot attach it and that client's email fails
  with 'Not sent - could not attach: ~$...' (three such failures in a row stop the batch).
- **When:** A colleague has a client's Excel or Word file open from the client-files folder - or
  Office closed badly earlier and left its lock file behind - at the moment the folder is read
  (Browse..., Rescan, a restored session or a profile), and that file's name contains the client's
  identifier. If the document is closed again before sending, the lock file has gone and that email
  is expected to fail with 'could not attach' until Rescan is clicked.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by several readers. Three readers each showed on dummy files
  that a hidden '~$' lock file (in one run also a '.TMP' file, in another Thumbs.db and desktop.ini)
  is listed and added to the client's attachments; no checker re-ran it and Codex did not report it.
  Not confirmed: whether classic Outlook can attach a lock file that Excel still holds (Outlook was
  never started), so which of the two outcomes occurs is unknown; the readers rated it MEDIUM, LOW
  and LOW, and MEDIUM was settled here because either outcome - a failed email or a stray file
  naming a staff member - is a visible fault in a client's email, not a cosmetic one.
- **The repair:** When reading the folder, leave out files whose name starts with '~$', files
  Windows marks as hidden or system, and Thumbs.db / desktop.ini, and say in the 'Found N files'
  line how many were left out.
- **Where in the code:** utils/file_utils.py:293-315 (297-298, 309-310: every file is taken; no
  check of the hidden/system attribute or the '~$' prefix), 325-340; ui/tab_attachments.py:297 (no
  file-type filter is passed); core/attachment_matcher.py:131-134; core/outlook_sender.py:340-356

### G87 — The 'All N emails valid' line and red cells are not redone when the To Email column changes

- **What happens:** The green 'All N emails valid' line and the red cells on the Excel tab are
  worked out once, when the list is read, for the column the app itself picked as To Email. Choosing
  another To Email column changes where the emails go, but the line and the red cells are not worked
  out again: with three malformed addresses and one blank in the newly chosen column the tab still
  said 'All 5 emails valid' and marked nothing red. Validate Emails does list the problems in a
  pop-up, but the green line stays, also after Refresh and after closing and restoring the session.
  It also works the other way: a red 'N invalid email(s)' line and its red cell stay after To Email
  is moved to a clean column.
- **When:** A list with two or more address columns (for example Email and AlternateEmail), or any
  list where the app's own pick for To Email is not the wanted one (G28). The list loads and the
  user picks a different column in the To Email drop-down; from then on the line and the red cells
  describe the app's first pick. The same after Refresh, Restore Previous Session and Load Profile,
  because each of them checks the list first and puts the saved To Email column back afterwards.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Two readers reproduced it and Codex reported it
  (window-16); a checker reproduced it through the real main window in both directions, also after
  Refresh and after a restart with restore, and two other checkers reproduced it independently as
  side findings. One reader's note that loading a sheet with no rows leaves the old 'Showing first
  100 of N rows' text is confirmed by reading ui/tab_excel.py:558-562 only.
- **Already decided:** Change 7: partly - blank and invalid addresses would be listed before a run,
  so the false 'all valid' line could no longer let them through; the line and the red cells on the
  Excel tab would still describe the wrong column
- **The repair:** Work the line and the red cells out again whenever the To Email column changes, by
  hand or after a Refresh, a restore or a profile has put the saved column back, and let Validate
  Emails update the same line.
- **Where in the code:** ui/tab_excel.py:486 (the only call of _populate_preview_table, inside
  _load_sheet_data 473-489), 548-628 (the check: column picked at 572-575, red cells 599-604, count
  611-620), 630-654 (the line), 656-659 (_on_mapping_changed only passes the choice on), 661-686
  (Validate Emails never updates the line), 699-705 (Refresh checks first and puts the mapping back
  afterwards), 717-757 and 781-791 (restore and profile); 558-562 (an empty sheet leaves the old
  'Showing first 100 of N rows' text)

### G88 — The address check passes addresses that cannot exist (gmail..com) and marks some valid ones as invalid

- **What happens:** The address check only looks at the rough shape of an address. It accepts
  addresses that cannot exist (two dots together as in bina@example..com, a dot just before or after
  the @, a dot or hyphen at the start or end of a part of the domain): the cell is not red, the
  Excel tab says 'All N emails valid', Validate Emails lists nothing, and the address is handed to
  Outlook exactly as typed. The other way round, a real address with an apostrophe or '&' before the
  @ (o'brien@...) is shown red and counted as invalid; it is still sent, because today the check
  never stops anything. What the real Outlook or the mail server then does with an impossible
  address could not be tested: either Outlook refuses it (that client shows as failed) or it is
  accepted and comes back later as undeliverable while the app says 'Sent'.
- **When:** A cell in the To Email column with a doubled dot or a dot or hyphen in the wrong place
  (for example asha@example..com, asha@.example.com, .asha@example.com, asha.@example.com,
  asha@-example.com, also inside a ';' list), or a valid address with ' or & before the @. No clicks
  are needed beyond loading the list: the red cells, the count line and Validate Emails all use this
  one check. Clearly wrong shapes are still caught (no @, no ending, a space, a comma, a trailing
  dot).
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader found it (28 dummy addresses tried);
  Codex did not report it. A checker reproduced it with the real Excel tab and end to end with a
  fake Outlook (bina@example..com and cara.@example.com not red, 'All 8 emails valid', handed over
  unchanged; a&b@ and o'brien@ shown red); what the real Outlook or a mail server does with such an
  address was not tested.
- **The repair:** Check the name and the domain separately: refuse two dots together, a dot at
  either end of the name, and domain parts that are empty or start or end with a hyphen, and allow
  the other characters real addresses may have before the @ (at least ' and &). Do it before or
  together with Change 7, which will rely on this same check, and bring rule R1 in the Brief into
  line.
- **Where in the code:** core/validators.py:33 (the single pattern, in validate_email_address 15-45;
  is_valid_email 48-78); used at ui/tab_excel.py:599-604 and 613-618, and through
  validate_email_list at core/excel_handler.py:427

### G89 — CC, BCC and Universal BCC addresses are never checked: no red cell, no warning, sent as typed

- **What happens:** The address check on the Excel tab looks only at the 'To Email' column. A CC
  cell holding 'broken@' or a person's name, a BCC cell holding 'audit@example' or two addresses
  joined by a comma, and 'records@firm' typed in the Universal BCC box all pass unnoticed: no cell
  turns red, the tab says 'All 3 emails valid', Validate Emails says 'All 3 email addresses are
  valid!', and every value is handed to Outlook exactly as typed. Preview does not show CC or BCC
  today, so nothing on screen reveals it. What the real Outlook then does was not tested: it may
  refuse that whole email or send it without the copy, and a mistyped Universal BCC would touch
  every email of the run or lose the office's record copy.
- **When:** A CC or BCC column is chosen on the Excel tab and one of its cells holds something that
  is not a valid address (a typing slip, a name, a comma instead of ';'), or a mistyped address sits
  in the 'Universal BCC (added to all emails)' box on the Compose tab. No extra click is needed:
  nothing checks these values at any step up to Start Sending.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by one reader. No reader and not Codex: a checker came across
  it and ran it once through the real main window with a recorder in place of Outlook (CC='Ramesh
  Kumar' and BCC='a@example.com, b@example.com; records@firm' were handed over and the run ended
  'Complete: 3 sent, 0 failed'); I confirmed in the code that only the To column is ever examined.
  Not confirmed: what the real Outlook does with such a CC or BCC (refuse the email, match a name
  against the address book, or send without the copy).
- **Known gap:** extends G6. G6 and Change 7 speak of the To address only; the CC and BCC columns
  and the Universal BCC box are equally unchecked, and a bad Universal BCC touches every email of a
  run.
- **Already decided:** Change 7: partly - it is worded for the row's To address; CC and BCC cells
  and the Universal BCC box would stay unchecked unless its plan includes them (Change 3 would only
  make CC and BCC visible in Preview)
- **The repair:** Check the CC and BCC cells and the Universal BCC box with the same address check
  as the To column: mark bad cells, count them in the line above the Data Preview, let Validate
  Emails list them, and include them in the list shown before a run under Change 7. Build it
  together with Change 7.
- **Your call:** When a row's CC or BCC address is invalid, or the Universal BCC is invalid, should
  the app treat it like an invalid To address under Change 7 - list the row and leave it out unless
  you confirm, and not start a run while the Universal BCC is invalid? (Recommended: yes)
- **Where in the code:** ui/tab_excel.py:572-575, 599-604, 613-618 (red cells and the count look
  only at the To column), 661-668 (Validate Emails checks only the To column);
  core/excel_handler.py:404-441; ui/tab_compose.py:404-407 (the Universal BCC is only trimmed);
  core/email_builder.py:225-243, 315-332 (CC, BCC and Universal BCC are passed on as typed);
  core/outlook_sender.py:323-327

### G90 — Session restore says nothing when the saved client folder cannot be reached, and the next save forgets it

- **What happens:** Unlike a missing Excel file, nothing is said about the folder: the list,
  subject, body and static files come back, but the Attachments tab shows 'No folder selected' and
  every email is built without client files. With a static file attached, the '3. Attachments' tab
  keeps its tick and the Send tab says 'All have attachments', so the run goes out with the static
  file only and ends 'Successfully sent'; without one, the Send tab does warn 'N without
  attachments'. At the next auto-save (3 minutes) or on closing, the session is saved without the
  folder and with 'Include subfolders' unticked, so the folder does not come back at a later start
  even when it can be reached again.
- **When:** The saved session names a client-files folder that cannot be reached when the app starts
  - the server drive is not connected yet, or the folder was renamed or moved - and the user answers
  Yes to 'Restore Previous Session?'. Loading a profile in the same situation does show 'Attachment
  Folder Not Found'; a session restore shows nothing.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** reproduced by several readers. Four readers reproduced it, and a checker
  reproduced it independently as a side finding through the real window (folder really renamed away:
  only the restore question appeared, both emails went with the covering letter only under 'All have
  attachments', the session file was saved with an empty folder, and the box stayed empty at the
  next start with the folder back); there was no dedicated re-check and Codex did not report it.
  Read from the code only: a saved static file that no longer exists is restored just as quietly
  (shown in red in the list), and each email would then fail with 'could not attach'.
- **The repair:** At restore, name the saved folder (and any saved static file) that could not be
  found, as the app already does for a missing Excel file and when a profile is loaded. Keep the
  folder in the saved session - shown as 'not found', with a way to try again - until the user
  chooses another one.
- **Where in the code:** ui/main_window.py:538-543 (the result of set_folder is ignored; compare the
  warnings at 519-526 and 885-890), 501-502 (the session then saves a blank folder and the unticked
  subfolders box); ui/tab_attachments.py:542-544 (returns before the box or the tick is touched)

### G91 — Save on the Compose tab overwrites whichever template the drop-down shows, without asking

- **What happens:** Choosing a template in the Template drop-down does not load it - only the Load
  button does - but Save writes whatever is on screen into the template the drop-down is showing at
  that moment, at once, without asking and without keeping the old text. The only sign is a
  four-second line at the bottom of the window ('Template ... saved'), and the edits meant for the
  template that was loaded are not saved there either. Done just after start-up with nothing typed,
  it replaces the chosen template with an empty one. The templates sit in the shared folder, so the
  template is replaced for every user.
- **When:** Compose tab. The drop-down shows a saved template other than the one whose text is on
  screen: it was picked without clicking Load (to look, or meaning to load it), it was moved by one
  notch of the mouse wheel while the pointer rested on it, or it was left as it was by Profile >
  Load Profile, which changes the text but not the drop-down. Then one click on Save, which sits
  next to Load. It does not happen after a start-up restore: there the drop-down shows '-- New
  Template --' and Save asks for a name.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Four readers reported it (three ran it, one read
  the code) and Codex did not; a checker reproduced it by clicking the real Load, Save and Save As
  buttons (no question shown, 'ITR Notice' on disk held the GST letter, no backup file) and refuted
  one reader's claim that it also happens after a session restore, which is left out here. A checker
  also reproduced it and rated it LOW, but the dedicated verdict's MEDIUM is used; the mouse-wheel
  route was shown off-screen, not with a real mouse.
- **The repair:** Remember which template the text on screen came from; when Save would write into
  any other template, or the screen is empty, ask 'Replace template X with the text on screen?'
  first, as Save As... already does. Keeping the previous version as a backup copy would make a slip
  recoverable.
- **Where in the code:** ui/tab_compose.py:209-225, 69-84, 237-245; data/template_storage.py:76-77,
  103-104; ui/main_window.py:857-861

### G92 — Leaving 'Restore Previous Session?' unanswered for 3 minutes wipes the saved session; Yes restores nothing

- **What happens:** The app starts its three-minute auto-save clock when the window opens, before it
  asks 'Restore Previous Session?', and the clock keeps running while the question waits. If the
  question is still open three minutes after start-up, the app saves the empty window over the saved
  session. Clicking Yes then reads that emptied file: the status bar says 'Session restored', but no
  list, column choices, subject, email text, Universal BCC, attachment settings or ticks come back,
  and the earlier session is gone for good. Later starts offer only the empty session.
- **When:** A saved session exists (the app was last closed with work in it). Start the app and
  leave 'Restore Previous Session?' unanswered for three minutes or more - a phone call, tea, or the
  question hidden behind another window - then click Yes. Answering within three minutes restores
  normally. (Answering No loses the session too: see G93.) Because every PC shares one data folder
  today (G24), the session wiped this way can be a colleague's.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Five readers reproduced it and Codex reported it
  twice (as 'possible', not run); a checker confirmed with untouched settings that the 180 s clock
  is already running before the question, then reproduced the loss through the real main window
  (auto-save shortened to 1 s, question open 2.6 s; a control answered after 0.4 s restored
  normally), and three other checkers reproduced it in passing. Not waited out at the real 180 s nor
  run on a real screen (the stock question box crashes off-screen, so a stand-in box that waits the
  same way was used); readers and Codex rated it HIGH, the checker MEDIUM because no email is
  affected and the set-up can be redone by hand.
- **The repair:** Start the auto-save only after the restore question has been answered and the
  restore has finished, and restore from the copy already read before the question instead of
  reading the file again. As a second guard, never let an automatic save replace a saved session
  that holds work with an empty window.
- **Where in the code:** ui/main_window.py:56 and 324-329 (auto-save started while the window is
  built), 563-615 (session read at 568, question at 599-608, file read AGAIN at 611 after Yes);
  data/session_manager.py:333-343 (_do_save skips only while a send is running); config.py:56 (180
  s); main.py:64-66 (question asked only after the window is shown)

### G93 — Answering No to 'Restore Previous Session?' (or Esc, or the X) throws the saved session away for good

- **What happens:** If the answer to 'Restore Previous Session?' is No - and pressing Esc or
  clicking the X counts as No - nothing is restored and nothing is said. The app then saves the
  empty window over the saved session, at the next automatic save (at most three minutes after
  start) or the moment the window is closed. After that the Excel file choice, column choices,
  subject, email text, Universal BCC, attachment settings and ticked clients are gone: no menu
  command brings them back, and the next start offers only an empty session. Closing the app quickly
  in order to answer again is exactly what wipes it.
- **When:** A saved session that holds real work and was not also saved as a Profile or a template.
  Start the app; on 'Restore Previous Session?' click No, press Esc or click the X; then leave the
  app open for three minutes or close the window. It is easy to answer wrongly, because the question
  appears at every start, even for an empty session, and always says 'Template: Custom' and
  'Recipients: 0 selected' (G21). With today's shared data folder a colleague's No wipes your
  session the same way (G24).
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader found it by reading the code (rated
  'likely'); Codex did not report it. A checker reproduced the No path through the real main window
  (the file still held the campaign right after No, was empty after the auto-save and after
  No-then-close, no box was shown, no menu command restores); the 3 minutes were not waited out (the
  auto-save was fired by hand), and Esc and the X were tried on an identical Qt Yes/No box, not the
  app's own, which cannot be opened off-screen.
- **The repair:** Never let an untouched, empty window overwrite a saved session that holds work:
  save only once the user has changed something, or keep the declined session so that a File-menu
  command can bring it back. Treat Esc and the X as 'ask me again next time', not as No.
- **Your call:** When you answer No to 'Restore Previous Session?', should the app keep that saved
  session so you can still bring it back later (for example from the File menu) until you really
  start new work, or should No throw it away, as it does today? (Recommended: keep it until real new
  work replaces it.)
- **Where in the code:** ui/main_window.py:599-615 (after anything but Yes the function simply
  ends), 677-679 (every close saves the window as it is); ui/components/dialogs.py:71-75 (only Yes
  counts as Yes); data/session_manager.py:333-343 (auto-save, no check for an empty window);
  utils/file_utils.py:16-29 (the old file is replaced, no backup copy); ui/main_window.py:88-108
  (File menu has no restore command)

### G94 — Pictures that arrive by Ctrl+V, by dragging from a browser or by Import File go out as links, not pictures

- **What happens:** When staff copy something that contains a picture from Word or Outlook (the
  firm's signature with its logo, a letter with a screenshot) and paste it into the body with
  Ctrl+V, the app keeps only the address of a temporary file on that PC, not the picture itself. The
  picture shows normally in the body and in Preview and nothing warns, but the email handed to
  Outlook carries only that address (which also shows the sender's Windows user folder), so a
  client's mail program most likely has nothing to display - that last step needs real Outlook and
  was not tested. Pictures pasted or dragged from a web page, and pictures in an imported .html
  file, also go out as mere addresses, but those already show as a grey blank icon in the body and
  in Preview. A template or session saved with a pasted Word or Outlook picture later shows a
  different picture, or none, once that temporary file changes.
- **When:** A picture reaches the body by any way other than the Image button: (1) Ctrl+V of content
  copied from Word or Outlook that includes a picture - the silent case, because the file exists on
  this PC and is displayed; (2) Ctrl+V after 'Copy image' in a web browser, or a picture dragged
  from a browser; (3) Import File... with an .html or .htm file whose pictures are separate files or
  web addresses. Then Preview, Send Test Email or Start Sending as usual; no setting is involved.
  Pictures put in with Image > From File... or Image > From Clipboard are sent correctly, and Ctrl+V
  of a bare screenshot pastes nothing at all.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. One reader found it and Codex did not; a checker
  reproduced it with the real window, Qt's off-screen clipboard and a fake Outlook (the pasted logo
  was displayed in the editor and Preview, only the control picture was recognised, and the body
  handed over still held an img tag pointing at file:///.../msohtmlclip1/01/clip_image002.png, with
  'Complete: 2 sent, 0 failed'). Not run: a live Word or Outlook clipboard (its usual shape was
  written by hand), real Outlook and a real recipient - so what clients actually see, and whether a
  test email opened on the same PC hides the fault, needs one check on an office PC.
- **Known gap:** extends G34. G34 is rated LOW from code reading and blames single quotes or other
  formats; the real trigger is a picture pasted from Word or Outlook, which looks right on screen,
  and G34's own example is wrong because a picture written with single quotes is recognised.
- **The repair:** On paste, drop and import, turn every picture that points at a file on this PC
  into a real inline picture at once, keeping its width and height, and before any send - the test
  email included - list the pictures that are still only an address and stop or ask. Let Ctrl+V of a
  bare screenshot insert the picture too.
- **Your call:** When the body contains a picture that is only a link (pasted from Word, Outlook or
  a web page, or brought in with an .html file), should the app turn it into a real inline picture
  when the file is on this PC and refuse to send while any picture is still only a link, or only
  warn and let staff send anyway? (Recommended: turn it into a real picture automatically and refuse
  to send while any picture is still only a link, as decided for {MISSING} in Change 5.)
- **Where in the code:** ui/components/rich_text_editor.py:741-769 (line 755);
  core/outlook_sender.py:332-338, 394-423; ui/tab_compose.py:487-491, 549-567;
  utils/html_converter.py:202

### G95 — Opening the Send tab with a large picture in the body freezes the window and uses a great deal of memory

- **What happens:** Every time the '6. Send' tab is opened, the app writes out the full email for
  every ticked client before it shows anything, and when the body contains a variable such as {Name}
  each email keeps its own complete copy of any picture in the body. With no picture or a small logo
  this is not noticeable; in the tests a 1 MB picture froze the window for about 1 second with 100
  clients and 6 to 9 seconds with 500, and a 3 MB picture for 4 to 6 seconds with 100 clients and
  about half a minute with 500, holding from 0.14 GB up to 2 GB of memory. Opening the tab again
  repeats the wait and briefly needs double the memory. No email goes wrong; the app closing without
  a message if the PC ran out of memory at that moment was shown only by imitating the memory
  failure.
- **When:** A picture of roughly 1 MB or more in the body (a photo or scan through Image > From
  File, or a large screenshot through Image > From Clipboard), about 100 or more ticked recipients,
  and at least one variable such as {Name} in the body (with no variable, all emails share one
  copy). Then every visit to '6. Send' (a click on the tab, Next, or Ctrl+6). A rupee sign or curly
  quotes in the body double the memory used per client.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: reproduced. Four readers measured it; a checker re-measured
  it through the real window (1 MB picture x 100 clients: about 1 s and +137 MB; 3 MB x 500: 31.7 s
  and +2,016 MB on a PC short of free memory) and a checker measured the same effect independently;
  Codex did not report it. The app closing on running out of memory was shown only with an injected
  error (known gap G35), timings are from off-screen runs on the development PC, and the verdict's
  MEDIUM is used although a checker's side finding and three readers rated it LOW.
- **The repair:** Keep each picture once instead of once per client (swap it for its short inline
  reference before the emails are built) and stop making the text-only copy that nothing uses. Build
  the emails in the background, or one at a time while sending, so the Send tab opens at once
  whatever the picture size.
- **Where in the code:** ui/main_window.py:443-445 and 473-488 (every email is built on the window's
  own thread at each visit, and the old list is replaced only afterwards);
  core/email_builder.py:249-251 (a new full body per email), 254-255 (a text-only copy, body_text,
  that nothing reads), 292; utils/html_converter.py:93-133; ui/tab_send.py:457 (the list is kept)

### G96 — Import File: Notepad 'UTF-16' and 'UTF-8 with BOM' text comes in wrong; Word tables are left out silently

- **What happens:** A text file saved from Notepad as 'UTF-8 with BOM' is imported with an invisible
  character at the very start of the body, which then goes out in every email; one saved as 'UTF-16'
  comes in as rubbish (two odd characters, then a hidden blank character after every letter) with no
  error, and {Name} in it no longer works. A Word file comes in as its plain paragraphs only - a
  table is left out, and lines typed with Shift+Enter (address and signature blocks) run together
  into one line - while the status bar still says 'Content imported'; this Word part was confirmed
  by reading and could not be run on the test PC. When the chosen file gives no text at all (a Word
  file that is only a table, a blank text file) nothing happens and no message says why. Read only
  from the published code of the Word-reading package, not run: words changed with Track Changes and
  not yet accepted (the struck-out and the newly typed ones alike), and text typed into fill-in
  fields, are left out as well.
- **When:** Compose tab > Import File... with (a) a .txt saved in Notepad with the encoding 'UTF-8
  with BOM' or 'UTF-16'; (b) a Word file that has a table, Shift+Enter line breaks or unaccepted
  tracked changes, on a PC where the Word-reading package (python-docx) is installed - without it
  the app only says 'python-docx not installed' and imports nothing; or (c) a file with no text in
  it. Related, read from the code only: a profile file re-saved in Notepad as 'UTF-8 with BOM' is
  refused by Load Profile with 'Invalid JSON file'.
- **How serious, how often:** MEDIUM · it shows up now and then (ordinary use plus a plausible habit
  or kind of list).
- **How it was confirmed:** re-checked: confirmed by reading the code. Three readers each reproduced
  the two text-file faults on dummy files; Codex reported the Word-table loss, which the checker
  confirmed from the app's code and the published source of python-docx but could not run, because
  python-docx is not installed on the test PC (a stand-in was used). The checker did run the
  'nothing said' case with a blank text file and the joined lines in the app's own editor; the Track
  Changes, HTML-file and profile-file parts are from reading only. The audit (F7, Section 6) and the
  Brief (Section 6) list UTF-8-BOM text files as handled, which the readers' runs contradict.
- **The repair:** Read text files so that Notepad's 'UTF-8 with BOM' and 'UTF-16' files come in
  clean, and keep Shift+Enter line breaks from Word. Always say what happened: before importing a
  Word file, name what will be left out (tables, tracked changes), and show a message when a file
  gives no text.
- **Your call:** When a Word file you import has a table, should the app bring the table into the
  email body, or keep importing text only but tell you clearly that the table was left out?
  (Recommended: keep importing text only, as the Brief says, but name what was left out before
  importing.)
- **Where in the code:** ui/tab_compose.py:525-547 (text files: the order of encodings at 528 -
  plain utf-8 accepts a BOM file before utf-8-sig is tried, UTF-16 is never tried and cp1252/latin-1
  accept its bytes, so the error at 547 cannot be reached); ui/tab_compose.py:502-514 (Word:
  doc.paragraphs and para.text only, 510-512); ui/tab_compose.py:476-496 (no message when nothing
  came out; 'Content imported' at 496); ui/tab_compose.py:549-567 (HTML files use the same list of
  encodings, 551 - not run); ui/main_window.py:787-789 and 818-819 (profile read as plain utf-8)

### G97 — If a newly chosen folder cannot be opened, the Folder box shows it but the previous folder's files are used

- **What happens:** On the Attachments tab, when Browse... is used to choose a new client-files
  folder and Windows will not let the app open it, the app shows 'Cannot access directory:
  Permission denied' - but it has already written the new folder's name into the Folder box. The
  previous folder stays in use: its 'Found N files' and 'identifiers matched' lines stay on screen
  under the new name, Preview and Send still attach the previous folder's files, and the session
  saves the previous folder. Rescan is greyed, but unticking and re-ticking 'Enable Dynamic
  Attachments' brings it back, and it then re-reads the previous folder under the new folder's name.
  When such a folder arrives through Profile > Load Profile, the same mix-up happens with no message
  at all, only 'Profile loaded successfully!'.
- **When:** A client-files folder has already been read in this sitting. Then Browse... to a folder
  that exists but that this Windows user is not allowed to open (a server folder that stops
  answering between the pick and the check would do the same), click OK on the error, and go on to
  Preview or Send without choosing another folder. Or use Profile > Load Profile with a profile
  whose folder exists but cannot be opened. At a session restore with no folder yet in use, the
  unopenable folder's name is left in the box while no folder is in use and nothing is said (that
  silence is G90). Choosing any folder that does open puts everything right again.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** re-checked: reproduced. Two readers found it (both simulated the
  refusal), Codex did not; the checker reproduced it through the app's real main window with a
  folder Windows really refused, a fake Outlook and dummy data: the Folder box named the April
  folder while both emails went out with the March files and the session kept the March folder, and
  the Load Profile route (a further case of known gap G22) gave the same result with no message. Not
  run: the real Windows folder picker - a stand-in returned the chosen path.
- **Already decided:** Change 4: partly - only the Load Profile route, and only if a folder that
  cannot be opened is treated like a missing one; the Browse... route would remain
- **The repair:** Write the folder into the Folder box (and change the 'Include subfolders' tick)
  only after the folder has been accepted; after a refused pick keep showing the old folder and say
  in the message that it is still in use. Give the same message when the folder comes from a
  restored session or a profile, so that the box, the folder in use and the file list always change
  together.
- **Where in the code:** ui/tab_attachments.py:265-280; core/attachment_matcher.py:53-55;
  ui/tab_attachments.py:546-554; ui/main_window.py:538-543; ui/main_window.py:879-884;
  ui/tab_attachments.py:439

### G98 — New Session while a workbook is still loading: the old list comes back by itself, ticked

- **What happens:** Choosing File > New Session while a workbook is still loading empties the window
  and says 'New session started', but the loading already under way is not stopped. When it
  finishes, the old workbook and its clients reappear on the Excel tab with everyone ticked; if that
  workbook came from the start-up restore, the old column choices and old ticks come back and the
  status bar even says 'Session restored'. In between, Browse... stays greyed out with no 'Loading…'
  text to explain why, and when the app is closed the old workbook is saved again as the session to
  restore next time. Subject, body and attachments stay empty, so the old file name on the Excel tab
  is the visible sign; if no new list is loaded, the new message would go to the old list.
- **When:** A workbook is loading (after Yes on 'Restore Previous Session?', after Browse..., or
  after a file was dropped on the tab) and the user chooses File > New Session (Ctrl+N) and presses
  Yes before the load has finished. It needs a slow load: with nothing slowed down it was caught
  with a 300-client sheet inside a 2 MB, 13-sheet workbook (about 1.3 seconds to load) and with a
  20,000-row workbook (about 4 seconds); an ordinary small list loads in about 0.1 second and cannot
  be caught by hand. If the load ends while the 'New Session?' question is still on screen, nothing
  goes wrong.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** re-checked: reproduced. Three readers reproduced it with the load
  artificially slowed and Codex reported it twice as 'possible' (engine-15, flows-16); a checker
  reproduced it through the real main window, also with nothing slowed down on larger workbooks.
  Readers' slowed runs also gave, at other moments, the file name with 0 rows or an error box about
  the load (not seen by the checker); one reader's leftovers after any New Session are filed under
  G119 and G111, except the Recipients table keeping its old empty columns and the old headings in
  the list beside the search box, which is confirmed by reading
  ui/components/recipient_list.py:443-452 only (cosmetic).
- **The repair:** New Session should cancel or ignore a workbook that is still loading: its result
  is thrown away when it arrives, and Browse... is switched back on at once. The same repair is
  needed for a folder that is still being read (G64).
- **Where in the code:** ui/tab_excel.py:793-823 (reset: does not stop or mark the running load,
  closes the shared reader at 795, never switches Browse back on), 413-424 (_on_load_finished
  applies the late result, 422-424), 389-411, 473-489; ui/main_window.py:617-639 (_new_session);
  core/excel_handler.py:443-454 (close() while the load is using the reader);
  ui/tab_recipients.py:292-296; ui/components/recipient_list.py:443-452

### G99 — Variable pop-up: Enter can replace all the text between the '{' and the cursor, or insert nothing

- **What happens:** The list that pops up after typing '{' has two faults, in the Subject box and in
  the body. (1) If the list is left open and the cursor is moved elsewhere, the next Enter is taken
  as 'choose': everything between the '{' and the cursor is replaced by the highlighted column - a
  four-line email became 'Dear {Name} ' - and Ctrl+Z brings the text back only if the loss is
  noticed. (2) Once a letter has been typed to narrow the list, no row is highlighted, so Enter
  inserts nothing: the list closes, the key press is swallowed and the unfinished '{Na' stays in the
  text. If that is left behind it goes out as typed, with a green tick under the editor and no
  warning.
- **When:** (1) Type '{' (the list opens), do not choose, click elsewhere in the same box or press
  Ctrl+End, Home or the arrow keys, then press Enter - for example to start a new line; in the
  Subject box, Home then Enter gave 'Reminder for {Name} Reminder for {'. (2) Type '{' and one or
  more letters such as 'Na' or 'Mo', then press Enter; it works only straight after '{', after
  pressing the Down arrow first, or with a mouse click. Fault 1 needs an unusual sequence of steps;
  fault 2 happens every time the list is narrowed by typing and is easy to notice. Both were shown
  in tests with simulated key presses and clicks, not yet by hand on a real screen.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** reproduced by several readers. Two readers reproduced the text-replacing
  fault and one the nothing-inserted fault, and a checker (both faults) and a checker (the second)
  reproduced them as extra findings with the real Compose tab; Codex did not report it and there was
  no dedicated re-check, so severity and likelihood are those a checker gave the text-replacing
  fault (the other is LOW but common). Everything ran off-screen (the readers had to imitate
  keyboard focus), so behaviour on a real screen is not confirmed, and one reader's further claims -
  a slow mouse click inserting nothing, fast typing giving '{NaName} ' - were only imitated; the
  wrong narrowing after an emoji in the body is written up under G79.
- **The repair:** Close the list and forget the '{' as soon as the cursor is moved away from the
  letters typed after it, and before inserting check that the cursor is still directly after those
  letters. Keep the first row highlighted after every narrowing, so that Enter always takes it.
- **Where in the code:** ui/components/variable_completer.py:384-402, 242-258, 174-176, 296-298,
  106-112, 91-104, 133-138, 184-194, 306-332

### G100 — One stray cell far outside the list freezes the window or slows the load, and adds invented columns

- **What happens:** The app reads a sheet as far as the last cell the workbook records as in use,
  and gives every empty heading up to there an invented name ('Column_5', 'Column_6' ...). One stray
  cell far to the right - even one holding a single space - therefore creates thousands of invented
  columns, fills every drop-down with them and leaves the window not responding while the Data
  Preview is drawn: about 1.5 seconds with the stray cell in column 1,000, 22 seconds in column
  4,000, 148 seconds in column 8,000, and not finished after 170 seconds in the last column. An
  empty but formatted cell far below and to the right stretches the 'Loading...' wait instead (0.03
  seconds for a clean 300-client list, 2.3 seconds with the cell in column Z of the last row, 7.5
  seconds in column 100) and offers 26 or 100 columns, nearly all invented. No message explains it,
  and it happens again every time that workbook is read.
- **When:** A workbook in which a single cell far outside the list holds something or carries
  formatting - for example a space typed after Ctrl+Right, or a bold or bordered cell left in the
  last row. Every read of that workbook is affected: Browse..., a dropped file, Refresh, Apply, and
  Restore at start-up if the workbook is in the saved session. A stray cell far below in column A
  adds under a second, though one that holds a space also adds a blank 'client' row that is ticked.
  The test workbooks were written by a program; a file saved by Excel itself was not tested.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** reproduced by several readers. No reader and not Codex: two checkers
  came across it and timed it with their own scripts - a checker (a cell holding a space far to the
  right; real main window off-screen; rated MEDIUM; the last-column run was stopped at 170 s) and a
  checker (an empty formatted cell far below and right, through the real Browse... button; rated
  LOW); MEDIUM is used for the merged entry because of the unresponsive window, which also goes
  against contract C11. Timings come from off-screen Qt on the development PC with workbooks written
  by openpyxl - a file saved by Excel was not tested, and a checker's 'about 20 minutes for the far
  corner' is an estimate, not a run.
- **The repair:** Stop reading at the last row and column that hold real content, leave out columns
  that have neither a heading nor any value, and say so when columns were left out; fill the Data
  Preview without holding up the window. Plan it together with any repair of known gap G25, which
  comes from trusting the same recorded size of the sheet.
- **Where in the code:** core/excel_handler.py:143 (reads every row up to the sheet's recorded last
  cell), 158-163 (a 'Column_N' heading for every empty heading cell), 166-171 (each blank row is
  checked cell by cell); ui/tab_excel.py:548-609 (the Data Preview is filled and auto-sized on the
  window's own thread, 100 rows by every column), 491-508 (every column is added to five drop-downs)

### G101 — A client code stored in the workbook as 101.0 instead of 101 never matches its files

- **What happens:** If the list stores a whole-number client code with a decimal point (101.0
  instead of 101), the app takes the code as the text '101.0' and looks for exactly that in the file
  names. '101_ITR.pdf' does not contain '101.0', so no client file is attached for any such row, yet
  the emails still go out and are reported as sent. The Data Preview shows 101.0 and the Attachments
  tab shows the red 'N identifier(s) have NO matching files' line, but once a static file is
  attached the Send tab says 'All have attachments'. It only drops files: the decimal text can never
  pick up another client's file.
- **When:** The identifier column holds numbers (client codes), and the workbook was written by a
  program other than Excel that stores whole numbers with a decimal point or in the 1.01E2 style,
  and it is loaded with Browse... without first being opened and saved in Excel. Lists typed and
  saved in Excel are safe (Excel can produce this only when a formula result is a hair off a whole
  number); lists written by the usual Python tools (openpyxl, pandas, xlsxwriter) were checked and
  are not affected. Opening the list in Excel and saving it cures it.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** re-checked: reproduced. One reader found it (only as 'possible'), Codex
  did not; the checker reproduced it through the app's real main window with a fake Outlook and two
  dummy lists that differ only in how the code is stored (101 against 101.0): 3/3 matched with
  '101_ITR.pdf' sent, against 0/3 matched and three emails sent with no client file. The decimal
  list was hand-made by editing the stored number, and which of the office's sources, if any, write
  whole numbers this way is not known (programs built on Apache POI are known to); the audit has
  only a one-line note in 7.7, and G32 covers the email text, not lost files.
- **Already decided:** Change 6: partly - as worded it covers only how a value appears in the email
  text; file matching would still look for 101.0 unless the same clean-up is also used for the
  identifier
- **The repair:** When the identifier is taken from the list, write a number that is whole as its
  plain digits (101, not 101.0), once, where the list is read, so that the emails, the statistics
  and Preview all agree. Note for Change 6: a code column formatted in Excel with two decimals
  displays 101.00, so identifiers should use the whole number, not the displayed text.
- **Where in the code:** core/email_builder.py:270; core/email_builder.py:276;
  ui/main_window.py:371; ui/main_window.py:375; core/excel_handler.py:177;
  core/email_builder.py:426; core/email_builder.py:431

### G102 — Very long folder paths: files deep in subfolders may be left out of the scan without a message

- **What happens:** The app's protection for very long paths (a path is a file's full address:
  drive, folders and file name) is applied only when the chosen folder's own path is longer than 240
  characters. With 'Include subfolders' ticked and a shorter chosen folder, a file whose full path
  is longer than about 260 characters is expected to be left out of the scan without any message on
  a PC where Windows' long-path setting is off, so that client's email would go without it. This
  could not be tried: the test PC has the setting on, and there such files were found. Separately,
  when the chosen folder's own path is longer than 240 characters, every file found carries a
  special Windows long-path marker in front of its path and is handed in that form to Outlook, Copy
  Path and Open File Location; how Outlook treats such a path, or one longer than 260 characters,
  was not tested.
- **When:** 'Include subfolders' is ticked, the chosen folder's own path is shorter than 240
  characters, and a client's file sits so deep (long folder and file names) that its full path is
  longer than about 260 characters, on a PC where Windows' long-path setting is off (the Windows
  default; the office PCs' setting is not known). Without 'Include subfolders' the same file is
  expected to be listed. The marker case needs a chosen folder whose own path is longer than 240
  characters.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** read from the code only. Two readers reported it, both only as
  'possible'; Codex did not, and no checker re-ran it. One reader's experiment on a PC with Windows
  long paths switched on found the 269- and 291-character files and showed prefixed paths for a
  250-character folder, but a PC with the setting off, and Outlook with a prefixed or over-long
  path, were never run, so the silent skip and Outlook's reaction are unconfirmed (the audit, rule
  R28, lists long paths as covered). Both readers rated it LOW; MEDIUM is used here because the
  skip, if it happens, leaves a client's file out with no message - the outcome a checker reproduced
  for unreadable sub-folders (G69).
- **The repair:** First check the Windows long-path setting on one office PC. Then make the scan use
  the long-path form for every file that needs it, hand Outlook an ordinary path, and list at scan
  time every file that could not be read or is too long to attach, instead of leaving it out
  silently.
- **Where in the code:** utils/file_utils.py:286; utils/file_utils.py:82-88;
  utils/file_utils.py:296-305; utils/file_utils.py:308-315; core/outlook_sender.py:344-349

### G103 — Refresh beside 'Send from' during a run switches the remaining emails to the first Outlook account

- **What happens:** While emails are going out, the 'Send from' list is greyed out but the Refresh
  button beside it still works. One click makes the app read Outlook's accounts again and quietly go
  back to the first account in the list, so every email still waiting in that run goes out from that
  mailbox instead of the one chosen. Nothing tells the user: the run still ends 'Complete: N sent, 0
  failed', and the only sign is that the greyed-out list now shows the other account. Outside a run
  the same click also puts 'Send from' back to the first account, where it can at least be seen, and
  a Start, Resume or Retry that follows uses it unless the user changes it back.
- **When:** Outlook has two or more accounts and the one chosen in 'Send from' is not the first in
  the list. The user clicks Start Sending and, while the run is going, clicks Refresh beside 'Send
  from'. The same switch happens when Refresh is clicked between a stop and Resume Previous, for
  example to reconnect after 'Outlook may be unavailable'.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** re-checked: reproduced. Four readers reproduced it and Codex reported it
  in all three jobs; the checker reproduced it on the real main window with a real click on Refresh
  after the 2nd of 5 emails (emails 3-5 left from the first account while the progress file still
  named the chosen one), and two other checkers reproduced it independently. Outlook was simulated:
  that a real Outlook then sends from the other mailbox is not confirmed.
- **Known gap:** extends G7. G7 covers the account not being remembered and a silent fall-back when
  Outlook refuses it; this is a second way for the 'Send from' account to be swapped without notice,
  in the middle of a run.
- **Already decided:** Change 8: partly - contract C24 forbids this result, but the two rules
  written for Change 8 (remember the last account; fail instead of falling back when Outlook refuses
  it) do not mention the Refresh button or the jump back to the first account
- **The repair:** Fix the account for the whole run at the moment it starts, switch Refresh off
  while a run or a test email is in progress, and make Refresh keep the current choice (the same
  address) instead of jumping to the first account.
- **Where in the code:** core/outlook_sender.py:177-179, 197-209, 310-316; ui/tab_send.py:412-433,
  620-629, 209-211

### G104 — The 'Send from' account is found by its place in Outlook's list; if the list changes, another account sends

- **What happens:** The app keeps track of the chosen 'Send from' account by its place in Outlook's
  list of accounts (first, second, and so on) as that list stood when the app last read it, not by
  its address. If Outlook's list has changed since then, every email is sent from whichever account
  now sits in that place, while the 'Send from' drop-down still shows the account that was chosen
  and nothing is said. If that place no longer exists, the known fallback to Outlook's default
  account applies (G7). This was seen only with a stand-in for Outlook.
- **When:** The app is open and connected with an account chosen in 'Send from'. The accounts in
  Outlook then change (an account is removed or added, or Outlook is reopened with a different set
  of accounts) and Refresh beside 'Send from' is not clicked before Start Sending, Resume Previous,
  Retry Failed or Send Test Email First. How easily classic Outlook's list changes in this way while
  the app is open was not checked.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** reproduced by one reader. One reader reproduced it with a fake Outlook
  whose account list changed after the app had read it (the drop-down showed office@example.com
  while the emails left from records@example.com); Codex did not report it, no checker re-ran it,
  and whether real Outlook changes its list while running is not confirmed - I read the code and it
  agrees with the reader. The reader rated it LOW because of that uncertainty; I rate the harm
  MEDIUM, as for known gap G7 and the re-checked Refresh defect G103 (emails leaving from another
  mailbox unnoticed), and show the uncertainty in the likelihood.
- **Known gap:** extends G7. G7 covers the account not being remembered and the silent fallback when
  Outlook refuses the chosen account; here Outlook refuses nothing and a different account sends,
  because the app points at a place in the list instead of an address.
- **Already decided:** Change 8: partly - its promise that every email goes from the chosen account
  or is not sent forbids this, but its two written rules (remember the last account; fail the email
  when Outlook refuses the account) do not make the app find the account by its address at the
  moment of sending, so a changed list could still send from another account
- **The repair:** At the moment each email is sent, find the chosen account in Outlook's current
  list by its address. If it is no longer there, do not send that email and show it as failed, as
  Change 8 already decides for an account that Outlook refuses.
- **Where in the code:** core/outlook_sender.py:168-175 (the position is stored when the list is
  read, line 174), 310-316 (the stored position is used for every email at line 315, with no check
  that the account there still has the chosen address); core/outlook_sender.py:211-228 with
  ui/tab_send.py:527-529, 602-605, 691-693 and 787-789 (the drop-down's address is matched only
  against the stored list)

### G105 — Template names: two different names can share one file; a template named '-- New Template --' cannot be used

- **What happens:** Each template is kept in a file named after it, but only letters, digits,
  spaces, hyphens and underscores are kept and the name is cut at 50 characters, so two different
  names can be one and the same file ('Fee reminder 1.5 lakh' and 'Fee reminder 15 lakh', or two
  long names that differ only at the end). Save As then asks whether to overwrite a template with
  the name just typed, although no template of that name is in the list: Yes replaces the earlier
  template, which simply disappears from the Template list, and No means the new letter cannot be
  saved under that name. Names made only of symbols (***, ???) all share one nameless file, and
  Hindi names lose their vowel signs and can clash the same way. Separately, a template saved under
  the exact name '-- New Template --' shows as a second identical line and cannot be used: Load
  empties the subject and body, Delete does nothing and Save asks for a new name.
- **When:** Compose tab > Save As... with a name that equals an existing template's name once
  punctuation is dropped and the name is cut to 50 characters, then Yes to 'Overwrite?'. Or Save
  As... with the name typed exactly as '-- New Template --'. With the shared server folder there is
  one more route, simulated with two Compose tabs on one folder: a PC whose list still shows the
  replaced name clicks Load and gets the other letter, while the status bar names the old one.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** re-checked: reproduced. One reader found the shared file and Codex found
  the '-- New Template --' name; two checkers reproduced both with the app's real Save As, Load,
  Delete and Save buttons on dummy templates. Severity follows the checker of the shared-file part
  (MEDIUM); the other checker rated the '-- New Template --' part LOW, saw no decision in it and
  found names that differ only in capitals harmless - I kept the question because the Brief keeps
  rule R21 and F8 as-is. The audit (F8, R21) and the Brief already record that names differing only
  in symbols share one file; new are the clash at the 50-character cut, the question naming the
  wrong template, the nameless file, the Hindi case and the unusable name.
- **The repair:** Give every template name its own file and treat a template as already existing
  only when the saved name is the name typed; if a save would still replace a differently named
  template, name that template in the question. Refuse a name with no letters or digits and the name
  '-- New Template --'.
- **Your call:** Two template names that differ only in punctuation, or only after the 50th
  character, count as one template today, so saving the second replaces the first: should the app
  keep both as separate templates, or refuse the second name and ask you to type a different one?
  (Recommended: keep both as separate templates.)
- **Where in the code:** data/template_storage.py:39-52 (lines 50-51: characters dropped, name cut
  at 50), 211-221 (template_exists tests the cleaned file name), 73-74 (only an empty name is
  refused); ui/tab_compose.py:236-245 (the question shows the name just typed), 255 (selects the
  first line with that text), 174-184 (built-in line plus saved names), 195-198, 211-214 and 262-264
  (the built-in first line is recognised by its wording)

### G106 — Two different saved-list names can be one file; Yes to the overwrite question destroys the other list

- **What happens:** A saved recipient list is kept in a file named after the list, but only letters,
  digits, spaces, hyphens and underscores are kept and the name is cut to 50 characters, so two
  different names can be one file ('A&B Traders' and 'AB Traders', or two long names that differ
  only at the end). Saving the second asks "List 'AB Traders' already exists. Overwrite?" - it names
  the new list, not the one about to be lost - and Yes replaces the first list, which vanishes from
  the Saved Lists drop-down. On another PC whose drop-down still shows the old name, picking it and
  clicking Load ticks the other list's clients with no warning. A name made only of symbols is kept
  in a file with no name, which all such names share.
- **When:** Recipients tab > tick clients > Save Selection... > type a name that, once punctuation
  is dropped and the name is cut to 50 characters, equals an existing list's name: 'A&B Traders'
  then 'AB Traders'; 'Q1 (2025-26)' then 'Q1 2025-26'; two names longer than 50 characters that
  begin the same; a second name made only of symbols; two Hindi names that differ only in a vowel
  sign. Then answer Yes to the overwrite question. Wrong clients get ticked only in the two-PC case:
  another PC, started before the overwrite, picks the old name and clicks Load (the saved lists are
  shared between PCs today).
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** re-checked: reproduced. One reader found it (rated LOW) and Codex did
  not; a checker reproduced it through the real Recipients tab with the real Save Selection... and
  Load buttons, including a second tab on the same folder standing in for a second PC, and rated it
  MEDIUM. The checker refuted one detail, left out here: a name of spaces only is not stored from
  the window (the name box trims it and nothing is saved, with no message). The cleaning rule itself
  is recorded as rule R21 and kept in the Brief; the misleading question, the 50-character clash and
  the lost list are not recorded anywhere.
- **The repair:** Give every distinct name its own file and decide 'already exists' by the name
  stored inside the file, so the question can only appear for the list really being replaced, and
  name that list in it. On Load, check that the list found is the one chosen and say so if it is
  not; refuse a name with no letters or digits. Template names are stored the same way and need the
  same repair (G105).
- **Your call:** When a new list name differs from an existing one only in punctuation, or only
  after the 50th character, should the app keep both lists separately, or refuse the new name and
  ask for a different one? (Recommended: keep both as separate lists, the same answer as for
  template names)
- **Where in the code:** data/recipient_lists.py:50-52 (the cleaning and the 50-character cut),
  273-283 (list_exists looks only at the cleaned file name), 119-144 (load never compares the name
  stored in the file); ui/tab_recipients.py:202-211 (the question shows the typed name), 111-128
  (the drop-down is refilled only at start-up and after this PC's own save or delete), 130-139

### G107 — The Table button with plain tab-separated text drops a blank top-left cell; headings shift one column left

- **What happens:** The Table button reads copied cells in two ways. When the copy also carries its
  formatted version (a straight copy from Excel, Google Sheets, Word or a web page), the table comes
  in correctly. When the clipboard holds only plain text with tabs between the columns, the app
  trims the blank cell or cells at the very start, so the heading row comes out one cell short and
  every heading sits one column to the left of its figures - 'FY2025' above the row labels and
  'FY2026' above the FY2025 amounts. The mis-aligned table is visible in the body, and in the test
  it went to the test clients exactly like that.
- **When:** The copied cells are on the clipboard as plain text only - for example cells first
  pasted into Notepad and copied again from there, or a program that copies plain text - and the
  first row starts with one or more blank cells (the usual blank corner of a year-by-year table).
  Then Compose tab > the Table button, or Ctrl+Shift+V. A straight copy from Excel does not trigger
  it.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** re-checked: reproduced. One reader and two Codex jobs found it; a
  checker reproduced it with the app's own window, the real Table button and a faked Outlook
  (heading row '| FY2025 | FY2026 | |', and the same table in the email handed over), and showed
  that blank cells elsewhere and an Excel-style formatted copy come out right. Not captured live:
  what Excel itself puts on the clipboard (judged from Qt's source and a published dump); the
  reader's remark that a blank cell at the end of the last row is dropped made no visible difference
  in the checker's runs.
- **The repair:** Stop trimming the whole copied text: remove only the line break at its very end,
  keep the tabs at the start of the first row, and give every row the same number of cells.
- **Where in the code:** ui/components/rich_text_editor.py:607 (text.strip() removes the tab or tabs
  at the start of the first row; whole function 597-633, one cell per remaining tab at 612-626);
  509-519 (the plain-text route is taken only when the clipboard holds no HTML table)

### G108 — A turn of the mouse wheel over a drop-down or number box changes it without a click (Excel tab and others)

- **What happens:** If the pointer is resting on a drop-down or a number box and the mouse wheel is
  turned, the box moves to its next entry without a click and with no message; the only sign is the
  changed text in the box. On the Excel tab one notch moved 'To Email' from 'Email' to the next
  column, so the emails were then addressed from that column while the green 'All N emails valid'
  line stayed as it was; over 'Worksheet' it swapped the list for another sheet's clients, all
  ticked; over the 'Row' box it changed 1 to 2, and the next Refresh turned the first client into
  the headings. The same happened to 'Send from' on the Send tab (the question before sending does
  not name the account) and to 'Template' on the Compose tab.
- **When:** The pointer is left resting on a drop-down or number box - for example just after
  choosing from it - and the wheel is turned, meaning to scroll the Data Preview. No click is needed
  and the box does not have to be selected first. It was checked by sending a wheel turn to the
  app's own boxes in a hidden window, not with a real mouse on a real screen.
- **How serious, how often:** MEDIUM · it shows up rarely (unusual data, or a click at just the
  wrong second).
- **How it was confirmed:** reproduced by several readers. No reader and not Codex: two checkers
  came across it independently and each reproduced it by sending one wheel turn to the app's own
  controls on the real main window, off-screen - a checker on To Email, Worksheet and the Row box, a
  checker on To Email, Send from and Template (under the 'windowsvista' look the app uses); both
  rated it MEDIUM. Not tried with a real mouse on a real screen, and the CC, BCC, Identifier and
  Column controls were not tried (same kind of control).
- **The repair:** Make every drop-down and number box ignore the mouse wheel unless it has been
  clicked first, so a stray turn of the wheel changes nothing. Apply it across the whole app,
  including 'Send from' and 'Template'.
- **Where in the code:** ui/tab_excel.py:158-162 (Worksheet), 179-192 (Row / Column boxes), 232-293
  (To Email, CC, BCC, Identifier 1, Identifier 2); ui/tab_send.py:205-207 (Send from);
  ui/tab_compose.py:69-74 (Template). No wheel guard exists anywhere in the code: no wheelEvent
  override, focus policy or event filter on any QComboBox or QSpinBox.

### G109 — A save of a template, profile or theme choice that stops part-way destroys the previous version

- **What happens:** When the app saves an email template, a profile file or the theme choice, it
  empties the existing file first and then writes the new contents into it. If the writing stops
  part-way, the old version is already gone: the damaged template disappears from the Template list
  at the next start with no message, a damaged profile gives 'Invalid JSON file' when it is loaded,
  and damaged preferences quietly go back to the defaults (theme, window size, remembered folders) -
  the next thing the app remembers then rewrites the file with only that one entry. For a template
  or profile an error box appears if the app is still running; for the theme nothing is shown. The
  session, the send progress, saved recipient lists and the folder and window-size preferences are
  saved the safe way and kept their old version in the same test.
- **When:** An existing template is saved again (Save, or Save As and Yes to Overwrite), an existing
  profile file is saved over, or a theme is picked in View > Theme, and the writing is cut short:
  the server share or network drops, the disk is full, the power goes or the program is ended. The
  exposure is larger for templates with pasted pictures (files of several MB) on the server share. A
  file that is merely locked by another program does not cause it: that save is refused and the old
  file stays.
- **How serious, how often:** MEDIUM · it shows up only when something else fails (disk, network,
  another program).
- **How it was confirmed:** re-checked: reproduced. Three readers and all three Codex jobs reported
  it; a checker reproduced it for templates, profiles and the theme choice by stopping the write
  just after the app had opened the file ('GST Reminder.json: 373 bytes, NOT valid JSON', gone from
  the list at the next start) and showed that the safely saved files keep their old version under
  the same fault; a second checker reproduced the template case on its own. Severity follows the
  checker (MEDIUM, needs a fault), not Codex's HIGH; the claimed 'sync lock' cause was refuted, the
  two-PC timing was only simulated, and the one cause without an outside fault (damaged text holding
  half an emoji in the body) could not be produced by ordinary typing. The audit records the direct
  write only as rule R41, and Brief contract C8 is not kept for the theme choice in the preferences
  file.
- **The repair:** Save templates, profiles and the theme choice the same safe way as the session
  (write the new file completely, then swap it in), with one single place that writes the
  preferences, and tell the user when a template file cannot be read instead of dropping it from the
  list. Change 9 (data on each PC) would only make the fault rarer; it does not change how these
  files are written.
- **Where in the code:** data/template_storage.py:103-104 (the file is opened for writing, which
  empties it, before the new text is written; error path 110-112; a damaged file is unreadable at
  137-139 and skipped from the list at 190-192); ui/main_window.py:755-756 (Save Profile, same
  pattern); utils/theme_manager.py:57-75 (write at 72-73; its own read of a damaged file at 66-68
  blocks the repair; a failure is only printed at 75); utils/file_utils.py:32-39 and 42-56 (damaged
  preferences read as defaults, the next save starts from nothing); ui/main_window.py:177-186 (theme
  menu tick taken from the file); for contrast the safe writer utils/file_utils.py:16-29

### G110 — A body picture that cannot be embedded does not stop the email: it is sent anyway and counted as sent

- **What happens:** A picture placed in the body has to be turned into an inline picture for every
  email at the moment it is sent. If that step fails, the app only writes a line in its log file and
  sends the email anyway, still carrying the picture in a raw form that mail programs normally do
  not display (what a client's mail program really shows was not tested). The email gets a green
  tick, is counted as sent and is not offered under Retry, although an ordinary attachment that
  cannot be added does stop the email. In most of the failure cases tested, one stray temporary
  picture file per email was left on the PC, and in one case the picture also travelled as an
  ordinary attachment with a random name such as tmpvwvfbsr9.png.
- **When:** The body holds a picture put in with Image > From File or Image > From Clipboard, and
  during sending one of these goes wrong for that picture: Outlook refuses the picture file, Outlook
  refuses to mark it as an inline picture, the Windows temporary folder cannot be written (missing
  or full), or the picture data held in the body is damaged. No unusual click is needed, and it is
  the same for Start Sending, Resume Previous, Retry Failed, a Preview-mode run and Send Test Email
  First.
- **How serious, how often:** MEDIUM · it shows up only when something else fails (disk, network,
  another program).
- **How it was confirmed:** re-checked: reproduced. Four readers and Codex (engine-14, flows-20)
  reported it; a checker reproduced it through the real window with a fake Outlook in four failure
  cases - two real failures of the app's own steps (temporary folder not writable, damaged picture
  data) and two refusals simulated inside the fake Outlook - with 3 of 3 emails sent and counted as
  sent each time and no Retry offered, and a checker reproduced it independently. Not tested: real
  Outlook, how often such a failure happens, and what a client's mail program shows for the
  left-over picture data.
- **The repair:** Treat a picture that cannot be put into the email like an attachment that cannot
  be added: do not send that email, and show it as failed with a plain message so that it appears
  under Retry. Delete the temporary picture file in every case, success or failure.
- **Your call:** If a picture in the email body cannot be put into a client's email, should that
  email be held back and shown as failed so it can be retried, as already happens when an attachment
  cannot be added, or should it still go out without the picture? (Recommended: hold it back and
  show it as failed.)
- **Where in the code:** core/outlook_sender.py:394-432 (the whole per-picture step sits in one try
  block; any error is only logged at 431-432; the body is changed only after every step worked,
  419-423; the temporary file is deleted only on the success path, 425-429);
  core/outlook_sender.py:333-338 and 358-364 (the email is then sent and reported as sent); compare
  core/outlook_sender.py:340-356 (an ordinary attachment that cannot be added stops the email)

## LOW (G111 to G143)

### G111 — After File > New Session, 'Validate Emails' and 'Apply' stay clickable with nothing loaded

- **What happens:** After a list has been loaded and File > New Session is chosen, the Excel tab is
  emptied and Refresh is greyed out, but 'Validate Emails' and 'Apply' can still be clicked. They
  only answer 'Please select an email column first.' and 'No file loaded.', so nothing is sent or
  changed. It is harmless by itself; the 'Row' and 'Column' boxes beside Apply are the ones that
  keep the previous list's numbers, which is a separate defect (G49).
- **When:** A workbook was loaded earlier in the same sitting; then File > New Session > Yes; then a
  click on 'Validate Emails' or 'Apply' on the Excel tab. At a fresh start both buttons are greyed
  out, as they should be.
- **How serious, how often:** LOW · it shows up in ordinary use.
- **How it was confirmed:** reproduced by one reader. A checker came across it and ran it once on
  the real main window ('Refresh enabled = False, Validate Emails enabled = True, Apply enabled =
  True', then the two messages); one reader noted the same in passing, Codex did not, and there was
  no dedicated re-check. I confirmed in the code that the New Session reset switches off only
  Refresh.
- **The repair:** On New Session, grey out 'Validate Emails' and 'Apply' together with Refresh until
  a list is loaded again.
- **Where in the code:** ui/tab_excel.py:793-823 (the New Session reset; only Refresh is switched
  off, line 803); 661-666 ('Please select an email column first.'); 870-874 ('No file loaded.');
  196-199 and 326-329 (both buttons start switched off), 457-460 (switched on after a load)

### G112 — The log holds more client detail than the audit lists (PANs, file names) and does not say who wrote a line

- **What happens:** After one campaign the shared app.log holds every client's email address with
  its result, every client's identifier such as a PAN or client code, the full location of the
  workbook, of the attachments folder and of any file that could not be attached, the sending
  account, and where profiles and match reports were saved. The audit lists only the addresses. Up
  to 20 MB of this is kept, readable by everyone who can open the app folder. Lines from different
  users are mixed with no user or PC name, and nothing records the subject or which files went to
  whom.
- **When:** Ordinary use: loading a list, choosing the attachments folder, opening the Preview or
  Send tab, saving or loading a profile, and sending. No special data or clicks are needed.
- **How serious, how often:** LOW · it shows up in ordinary use.
- **How it was confirmed:** read from the code only. One reader read every log call in the code;
  Codex did not report it and no checker re-checked it. The cited lines were re-read for this entry
  and are as described; no log file was opened.
- **Known gap:** extends G36. G36 and feature F24 say the log holds client addresses; it also holds
  client identifiers, the locations of the workbook, folder and files, and the sending account, with
  no user or PC name on any line.
- **Already decided:** Change 9: partly - the log would leave the shared folder, but it would still
  hold the same client details, be readable by every Windows user of that PC, and still not say who
  wrote a line
- **The repair:** Decide what the log is for and how long it is kept, and add the user's and the
  PC's name to every line. If it is to be the record of what was sent, add the subject and the files
  of each email; otherwise leave out or mask the identifiers and addresses.
- **Your call:** Should the log be the office's record of each run - who was sent what, and by whom
  - or only a fault-finding aid holding as little client detail as possible? (Recommended: make it
  the record of each run - keep the client's address, add the subject, the files sent and the user's
  name - and keep it only on each PC, as Change 9 plans.)
- **Where in the code:** utils/logger.py:50-67 (the file log takes everything from DEBUG up, 66);
  config.py:131 (line format has no user or PC field), 133-134 (5 MB x 4 files);
  core/attachment_matcher.py:139, 63, 79, 463; data/checkpoint.py:120, 137;
  core/outlook_sender.py:224, 242, 348; core/excel_handler.py:94, 207; ui/tab_excel.py:386;
  ui/main_window.py:766, 816; utils/logger.py:114-153 (the helpers that would record files per email
  are never called)

### G113 — A table pasted from Excel with the Table button loses its grid lines and cell padding

- **What happens:** The Table button is meant to give a table copied from Excel a thin grid, some
  space inside each cell and a blue heading row. In the reader's test, with a copy laid out the way
  Excel puts it on the clipboard, only the blue heading row arrived: the table in the body had no
  grid lines and no space inside the cells, so the text of neighbouring columns almost touches. The
  table looks like that in the editor too, so it can be seen before sending. A copy laid out the way
  Google Sheets does it came in with the grid and the padding as intended.
- **When:** Copy cells in Excel, then Compose tab > the Table button (or Ctrl+Shift+V). Expected on
  every copy from Excel, but tried only with a hand-made copy modelled on Excel's clipboard format,
  not with a real copy from Excel.
- **How serious, how often:** LOW · it shows up in ordinary use.
- **How it was confirmed:** reproduced by one reader. One reader ran the app's table code on HTML
  modelled on Excel's clipboard format: the table that reached the body had border 0, cell spacing 2
  and cell padding 0, while the same HTML without the two marker comments, and a Google-Sheets-style
  copy, gave border 1 and padding 6; Codex did not report it and no checker re-ran it. Not
  confirmed: a real copy from Excel (never captured on this PC) and how Outlook draws the table. I
  read the app's code and it matches the reader's account; that Qt keeps only what lies between the
  two markers rests on the reader's run.
- **The repair:** Take out the two hidden markers Excel puts inside a copied table before the table
  is put into the body, so the grid and padding the app adds are kept. Then check once with a real
  copy from Excel on an office PC.
- **Where in the code:** ui/components/rich_text_editor.py:534-577 (what Excel put inside its table,
  including its two marker comments, is wrapped in the new styled table at 562-566; the clean-up
  patterns at 556-559 match only double-quoted attributes); 522 (insertHtml, which in the reader's
  run kept only what lies between the two markers, so the styled wrapper was dropped)

### G114 — The email body goes out marked 10 point although the size box shows 11; choosing 11 does nothing

- **What happens:** The size box above the body shows 11, but text typed without touching it is
  written into the email as 10 point: the app's own look (the light and the dark theme both set 10
  point for everything) overrides the 11 point the editor asks for. Selecting the text and choosing
  11 changes nothing, because 11 is already the value shown; another size has to be picked first and
  then 11. The app's tests do not notice, because they never switch the app's look on.
- **When:** Every email whose body is typed without changing the size box - the ordinary case. Also:
  choosing 11 in the size box while it already shows 11.
- **How serious, how often:** LOW · it shows up in ordinary use.
- **How it was confirmed:** reproduced by one reader. One reader applied resources/style.qss the way
  the app does: the body tag said 'font-size:10pt' while the size box showed 11, choosing 11 added
  nothing, and 12 followed by 11 added 'font-size:11pt'; without the sheet the tag says 11pt. Codex
  did not report it and no checker re-ran it; how Outlook then draws the text was not checked, and
  the dark theme's sheet was read (same rule), not run. The reader saw no business decision in it; I
  flag one because the repair changes either the box or the size of every email.
- **The repair:** Make the size box and the real starting size of the body agree, whichever size is
  chosen, and apply a size when it is picked even if it is the value already shown.
- **Your call:** The size box shows 11 but the body is written into emails as 10 point: should the
  body stay at 10 point with the box corrected to show 10, or should new emails really start at 11
  point? (Recommended: stay at 10 point, so emails keep the look they have today, and make the box
  show 10.)
- **Where in the code:** ui/components/rich_text_editor.py:69 (the editor asks for Segoe UI 11),
  123-129 (the size box starts at 11 and, line 127, reacts only when its value changes), 296-300 (it
  shows 11 whenever the text carries no size of its own), 308-316; resources/style.qss:7-11 and
  resources/style_dark.qss:7-11 (app-wide 'font-size: 10pt', applied through main.py:44-47)

### G115 — An empty body is never seen as empty: '2. Compose' always gets its tick and a blank session is offered

- **What happens:** The app decides whether the email body is empty with a test that can never
  answer 'empty': the editor's blank page still carries one line of hidden formatting text, and the
  test takes that line for writing. So the '2. Compose' tab gets its done-tick as soon as a client
  list is loaded (or anything else refreshes the tab titles) although no subject and no letter
  exist, and it never loses the tick again. And a saved session with nothing in it is offered at the
  next start - 'Restore Previous Session?' with a blank 'File:' line, 'Template: Custom' and
  'Recipients: 0 selected' - after simply opening and closing the app or after File > New Session;
  Yes restores nothing, yet the status bar says 'Session restored'. Nothing wrong is sent because of
  this alone, but the false tick removes the one sign that the letter is still missing, and a
  question at every start teaches staff to answer it without reading.
- **When:** The tick: the letter is not written yet and a list is loaded, a client is ticked or
  unticked, an attachments folder is chosen or File > New Session is used. The question: the app is
  closed with nothing loaded and nothing written (opened and closed untouched, or after New
  Session); every later start asks again until a real session has been saved.
- **How serious, how often:** LOW · it shows up in ordinary use.
- **How it was confirmed:** re-checked: reproduced. Three readers reproduced it (Codex did not
  report it); a dedicated checker reproduced both effects with the app's real window over four
  separate starts, and four other checkers ran into it on their own - one of them also saw the same
  blind spot let Save store a blank template. It contradicts audit rule R40, the audit's Section 6
  line 'Empty session after New Session - not offered for restore' and F25's 'Compose has text'; the
  existing test passes only because its 'empty' body is hand-written and lacks the hidden formatting
  line.
- **The repair:** Judge 'is the body empty?' by what a reader would see - no visible text and no
  picture - in both places and when a template is saved, and correct the two tests so they use a
  really empty editor and check that Compose has no tick while empty.
- **Where in the code:** data/session_manager.py:119-123 (has_meaningful_content strips the tags and
  counts what is left); ui/main_window.py:224-229 (same test for the tab tick), 565-570 (the restore
  check that relies on it); ui/components/rich_text_editor.py:441-448 (the body is the editor's full
  HTML, whose style block 'p, li { white-space: pre-wrap; }' survives the stripping; the correct
  test at 472-479 is not used); data/template_storage.py:76-77 (same blind spot when a template is
  saved); tests/test_new_session_reset.py:93-104 and tests/test_polish.py:247-256 (hand-written
  empty body; the Compose tick is never looked at)

### G116 — A cancelled or stopped run is logged as 'Completed'; the 'Resuming' and 'Retrying' lines vanish at once

- **What happens:** After Cancel at 3 of 10 emails, the Progress list first shows 'Completed: Email
  sending (3 successful)' in green and the summary 'Done: 3/3' - counting the emails attempted, not
  the emails planned - and only then 'Operation cancelled by user'; after the app's own stop with 2
  sent and 3 failed out of 8, the summary reads 'Done: 2/5'. When Resume Previous or 'Retry N
  Failed' is clicked, the app writes 'Resuming with N remaining' or 'Retrying N failed
  recipient(s)…' and clears the Progress list in its very next step, so that line is never seen. The
  earlier lines (who was sent, who failed and why) disappear at the same moment.
- **When:** Ordinary use: every run that is cancelled or stops itself shows the 'Completed' line and
  the short 'Done' count, and every click on Resume Previous or 'Retry N Failed' wipes the Progress
  list.
- **How serious, how often:** LOW · it shows up in ordinary use.
- **How it was confirmed:** reproduced by several readers. One reader reproduced both parts and
  Codex did not report it; there was no dedicated re-check, but one checker reproduced the wiped
  lines as an extra finding and two checkers' saved outputs show 'Completed: Email sending' logged
  after a Cancel. I read the code and it agrees: the 'Completed' line is written for every outcome
  (ui/tab_send.py:743) and the list is cleared after the Resume or Retry line is written (:631).
- **Already decided:** Change 1: partly - its question before Resume and Retry would show the number
  of emails that the wiped line was meant to give; the 'Completed' wording and the short 'Done'
  count after a cancelled or stopped run, and the loss of the earlier lines, would remain
- **The repair:** Give the summary the planned total and the real outcome (completed, cancelled or
  stopped), write the Resume or Retry line after the list is cleared, and consider keeping the
  earlier lines when a run is resumed.
- **Where in the code:** ui/components/progress_log.py:266-279; ui/tab_send.py:743, 631, 695-696,
  797-800

### G117 — Both themes: drop-downs show no arrow, the font-size box shows one digit, the open tab's title is cut off

- **What happens:** In both themes the drop-downs (Worksheet, To Email, CC, BCC, Identifier,
  Template, Saved Lists, Send from) are drawn without their arrow, so nothing shows that they open a
  list. In the body editor's toolbar the font-size box has room for one digit only: 10, 11, 12, 14,
  16 and 18 all read '1'. The title of the tab that is open is in bold and wider than its tab, so
  its first digit and its done-tick are clipped. This was measured in off-screen pictures; how a
  real Windows screen draws it is not confirmed.
- **When:** Always, in the light and in the dark theme; no special data or clicks are needed.
- **How serious, how often:** LOW · it shows up in ordinary use.
- **How it was confirmed:** reproduced by one reader. One reader, from off-screen pictures of every
  tab in both themes: the arrow area held one single colour, the size box left 10 px for text that
  needs 16 px, and the tab text measured 85 px normal against 91 px bold. Codex did not report it,
  no checker re-checked it, and the reader rated it 'likely' because it was not confirmed on a real
  Windows screen.
- **The repair:** Draw an arrow on the drop-downs, make the font-size box wide enough for two
  digits, and size each tab for its bold title (or mark the open tab by colour instead of bold).
- **Where in the code:** resources/style.qss:138-164 (156-159 drop-down and 161-164 down-arrow with
  no picture; padding at 139-145), 34-38 (bold title for the open tab);
  resources/style_dark.qss:149-175, 36-41; ui/components/rich_text_editor.py:123-128 (size box fixed
  at 60 px)

### G118 — Attachments tab statistics and match report keep the previous list's identifiers when none is mapped

- **What happens:** When the column mapping no longer has an identifier column, the Attachments tab
  is not told. It keeps showing the earlier list's line (for example '50/50 identifiers matched
  (100%)'), the red 'N identifier(s) have NO matching files' warning with its View List, and
  Generate Report writes a report for the earlier list's clients. In fact no client file is attached
  to any email any more; the Send tab does say 'N without attachments', unless a static file hides
  it.
- **When:** A list with an identifier column (say PAN) is loaded and its folder read, so the
  statistics line is showing. Then Identifier 1 and Identifier 2 are set to '-- None --' by hand, or
  a list or worksheet with no code-like heading is loaded, or a worksheet switch leaves both on '--
  None --'.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by several readers. Three readers and two checkers (as side
  findings, through the real window) reproduced the stale statistics line; that Generate Report
  writes the earlier list's identifiers rests on the stored identifiers seen unchanged plus code
  reading (ui/tab_attachments.py:392-410), not on a report actually written. No dedicated re-check
  and Codex did not report it; severity follows the two checkers and one reader (LOW) - two readers
  rated it MEDIUM because the stale '100% matched' line gives false comfort when a static file also
  hides the Send tab's warning (G41).
- **The repair:** Always tell the Attachments tab the current identifiers - an empty list when no
  identifier column is mapped - and have it clear the statistics line, the red warning, View List
  and the Generate Report button in that case.
- **Where in the code:** ui/main_window.py:362-378 (366: identifiers are passed on only when an
  identifier column is mapped; nothing clears them otherwise); ui/tab_attachments.py:482-492,
  325-354, 356-373, 392-410

### G119 — New Session leaves the old 'NO matching files' warning and both attachment switches as they were

- **What happens:** After File > New Session ('This will clear all current data'), the Attachments
  tab still shows the previous campaign's red line 'N identifier(s) have NO matching files', and its
  View List button still lists the previous campaign's client codes. The Test Matching box keeps its
  old title 'Matched Files for: <last code tested>' and Generate Report stays clickable. The two
  switches 'Enable Static Attachments' and 'Enable Dynamic Attachments' also stay as they were, so
  if one was unticked in the last campaign the new campaign starts with it off and its buttons
  greyed (Browse..., or Add Files...). No wrong email was seen because of this: it is misleading
  leftover display, and the greyed buttons show that a switch is off.
- **When:** The previous campaign had identifiers with no files (so the red line was showing), or a
  Test had been run, or one of the two switches had been unticked; then File > New Session > Yes.
  The red line stays until a folder is scanned for the new campaign, and for good if the new list
  has no identifier column chosen. Restoring a session and Load Profile set the two switches
  themselves, so only New Session leaves them.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by several readers. Two readers reproduced it separately with
  the real main window off-screen (one the leftover warning, list, title and the dynamic switch; the
  other both switches, which were also copied into the new campaign's email builder), and a checker
  came across the display leftovers and reproduced them with the real File > New Session menu action
  and View List button. Codex did not report it, and there was no dedicated re-check.
- **The repair:** Have New Session also hide the red warning line, empty its list, put the Test
  Matching title back, grey Generate Report and tick both switches again.
- **Where in the code:** ui/tab_attachments.py:514-529; ui/tab_attachments.py:77-89;
  ui/tab_attachments.py:340-354; ui/tab_attachments.py:356-373; ui/tab_attachments.py:309;
  ui/components/file_list.py:321-326; ui/main_window.py:617-639; ui/main_window.py:406-419

### G120 — A line break inside an Excel cell (Alt+Enter) is not kept in the email; Preview glues the lines together

- **What happens:** When a cell holds several lines typed with Alt+Enter - for example an address
  'Flat 4', 'MG Road', 'Pune 411001' - the app puts the value into the body as it is, without
  turning its line breaks into line breaks an email shows. On the Preview tab the lines appear glued
  together with no space between them ('Address: Flat 4MG RoadPune 411001'). The email handed to
  Outlook still carries the raw line breaks; a break of that kind normally shows as a single space,
  so the client most probably reads one line and not three - how Outlook and Gmail really show it
  was not checked.
- **When:** The body uses a {Column} whose cell has more than one line in Excel (typed with
  Alt+Enter): addresses, remarks, lists of documents. It applies to every client with such a cell,
  on every send, and the Preview tab does not show it the way a mail program will.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by one reader. One reader built an email from a dummy row
  with a three-line value: the body handed over still held the three parts with raw line breaks
  between them, and the Preview box showed 'Flat 4MG RoadPune 411001'; Codex did not report it and
  no checker re-ran it. Not confirmed: what Outlook and Gmail show (Outlook was never started), and
  the reader's further worry that runs of spaces typed in the body shrink in mail programs, which
  nobody tested. It sits at the same step as known gap G33, which covers only & < > in a value.
- **The repair:** When a value is put into the body, turn each line break inside it into a line
  break the email shows, in the same step that makes & < > safe (G33). Then check once on an office
  PC how Outlook and Gmail show the result.
- **Where in the code:** core/template_engine.py:80-85 (the value is inserted as str(value), line
  85, with no conversion of line breaks); core/email_builder.py:249-251 (the body is built from it);
  ui/tab_preview.py:375 (the Preview draws the same HTML with Qt, which in the reader's run dropped
  the line breaks)

### G121 — The Worksheet list offers chart sheets and hidden sheets; a chart sheet left in view stops the list loading

- **What happens:** The Worksheet list on the Excel tab offers every sheet in the workbook,
  including chart sheets (a chart on a tab of its own) and sheets that are hidden in Excel. A chart
  sheet has no rows: if the workbook was last saved with a chart sheet in view, Browse... fails with
  "Error loading file: 'Chartsheet' object has no attribute 'iter_rows'" and the list cannot be
  loaded until the workbook is saved again with a data sheet in view; picking a chart sheet in the
  Worksheet list gives the same message while the earlier rows stay on screen (known gap G29).
  Refresh never updates the Worksheet list, so a sheet added in Excel after loading cannot be
  picked, and if the sheet in use was renamed Refresh fails with "Sheet 'X' not found".
- **When:** (a) A workbook whose chart sheet was the tab in view when it was last saved is chosen
  with Browse... or dropped on the tab; (b) a workbook that has a chart sheet or a hidden sheet is
  loaded and that sheet is picked in the Worksheet list; (c) a sheet is added or renamed in Excel
  while the workbook is loaded in the app, and Refresh is clicked. Chart sheets are unusual in a
  client list; hidden sheets and renamed sheets are ordinary.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by one reader. One reader ran the chart-sheet and
  hidden-sheet parts on a dummy workbook written for the test, not saved by Excel itself; Codex did
  not report it and no checker re-ran it. The Refresh part is from reading the code, which I re-read
  and agree with (openpyxl keeps chart sheets and hidden sheets in its sheet list even in read-only
  mode, and takes the sheet in view from the workbook's saved active tab); the reader left the
  hidden-sheet rule open, so it is put as a question.
- **Already decided:** Change 12: partly - a newly chosen workbook would open on its first sheet
  instead of the sheet in view, so a chart sheet left in view would no longer stop the load (unless
  the first sheet is itself a chart sheet); chart sheets and hidden sheets would still be offered, a
  hidden first sheet would be opened by itself, and Refresh would still not update the Worksheet
  list
- **The repair:** Offer only sheets that hold rows - no chart sheets, and hidden sheets according to
  the office's answer - open the first such sheet when the sheet in view is a chart sheet, bring the
  Worksheet list up to date on Refresh, and replace the two messages with plain-English ones.
- **Your call:** Should sheets that are hidden in Excel be left out of the Worksheet list, so that a
  hidden sheet is never read unless it is first shown again in Excel? (Recommended: yes - leave
  hidden sheets out, together with chart sheets, which hold no rows.)
- **Where in the code:** core/excel_handler.py:108-114 and 218-224 (the sheet taken can be a chart
  sheet), 143 (its rows cannot be read, which gives the message), 393-402 (every sheet name is
  offered, chart and hidden sheets included); ui/tab_excel.py:449-455 (the only place the Worksheet
  list is filled), 465-471 (picking a sheet), 699-705 (Refresh re-reads the rows but not the list)

### G122 — Saved list: a ticked client with a blank address is never ticked again; the warning shows an empty line

- **What happens:** A saved list recognises each ticked client by email address. A client whose To
  cell was empty when the list was saved is stored as a blank, and a blank is never matched: on Load
  that client is not ticked although the row is still in the workbook, even after the address has
  been filled in. The 'Partial Load' warning says '1 saved recipient(s) are not in the current Excel
  data and were skipped:' followed by an empty line, so nothing says which client it was. If every
  saved address was blank, the list ticks nobody.
- **When:** Recipients tab > Save Selection... while at least one ticked row has an empty cell in
  the To column (for example an address not known yet); later pick that list under 'Saved Lists' and
  click Load.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by one reader. One reader found it and ran it in its own
  experiment ('indices: [1] | missing: ['']'); Codex did not report it and no checker re-ran it. I
  read the cited lines and they behave as described; the case where the address is filled in later
  follows from the code and was not run.
- **The repair:** Do not use a blank address to recognise a client: at Save Selection..., say how
  many ticked rows have no address and so cannot be remembered, or remember such rows by another
  column such as the identifier, and make the warning say which client was skipped. Change 2 will
  also find clients again by email address after Refresh, so it needs the same care for rows with no
  address.
- **Where in the code:** data/recipient_lists.py:173-177 (rows with a blank address are never
  recorded for matching), 181-187 (a saved blank is always reported as missing), 105-106;
  ui/tab_recipients.py:215-220 (blank addresses are saved as empty text), 157-166 (the warning
  prints an empty bullet)

### G123 — 'Open File Location' on a static file probably opens Explorer's default folder, not the file's folder

- **What happens:** On the Attachments tab, right-clicking a file in the Static Files list and
  choosing 'Open File Location' is expected to open Windows Explorer at its default folder (such as
  Documents) instead of at the file's own folder. The same right-click entry works for files in the
  Matched Files list. Nothing is sent wrongly because of it. It rests on how Windows Explorer is
  known to behave when a file's address is written with forward slashes; Explorer itself was not
  started during the hunt.
- **When:** A static file was added with 'Add Files...' or by dragging it in from Explorer (both
  give the app the file's address written with forward slashes), then right-click it and choose Open
  File Location.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** read from the code only. Two readers reported it; neither Codex nor a
  checker did. One reader's experiment confirmed that static files carry forward slashes
  (C:/Users/...) while scanned files carry back-slashes, but Explorer was never started, so the
  wrong-folder result rests on Explorer's known handling of its /select switch. That reader's side
  remark that the same file can be listed and attached twice was shown only by feeding a back-slash
  path in directly; from reading the code, Add Files... and drag-in both give forward slashes, so no
  route through the window was shown and it is left out here.
- **The repair:** Before calling Explorer, rewrite the file's address in the Windows form
  (back-slashes). The same tidy form could be used where the static list checks whether a file is
  already in it, as a precaution.
- **Where in the code:** ui/components/file_list.py:200-208; ui/components/file_list.py:144-155;
  ui/components/dialogs.py:176-181; ui/components/file_list.py:269; ui/components/file_list.py:247

### G124 — Refresh (when already connected) and the 'Online' check can freeze the window while Outlook answers

- **What happens:** The first connection to Outlook is made in the background, but two later
  contacts with Outlook are not: the Refresh button beside 'Send from' when the app is already
  connected, and the 'Online' check made once, straight after each successful connection. While
  Outlook takes time to answer, the whole window stops responding and shows nothing to explain why.
  Nobody could run this with real Outlook, so whether and for how long the window freezes was not
  observed.
- **When:** The app has connected to Outlook; Outlook is then closed (or is busy, or is waiting
  behind a box of its own such as a profile or password prompt) and the user clicks Refresh beside
  'Send from'. The app then asks Windows for Outlook again, which has to start or answer first, and
  the window waits for it.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** read from the code only. Two readers found it by reading the code; Codex
  did not report it and no checker re-ran it, and because Outlook could not be started the freeze
  and its length were never observed. The project's own test file
  (tests/test_tab_send_startup.py:4-6) says the same connection used to freeze start-up for seconds,
  longer if Outlook was not running, and Brief contract C11 says the Outlook connection never
  freezes the window.
- **The repair:** Make Refresh and the 'Online' check contact Outlook in the background, the same
  way the first connection does, so the window keeps responding and shows that it is waiting for
  Outlook.
- **Where in the code:** ui/tab_send.py:412-419 (line 418: Refresh re-reads the accounts on the GUI
  thread), 385-391 (line 390) with 435-444 (the online check on the GUI thread);
  core/outlook_sender.py:143-157, 159-182, 197-209 and 255-278 (each makes a fresh COM connection,
  which starts Outlook if it is not running); only the first connection uses OutlookInitWorker
  (ui/tab_send.py:100-128, 370-383)

### G125 — Dragging a picture file onto the body types the file's address into the email instead of the picture

- **What happens:** When a picture file such as logo.png or a scanned notice is dragged from a
  folder onto the body, no picture appears: the text 'file:///C:/Users/<name>/.../logo.png' is typed
  into the body at the place where it was dropped. If it is not noticed and deleted, every client
  receives that line of text, which shows a folder on the sender's PC. The app does have its own
  routine for dropped pictures, but it never gets to run; Image > From File... and Image > From
  Clipboard work.
- **When:** Compose tab: drag a .png, .jpg, .jpeg, .gif or .bmp file from a folder window and drop
  it on the body, as the changelog promises ('Drag & Drop (like Gmail!)'). Expected every time, with
  no special data or saved state; it was shown with simulated drops, and a real drag with the mouse
  has not been tried yet. A picture dragged from a web browser also misses the app's picture routine
  and stays a web link (see G94).
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by several readers. Two readers and a checker (an extra
  finding, real window off-screen) each reproduced it by sending Qt's own drag-and-drop events to
  the editor's inner viewport (_insert_image ran 0 times; body text 'Dear
  {Name},file:///.../dummy_logo_red.png'), while the same drop sent to the QTextEdit object itself
  embedded the picture; Codex did not report it and there was no dedicated re-check. Nobody did a
  real mouse drag from a folder window on a visible screen, so that last step is not confirmed; the
  audit's F6 lists drag-and-drop of pictures as working.
- **The repair:** Let the app's own picture routine receive what is dropped on the body, so that a
  dropped picture file is put in as a real inline picture exactly as Image > From File... does; the
  same repair can make Ctrl+V of a copied picture work.
- **Where in the code:** ui/components/rich_text_editor.py:77-78, 235-274, 70-71; CHANGELOG.md:138

### G126 — The bullet and number buttons cannot switch a list off

- **What happens:** Clicking the bullet button (•) or the number button (1.) always starts a list;
  clicking it a second time does not end the list, as it does in Word or Outlook. After the last
  item the user presses Enter and clicks the button again to stop: the line is still a bullet, so
  'Regards' typed next becomes a bullet, or an empty bullet is left at the end of the email.
  Pressing Backspace on the empty bullet is the only way back to ordinary text.
- **When:** A body with a bullet or numbered list: after the last item, Enter and then a click on
  the same list button to go back to ordinary text.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by one reader. One reader ran the editor: the cursor was in a
  list after the first click and still in one after the second, and a list ended with Enter produced
  HTML ending in an empty list item; Codex did not report it and no checker re-ran it. I read the
  code and it matches; how Outlook shows the empty last bullet was not checked.
- **The repair:** When the cursor is already in a list of that kind, a click on the button takes the
  line out of the list instead of starting another.
- **Where in the code:** ui/components/rich_text_editor.py:365-385 (both buttons always call
  createList; nothing checks whether the cursor is already in a list, although the comments say
  'Insert or toggle'); the buttons are set up at 180-190

### G127 — Load on the Compose tab wipes the subject and body without asking while '-- New Template --' is shown

- **What happens:** While the Template list shows its first line, '-- New Template --' (what it
  shows after every start, also when a session restore has brought a letter back), a click on Load
  empties the subject and the body at once, with no question and no message. Ctrl+Z brings back the
  subject but not the body. A letter typed by hand and not saved as a template is gone; the '2.
  Compose' tick stays on, and nothing later stops the now-empty email (see G115 and G80).
- **When:** A letter is on screen that did not come from the Template list - typed by hand,
  imported, or brought back by session restore - and the user clicks Load (a slip, or expecting it
  to load something) while the list still shows '-- New Template --'.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by one reader. Found and reproduced by one checker as a side
  finding (real window off-screen: subject and body empty after Load, no message box, undo available
  for the subject only); no reader and no Codex job reported it and nobody re-checked it, so it is
  labelled as a single reproduction. I read the code and it matches. The audit's feature note F8
  already says that Load on '-- New Template --' clears the subject and body without asking, but it
  is not among the gaps G1-G43.
- **The repair:** Ask before emptying a subject or body that has something in it, and keep the
  emptied body recoverable with Ctrl+Z.
- **Where in the code:** ui/tab_compose.py:193-198 (Load on the first line calls _clear_content and
  returns), 288-291 (_clear_content); ui/components/rich_text_editor.py:468-470 (clearing the editor
  also drops its undo history)

### G128 — Send tab: the 'N without attachments' warning is shown in green once 'All have attachments' has been shown

- **What happens:** In the Pre-Send Summary on the Send tab, the note 'N without attachments' is
  meant to be amber. Once the tab has shown 'All have attachments' in green during the same sitting,
  a later 'N without attachments' note is painted in that same green. The separate red line 'N
  recipient(s) have no attachments' with its View List button still appears, so the warning is
  weakened, not lost.
- **When:** Open the Send tab when every email has an attachment ('All have attachments' appears in
  green), then open it again in the same sitting when some emails have none: another folder,
  attachments switched off, another list or different ticks.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by several readers. Two readers and a checker (as a side
  finding, x3_summary_colour.py) each reproduced it with the real Send tab off-screen: the label's
  colour stayed #28a745 (green) while its text read '3 without attachments'. Codex did not report it
  and there was no dedicated re-check.
- **The repair:** Set the colour every time the note is written: amber for 'N without attachments',
  green for 'All have attachments'.
- **Where in the code:** ui/tab_send.py:491-498 (the green colour is set at line 497; the warning
  branch at 491-494 sets only the text), 269-270 (the amber colour is set once, when the label is
  created)

### G129 — After a Resume, 'Complete with Errors' names a different number from the 'Retry N Failed' button

- **What happens:** At the end of a run, the 'Complete with Errors' pop-up counts only the failures
  of the part that has just run, while the Retry button counts every failed client of the whole run.
  In the test the pop-up said 'Sent: 1, Failed: 1 - Use 'Retry 1 Failed' to send again to just those
  recipients' while the button read 'Retry 4 Failed', because it also covered three earlier
  failures. Nothing wrong is sent because of this, but the two numbers do not agree at a moment when
  the user is already unsure who has been emailed.
- **When:** A run stops after three failures in a row (or is cancelled after a failure), the user
  clicks Resume Previous, and at least one more email fails in the resumed part, which then runs to
  its end.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by one reader. Found and reproduced by one checker as a side
  finding, with the real window and a fake Outlook (hi_variants.py, Variant 4: pop-up 'Sent: 1 |
  Failed: 1 | Use 'Retry 1 Failed'', button 'Retry 4 Failed', progress record failed=[0,1,2,4]). No
  reader or Codex reported it and nobody re-checked it; I read the code and it agrees.
- **The repair:** Word the end-of-run message from the same count as the button: say how many emails
  failed in the part just run and how many failed clients in all the Retry button will send to.
- **Where in the code:** ui/tab_send.py:759-765 (the message uses this part's failure count, read at
  line 724), 767-773 (the button counts every failed row held in the progress record that is in the
  current list); data/checkpoint.py:313-314 (Resume brings the earlier failures back into that
  record) and 134 (new failures are added to it)

### G130 — A password-protected or damaged workbook only gets the message 'File is not a zip file'

- **What happens:** When the chosen workbook needs a password to open, or is damaged or only half
  copied, the app cannot read it and shows 'Error loading file: File is not a zip file'. The message
  says neither what is wrong nor what to do, so staff cannot tell a protected list from a broken
  one. The plain message the app has ready for an unreadable workbook, 'Invalid Excel file format',
  can never appear because of the way the app opens the file. The new list simply does not load.
- **When:** Browse..., a file dropped on the tab, Refresh, 'Restore Previous Session' or Load
  Profile, on a .xlsx or .xlsm file that is protected with a password to open, is damaged, or has
  not finished copying or syncing.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by several readers. One reader got the message with a file
  imitating a password-protected workbook, and a checker saw the same message for a damaged file
  while checking another finding (route 2); Codex did not report it and there was no dedicated
  re-check. A workbook really protected with a password in Excel was not tried; I confirmed in the
  library's code (openpyxl/reader/excel.py:75-95) that the 'Invalid Excel file format' case cannot
  arise when the file is opened from memory, although the audit's Section 6 lists that message as
  the handled case.
- **The repair:** Recognise a workbook that cannot be opened because it needs a password, is damaged
  or is only half copied, and say so in plain words with what to do next (remove the password in
  Excel, or wait until the file has finished copying and try again).
- **Where in the code:** core/excel_handler.py:53-59 (the workbook is opened from a copy held in
  memory), 124-125 and 233-234 (the plain message 'Invalid Excel file format', never reached),
  128-130 and 237-239 (the general message that is shown instead); ui/tab_excel.py:417-420

### G131 — 'Export Blank Template' is not blank: it holds two sample clients that load and are ticked like real ones

- **What happens:** The file saved by 'Export Blank Template' is not blank: its Recipients sheet
  already holds two made-up clients, John Doe (john@example.com, PAN001) and Jane Smith
  (jane@example.com with a CC to manager@example.com, PAN002). Nothing marks them as examples, so if
  they are left in, the app loads them as clients, ticks them like everyone else and includes them
  in the send, with any attachment that goes to everybody. The addresses are on a reserved test
  domain, so those emails should bounce rather than reach anyone, but that was not tried with
  Outlook.
- **When:** Staff click 'Export Blank Template' on the Excel tab, type their own clients under the
  two example rows, forget to delete the examples, and load that file.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by one reader. One reader exported the template with the
  app's own code and loaded it unchanged: 2 rows, '2 of 2 recipients selected', Identifier 1 chosen
  by the app; Codex did not report it and no checker re-ran it. The sample rows are plain in the
  code and the audit's F4 mentions them as a fact, not as a gap; what Outlook does with the
  example.com addresses was not tried.
- **The repair:** Export the Recipients sheet with the headings only and show the two examples on
  the Instructions sheet instead.
- **Where in the code:** ui/tab_excel.py:923-932 (the two sample rows written into the Recipients
  sheet), 204-205 (the button's caption), 893-978 (the whole export)

### G132 — The box is labelled 'Data starts at: Row' but the number is used as the row of the headings

- **What happens:** On the Excel tab the two boxes are captioned 'Data starts at: Row / Column', but
  the Row number is used as the row that holds the headings; the clients are read from the row below
  it. A user who follows the caption and enters the row of the first client, then presses Apply,
  turns that client's details into the column headings and drops that client from the list, while
  the status bar confirms 'Reloaded starting from row N, column 1'. Only the hint that appears when
  the pointer rests on the box says 'Row number where headers are'.
- **When:** Someone sets the Row box by its caption rather than by the hint - most likely for a list
  whose headings are below row 1, which the office has: for headings in row 3 and the first client
  in row 4 they type 4 and press Apply. Even the starting value 1 does not fit the caption, since
  the clients then start in row 2.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** read from the code only. One reader, from reading the code only; Codex
  did not report it and no checker examined the caption. I re-read the lines and agree, and the
  checker's runs for G49 show the effect of a number that is too high: with the Row box at 2 or 3 on
  a list whose headings are in row 1, a client's details became the headings and the clients above
  were dropped.
- **The repair:** Reword the caption so it says what the number means, for example 'Headings are in
  row', and word the status line to match. Change 11, which already reworks these boxes, is the
  natural moment.
- **Where in the code:** ui/tab_excel.py:175-183 (caption 'Data starts at:' and 'Row:', hint 'Row
  number where headers are'), 881-883 (status line 'Reloaded starting from row N');
  core/excel_handler.py:150-166 (the number is taken as the heading row and the clients are read
  from the row after it)

### G133 — Left and Right arrow keys do nothing in tables and on the OR/AND buttons: the window keeps them for Preview

- **What happens:** The window claims the Left and Right arrow keys on every tab, so that they can
  step through recipients on the Preview tab. On any other tab the key press is simply swallowed: in
  the Data Preview table on the Excel tab and in the Recipients table the Right arrow does not move
  to the next column, and with the keyboard on 'OR (either)' it does not move to 'AND (both)'. Up
  and Down still work, and the arrows still move the cursor inside text boxes.
- **When:** On any tab except 5. Preview: click a cell of a table (or move the keyboard onto the
  OR/AND buttons) and press the Left or Right arrow.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by one reader. One reader reproduced it off-screen with
  simulated key presses (the column did not change in the app's tables, the OR/AND buttons did not
  switch, a plain table without these shortcuts did move, the Subject box still moved its cursor);
  Codex did not report it and no checker re-checked it. Not tried on a real screen, and other
  controls were not tried.
- **The repair:** Let the Left and Right arrows change the previewed recipient only while the
  Preview tab is open, and leave them to tables and buttons everywhere else.
- **Where in the code:** ui/main_window.py:260-265 (window-wide QShortcut for Qt.Key_Left and
  Qt.Key_Right), 279-287 (_preview_prev / _preview_next do nothing unless tab 5 is open)

### G134 — Dark theme: the Subject line on the Preview tab and the list that opens after typing '{' cannot be read

- **What happens:** In the dark theme the Subject line on the Preview tab is drawn in light grey on
  a near-white box (measured contrast about 1.2 to 1), so the subject each client will get cannot be
  read there. The list of column names that pops up after typing '{' in the subject or the body is
  light grey on white: only the highlighted row can be read. The light theme shows both correctly.
- **When:** Windows is in dark mode and the app's theme is 'System (Auto)' (the default), or View >
  Theme > Dark is chosen. Then open 5. Preview, or type '{' on the Compose tab.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by several readers. Two readers reproduced the pop-up
  independently (one measured the painted colours in an off-screen picture, one the colours the list
  resolves to), and one reader measured the Preview Subject line (#E0E0E0 on #F5F5F5, 1.21 to 1).
  Codex did not report it, no checker re-checked it, and it was not looked at on a real Windows
  screen.
- **The repair:** Give the Subject box and the pop-up list a text colour that goes with their own
  background, or take both colours from the theme.
- **Where in the code:** ui/tab_preview.py:135 (fixed light background, no text colour) with
  resources/style_dark.qss:437-439 (label text #E0E0E0); ui/components/variable_completer.py:46-66
  (white background, a text colour only for the selected row) with resources/style_dark.qss:7-12 and
  258-263

### G135 — At the app's default window size the Send tab's Progress log shows one line; on a smaller window, none

- **What happens:** The fixed parts of the Send tab (Send Configuration, Pre-Send Summary, the
  status line and the button rows) need about 714 pixels of height, and the tab gets about 642 at
  the default window size of 1100 x 750. The Progress log is the only part that can shrink, so it is
  squeezed to one line; at the smallest allowed window (900 x 600), or maximised on a 1920 x 1080
  screen at 150% scaling, it shows no line at all. During a batch the user then cannot see which
  clients were sent or failed, and the names of failed recipients are shown only in that log.
  Measured in an off-screen layout, not on a real screen.
- **When:** The window is at its default size or smaller, or the PC's display scale is 150% on a
  1080p screen; then open 6. Send. On a maximised window at 100% scale the log has about 12 lines.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by one reader. One reader measured the layout off-screen in
  the light theme: log text area 19 px (one line) at 1100x750, 0 px at 900x600, 5 px at 1280x680 and
  244 px (12 lines) at 1920x1000. Codex did not report it, no checker re-checked it, it was not
  confirmed on a real Windows screen, and the office's display scale is still an open office-PC
  check (12).
- **The repair:** Give the Progress log a minimum height of several lines and let the upper part of
  the Send tab shrink or scroll instead; raise the smallest allowed window height or reduce the
  spacing.
- **Where in the code:** ui/tab_send.py:328-335 (the log is the only stretching part of the tab;
  layout 191-368); config.py:91-94 (default 1100 x 750, minimum 900 x 600) used at
  ui/main_window.py:69-70; resources/style.qss:45-52 and 64-70 (group-box and button paddings)

### G136 — Shared log reaching 5 MB with two copies of the app open: log lines are lost and older logs deleted

- **What happens:** When app.log reaches its 5 MB limit the app must rename it to start a new one,
  and Windows refuses while another copy of the app has the same file open. Every line the app then
  tries to write is dropped - including the 'Checkpoint: sent #N to ...' lines of a send in progress
  - until the other copy has itself written two more lines to the log (an idle copy writes about one
  line at each three-minute auto-save, so several minutes can pass). Each failed attempt also
  shuffles the older logs along, so two of the three are deleted. Nothing is shown on screen.
- **When:** Two copies of the app are open on the shared folder (two users, or the app opened twice)
  at the moment app.log reaches 5 MB. With only one copy open the change-over works normally.
- **How serious, how often:** LOW · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** reproduced by several readers. Two readers reproduced it independently
  with the app's own log settings and a small size limit (lines lost; only one of three old logs
  left); Codex did not report it, no checker re-checked it, and two real copies of the app were not
  run. The readers differ on how long the loss lasts; settled for this entry by reading both
  experiment scripts: 'until one copy is closed' came from a stand-in that merely held the file open
  and never let go, while the run with a second logger like the app's lost lines #39-#110 of 120,
  until that logger's own second write.
- **Known gap:** extends G39. G39 only inferred that the change-over can fail; the experiments show
  what follows - log lines of a send in progress are dropped and two of the three older logs are
  deleted.
- **Already decided:** Change 9: partly - each PC would have its own log, but two copies open on one
  PC (two Windows users, or the app opened twice) would still share it
- **The repair:** Give each running copy its own log file (for example one per user and day), or
  start new log files by date instead of renaming a file that another copy may have open, so that a
  failed change-over can never drop lines or delete older logs.
- **Where in the code:** utils/logger.py:58-67 (one rotating app.log for every copy, set up at
  59-65); config.py:133-134 (5 MB, 3 older files); config.py:24 and 29 (the log sits in the shared
  .app_data); data/session_manager.py:68 (the one line an idle copy writes at each auto-save)

### G137 — The same picture used twice adds a stray attachment; a body picture with a set size is sent at full size

- **What happens:** When the very same picture is placed twice in one body (a logo at the top and
  again at the bottom), the body still looks right, but every email of the run carries one extra
  copy of the picture under a random name such as tmp6s8oi6ja.png that nothing in the body points
  to. A mail program may list that copy as an ordinary attachment beside the client's documents; how
  mail programs show it was not tested. Separately, a picture that was given a width and height in
  the underlying HTML is shown at that size in Compose and Preview but is sent without any size and
  without its description text, so the client sees it at full size. A picture put in with the Image
  button carries no size at all, so in ordinary use this second fault does not arise.
- **When:** (a) The same picture inserted twice in one body; a picture used N times gives N-1 stray
  copies on every email. (b) Only a picture whose HTML carries a size: typed in through the View
  HTML button, pasted with Ctrl+V or brought in with Import File from a web-style page that holds
  the picture inside it, or loaded from a template or session saved from such a body. Not triggered
  by Image > From File, Image > From Clipboard or drag-and-drop.
- **How serious, how often:** LOW · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** re-checked: partly true. Codex (flows-21) and one reader reported the
  lost size: a checker (its verdict, partly) found it true only for a picture whose HTML carries a
  size - the editor cannot resize a picture and Qt drops the app's own 'max-width' request - and
  measured it end to end (Compose and Preview 120x80, sent 240x160), and a checker reproduced it
  with an imported .html. The stray attachment was reproduced by three readers and by a checker as a
  side finding; real Outlook and a client's mail program were not tested, and the '.png ending for
  other picture kinds' is from reading the code only.
- **The repair:** Attach each distinct picture once and point every place in the body at that one
  copy. When swapping a picture for its inline version, change only where the picture comes from and
  keep its size and description text.
- **Where in the code:** core/outlook_sender.py:419-423 (the whole picture tag is replaced by a bare
  one, and line 423 replaces every identical tag at once), 412-417 (each found picture still gets
  its own attachment and id), 396-404 (other picture kinds get a .png ending);
  ui/components/rich_text_editor.py:755-767 (one entry and one new id per picture tag), 706 and 737
  (the Image button stores no size), 783-785 (the same replacement pattern)

### G138 — Preview: the 'exceeds the 25 MB limit' warning of the last client stays on screen when nobody is ticked

- **What happens:** The Preview tab shows an orange warning when one client's attachments add up to
  more than 25 MB. When the tab is next opened with nobody ticked, the app empties the subject, To,
  body and attachment list and shows '0 / 0' and 'No attachments', but leaves that warning where it
  was. The screen then says 'No attachments' and, under the empty list, '⚠ 26.0 MB of attachments —
  exceeds the 25 MB limit; this email may be rejected'. Nothing wrong is sent because of it; it is a
  leftover message that can confuse.
- **When:** A client whose files total more than 25 MB was the one shown on the Preview tab; then
  every client is unticked on the Recipients tab and the Preview tab is opened again. The same is
  expected after File > New Session (read from the code, not run).
- **How serious, how often:** LOW · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** reproduced by one reader. One reader reproduced it with the app's real
  window off-screen and a 26 MB dummy file (position '0 / 0', summary 'No attachments', warning text
  unchanged); Codex did not report it and no checker re-ran it. I read the code and it matches; the
  New Session route is from reading only.
- **The repair:** When the Preview tab is emptied, empty the size warning as well.
- **Where in the code:** ui/tab_preview.py:440-448 (_clear_preview resets everything except
  size_warning; compare 391-394 and 428-438); reached from ui/tab_preview.py:261-267 when no row is
  ticked; ui/main_window.py:439-441 and 454-471 (the Preview tab is refreshed only when it is
  opened)

### G139 — If PyQt5 is missing the app fails to start without any message; other missing packages are not named

- **What happens:** At start the app checks that its packages are installed, but it loads PyQt5 (the
  package that draws the window) before that check. If PyQt5 is missing the program stops right
  there: started from a shortcut without a console window nothing appears at all, and with a console
  the error would only flash past as the black window closes. If only openpyxl or pywin32 is
  missing, a box says 'Required dependencies are not installed' and to run pip install, without
  saying which package; the name is only printed to a console that staff do not see.
- **When:** A PC where Python is installed but this app's packages are not (a new or re-installed
  PC, or after a newer Python version was installed), and the app is started from its desktop
  shortcut.
- **How serious, how often:** LOW · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** read from the code only. One reader, by reading the code; Codex did not
  report it and no checker re-checked it. main.py was re-read for this entry and is as described;
  nobody started the app on a PC without the packages, and what the office shortcut runs (with or
  without a console) is still an open office-PC check (11).
- **The repair:** Check for the packages before anything needs them, and report a missing one in a
  plain Windows message box that names the package and tells the user to inform the office in-charge
  - for example in the launcher that Standard 13 describes.
- **Where in the code:** main.py:23-24 (PyQt5 imported at the top of main(), outside the try that
  starts at 33), 49-57 (the check and its box), 91-114 (_check_dependencies; the package name goes
  only to print() at 111)

### G140 — The window freezes for about 20 seconds when a saved folder or file is on a server that does not answer

- **What happens:** Before its background reading starts, the app checks whether the saved workbook,
  the static files and the client-files folder can be reached, and it does this as part of the
  window's own work. When they sit on a server that is switched off or cannot be reached, Windows
  takes about 20 seconds to give up (measured on the test PC), and for that time the window does not
  respond and shows nothing; staff may take it for a crash. Afterwards the app carries on normally.
  With a very large folder, each change of folder also lists the whole folder once in the same way
  before the background scan starts (how long that takes was not measured).
- **When:** The saved session or a profile names a client-files folder, static files or a workbook
  on a server that is switched off or unreachable, and the user answers Yes to 'Restore Previous
  Session?' or uses Profile > Load Profile. The same wait is expected when Browse... is pointed at a
  folder on a server that has just stopped answering. A server name that does not exist at all gives
  up in about a second.
- **How serious, how often:** LOW · it shows up only when something else fails (disk, network,
  another program).
- **How it was confirmed:** reproduced by one reader. One reader found it; Codex did not, and no
  checker re-ran it. The reader timed the app's own checks outside the window - 21.0 seconds for an
  address that does not answer, 1.3 seconds for an unknown server name, and no wait on a second
  check straight afterwards - but the app's window was not run in that state, so the freeze itself
  is concluded from the code, where these checks run on the window's own thread before the scan
  worker starts (ui/tab_excel.py:995, the same check for the workbook, was added from reading the
  code).
- **The repair:** Make these checks part of the background reading and report the result back to the
  window, with a 'Checking the folder...' line meanwhile, so that the Brief's promise C11 (slow work
  never freezes the window) also holds when a server is down.
- **Where in the code:** ui/tab_attachments.py:542-544; ui/tab_attachments.py:269-272;
  core/attachment_matcher.py:53; utils/file_utils.py:130-141; ui/components/file_list.py:231-234;
  ui/components/file_list.py:284; ui/components/file_list.py:295;
  ui/components/file_list.py:361-364; ui/main_window.py:837; ui/main_window.py:868;
  ui/main_window.py:880; ui/tab_excel.py:995

### G141 — No time limit on connecting to Outlook; Refresh looks usable but does nothing while it is connecting

- **What happens:** While the Send tab says 'Connecting to Outlook...', every click on Refresh is
  ignored with no message, and the button is not greyed out. That is harmless when Outlook answers.
  If Outlook never answers (for example it is stuck behind a box of its own), the app sets no time
  limit: the tab stays on 'Connecting to Outlook...' with Start Sending switched off, and the only
  way out is to close and reopen the app, which works normally. The never-answering Outlook was
  imitated with a stand-in, not seen with real Outlook.
- **When:** Clicking Refresh beside 'Send from' while the Send tab still says 'Connecting to
  Outlook...' (at start-up, or after an earlier Refresh started a new attempt): the click is
  ignored. Getting stuck needs Outlook itself to stall while the app is contacting it.
- **How serious, how often:** LOW · it shows up only when something else fails (disk, network,
  another program).
- **How it was confirmed:** reproduced by one reader. Found by one checker while re-checking a test:
  four clicks on the real Refresh button during a held-open connection attempt gave one attempt, no
  message and a still-clickable button, and closing the window during a stuck attempt ended the app
  normally; no reader or Codex reported the app side and nobody re-checked it. The never-answering
  Outlook was imitated with a stand-in, and the missing time limit is from reading the code.
- **The repair:** While the app is connecting, grey out Refresh and show 'Connecting to Outlook...'
  beside it so that a click is not silently lost. Give the attempt a time limit, after which the tab
  says that Outlook did not answer and Refresh works again.
- **Where in the code:** ui/tab_send.py:370-383 (a request made while an attempt is running returns
  silently, lines 374-375; Start Sending is switched off at 379), 412-416 (Refresh only asks for a
  new attempt when not connected), 100-128 (the attempt itself); core/outlook_sender.py:117-123 (the
  connection calls have no time limit)

### G142 — When the session cannot be saved, auto-save and closing the app fail without telling the user

- **What happens:** When the session file cannot be written, the three-minute auto-save and the save
  made on closing both fail without any message. The failure is only written to the log, which sits
  in the same folder and may be just as unreachable. The user keeps working and closes the window as
  usual, and the next start offers an older session or none. Only File > Save Session shows 'Could
  not save session.'
- **When:** The data folder cannot be written at that moment: the connection to the server folder
  has dropped, or another copy of the app is writing the same session file (G24). The user composes
  or changes the campaign during that time and then closes the app.
- **How serious, how often:** LOW · it shows up only when something else fails (disk, network,
  another program).
- **How it was confirmed:** read from the code only. One reader, by reading the code; Codex did not
  report it and no checker re-checked it. The cited lines were re-read for this entry and are as
  described; no failed save was staged, so how the app behaves when the server folder really drops
  was not run.
- **Already decided:** Change 9: partly - a dropped server connection would no longer stop the save,
  but a save that fails for another reason (file in use, disk full) would still fail without a word
- **The repair:** After a failed auto-save show a warning in the status bar; on closing, tell the
  user that the last save failed and let them retry or stay in the app.
- **Where in the code:** ui/main_window.py:677-679 (closeEvent ignores the True/False result of
  save_now()); data/session_manager.py:333-343 (_do_save catches everything and only logs), 71-73
  (save_session logs and returns False), 345-356; ui/main_window.py:641-647 (only the menu command
  shows a warning)

### G143 — The 'crash-safe' save is not forced onto the disk before the swap, and always uses one spare file name

- **What happens:** The session, the send progress file, saved lists and preferences are saved by
  writing a spare file and swapping it in, which protects them when the app itself stops half-way.
  But the app never makes Windows finish writing the spare file to the disk before the swap, so
  after a power cut or a Windows crash within moments of a save the file can come back empty or
  unreadable. The app then treats it as 'no session' or 'no unfinished run' without a word: no
  restore question and no Resume Previous button. Separately, the spare file always has the same
  name, so two copies of the app saving the same file at the same moment write into one spare file.
- **When:** A power cut or a Windows crash a moment after a save; during a send the progress file is
  rewritten after every email, so there is always a just-written file. Today the files sit on the
  server, so it is mainly a server power cut that matters; after Change 9 it would be a power cut on
  the PC itself. The second part needs two copies of the app saving the same file at the same
  instant in the shared data folder (G24).
- **How serious, how often:** LOW · it shows up only when something else fails (disk, network,
  another program).
- **How it was confirmed:** read from the code only. Two readers and a checker (as an extra finding)
  read the same thing in the code, and the checker saw the fixed-name leftover files after a failed
  write; Codex did not report it. Nobody ran it - it needs a real power cut, and what Windows or the
  server leaves behind then is not confirmed; it qualifies contract C8 and the audit's Section 6
  line 'Crash or power cut while saving -> atomic writes' (one reader's side note on preferences
  belongs to G109).
- **Already decided:** Change 9: partly - two PCs would no longer write into the same spare file,
  but the save would still not be forced onto the disk (and the files would then sit on each PC's
  own disk, where a power cut during a send matters more), and two copies on one PC would still
  share the spare file name
- **The repair:** Before the swap, make the app wait until Windows has really written the spare file
  to the disk, and give every save its own spare file name. When one of the app's own files exists
  but cannot be read, say so instead of treating it as missing.
- **Where in the code:** utils/file_utils.py:16-29 (26: fixed '<name>.tmp'; 27-29: write, then
  os.replace, with no flush or fsync; the note at 20-21 promises more than the code does);
  data/session_manager.py:92-97 and data/checkpoint.py:169-179 (a file that cannot be read is
  treated as absent); callers data/session_manager.py:62-66, data/checkpoint.py:163-164

## Weak tests (T1 to T3)

### T1 — The tests are not kept away from the app's real data folder: they write into its log and read real lists

- **What happens:** Nothing in the test set-up points the app's data folder at a temporary place.
  Every run of the tests creates the .app_data folders next to the code if they are missing, adds
  lines to the same app.log the office uses (159 lines for the whole suite in a copy), and the
  windows the tests build read the real saved recipient lists and templates. Only single files
  (session, send progress, lists, preferences) are redirected, and only after the window or its
  parts have already been built. Nothing real is overwritten today, but nothing prevents a later
  test from doing so.
- **When:** Whenever the tests are run in a folder that holds real data - for example office-PC
  check 1 in the Decisions Log, which asks for the tests to be run in the app folder on an office
  PC, that is the shared live folder. Staff using the app never trigger it.
- **How serious, how often:** LOW · it shows up now and then (ordinary use plus a plausible habit or
  kind of list).
- **How it was confirmed:** reproduced by several readers. Two readers ran tests in throwaway copies
  (26 and 82 passed): .app_data was created and app.log received the tests' lines (21 for one file,
  159 for the whole suite); Codex did not report it, no checker re-checked it, and the audit's
  Section 9 already notes that the tests create .app_data. Read from the code for this entry, not
  run: tests/test_compose_debounce.py:63-77 builds the main window without redirecting the session
  file at all (it is not written today, because that test neither saves nor closes the window).
- **The repair:** Add one automatic step to the test set-up that points every data location of the
  app (data folder, log, sessions, lists, templates, send progress, preferences) at a temporary
  folder before any part of the app is built; keep it when Change 9 moves the data folder.
- **Where in the code:** tests/conftest.py:1-40 (nothing redirects config.USER_DATA_DIR and its
  sub-folders); tests/test_polish.py:229-244; tests/test_compose_debounce.py:63-77;
  tests/test_recipient_lists.py:15-19, 105-106; tests/test_recipient_selection.py:8-12;
  tests/test_persistence.py:12-16; tests/test_tab_send_startup.py:45-55;
  tests/test_new_session_reset.py:52-55; data/session_manager.py:33-41,
  data/recipient_lists.py:29-37, data/checkpoint.py:33-51, data/template_storage.py:31-37,
  utils/logger.py:38-39 and 58-65 (each creates the folders and uses the real locations);
  ui/tab_recipients.py:61, ui/tab_compose.py:46

### T2 — Eight of the 82 tests cannot fail, or do not test what their names say

- **What happens:** The app behaves correctly today in the three cases a checker tried: a save cut
  off half-way keeps the last good session, Cancel during the pause between emails stops within a
  tenth of a second, and restoring a saved set-up switches AND back to OR. But the tests meant to
  guard these would not notice if they broke: when the checker deliberately broke each one in a
  copy, all 82 tests still passed. Five more tests are weak in the same way: the Test Matching test
  passes when nothing matches, the step-tick test never looks at the Compose tab, the 'empty
  session' test uses a hand-written empty body that the real editor never produces (so it passes
  while the real check fails), the column-mapping test never checks CC and BCC, and the 'controls
  disabled while loading' test really checks only the Browse button.
- **When:** Nothing a staff member clicks. It matters when this code is next changed - the decided
  Changes 4, 9 and 11 rework the saving and restore code - because a mistake there would pass the
  tests unnoticed: a wiped session or send progress file after an interrupted save, Cancel waiting
  out the whole delay, or AND left on so that clients' files stop matching.
- **How serious, how often:** LOW · it shows up not applicable.
- **How it was confirmed:** re-checked: reproduced. Four readers and Codex (three findings) reported
  weak tests; a checker reproduced the first three by breaking the code in a copy (all 82 tests
  still passed while its own checks showed the saved session lost, Cancel taking 7.5 s and AND left
  on), and a checker confirmed the 'empty session' and step-tick tests. The Test Matching, CC/BCC
  and Refresh points rest on readers alone (code reading, plus one sandbox run), and Codex rated its
  three MEDIUM where the checker says LOW.
- **The repair:** Rewrite each test so that it fails when the behaviour breaks: cut a save off
  half-way and check the earlier session still reads; press Cancel a moment after the pause has
  begun; tick AND before restoring a set-up that says OR; check the matched files, the exact tab
  titles and the CC and BCC boxes; and build the 'empty' state from a real Compose tab. Do this
  before or together with Changes 4, 9 and 11.
- **Where in the code:** tests/test_persistence.py:19-26; tests/test_send_batch.py:27-46 (cancel set
  at 32-33, before the pause at core/outlook_sender.py:522-523);
  tests/test_tab_excel_mapping.py:16-25, 28-44, 47-50 (OR is already ticked at
  ui/tab_excel.py:303-304; restore at 746-750); tests/test_tab_excel_async_load.py:59-78 (74; helper
  at 42-43 never used; ui/tab_excel.py:426-432); tests/test_polish.py:207-213 (both outcomes put the
  identifier in the title: ui/components/file_list.py:417, ui/tab_attachments.py:389-390), 247-256;
  tests/test_new_session_reset.py:93-104 (97)

### T3 — Two tests depend on timing: one fails now and then on a busy PC, the other could freeze a test run

- **What happens:** The reconnect test asks for a retry the instant the Send tab says 'Outlook not
  available - click Refresh to retry', a moment before the first connection attempt has completely
  ended; a retry asked in that moment is ignored without a message, and the test then fails after a
  5-second wait. It passed 2,000 times out of 2,000 on an idle PC and failed 8 times in 150 on a
  busy one. The test-email test ends before the window has received the result of the send: today
  nothing comes of it, but if that test ever failed on a PC without one add-on to the test tool and
  another test ran after it, a real 'Test Sent' box would open and the unattended test run would
  freeze instead of reporting a failure.
- **When:** Only when the tests are run, never for staff. The first: a busy PC (other programs, a
  virus scan, several test runs at once). The second needs three things together that do not hold
  today: only the basic test tool installed, the test-email test failing after its send has
  finished, and a further test running after it (it is the last of the 82 today).
- **How serious, how often:** LOW · it shows up rarely (unusual data, or a click at just the wrong
  second).
- **How it was confirmed:** re-checked: partly true. Codex alone reported both (no reader did); a
  checker reproduced the reconnect test failing (8 of 150 runs on a busy PC, each 'Timed out waiting
  for: reconnect'; 2,000 of 2,000 passed idle; the risky moment measured 0.6 ms idle and up to 60 ms
  busy). The hang was confirmed only in part: the result is left waiting, but a real box appeared
  only with pytest-qt switched off, the test made to fail and a probe test run afterwards - and the
  staff-side point (Refresh ignored while 'Connecting to Outlook...') is a separate defect.
- **The repair:** Make the reconnect test wait until the first connection attempt has completely
  ended before asking for the retry, and end the test-email test only after the window has shown the
  result, while the stand-in message boxes are still in place. List the test tools in a development
  requirements file so that every PC runs the same set.
- **Where in the code:** tests/test_tab_send_startup.py:76-96 (waits only for the label at 83-86,
  asks for the retry at 92); ui/tab_send.py:109-128 (result sent at 128, before the attempt has
  ended), 370-383 (a retry while the old attempt is still running is dropped at 374-375), 412-416;
  tests/test_tab_send_test_email.py:88-118 (ends at worker.wait, 111), 18-45;
  ui/tab_send.py:141-148, 565-580; ui/components/dialogs.py:26; tests/conftest.py:17-23

## Where each entry came from

For the record: which of the readers' 217 findings and of Codex's 60 findings were merged into
each entry. A reader's finding is named by the reader's area and a number (for example
`sending-3`); those raw findings were working papers of the session and are not kept in this
repository. A Codex finding is named by its job and its number in
`BUG_HUNT_codex_reports_advanced_email_tool.md` (for example `engine-7` is item 7 of Job 1). Four
of the readers' findings are not in this table: they are the ones behind the correction of G13.

| No. | The readers' findings | Codex's findings |
|---|---|---|
| G44 | threads-8, sending-1, failure-paths-1, integrity-3 | engine-8, window-9, flows-11 |
| G45 | sending-2, integrity-2 | engine-7, flows-9 |
| G46 | threads-9, sending-3 | — |
| G47 | sending-8, integrity-14, main-window-10 | — |
| G48 | excel-2, threads-11, compose-build-preview-1, sending-4, recipients-session-6, failure-paths-3, integrity-4, main-window-2, editor-templates-3 | window-5, flows-5 |
| G49 | threads-16, main-window-21 | engine-10, window-10, flows-13 |
| G50 | attachments-3, main-window-5 | — |
| G51 | compose-build-preview-3, integrity-5, editor-templates-1, failure-paths-5 | — |
| G52 | excel-1, compose-build-preview-4, integrity-9, editor-templates-2 | engine-12, window-11 |
| G53 | excel-3, threads-7, recipients-session-5, failure-paths-2, integrity-10, main-window-6 | — |
| G54 | excel-4 | — |
| G55 | excel-5, threads-10, recipients-session-10, integrity-8, main-window-14 | — |
| G56 | recipients-session-3, integrity-15 | engine-4, window-7, flows-7 |
| G57 | recipients-session-4 | — |
| G58 | a checker's side finding | — |
| G59 | attachments-4, compose-build-preview-6, failure-paths-6 | — |
| G60 | attachments-12 | flows-17 |
| G61 | compose-build-preview-5, main-window-3 | window-1, flows-2 |
| G62 | compose-build-preview-8, failure-paths-14, integrity-20, main-window-16, editor-templates-7, editor-templates-8 | window-4, flows-12 |
| G63 | attachments-1, threads-3, failure-paths-4, integrity-1, main-window-7 | engine-2, window-2, flows-3 |
| G64 | attachments-2, threads-4, main-window-8 | — |
| G65 | threads-12, main-window-4 | — |
| G66 | excel-13, threads-6, integrity-11 | engine-3, window-3, flows-4 |
| G67 | excel-6, compose-build-preview-2, integrity-6 | engine-1, flows-1 |
| G68 | excel-10, compose-build-preview-7, integrity-16 | — |
| G69 | attachments-5, failure-paths-12 | — |
| G70 | sending-5, recipients-session-2 | — |
| G71 | threads-13, sending-10, failure-paths-9 | engine-6, window-8, flows-8 |
| G72 | editor-templates-5 | flows-23 |
| G73 | sending-12 | — |
| G74 | sending-7, failure-paths-8, integrity-13 | engine-9, flows-10 |
| G75 | sending-9 | — |
| G76 | sending-11 | — |
| G77 | main-window-17 | — |
| G78 | main-window-11 | — |
| G79 | editor-templates-4 | — |
| G80 | editor-templates-13 | — |
| G81 | main-window-18 | — |
| G82 | excel-7, threads-14, recipients-session-8, failure-paths-16, integrity-19, main-window-13 | — |
| G83 | excel-8, recipients-session-9, main-window-12 | engine-5, window-6, flows-6 |
| G84 | excel-19, failure-paths-19, integrity-17 | — |
| G85 | recipients-session-11 | — |
| G86 | attachments-6, failure-paths-20, integrity-21 | — |
| G87 | excel-9, main-window-19 | window-16 |
| G88 | excel-11 | — |
| G89 | a checker's side finding | — |
| G90 | attachments-7, recipients-session-7, failure-paths-10, main-window-9 | — |
| G91 | compose-build-preview-9, failure-paths-18, integrity-18, editor-templates-6 | — |
| G92 | threads-1, recipients-session-1, failure-paths-7, integrity-7, main-window-1 | window-13, flows-15 |
| G93 | recipients-session-12 | — |
| G94 | editor-templates-10 | — |
| G95 | compose-build-preview-10, failure-paths-24, main-window-33, editor-templates-24 | — |
| G96 | compose-build-preview-17, failure-paths-23, editor-templates-23 | flows-19 |
| G97 | attachments-9, failure-paths-11 | — |
| G98 | excel-12, threads-5, recipients-session-15 | engine-15, flows-16 |
| G99 | compose-build-preview-11, editor-templates-9, editor-templates-18 | — |
| G100 | a checker's side finding | — |
| G101 | attachments-10 | — |
| G102 | attachments-11, failure-paths-22 | — |
| G103 | threads-2, sending-6, failure-paths-13, integrity-12 | engine-13, window-14, flows-18 |
| G104 | sending-15 | — |
| G105 | editor-templates-12 | window-17 |
| G106 | recipients-session-14 | — |
| G107 | editor-templates-14 | window-15, flows-22 |
| G108 | a checker's side finding | — |
| G109 | failure-paths-17, editor-templates-19, main-window-31 | engine-11, window-12, flows-14 |
| G110 | compose-build-preview-13, sending-14, failure-paths-15, editor-templates-11 | engine-14, flows-20 |
| G111 | a checker's side finding | — |
| G112 | main-window-23 | — |
| G113 | editor-templates-15 | — |
| G114 | editor-templates-22 | — |
| G115 | recipients-session-13, main-window-15, editor-templates-16 | — |
| G116 | sending-13 | — |
| G117 | main-window-27 | — |
| G118 | attachments-8, excel-16, main-window-20 | — |
| G119 | attachments-14, compose-build-preview-18 | — |
| G120 | compose-build-preview-16 | — |
| G121 | excel-14 | — |
| G122 | recipients-session-16 | — |
| G123 | attachments-13, failure-paths-25 | — |
| G124 | threads-15, sending-16 | — |
| G125 | compose-build-preview-14, editor-templates-17 | — |
| G126 | editor-templates-25 | — |
| G127 | a checker's side finding | — |
| G128 | sending-17, main-window-29 | — |
| G129 | a checker's side finding | — |
| G130 | excel-15 | — |
| G131 | excel-17 | — |
| G132 | excel-18 | — |
| G133 | main-window-24 | — |
| G134 | main-window-25, main-window-26, editor-templates-21 | — |
| G135 | main-window-28 | — |
| G136 | failure-paths-21, main-window-22 | — |
| G137 | compose-build-preview-12, editor-templates-20 | flows-21 |
| G138 | compose-build-preview-15 | — |
| G139 | main-window-32 | — |
| G140 | attachments-15 | — |
| G141 | a checker's side finding | — |
| G142 | main-window-30 | — |
| G143 | attachments-16, recipients-session-18 | — |
| T1 | recipients-session-17, main-window-35 | — |
| T2 | attachments-18, excel-21, sending-18, main-window-36 | flows-24, flows-25, flows-26 |
| T3 | — | flows-27, flows-28 |
