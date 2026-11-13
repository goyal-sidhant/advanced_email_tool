# Bug Hunt, Codex's reports: Advanced Email Tool

> **What is this file?** The three reports that Codex wrote for the bug hunt of 13-11-2026, saved
> word for word. Codex is a different company's model (OpenAI), used so that a mistake Claude's
> readers share would still be caught. Its findings were then checked one by one by independent
> Claude checkers; what survived is in `BUG_HUNT_advanced_email_tool.md` and
> `BUG_HUNT_details_advanced_email_tool.md`. In those files a Codex finding is named by its job
> and number: `engine-7` is item 7 of Job 1 below, `window-4` item 4 of Job 2, `flows-12` item 12
> of Job 3.

**How Codex was run**

- Three read-only jobs, each on its own clean copy of the tracked files (commit `6fb760c`; the
  code files are those of v1.8.0). The copies held no `.app_data`, so Codex never saw the app's
  own data folder. It was told not to start the app or Outlook and to change nothing.
- Driven from the codex-companion script, with no model and no effort passed, so the settings in
  `~/.codex/config.toml` applied. Checked afterwards in Codex's own session logs: **model
  gpt-6-astra, effort ultra** on all three jobs.
- A first attempt stopped within 20 seconds because Codex's sign-in on this PC had expired; the
  three jobs below ran after the author signed in again.

| Job | Codex session | Time taken | Findings |
|---|---|---|---|
| 1 — the engine | `01a1d31e-b027-7073-9d8f-c998544157c3` | 11 min 25 s | 15 |
| 2 — the window | `01a1d31f-7b09-70d3-a448-64372f639303` | 11 min 20 s | 17 |
| 3 — the flows and the tests | `01a1d31f-8f74-7c83-b482-ebac8565a77d` | 18 min 16 s | 28 |

**What the checkers found.** The 60 findings overlap; they come to 26 distinct defects in the app
and 5 weak tests. Of those 31 claims, 28 were reproduced on dummy data, 1 was confirmed by reading
the code (Word import: the needed package is not installed on this PC), 2 were found only partly
true, and none was refuted.

**Each job was given the same brief**, apart from its part of the code: read every file in that
part to the last line; read the audit's known gaps first and do not report them again; report
only what the code supports, with the lines quoted and a concrete way to trigger it; give
severity, confidence, the known gap it extends if any, and a direction for the repair; and list
the files read in full.

---

## Job 1 — the engine (config.py, main.py, core/, data/, utils/ and their tests)

1. **Title:** Sending can use a different address column from the one selected and previewed.  
   **Where:** `core/email_builder.py:104–111,220–236,397–398`; `ui/tab_preview.py:364–372`.  
   **What goes wrong:** A workbook has distinct columns `Email` and `EMAIL`, containing different addresses. Select `EMAIL` as To, preview the correct client, then send. The builder instead addresses the email—and that client’s attachments—to the first `Email` column.  
   **Why:** `_find_key()` returns the first case-insensitive match: `if k.lower() == key_lower:` followed by `return k` (`core/email_builder.py:110–111`). Sending uses that lookup at lines 221–223. Preview instead uses the exact selected key: `row_data.get(self.email_column, "")` at line 397. CC and BCC have the same ambiguity. Unlike G26’s identical headers, these two dictionary keys survive loading separately.  
   **Severity:** HIGH  
   **Confidence:** certain — traced Preview and sending; an isolated, read-only execution of the lookup returned `Email` when explicitly asked for `EMAIL`.  
   **Known gap:** G26  
   **Fix direction:** Prefer an exact column-name match and reject ambiguous fallback matches. Build Preview from the same recipient-resolution logic used for sending.

2. **Title:** Changing folders during a scan can attach documents from the previous campaign.  
   **Where:** `core/attachment_matcher.py:57–61,86–95`; `ui/tab_attachments.py:265–300`.  
   **What goes wrong:** Start scanning campaign A’s large folder. Before it finishes, browse to campaign B’s folder. A’s remaining files can become B’s index while B’s scan never starts. If the campaigns reuse client codes, sending B’s clients can attach A’s clients’ documents.  
   **Why:** Changing folders replaces `self.directory` and clears `self.file_index` (`core/attachment_matcher.py:57–60`), but the existing iterator continues executing `self.file_index.append((full_path, filename, size))` at line 91. The requested replacement scan exits at `if self._scan_worker and self._scan_worker.isRunning(): return` (`ui/tab_attachments.py:284–285`). Browse remains available. This extends G14 from incomplete matches to documents crossing campaign boundaries.  
   **Severity:** HIGH  
   **Confidence:** possible — an isolated in-memory scan interleaving reproduced a configured B folder containing an A document; actual GUI timing was not exercised.  
   **Known gap:** G14  
   **Fix direction:** Scan into a private result associated with its folder and request identifier. Publish it only if that request is still current; queue or reject folder changes during scanning.

3. **Title:** Loading a profile during an Excel load combines recipients from one campaign with another campaign’s content.  
   **Where:** `ui/tab_excel.py:398–424,980–1004`; `ui/main_window.py:812–815,837–870`.  
   **What goes wrong:** Begin loading workbook A. While it is still loading, load profile B containing another workbook, message and static attachments. B’s workbook request is discarded, but B’s content is applied. When A finishes, sending uses A’s clients with B’s message and attachments.  
   **Why:** `_start_load()` returns immediately when a worker is running (`ui/tab_excel.py:398–399`), yet `load_file_path()` still returns `True` after calling it (`1003–1004`). Profile application continues with `set_subject_template(...)`, `set_body_template(...)` and `set_static_attachments(existing_static)` (`ui/main_window.py:859–870`). The caller announces `"Profile loaded successfully!"` at line 814.  
   **Severity:** HIGH  
   **Confidence:** possible — traced the rejected request and independently applied profile settings; requires the first worker to remain active during profile application.  
   **Known gap:** new  
   **Fix direction:** Apply a profile only after its own workbook loads successfully. Treat an overlapping load as rejection, queuing or replacement of the entire profile operation.

4. **Title:** Loading a saved recipient list silently adds previously excluded rows.  
   **Where:** `data/recipient_lists.py:166–189`; `ui/tab_recipients.py:143–168,213–224`.  
   **What goes wrong:** Two rows share an email address. Tick only one and save the selection. Loading that list against the unchanged workbook ticks both rows. Sending produces an extra email, potentially with an excluded row’s obsolete or different documents.  
   **Why:** Resolution groups every row under its address using `email_rows.setdefault(key, []).append(idx)` (`data/recipient_lists.py:177`), then expands each saved address with `indices.extend(rows)` at line 185. Saved row membership is ignored whenever saved emails exist. The UI applies the expanded selection at `ui/tab_recipients.py:168`, warning only about missing addresses. G9 assumes both rows were already ticked; this defect creates that selection.  
   **Severity:** HIGH  
   **Confidence:** certain — traced saving and loading; a read-only reproduction of the selection logic expanded saved `[0]` into `[0, 1]`.  
   **Known gap:** G9  
   **Fix direction:** Persist a stable client identity alongside the address. Treat multiple matching rows as ambiguous instead of selecting them all.

5. **Title:** Restoring an explicitly empty selection selects every client.  
   **Where:** `ui/main_window.py:505,551–559`; `ui/tab_recipients.py:288–296`.  
   **What goes wrong:** Load a workbook, clear all recipient ticks, save the session and close. Restore that session with the workbook unchanged. Every client is ticked; proceeding to Send emails people the saved selection excluded.  
   **Why:** Saving records `'selected_recipients': self.tab_recipients.get_selected_indices()` (`ui/main_window.py:505`), including `[]`. Loading initially calls `self.recipient_list.select_all()` (`ui/tab_recipients.py:296`). Restoration then skips the empty selection because it uses `if selected:` before applying it (`ui/main_window.py:557–559`). This occurs without the row movement described in G20.  
   **Severity:** HIGH  
   **Confidence:** certain — traced serialization, load-time selection and the restore callback.  
   **Known gap:** G20  
   **Fix direction:** Distinguish an absent selection field from a saved empty list. Apply an explicitly saved empty selection.

6. **Title:** Failed checkpoint writes can cause an already sent client to be emailed again.  
   **Where:** `data/checkpoint.py:117–118,160–167,219–230,288–292,301–318`.  
   **What goes wrong:** Start a batch with a valid checkpoint. One email succeeds, but saving that success fails—for example, because replacement of the checkpoint is temporarily blocked. Cancel before another send, resolve the storage problem and Resume. The already emailed client is treated as pending and sent again, even without restarting the app.  
   **Why:** Success is added in memory with `self.completed.append(index)` (`117`), but `_save_checkpoint()` catches persistence errors and only logs them (`166–167`). Suspension merely sets `self.is_active = False` (`229`). Resume replaces the in-memory successes with `self.completed = checkpoint_data.get('completed_indices', [])` (`313`), restoring stale disk state. This is a concrete duplicate-send consequence of G36’s replacement-failure risk.  
   **Severity:** HIGH  
   **Confidence:** possible — the storage failure was not induced; the stale-state recovery path is established by code inspection.  
   **Known gap:** G36  
   **Fix direction:** Surface checkpoint failures and stop sending until progress is safely recorded. Preserve and reconcile known in-memory successes before allowing Resume.

7. **Title:** Retry Failed discards clients that an aborted batch never attempted.  
   **Where:** `core/outlook_sender.py:511–518`; `ui/tab_send.py:767–800`; `data/checkpoint.py:81–101`.  
   **What goes wrong:** Start a five-client batch. The first three attempts fail, stopping the batch before clients four and five. Fix the problem and choose Retry Failed. The three failures are retried, but the two unattempted clients disappear from recovery; a successful retry reports completion.  
   **Why:** Retry starts a replacement checkpoint containing only `[e.row_index for e in retry_emails]` (`ui/tab_send.py:792–795`). `start_session()` replaces `self.planned`, clears previous outcomes and saves this smaller plan (`data/checkpoint.py:81–101`). No record of the unattempted clients survives in that checkpoint.  
   **Severity:** HIGH  
   **Confidence:** certain — traced the automatic-abort, retry and checkpoint paths; reviewed their tests without running them.  
   **Known gap:** new  
   **Fix direction:** Retry failures within the original campaign checkpoint. Preserve unattempted rows and keep them available for Resume.

8. **Title:** Resume hides earlier failures and declares the campaign complete.  
   **Where:** `data/checkpoint.py:288–292,313–318`; `ui/tab_send.py:628,723–733,755–773`.  
   **What goes wrong:** A five-client batch stops after its first three attempts fail. Choose Resume, immediately or after restarting. Only clients four and five are attempted. If they succeed, the app reports success, finalizes the checkpoint and removes recovery controls while the first three clients remain unsent.  
   **Why:** Pending calculation excludes failures through `processed = completed | failed` (`data/checkpoint.py:290`). The completion handler reads only the latest batch’s `failed = results.get('failed', 0)` (`ui/tab_send.py:724`), calls `complete_session(success=True)` at line 733, and exposes Retry only under `if failed > 0:` at line 768. Earlier persisted failures are ignored.  
   **Severity:** HIGH  
   **Confidence:** certain — traced persisted failure restoration, pending calculation and completion controls.  
   **Known gap:** new  
   **Fix direction:** Derive campaign completion and retry availability from all checkpoint outcomes. Preserve access to previous failures after every resumed batch.

9. **Title:** Resuming a partial selection permanently removes other pending clients from recovery.  
   **Where:** `ui/tab_send.py:675–696,728–733`; `data/checkpoint.py:195–201,239–243`.  
   **What goes wrong:** Start clients A, B and C, then cancel after A succeeds. Leave only B ticked and click Resume. B is sent, but C remains unsent while the original checkpoint becomes completed. Selecting C again does not restore Resume.  
   **Why:** Resume intersects pending rows with current selections: `resume_emails = [e for e in self._emails if e.row_index in remaining_set]` (`ui/tab_send.py:678`). It rejects only an entirely empty intersection at line 680. Finishing that subset calls `complete_session(success=True)` (`733`), which writes completed status without checking for pending rows (`data/checkpoint.py:197`). Unlike G1’s changed-workbook case, row identities here remain unchanged.  
   **Severity:** HIGH  
   **Confidence:** certain — traced the nonempty partial-intersection branch and final status change.  
   **Known gap:** G1  
   **Fix direction:** Require all pending rows to be available, or retain omitted rows as pending. Finalize only after checking the original campaign plan.

10. **Title:** Refresh applies a previous campaign’s header offset to a newly opened workbook.  
    **Where:** `ui/tab_excel.py:379–387,694–715,793–823`; `core/excel_handler.py:132,150–166`.  
    **What goes wrong:** Use header row 3 for workbook A. Start New Session and open workbook B, whose headers are in row 1 and clients in rows 2–4. B initially shows all three clients. Refresh then uses the retained row-3 setting, treats the second client as headers and drops the first two clients from the campaign.  
    **Why:** Initial opening calls `_start_load(file_path, on_success=self._update_ui_after_load)` without offsets (`ui/tab_excel.py:387`). Reset does not reset the offset controls. Refresh reads `current_row_offset = self.start_row_spin.value()` (`696`) and passes it into loading (`709–712`). The parser then iterates `rows[header_row_idx + 1:]` (`core/excel_handler.py:166`). This extends G23 to offsets leaking between campaigns without session restoration.  
    **Severity:** HIGH  
    **Confidence:** certain — traced both loading paths, reset and the resulting row slicing.  
    **Known gap:** G23  
    **Fix direction:** Reset offsets when opening a different workbook or session. Refresh should reuse the offsets actually applied to the displayed data.

11. **Title:** A failed template overwrite destroys the previous saved template.  
    **Where:** `data/template_storage.py:103–112,131–139,178–192`; `ui/tab_compose.py:209–225`.  
    **What goes wrong:** Edit an existing template and click Save. If writing fails after the file opens, or the process stops during writing, the previous template has already been truncated. On reopening, it cannot load and can disappear from the template dropdown.  
    **Why:** Saving directly opens the destination with `open(template_path, 'w', encoding='utf-8')` and then calls `json.dump(...)` (`data/template_storage.py:103–104`). The failure handler returns an error without restoring the original (`110–112`). Invalid JSON returns `None` during loading (`137–139`) and is skipped during listing (`190–192`).  
    **Severity:** HIGH  
    **Confidence:** possible — the interruption/storage failure was not induced; the destructive overwrite sequence is explicit in the code.  
    **Known gap:** new  
    **Fix direction:** Use the existing atomic JSON writer for templates. Preserve the old file until the replacement has been completely serialized.

12. **Title:** Some variables inserted from valid columns are silently sent literally.  
    **Where:** `core/template_engine.py:28,90,139,263–280`; `ui/tab_compose.py:300–307,335–354`.  
    **What goes wrong:** Load a column named `Tax: Due` containing the client’s amount. Use Insert Variable to add it to the subject, then send. The email contains `{Tax: Due}` instead of the amount, while the editor can report “No variables used (static email).”  
    **Why:** Insertion constructs `f"{{{var_name}}}"` (`ui/tab_compose.py:306`), but the engine recognizes only `r'\{([^{}:;]+)\}'` (`core/template_engine.py:28`). Both substitution and validation use that pattern. Consequently, a colon or semicolon makes the placeholder invisible to both operations. Unlike G31, the column exists and no missing-column warning is generated.  
    **Severity:** MEDIUM  
    **Confidence:** certain — a read-only regex check confirmed that `{Tax: Due}` produces no recognized variable; insertion and validation were traced.  
    **Known gap:** G31  
    **Fix direction:** Recognize placeholders using the available column names, with proper escaping. Explicitly reject unsupported placeholders instead of treating them as static text.

13. **Title:** Refresh can change the sending account halfway through a batch.  
    **Where:** `core/outlook_sender.py:178–179,204–206,309–315`; `ui/tab_send.py:412–419,623–629`.  
    **What goes wrong:** Outlook lists a personal account first and an office account second. Select the office account, start sending, then click Refresh after the first email. Subsequent emails attempt to use the personal account.  
    **Why:** Refresh remains available during sending and reloads accounts. Reload executes `self.selected_account = self.accounts[0]` (`core/outlook_sender.py:179`). Each email consults that mutable selection through `accounts.Item(self.selected_account.index)` at line 315. This extends G7 to an account change during an active batch.  
    **Severity:** MEDIUM  
    **Confidence:** possible — the selection mutation is explicit; actual sending from the changed account depends on Outlook accepting the COM assignment.  
    **Known gap:** G7  
    **Fix direction:** Capture the account identity when starting the batch and retain it throughout. Disable refresh during sending and preserve the selected identity when refreshing.

14. **Title:** Inline-image attachment failures still allow the email to be reported as sent.  
    **Where:** `core/outlook_sender.py:334–338,363–364,407–434`.  
    **What goes wrong:** Compose an email containing an inserted image, such as a payment instruction or calculation. If creating or attaching its temporary image fails but the subsequent send succeeds, the app reports success even though the intended inline image may be missing or broken.  
    **Why:** Image processing calls `mail.Attachments.Add(temp_path)` (`413`) and sets the content ID (`417`), but catches any failure with only `self.logger.warning(f"Could not embed image: {e}")` (`432`). It returns the body at line 434, allowing `mail.Send()` and `"Email sent successfully"` (`363–364`). Regular attachment failures have a blocking check; inline-image failures do not.  
    **Severity:** MEDIUM  
    **Confidence:** possible — the swallowed-error path is explicit; the failure trigger and rendering of the remaining base64 HTML depend on the environment and Outlook.  
    **Known gap:** new  
    **Fix direction:** Propagate inline-image preparation failures and prevent sending incomplete content. Clean temporary images in a `finally` block.

15. **Title:** New Session can be repopulated by an Excel load from the previous session.  
    **Where:** `core/excel_handler.py:104–119`; `ui/tab_excel.py:405–424,473–489,793–823`; `ui/main_window.py:625–639`.  
    **What goes wrong:** Begin opening workbook A and choose New Session while its worker is still opening the workbook. The window clears, but the old worker can later restore A’s data and recipients into the new session. Subsequent composition therefore operates on the previous campaign’s clients.  
    **Why:** Reset calls `self.excel_handler.close()` (`ui/tab_excel.py:795`) but does not invalidate the running request. The worker can subsequently complete `self.workbook = self._open_workbook(file_path)` (`core/excel_handler.py:105`). Its callback unconditionally reinstates `self._file_path = file_path` and runs the success callback (`ui/tab_excel.py:422–424`), which publishes the old data.  
    **Severity:** MEDIUM  
    **Confidence:** possible — traced the interleaving where reset occurs before the opened workbook is assigned; Qt timing was not exercised.  
    **Known gap:** new  
    **Fix direction:** Invalidate outstanding requests when resetting and discard their completions. Give each worker private loading state that is committed only to its originating session.

Files read in full: `config.py`, `main.py`; `core/__init__.py`, `core/attachment_matcher.py`, `core/email_builder.py`, `core/excel_handler.py`, `core/outlook_sender.py`, `core/template_engine.py`, `core/validators.py`; `data/__init__.py`, `data/checkpoint.py`, `data/recipient_lists.py`, `data/session_manager.py`, `data/template_storage.py`; `utils/__init__.py`, `utils/file_utils.py`, `utils/html_converter.py`, `utils/logger.py`, `utils/theme_manager.py`; `tests/conftest.py`, `tests/test_attachment_matcher.py`, `tests/test_checkpoint.py`, `tests/test_compose_debounce.py`, `tests/test_excel_handler.py`, `tests/test_new_session_reset.py`, `tests/test_outlook_sender_attachments.py`, `tests/test_outlook_thread_safety.py`, `tests/test_persistence.py`, `tests/test_polish.py`, `tests/test_recipient_lists.py`, `tests/test_recipient_selection.py`, `tests/test_recipient_table.py`, `tests/test_send_batch.py`, `tests/test_send_ux.py`, `tests/test_tab_excel_async_load.py`, `tests/test_tab_excel_mapping.py`, `tests/test_tab_send_resume.py`, `tests/test_tab_send_startup.py`, `tests/test_tab_send_test_email.py`; `ui/main_window.py`, `ui/tab_attachments.py`, `ui/tab_compose.py`, `ui/tab_excel.py`, `ui/tab_preview.py`, `ui/tab_recipients.py`, `ui/tab_send.py`, `ui/components/rich_text_editor.py`.  
Not examined: None unfinished in the assigned scope. The audit’s Section 7 was read first; application startup, Outlook/COM and test execution were not performed.

Codex session ID: 01a1d31e-b027-7073-9d8f-c998544157c3
Resume in Codex: codex resume 01a1d31e-b027-7073-9d8f-c998544157c3

## Job 2 — the window (ui/, ui/components/, resources/ and their tests)

1. **Title:** Clearing or changing Universal BCC can still disclose emails to the old address.
   - **Where:** `ui/tab_compose.py:120,146,157–159,310–328`; `ui/main_window.py:391–399,447–452`; `core/email_builder.py:238–243`.
   - **What goes wrong:** Set BCC to A’s address, edit the subject/body, and let the debounce finish. Then clear or replace only BCC and send. A’s old address still receives every email and attachment. This extends G4 from a missing copy to disclosure to an unwanted recipient.
   - **Why:** Subject and body changes have connections; the BCC field has none. Flushing requires `if self._change_timer.isActive():` (`tab_compose.py:326`). The unchanged builder subsequently executes `bcc_list.append(self.universal_bcc)` (`email_builder.py:241`).
   - **Severity:** HIGH.
   - **Confidence:** certain; traced field connections, flushing, builder updates and recipient construction.
   - **Known gap:** G4.
   - **Fix direction:** Connect BCC changes to state updates and read all current compose fields before building emails.

2. **Title:** Changing attachment folders during a scan can attach another campaign’s documents.
   - **Where:** `ui/tab_attachments.py:259–315`; `core/attachment_matcher.py:53–61,85–95`; `utils/file_utils.py:286,308–313`; `core/email_builder.py:265–287`.
   - **What goes wrong:** Start a slow scan of folder A, then Browse to folder B before it finishes. If both campaigns reuse identifier `001`, B’s client can receive A’s `001` document: the window names B while the index contains files from A.
   - **Why:** Browse calls `self.attachment_matcher.set_directory(...)` before `_scan_folder()` (`tab_attachments.py:269–277`). The latter returns when a worker is running (`:284–285`). Meanwhile, the original scan continues `self.file_index.append((full_path, filename, size))` (`attachment_matcher.py:91`) into the replacement index.
   - **Severity:** HIGH.
   - **Confidence:** certain under the stated timing; an extracted-method check with a simulated directory iterator produced directory B containing an A attachment. No files or threads were created.
   - **Known gap:** G14.
   - **Fix direction:** Build each scan’s index privately and publish it only if its folder and campaign are still current. Invalidate outstanding scans on folder changes and resets.

3. **Title:** Loading a profile during an Excel load mixes its documents with the other workbook’s clients.
   - **Where:** `ui/tab_excel.py:398–424,980–1004`; `ui/main_window.py:812–815,837–870`.
   - **What goes wrong:** While workbook A is loading, load profile B containing an existing workbook and static attachment. B’s workbook request is discarded, but B’s text and attachments are applied and “Profile loaded successfully!” appears. When A finishes, entering Send builds B’s correspondence for A’s clients.
   - **Why:** `_start_load()` executes `if self._load_worker and self._load_worker.isRunning(): return` (`tab_excel.py:398–399`), while `load_file_path()` nevertheless returns `True` (`:1003–1004`). Profile application continues with B’s body and attachments (`main_window.py:859–870`). A’s completion unconditionally accepts its path and callback (`tab_excel.py:422–424`).
   - **Severity:** HIGH.
   - **Confidence:** certain under the stated timing; independently traced both operations and confirmed the busy-load branch with an extracted-method check.
   - **Known gap:** new.
   - **Fix direction:** Apply a profile only after its workbook loads successfully. Reject or queue competing requests explicitly and discard obsolete completion callbacks.

4. **Title:** HTML source can restore a previous client’s body after New Session.
   - **Where:** `ui/components/rich_text_editor.py:397–414,432–448,468–470`; `ui/tab_compose.py:288–298`; `ui/main_window.py:632–635`.
   - **What goes wrong:** Open View HTML for campaign A containing confidential client text. Start New Session and load B’s template, then click Hide HTML. A’s retained source overwrites B’s body and can be sent to B’s clients. Editing source and sending without hiding it instead sends the old body.
   - **Why:** Opening source copies `self.editor.toHtml()` into `source_view` (`rich_text_editor.py:403–404`). Hiding it unconditionally executes `self.editor.setHtml(html)` from that buffer (`:410–411`). However, replacement, clearing and reading touch only the rich editor: `self.editor.setHtml(html)` (`:439`), `self.editor.clear()` (`:470`), and `return self.editor.toHtml()` (`:448`).
   - **Severity:** HIGH.
   - **Confidence:** certain; traced both buffers through reset, template loading, saving and email construction.
   - **Known gap:** new.
   - **Fix direction:** Synchronize source edits before every read and reset both buffers together. Template replacement must also replace or close source mode.

5. **Title:** Loading a profile on the Send tab leaves the previous campaign queued.
   - **Where:** `ui/main_window.py:331–399,426–445,473–488,824–896`; `ui/tab_send.py:450–457,582–614`.
   - **What goes wrong:** Prepare campaign A and enter Send. Use the global menu to load campaign B and wait for its workbook to finish. Without leaving Send, click Start Sending: A’s prepared recipients, content and attachments are sent, despite B having loaded successfully.
   - **Why:** Email rebuilding happens when entering Send: `elif index == 5: self._update_send_tab()` (`main_window.py:443–445`). Profile and data-change handlers do not rebuild that list. Start uses the cached objects directly: `self._launch_send(self._emails)` (`tab_send.py:614`).
   - **Severity:** HIGH.
   - **Confidence:** certain; traced profile completion, signal handlers, cached Email objects and Start Sending.
   - **Known gap:** new.
   - **Fix direction:** Invalidate prepared emails whenever campaign state changes. Rebuild and validate the current campaign immediately before confirmation and sending.

6. **Title:** Restoring an explicitly empty selection ticks every client.
   - **Where:** `ui/main_window.py:340–344,505,551–559`; `ui/tab_recipients.py:288–296`.
   - **What goes wrong:** With an unchanged workbook, untick everyone, save the session, restart and restore it. All recipients become selected instead of none; proceeding to Send includes clients deliberately excluded from the saved session.
   - **Why:** Loading defaults to `self.recipient_list.select_all()` (`tab_recipients.py:296`). Restoration applies saved selection only under `if selected:` (`main_window.py:558`), so the saved `[]` never replaces that default.
   - **Severity:** HIGH.
   - **Confidence:** certain; an extracted-method check restored saved `[]` over `[0, 1]` and left `[0, 1]` selected.
   - **Known gap:** new.
   - **Fix direction:** Distinguish an absent selection field from an explicitly empty list and restore the latter.

7. **Title:** Reloading a saved list selects excluded rows sharing the same email address.
   - **Where:** `ui/tab_recipients.py:143–168,213–224`; `data/recipient_lists.py:166–189`.
   - **What goes wrong:** Two workbook rows share one To address but have different identifiers or correspondence. Select only the first and save a list. Reloading that list on the unchanged workbook ticks both, creating an additional email with previously excluded attachments.
   - **Why:** Restoration groups all rows with `email_rows.setdefault(key, []).append(idx)` (`recipient_lists.py:177`), then expands each saved email using `indices.extend(rows)` (`:185`). Those indices replace the selection without an ambiguity warning.
   - **Severity:** HIGH.
   - **Confidence:** certain; the extracted resolver returned `([0, 1], [])` for a list originally containing only row 0.
   - **Known gap:** new.
   - **Fix direction:** Save stable client identities alongside addresses. Require resolution when one saved address matches multiple clients.

8. **Title:** A failed checkpoint write can make Resume resend an already-sent email.
   - **Where:** `ui/tab_send.py:65–73,667–678`; `data/checkpoint.py:114–118,160–167,288–292,301–318`; `utils/file_utils.py:25–29`.
   - **What goes wrong:** Row 0 sends and its checkpoint saves. Row 1 sends, but its checkpoint write fails, for example because storage fills. Cancel before row 2. Once storage works again, Resume reloads the older checkpoint and sends row 1 twice—even without restarting.
   - **Why:** Successful progress calls `self.checkpoint.record_success(...)` (`tab_send.py:71`). Persistence failure is swallowed with only `self.logger.error(...)` (`checkpoint.py:166–167`). Resume reloads disk and replaces the completed list: `self.completed = checkpoint_data.get('completed_indices', [])` (`:313`).
   - **Severity:** HIGH.
   - **Confidence:** certain for the specified write failure; traced recording, atomic replacement, swallowed errors and disk-based recovery. No write failure or send was induced.
   - **Known gap:** new.
   - **Fix direction:** Propagate checkpoint failures and stop further sending with an explicit recovery state. Preserve known successful in-memory results instead of silently reverting to older disk state.

9. **Title:** Resume and Retry can discard unsent clients while completing the campaign.
   - **Where:** `ui/tab_send.py:628–629,667–696,723–800`; `data/checkpoint.py:81–101,195–201,239–243,284–292`; `core/outlook_sender.py:298–299,511–518`.
   - **What goes wrong:** Select five rows whose first three To cells are blank. Their failures stop the batch before the last two. Correct the addresses and refresh without changing row order. Resume sends only the last two, then announces success and hides recovery for the first three. Choosing Retry first replaces the checkpoint with the first three, losing recovery for the two never attempted.
   - **Why:** Resume excludes failures through `processed = completed | failed` (`checkpoint.py:290`). Completion uses only the latest worker’s failure count and calls `complete_session(success=True)` (`tab_send.py:724,733`); Retry is restored only under `if failed > 0:` (`:768`). Retry instead starts a new checkpoint containing only `retry_emails` (`:791–795`). Completed checkpoints are excluded from startup recovery (`checkpoint.py:243`), so closing after “Complete with Errors” also loses the Retry option.
   - **Severity:** HIGH.
   - **Confidence:** certain; traced both recovery branches and checkpoint initialization/completion. The triggering blank-address failures occur before Outlook calls.
   - **Known gap:** new.
   - **Fix direction:** Retain the original campaign’s completed, failed and unattempted sets through every recovery operation and restart. Finalize only when no unresolved recipients remain.

10. **Title:** Header offsets survive New Session and make Refresh drop clients from the next workbook.
    - **Where:** `ui/tab_excel.py:45–53,387,694–712,793–823`; `core/excel_handler.py:132,149–179`.
    - **What goes wrong:** Use header row 4 in campaign A, start New Session, then load B with headers in row 1 and four clients. B initially loads correctly. Refresh silently reuses row 4, treats B’s third client as headers, and leaves only its fourth client available for sending.
    - **Why:** Reset never resets the offset controls. Initial loading passes no offsets, but Refresh reads `current_row_offset = self.start_row_spin.value()` (`tab_excel.py:696`) and passes it into loading (`:709–712`). The reader uses `header_row_idx = start_row - 1` and reads only subsequent rows (`excel_handler.py:150,166`).
    - **Severity:** HIGH.
    - **Confidence:** certain; an extracted reader check changed the same four-client input from four recipients to one when the retained offset was applied.
    - **Known gap:** new.
    - **Fix direction:** Reset offsets for new campaigns and synchronize displayed offsets with the actual loaded data.

11. **Title:** Insert Variable can generate unsupported placeholders and falsely describe the email as static.
    - **Where:** `ui/tab_compose.py:300–308,335–353,365–369`; `ui/components/rich_text_editor.py:391–395`; `core/template_engine.py:28,90,139,263–280`.
    - **What goes wrong:** Load column `Tax: Payable` containing `5000`, then insert it through the app’s variable picker. `Tax due: {Tax: Payable}` is sent literally. With no other variables, the editor says “No variables used (static email).” This extends G31 to a correctly named, existing column that bypasses the warning.
    - **Why:** Insertion produces `f"{{{var_name}}}"` (`tab_compose.py:306`), but the parser is `re.compile(r'\{([^{}:;]+)\}')` (`template_engine.py:28`). Both substitution and variable discovery use that pattern (`:90,139`).
    - **Severity:** HIGH.
    - **Confidence:** certain; a pure regex check found no variable and left the generated placeholder unchanged.
    - **Known gap:** G31.
    - **Fix direction:** Make insertion and parsing support the same column names, or reject unsupported names before offering them.

12. **Title:** Failed template or profile overwrites can destroy the previously saved version.
    - **Where:** `ui/tab_compose.py:216–225`; `data/template_storage.py:103–112,178–192`; `ui/main_window.py:752–770`.
    - **What goes wrong:** Overwrite an existing template or profile, and a write fails after opening the destination—for example, storage fills while writing a large body. The previous saved version is already truncated. The error dialog does not recover it; malformed templates subsequently disappear from the list.
    - **Why:** Template saving directly uses `with open(template_path, 'w', encoding='utf-8')` followed by `json.dump(...)` (`template_storage.py:103–104`). Profile saving does the same (`main_window.py:755–756`). Error handlers report failure without restoring the previous contents.
    - **Severity:** HIGH.
    - **Confidence:** certain for a failure after truncation; checked write ordering and error paths without writing files.
    - **Known gap:** new.
    - **Fix direction:** Write and close a temporary file successfully before atomically replacing the existing template or profile.

13. **Title:** Autosave can erase the saved campaign while the restore question remains unanswered.
    - **Where:** `ui/main_window.py:56,324–329,494–507,568–614`; `ui/components/dialogs.py:71–75`; `data/session_manager.py:320–341`; `config.py:56`.
    - **What goes wrong:** Start with a saved campaign, leave Restore Previous Session unanswered for over three minutes, then choose Yes. If Qt delivers the autosave timer during the modal question, the empty startup state overwrites that campaign; Yes reloads it and reports “Session restored.”
    - **Why:** Autosave starts before restoration, with `AUTO_SAVE_INTERVAL = 180`. Its only pause predicate is `self.tab_send.is_sending` (`main_window.py:328`). The empty window still produces a nonempty dictionary that `_do_save()` saves (`session_manager.py:338–341`). After the question, restoration rereads disk: `state = self.session_manager.load_session()` (`main_window.py:611`).
    - **Severity:** HIGH.
    - **Confidence:** possible; the application-side path is confirmed, but Qt timer delivery during the modal dialog was not exercised.
    - **Known gap:** new.
    - **Fix direction:** Start autosave after the restore decision and load complete. Retain the originally loaded snapshot throughout the question.

14. **Title:** Account Refresh can change the sending account halfway through a batch.
    - **Where:** `ui/tab_send.py:209–210,412–419,602–629`; `core/outlook_sender.py:177–179,204–206,309–315`.
    - **What goes wrong:** Outlook lists Personal first and Office second. Select Office, start a batch, then click the still-enabled account Refresh button between sends. Subsequent emails request Personal instead of Office.
    - **Why:** Refresh calls `_load_accounts()`, which executes `self.selected_account = self.accounts[0]` (`outlook_sender.py:179`). Each send reads that mutable selection through `accounts.Item(self.selected_account.index)` (`:315`). Batch startup disables the account dropdown but leaves Refresh enabled.
    - **Severity:** MEDIUM.
    - **Confidence:** possible for the outgoing account; the state change and subsequent COM argument are certain, but Outlook behavior was not exercised.
    - **Known gap:** G7.
    - **Fix direction:** Freeze the chosen account into the batch configuration and preserve that choice during account refresh.

15. **Title:** Pasting a text table removes its blank top-left cell and mislabels financial columns.
    - **Where:** `ui/components/rich_text_editor.py:515–523,607–626`.
    - **What goes wrong:** Paste plain TSV containing `\tFY2025\tFY2026\nIncome\t100\t200\nTax\t10\t20\n`. The empty first heading disappears, placing FY2025 over row labels and FY2026 over FY2025 amounts.
    - **Why:** Conversion starts with `lines = text.strip().split('\n')` (`:607`), removing the leading tab. It then uses `cells = line.split('\t')` (`:613`) and generates the shortened header directly.
    - **Severity:** MEDIUM.
    - **Confidence:** certain; a pure string check reduced the header from three cells to two while subsequent rows retained three.
    - **Known gap:** new.
    - **Fix direction:** Preserve tabs and empty boundary cells; remove only appropriate trailing row delimiters.

16. **Title:** Changing the To mapping leaves a stale “All emails valid” result.
    - **Where:** `ui/tab_excel.py:234,486,611–620,649–686`; `ui/main_window.py:350–389`.
    - **What goes wrong:** Load valid addresses under Email and malformed addresses under AlternateEmail. After the initial green validation result, change To to AlternateEmail. The builder uses the malformed addresses while the success label and highlights still describe Email. Explicit validation opens an error dialog but leaves that success label unchanged.
    - **Why:** The mapping handler only obtains the mapping and calls `self.mapping_changed.emit(mapping)` (`tab_excel.py:658–659`). Persistent validation is calculated in `_populate_preview_table()` (`:611–620`); neither mapping changes nor `_validate_emails()` refresh it.
    - **Severity:** MEDIUM.
    - **Confidence:** certain; traced mapping connections, the window handler and both validation paths.
    - **Known gap:** new.
    - **Fix direction:** Recalculate validation and highlights whenever To changes and after explicit validation.

17. **Title:** Saving a template named “-- New Template --” makes it inaccessible through the UI.
    - **Where:** `ui/tab_compose.py:180–198,209–255,260–264`; `data/template_storage.py:73–104`.
    - **What goes wrong:** Enter `-- New Template --` in Save As. Saving succeeds, but Load clears the editor, Delete does nothing, and Save opens Save As again.
    - **Why:** Saved names are added alongside the identical special entry (`tab_compose.py:180–184`). Handlers identify that special entry solely by text: `if name == "-- New Template --":` (`:196,212,263`). Storage accepts and saves that name.
    - **Severity:** MEDIUM.
    - **Confidence:** certain; traced name acceptance, persistence and all relevant handlers.
    - **Known gap:** new.
    - **Fix direction:** Identify the special entry through item data rather than display text, or reject the reserved name.

Files read in full: `ui/__init__.py`, `ui/main_window.py`, `ui/tab_excel.py`, `ui/tab_compose.py`, `ui/tab_attachments.py`, `ui/tab_recipients.py`, `ui/tab_preview.py`, `ui/tab_send.py`, `ui/components/__init__.py`, `ui/components/dialogs.py`, `ui/components/file_list.py`, `ui/components/progress_log.py`, `ui/components/recipient_list.py`, `ui/components/rich_text_editor.py`, `ui/components/tab_navigation.py`, `ui/components/variable_completer.py`, `resources/style.qss`, `resources/style_dark.qss`, `tests/conftest.py`, `tests/test_attachment_matcher.py`, `tests/test_checkpoint.py`, `tests/test_compose_debounce.py`, `tests/test_excel_handler.py`, `tests/test_new_session_reset.py`, `tests/test_outlook_sender_attachments.py`, `tests/test_outlook_thread_safety.py`, `tests/test_persistence.py`, `tests/test_polish.py`, `tests/test_recipient_lists.py`, `tests/test_recipient_selection.py`, `tests/test_recipient_table.py`, `tests/test_send_batch.py`, `tests/test_send_ux.py`, `tests/test_tab_excel_async_load.py`, `tests/test_tab_excel_mapping.py`, `tests/test_tab_send_resume.py`, `tests/test_tab_send_startup.py`, `tests/test_tab_send_test_email.py`, `core/attachment_matcher.py`, `core/email_builder.py`, `core/excel_handler.py`, `core/outlook_sender.py`, `core/template_engine.py`, `data/checkpoint.py`, `data/recipient_lists.py`, `data/session_manager.py`, `data/template_storage.py`, `utils/file_utils.py`, `config.py`, `main.py`.  
Not examined: None in the assigned scope.

Codex session ID: 01a1d31f-7b09-70d3-a448-64372f639303
Resume in Codex: codex resume 01a1d31f-7b09-70d3-a448-64372f639303

## Job 3 — the flows across files, and every test

1. **Title:** Case-distinct column names can send to a different address from the one shown in Preview  
   **Where:** `core/email_builder.py:104-112,220-236,396-398`; `ui/tab_preview.py:365-372`; `core/outlook_sender.py:321`.  
   **What goes wrong:** A workbook has columns `Email`, `email`, and `PAN`. A row contains another person’s address under `Email` and the intended client’s address under `email`. Map To to lowercase `email`. Preview shows the intended client, but sending uses the other address, with that row’s personalised content and attachments.  
   **Why:** Preview uses the exact key: `row_data.get(self.email_column, "")` (`email_builder.py:397`). Building instead calls `_find_key()` (`:221`), which returns the **first** key satisfying `if k.lower() == key_lower: return k` (`:108-111`). The sender uses that result in `mail.To = "; ".join(email.to)` (`outlook_sender.py:321`). CC and BCC use the same ambiguous lookup.  
   **Severity:** HIGH  
   **Confidence:** certain — traced mapping, preview, construction, and sending; a pure dictionary example confirmed the differing addresses.  
   **Known gap:** new  
   **Fix direction:** Resolve the selected column exactly and share that resolution between preview and sending. Reject ambiguous case-insensitive fallback matches.

2. **Title:** Clearing Universal BCC can leave the former recipient receiving every client’s documents  
   **Where:** `ui/tab_compose.py:157-159,319-328`; `ui/main_window.py:391-399,447-452`; `core/email_builder.py:239-243`; `core/outlook_sender.py:326-327`.  
   **What goes wrong:** Set Universal BCC to adviser A, edit the subject, and let the debounce finish. Then clear BCC or replace it with adviser B without another subject/body edit. Start sending: adviser A remains in the built emails despite the field displaying blank or B.  
   **Why:** The BCC input has no change connection (`tab_compose.py:157-159`). The builder receives BCC only through `_on_template_changed()` (`main_window.py:397-399`). Before building, `flush_pending_changes()` propagates changes only `if self._change_timer.isActive()` (`tab_compose.py:326`). The stale value is appended with `bcc_list.append(self.universal_bcc)` (`email_builder.py:241`) and passed to Outlook.  
   **Severity:** HIGH  
   **Confidence:** certain — traced the input, debounce, builder state, and Outlook assignment.  
   **Known gap:** G4 — the additional consequence is disclosure to a former BCC recipient, beyond the documented missing records copy.  
   **Fix direction:** Connect BCC changes to state propagation and explicitly read its current value whenever emails are built.

3. **Title:** Switching attachment folders during a scan can attach files from the previous folder  
   **Where:** `ui/tab_attachments.py:265-300,303-315`; `core/attachment_matcher.py:57-61,81-95`; `utils/file_utils.py:286,308-313`.  
   **What goes wrong:** Start a slow scan of campaign folder A. While it runs, browse to folder B, whose clients reuse identifiers found in A. If A’s iterator continues after the switch, the interface displays B while the matcher contains paths from A. Emails for B can receive A’s documents.  
   **Why:** Browsing immediately calls `set_directory()` (`tab_attachments.py:269-272`), which replaces `self.directory`, clears `self.file_index`, and clears matches (`attachment_matcher.py:57-60`). The replacement scan then exits because `if self._scan_worker and self._scan_worker.isRunning(): return` (`tab_attachments.py:284-285`). The existing iterator retains A’s directory and keeps executing `self.file_index.append((full_path, filename, size))` (`attachment_matcher.py:86-91`). Completion has no folder/version check.  
   **Severity:** HIGH  
   **Confidence:** possible — the shared-state interleaving is supported by the code; worker timing was not exercised.  
   **Known gap:** G14 — this extends partial-result caching to mixing files from different campaign folders.  
   **Fix direction:** Give each scan an immutable directory and private result list. Publish results only if they still belong to the current folder request.

4. **Title:** Loading a profile during an Excel load can combine the new campaign’s content with the old campaign’s clients  
   **Where:** `ui/tab_excel.py:398-424,980-1004`; `ui/main_window.py:812-815,837-895`.  
   **What goes wrong:** Start loading a slow workbook A, then load profile B before A finishes. B contains a valid different workbook and valid attachments. B’s workbook request is silently discarded, while B’s subject, body, and attachments are applied. A subsequently supplies the recipients. Sending can therefore deliver B’s material to A’s clients despite “Profile loaded successfully!”  
   **Why:** `_start_load()` returns immediately when another load is running (`tab_excel.py:398-399`). Nevertheless, `load_file_path()` calls it and unconditionally `return True` (`:1003-1004`). `_apply_profile()` proceeds from that request to applying compose and attachment settings (`main_window.py:841-895`). The original completion still accepts its captured path and invokes its callback (`tab_excel.py:422-424`).  
   **Severity:** HIGH  
   **Confidence:** certain — traced the explicit busy branch and unconditional profile application; the triggering condition is an outstanding load.  
   **Known gap:** new  
   **Fix direction:** Apply a profile as one operation tied to its workbook-load result. Reject or queue the entire operation while another load is outstanding.

5. **Title:** Loading a profile while on Send leaves the previous campaign’s emails ready to send  
   **Where:** `ui/main_window.py:331-424,426-445,475-488,812-895`; `ui/tab_send.py:582-614`.  
   **What goes wrong:** Prepare campaign A and enter Send, creating its email queue. Load profile B through the menu while remaining on Send, and wait for all loading to finish. Start Sending still uses A’s previously built recipients, content, and attachments. If A was already sent, this can resend it while B receives nothing.  
   **Why:** Emails are rebuilt on entering tab 5: `elif index == 5: self._update_send_tab()` (`main_window.py:443-445`). That method calls `self.tab_send.set_emails(emails)` (`:488`). Profile application and the data/template/attachment handlers do not rebuild or invalidate this queue. Start later calls `_launch_send(self._emails)` (`tab_send.py:614`).  
   **Severity:** HIGH  
   **Confidence:** certain — traced every queue update and the profile-change callbacks.  
   **Known gap:** new  
   **Fix direction:** Invalidate prepared emails whenever campaign inputs change. At Start, build and freeze a current snapshot only after outstanding loads and scans finish.

6. **Title:** Restoring a session with no selected recipients selects everyone  
   **Where:** `ui/main_window.py:331-344,494-507,557-559`; `ui/tab_recipients.py:292-296`.  
   **What goes wrong:** Load a workbook, select none, save/close, then restore the session against the unchanged workbook. Every row becomes selected, so a subsequent batch includes clients explicitly excluded before saving.  
   **Why:** Loading data defaults to `self.recipient_list.select_all()` (`tab_recipients.py:296`). Restoration then reads `selected = state.get('selected_recipients', [])` but applies it only `if selected:` (`main_window.py:557-559`). A deliberately saved empty list therefore leaves the select-all default intact.  
   **Severity:** HIGH  
   **Confidence:** certain — traced load-before-selection restoration and confirmed the empty-list branch with pure logic.  
   **Known gap:** new  
   **Fix direction:** Distinguish a missing selection field from an explicitly empty selection, and apply the empty list.

7. **Title:** Loading a saved recipient list silently adds unticked rows sharing an email address  
   **Where:** `ui/tab_recipients.py:139-168,213-224`; `data/recipient_lists.py:173-189`.  
   **What goes wrong:** Two rows represent different notices or clients using one shared address. Select only the first and save that recipient list. Reloading it against the unchanged workbook selects both rows, introducing an unwanted second email and its attachments.  
   **Why:** Saving extracts addresses only from `self.recipient_list.get_selected_data()` (`tab_recipients.py:219`). Resolution groups all current rows using `email_rows.setdefault(key, []).append(idx)` (`recipient_lists.py:177`), then selects every match through `indices.extend(rows)` (`:185`). The UI applies those expanded indices (`tab_recipients.py:168`).  
   **Severity:** HIGH  
   **Confidence:** certain — the extracted pure resolver returned indices `[0, 1]`, without an ambiguity warning, for a list saved from only row 0.  
   **Known gap:** G9 — the additional consequence is that loading the list itself selects the duplicate-address row.  
   **Fix direction:** Save a stable client/row identifier alongside the address. Treat multiple address matches as ambiguous instead of selecting all of them.

8. **Title:** Failed checkpoint writes allow successful emails to be sent again by Resume  
   **Where:** `data/checkpoint.py:101-118,139-167,219-230,301-318`; `ui/tab_send.py:65-73,609-614`.  
   **What goes wrong:** The initial checkpoint saves, but progress writes subsequently fail—for example, because the disk fills. Emails continue to send and appear successful. Cancel before any later successful write, then Resume: the disk checkpoint still treats those clients as pending, so they can receive duplicates.  
   **Why:** `_save_checkpoint()` catches exceptions and only logs them (`checkpoint.py:166-167`). Start proceeds after checkpoint creation (`tab_send.py:609-614`), and per-email progress is emitted before `record_success()` (`:67-71`). Suspension does not retry persistence (`checkpoint.py:219-230`), while resume reloads the on-disk state (`:301-318`).  
   **Severity:** HIGH  
   **Confidence:** certain — traced persistence failure handling, cancellation, and disk-based recovery; no failure was induced.  
   **Known gap:** new  
   **Fix direction:** Require durable checkpoint creation before sending. If recording an outcome fails, stop further sends and expose the uncertain outcome for reconciliation before recovery.

9. **Title:** Retry Failed discards clients that the interrupted batch never attempted  
   **Where:** `ui/tab_send.py:728-800`; `data/checkpoint.py:81-101`.  
   **What goes wrong:** Start a ten-client batch. The first three fail and trigger the circuit breaker, leaving clients 4–10 unattempted. Repair the problem and choose Retry Failed. After the first three succeed, the app reports completion and no longer offers recovery for clients 4–10.  
   **Why:** The interrupted batch exposes both Resume and Retry (`tab_send.py:752,773`). Retry calls `start_session([e.row_index for e in retry_emails], ...)` (`:792-795`). That replaces the original plan and clears its completed/failed state (`checkpoint.py:81-101`). Successful retry completion then calls `complete_session(success=True)` (`tab_send.py:733`).  
   **Severity:** HIGH  
   **Confidence:** certain — traced circuit-breaker completion, retry selection, and checkpoint replacement.  
   **Known gap:** new  
   **Fix direction:** Retry within the existing campaign checkpoint. Preserve never-attempted recipients until each has an explicit outcome.

10. **Title:** Resume completes the campaign after sending only a subset of its pending clients  
    **Where:** `ui/tab_send.py:667-696,728-757`; `data/checkpoint.py:191-201`.  
    **What goes wrong:** Cancel with B and C pending. Leave only B ticked in Recipients, return to Send, and Resume. B is sent, the checkpoint is marked completed, and success is shown. C remains unsent and is no longer recoverable through Resume.  
    **Why:** Resume takes the intersection: `resume_emails = [e for e in self._emails if e.row_index in remaining_set]` (`tab_send.py:678`). It rejects only an entirely empty intersection (`:680`). Successful completion unconditionally calls `complete_session(success=True)` (`:733`), which sets `checkpoint_data['status'] = 'completed'` (`checkpoint.py:197`) without checking remaining planned rows.  
    **Severity:** HIGH  
    **Confidence:** certain — traced the partial-match acceptance and campaign finalization.  
    **Known gap:** G1 — this loses pending clients even with the same workbook and unchanged row identities.  
    **Fix direction:** Require every pending recipient to resolve, or retain unresolved recipients as pending and prevent campaign completion.

11. **Title:** A successful Resume hides earlier failures and removes their Retry action  
    **Where:** `data/checkpoint.py:288-292,313-318`; `ui/tab_send.py:628,723-773`.  
    **What goes wrong:** Three clients fail and abort a larger batch. Fix the problem and Resume. The remaining clients succeed, but the original three are never retried. The window reports zero failures, hides Retry, and closes the checkpoint.  
    **Why:** Pending rows exclude both successes and failures: `processed = completed | failed` (`checkpoint.py:290`). Launching the resumed segment hides Retry (`tab_send.py:628`). Completion uses only that segment’s `failed = results.get('failed', 0)` (`:724`), finalizes the campaign (`:733`), and shows Retry only `if failed > 0:` (`:768`). Persisted earlier failures do not control these decisions.  
    **Severity:** HIGH  
    **Confidence:** certain — traced restored failures, pending selection, result totals, and button visibility.  
    **Known gap:** new  
    **Fix direction:** Calculate completion, failure totals, and recovery actions from cumulative campaign state, including failures from previous segments.

12. **Title:** HTML source edits are ignored by saving and sending, and old source survives New Session  
    **Where:** `ui/components/rich_text_editor.py:397-414,432-448,468-470`; `ui/tab_compose.py:193-220,288-298`.  
    **What goes wrong:** Edit the body in View HTML, leave that pane open, and save a template or proceed to sending: the old visual-editor body is used. Alternatively, open campaign A’s source, start New Session or load B’s template, then click Hide HTML: A’s retained source overwrites the new body.  
    **Why:** Opening source copies `self.editor.toHtml()` into `source_view` (`rich_text_editor.py:403-404`). Only hiding it commits `self.source_view.toPlainText()` through `self.editor.setHtml(html)` (`:410-411`). Meanwhile, `get_html()` always returns `self.editor.toHtml()` (`:448`); `set_html()` and `clear()` update only the visual editor (`:439,470`).  
    **Severity:** HIGH  
    **Confidence:** certain — traced both buffers through compose reads, template operations, and reset.  
    **Known gap:** new  
    **Fix direction:** Synchronize the active editing buffer before reads. Loading or clearing content must replace both buffers and reset source-view state.

13. **Title:** Header offsets survive New Session and can make Refresh silently drop clients from the next workbook  
    **Where:** `ui/tab_excel.py:386-387,694-715,793-823`; `core/excel_handler.py:117,132-166`.  
    **What goes wrong:** Campaign A uses header row 3. Start New Session and open B, whose header is row 1. B initially loads correctly, but the offset control still contains 3. Refresh now treats B’s second client row as its header and omits its first two clients. With email addresses in the first column and a fixed body, the remaining clients can still be sent normally.  
    **Why:** New-file loading passes no offsets (`tab_excel.py:387`), using the handler’s defaults. `reset()` clears rows and mappings but never resets the offset controls (`:793-823`). Refresh reads `current_row_offset = self.start_row_spin.value()` (`:696`) and passes it into the worker (`:708-711`); the handler uses that row as the header.  
    **Severity:** HIGH  
    **Confidence:** certain — traced initial loading, reset, refresh, and header/data slicing.  
    **Known gap:** G23 — the additional consequence is live offset leakage between campaigns, without saving or restoring a session.  
    **Fix direction:** Reset offsets for a new workbook/New Session, and keep the displayed offsets synchronized with those actually used to load the data.

14. **Title:** Failed overwrites can destroy saved templates, profiles, and preferences  
    **Where:** `data/template_storage.py:103-112,178-192`; `ui/main_window.py:755-770`; `utils/theme_manager.py:64-75`; `utils/file_utils.py:32-54`.  
    **What goes wrong:** Overwrite an existing template/profile, or change the theme, and encounter a disk-full error or process termination after truncation. The previous saved data is destroyed. Damaged templates disappear from listing; damaged preferences revert to defaults and can subsequently be replaced with only one newly saved setting.  
    **Why:** Templates use `with open(template_path, 'w', encoding='utf-8')` followed by `json.dump(...)` (`template_storage.py:103-104`). Profiles do the same (`main_window.py:755-756`). Theme saving directly opens the shared preferences file with `'w'` (`theme_manager.py:72-73`). Error paths provide no rollback; preference reads swallow errors and return defaults (`file_utils.py:36-39`).  
    **Severity:** HIGH  
    **Confidence:** certain — traced destructive write modes and subsequent read/error paths; no filesystem fault was induced.  
    **Known gap:** new  
    **Fix direction:** Use the existing atomic JSON writer for all three. Preserve and report malformed preference data instead of silently replacing it.

15. **Title:** Auto-save can overwrite the previous session while the restore question is unanswered  
    **Where:** `ui/main_window.py:324-329,494-507,568-613`; `data/session_manager.py:320-341`; `ui/components/dialogs.py:74`; `config.py:56`.  
    **What goes wrong:** Launch with a saved campaign and leave Restore Previous Session unanswered for more than three minutes. If Qt dispatches the timer during the modal question, auto-save replaces that campaign with the new window’s empty state. Clicking Yes then restores the overwritten file.  
    **Why:** Auto-save pauses only for sending: `set_pause_check(self.tab_send.is_sending)` (`main_window.py:328`). Its timer saves the current populated state dictionary through `if state: self.session_manager.save_session(state)` (`session_manager.py:339-341`). The restore code reads the original snapshot before prompting, then calls `load_session()` again after Yes (`main_window.py:568,611`). The interval is `AUTO_SAVE_INTERVAL = 180` (`config.py:56`).  
    **Severity:** HIGH  
    **Confidence:** possible — the overwrite/reload path is established; timer dispatch inside the modal Qt event loop was not exercised.  
    **Known gap:** new  
    **Fix direction:** Pause auto-save until restoration is decided and finished. Restore the snapshot already read for the question.

16. **Title:** An outstanding Excel load can repopulate a supposedly cleared New Session  
    **Where:** `ui/main_window.py:625-639`; `ui/tab_excel.py:405-424,473-489,793-798`; `core/excel_handler.py:105-117`.  
    **What goes wrong:** Start a slow workbook load and choose New Session while the worker is still opening it. After the interface reports the new session, the old load can finish and repopulate the old campaign’s rows, selecting them again.  
    **Why:** Reset calls `self.excel_handler.close()` and clears local data (`tab_excel.py:795-798`), but does not cancel or invalidate the worker. The worker can subsequently assign the opened workbook (`excel_handler.py:105`). Its connected callback unconditionally accepts the old `file_path` and invokes `on_success()` (`tab_excel.py:408-424`), eventually emitting `data_loaded` (`:489`).  
    **Severity:** MEDIUM  
    **Confidence:** possible — traced the shared handler and unguarded completion; the particular worker/reset interleaving was not run.  
    **Known gap:** new  
    **Fix direction:** Invalidate outstanding load generations on reset and ignore stale completions. Avoid having a reset window and a worker mutate the same handler.

17. **Title:** Removing a matched attachment changes the display but does not exclude it from sending  
    **Where:** `ui/components/file_list.py:62-63,144-167,193-196,392-429`; `ui/tab_attachments.py:114,236-237,387`.  
    **What goes wrong:** Test an identifier, right-click a matched document, and choose Remove. The document disappears from the results, but sending still obtains it from the unchanged matcher. Dropping a file into that results list likewise changes only the display.  
    **Why:** `MatchedFileListWidget` supplies `show_add_remove=False` (`file_list.py:397`), hiding buttons only. The base widget still accepts drops and connects the context-menu Remove action (`:63,195`). Removal changes its private `_files` list and emits `files_changed` (`:159-167`). The matched-results instance has no consumer for that signal; the connection at `tab_attachments.py:114` belongs to static attachments.  
    **Severity:** MEDIUM  
    **Confidence:** certain — traced inheritance, mutations, and every matched-list connection.  
    **Known gap:** new  
    **Fix direction:** Make match results read-only, including context menus and drops, or implement exclusions respected by email construction.

18. **Title:** Refresh can change the sending account halfway through a batch  
    **Where:** `ui/tab_send.py:209-210,412-419,621-629`; `core/outlook_sender.py:159-179,197-209,309-318`.  
    **What goes wrong:** Configure two Outlook accounts, choose the second, start a batch, and click the still-enabled Refresh button between emails. Later emails can use the first account instead.  
    **Why:** Starting disables `account_combo` but not `refresh_accounts_btn` (`tab_send.py:623-629`). Refresh calls `refresh_accounts()` (`:418`), which reloads accounts and assigns `self.selected_account = self.accounts[0]` (`outlook_sender.py:179,206`). Each email independently reads the mutable selection through `accounts.Item(self.selected_account.index)` (`:315`).  
    **Severity:** MEDIUM  
    **Confidence:** possible — the account mutation and per-email lookup are certain; the resulting Outlook From identity was not exercised.  
    **Known gap:** new  
    **Fix direction:** Freeze the chosen account identity for the batch. Preserve identity during refresh and prevent refresh from changing an active batch.

19. **Title:** Word import can silently omit tables containing the notice’s substantive content  
    **Where:** `ui/tab_compose.py:466-467,476-496,502-514`.  
    **What goes wrong:** Import a Word document with an introductory paragraph followed by a table of tax amounts or instructions, and choose Replace. The paragraph is imported, the table is omitted, and “Content imported” is reported.  
    **Why:** `_read_docx()` constructs the entire result with `for para in doc.paragraphs:` and `html_parts.append(f'<p>{para.text}</p>')` (`tab_compose.py:510-512`). There is no table traversal. The nonempty result is installed and reported as successful (`:488,494-496`).  
    **Severity:** MEDIUM  
    **Confidence:** possible — the complete import path was read; the consequence depends on python-docx’s separation of document paragraphs from table-cell paragraphs, which was not exercised.  
    **Known gap:** new  
    **Fix direction:** Traverse paragraphs and tables in document order. Warn about unsupported content before replacing the existing body.

20. **Title:** Inline-image preparation failures still produce a successful send  
    **Where:** `core/outlook_sender.py:332-338,358-364,407-434`.  
    **What goes wrong:** Compose a body containing an important embedded screenshot. If decoding, temporary-file writing, attaching the image, or assigning its CID fails, the email is still sent and recorded as successful. The image may be unusable, with no Retry Failed entry.  
    **Why:** Image preparation includes `mail.Attachments.Add(temp_path)` and CID assignment (`outlook_sender.py:413-417`), but its exception handler only logs `Could not embed image` (`:431-432`). It returns the body anyway (`:434`); the caller sets HTMLBody, calls `mail.Send()`, and returns success (`:335-338,363-364`).  
    **Severity:** MEDIUM  
    **Confidence:** possible — swallowed errors and success reporting are certain; whether the unconverted image remains renderable depends on Outlook.  
    **Known gap:** new  
    **Fix direction:** Propagate required-image preparation failures and block the affected email. Clean up temporary files in a `finally` block.

21. **Title:** Inline-image conversion removes dimensions and other attributes shown in Preview  
    **Where:** `core/outlook_sender.py:419-423`; `ui/components/rich_text_editor.py:741-769`.  
    **What goes wrong:** Use a base64 image whose HTML specifies a reduced width, height, or styling. Preview uses that HTML, but the outgoing CID conversion deletes those attributes, potentially displaying a large image at a different size or layout.  
    **Why:** Conversion constructs `cid_tag = f'<img src="cid:{cid}" />'` and replaces the entire `original_tag` (`outlook_sender.py:422-423`). This discards every original attribute except the replacement source, including dimensions, style, and alternative text.  
    **Severity:** MEDIUM  
    **Confidence:** possible — attribute deletion is certain from the replacement; visible impact depends on retained editor HTML and Outlook rendering.  
    **Known gap:** new  
    **Fix direction:** Replace only the image’s `src` value while preserving the remaining attributes.

22. **Title:** Pasting TSV with an empty first cell shifts the heading into the wrong column  
    **Where:** `ui/components/rich_text_editor.py:515-523,607-626`.  
    **What goes wrong:** Paste plain TSV `\tTax\nClient A\t100`, with no HTML clipboard format, using Paste Table. The empty first heading disappears, placing “Tax” above the client-name column instead of the amount column.  
    **Why:** Conversion starts with `lines = text.strip().split('\n')` (`rich_text_editor.py:607`). `strip()` removes the leading tab before `cells = line.split('\t')` (`:613`), permanently deleting that first empty cell.  
    **Severity:** MEDIUM  
    **Confidence:** certain — the extracted pure conversion function produced rows `[['Tax'], ['Client A', '100']]`.  
    **Known gap:** new  
    **Fix direction:** Preserve tab delimiters and remove only terminal line endings. Use delimiter-aware parsing where quoted cells are supported.

23. **Title:** Subject autocomplete can move the cursor backwards after inserting a variable  
    **Where:** `ui/components/variable_completer.py:156,201-220,242-258`; `ui/tab_compose.py:123-124`.  
    **What goes wrong:** Type `Reminder {`, accept `Name`, and continue typing. With synchronous change-signal delivery, the text becomes `Reminder {Name} ` but the cursor moves to position 6 instead of 16, so subsequent typing edits the prefix.  
    **Why:** Insertion calls `self.line_edit.setText(new_text)` (`variable_completer.py:255`). The connected `textChanged` handler (`:156`) sees the closing brace and sets `self._trigger_pos = -1` (`:212-214`). Insertion then calculates the cursor from that changed field: `setCursorPosition(self._trigger_pos + len(var_name) + 3)` (`:256`).  
    **Severity:** MEDIUM  
    **Confidence:** possible — extracted method bodies with a synchronous fake control reproduced position 6; actual Qt signal sequencing was not exercised.  
    **Known gap:** new  
    **Fix direction:** Capture the insertion position locally before changing the control, or block the completer callback during insertion.

24. **Title:** The atomic-save test passes for a non-atomic implementation  
    **Where:** `tests/test_persistence.py:19-26`; `data/session_manager.py:60-66`; `utils/file_utils.py:25-29`.  
    **What goes wrong:** Replace atomic session persistence with a direct destination overwrite. The test still passes, although an interrupted overwrite can destroy an existing saved session.  
    **Why:** The test saves a new file, reads its content, and checks `list(tmp_path.glob("*.tmp")) == []` (`test_persistence.py:20-26`). Direct writing produces all those observations. The production atomicity distinction is writing the temporary file before `os.replace(tmp_path, path)` (`file_utils.py:27-29`), which the assertions never distinguish.  
    **Severity:** MEDIUM  
    **Confidence:** certain — compared the asserted observations with atomic and direct-write behavior; no files were written.  
    **Known gap:** new  
    **Fix direction:** Seed an existing session, inject failure while writing or replacing its successor, and verify that the original remains intact.

25. **Title:** The sleep-slicing test cancels before any sleep and cannot verify interruption during the interval  
    **Where:** `tests/test_send_batch.py:27-46`; `core/outlook_sender.py:507-523,534-542`.  
    **What goes wrong:** A regression that checks cancellation once before an uninterruptible 30-second sleep would pass this test. Users cancelling after sleep begins would still wait the entire interval.  
    **Why:** The progress callback sets `cancelled["flag"] = True` (`test_send_batch.py:32-33`). It runs before `_interruptible_sleep()` (`outlook_sender.py:508-509,523`). Consequently, sleep returns at its first cancellation check (`:538-539`) without exercising any slice. The elapsed-time assertion nevertheless diagnoses failure as `"sleep is not sliced"` (`test_send_batch.py:46`).  
    **Severity:** MEDIUM  
    **Confidence:** certain — traced synchronous callback ordering and the sleep entry condition.  
    **Known gap:** new  
    **Fix direction:** Arrange cancellation after sleeping begins using controlled sleep/clock behavior or synchronization, then assert prompt exit.

26. **Title:** The OR-default test passes even if default restoration is removed  
    **Where:** `tests/test_tab_excel_mapping.py:16-25,47-50`; `ui/tab_excel.py:303-304,747-750`.  
    **What goes wrong:** Remove the restoration branch that resets an omitted identifier logic to OR. The test remains green, although loading an older mapping after an AND campaign would retain AND.  
    **Why:** Construction already executes `self.logic_or_radio.setChecked(True)` (`tab_excel.py:304`). The test immediately loads a mapping without `identifier_logic` and asserts the result is `"OR"` (`test_tab_excel_mapping.py:48-50`). Therefore, deleting the fallback at `tab_excel.py:749-750` does not change its observed state.  
    **Severity:** MEDIUM  
    **Confidence:** certain — traced fixture initialization and the restoration branch.  
    **Known gap:** new  
    **Fix direction:** First set and verify AND, then restore a mapping without the logic field and assert OR.

27. **Title:** A queued test-email completion can escape its patches and hang a later test  
    **Where:** `tests/test_tab_send_test_email.py:18-45,88-118`; `tests/conftest.py:17-23,31-37`; `ui/tab_send.py:141-148,565-576`; `ui/components/dialogs.py:26`.  
    **What goes wrong:** Run the off-UI-thread test before another test that processes Qt events. The first test can finish with its GUI result still queued. After its dialog patches are removed, later event processing can display a real offscreen “Test Sent” modal and hang the suite.  
    **Why:** The test waits using `assert worker.wait(5000)` and then ends without waiting for the GUI completion (`test_tab_send_test_email.py:111-118`). Its fixture merely `return t` (`:45`). The worker emits `finished_with_result` (`tab_send.py:148`); its connected handler calls `show_info(...)` (`:566,576`), whose real implementation opens `QMessageBox.information(...)` (`dialogs.py:26`). The QApplication is shared.  
    **Severity:** MEDIUM  
    **Confidence:** possible — traced queued completion and fixture teardown; occurrence depends on PyQt receiver lifetime and event delivery.  
    **Known gap:** new  
    **Fix direction:** Wait for both worker termination and GUI completion while patches remain installed. Explicitly dispose of the tab and pending work during teardown.

28. **Title:** The reconnect test treats a result signal as proof that its worker has terminated  
    **Where:** `tests/test_tab_send_startup.py:76-96`; `ui/tab_send.py:109-128,370-383,412-416`.  
    **What goes wrong:** The GUI processes the initialization-failure signal while its worker is still finishing. The test immediately requests reconnect, which is discarded by the running-worker guard, producing an intermittent timeout.  
    **Why:** The test comments `"worker done, UI updated"` but waits only for `"Refresh" in tab.online_label.text()` (`test_tab_send_startup.py:83-85`). The worker emits `self.done.emit(...)` before returning (`tab_send.py:128`). Reconnect reaches `if self._init_worker.isRunning(): return` (`:374-375`), with no deferred retry.  
    **Severity:** LOW  
    **Confidence:** possible — traced the signal-before-return ordering and guard; actual occurrence depends on Qt scheduling.  
    **Known gap:** new  
    **Fix direction:** Wait for both the failure UI and worker termination before reconnecting, and join outstanding workers during teardown.

Files read in full: `main.py`, `config.py`, `requirements.txt`; `core/__init__.py`, `core/validators.py`, `core/excel_handler.py`, `core/template_engine.py`, `core/attachment_matcher.py`, `core/email_builder.py`, `core/outlook_sender.py`; `data/__init__.py`, `data/session_manager.py`, `data/checkpoint.py`, `data/template_storage.py`, `data/recipient_lists.py`; `ui/__init__.py`, `ui/main_window.py`, `ui/tab_excel.py`, `ui/tab_compose.py`, `ui/tab_attachments.py`, `ui/tab_recipients.py`, `ui/tab_preview.py`, `ui/tab_send.py`; `ui/components/__init__.py`, `ui/components/dialogs.py`, `ui/components/file_list.py`, `ui/components/progress_log.py`, `ui/components/recipient_list.py`, `ui/components/rich_text_editor.py`, `ui/components/tab_navigation.py`, `ui/components/variable_completer.py`; `utils/__init__.py`, `utils/logger.py`, `utils/file_utils.py`, `utils/html_converter.py`, `utils/theme_manager.py`; `resources/style.qss`, `resources/style_dark.qss`; `tests/conftest.py`, `tests/test_attachment_matcher.py`, `tests/test_checkpoint.py`, `tests/test_compose_debounce.py`, `tests/test_excel_handler.py`, `tests/test_new_session_reset.py`, `tests/test_outlook_sender_attachments.py`, `tests/test_outlook_thread_safety.py`, `tests/test_persistence.py`, `tests/test_polish.py`, `tests/test_recipient_lists.py`, `tests/test_recipient_selection.py`, `tests/test_recipient_table.py`, `tests/test_send_batch.py`, `tests/test_send_ux.py`, `tests/test_tab_excel_async_load.py`, `tests/test_tab_excel_mapping.py`, `tests/test_tab_send_resume.py`, `tests/test_tab_send_startup.py`, `tests/test_tab_send_test_email.py`.  
Not examined: No requested source or test file remains unfinished. `.build-docs/PROJECT_AUDIT_advanced_email_tool.md` Section 7 was read first and in full; the rest of that document was not reviewed in full.

Codex session ID: 01a1d31f-8f74-7c83-b482-ebac8565a77d
Resume in Codex: codex resume 01a1d31f-8f74-7c83-b482-ebac8565a77d
