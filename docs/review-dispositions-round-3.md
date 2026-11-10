# Review dispositions — DESIGN lane, round 3 (final review; closes are author-side, unverified)

Records: requirements (0 must / 3 could), architecture (0 / 1), design-principles (0 / 3), design (1 / 1), system-test (2 / 2).
All round-1 and round-2 keys verified closed by all five lenses. Every rewrite below is applied verbatim from the record's
Rewrite column; no `disagree` rows. SDD = fprime-rust `docs/sdd.md`; plan = fprime-rust-reference
`FprimeRustReference/ReferenceDeployment/test/int/plan.json`.

| Finding key | Disposition | Where |
|---|---|---|
| design-fault-handling-gap:fprime-rust sdd/internal-port-hook-self-lock | fixed (must) | SDD §Behavior per-kind exception: "Overflow hooks of **internal ports** take no lock on either kind: their only caller is the instance's own handler, which holds the mutex."; UT-SHIM-9 extended: "an internal port with `hook` invoked from a handler on a full queue calls the Rust hook without re-locking" |
| final-state:helper-record-path | fixed (must) | `planted_faults.py` `prmdb_record_equals`: `f = ctx.record.path / "raw" / path`; `hasattr` branch dropped; `path` relative to record/raw; elicitation N-5 withdrawn in `docs/review-dispositions-round-2.md` |
| final-state:helper-absent-unverified | fixed (must) | absent file → `(False, f"{path} absent from record/raw — no file was downlinked", [], False)`; no UNVERIFIED branch; docstring updated; `threshold_not_saved.mechanism` "reports FAIL"; `faults-menu.json` regenerated; plan `final_state.rationale` updated |
| req-unclear:REQ-FprimeRust-034 | fixed | "A missing or empty `fpp-cache/stdout.txt`, or one listing a nonexistent file, shall fail generation naming the cache path." |
| req-unclear:REQ-RustMonitor-005 | fixed | "Each `run` shall deliver every queued count and command to its handler, then increment and publish `RunCount` and publish `Limit`." |
| req-set-gap:"struct/array/abstract as channel or parameter type" | fixed (anchor confirms the class reading) | rejected row: "struct, array or abstract type (e.g. `Fw.Buffer`, `Fw.ComBuffer`) used as an argument, return, channel or parameter type" |
| design-code-mismatch:RustMonitor sdd/drop-not-counted | fixed | RustMonitor SDD §Configure: "dropped without report (F Prime counts it in `getNumMsgsDropped()` but emits nothing) … a flight monitor would publish `ctx.num_msgs_dropped()` each run or use `hook` with a dropped-count channel" |
| jpl:DR-4.4.6.1:sdd.drop-counter | fixed | same sentence; SDD name-table row `dropped-message count (queued/active)` → `getNumMsgsDropped()` / `num_msgs_dropped` / `ctx.num_msgs_dropped() -> FwSizeType` |
| jpl:DR-4.11.4.13:sdd.parameter_updated-thread | fixed | SDD §Behavior after the hook sentence: "`parameter_updated` runs on the command caller's thread … and at start-up on the loading thread, under the instance mutex; it must not block and must not assume the component thread."; RustCounter §Behavior: "All port and command handlers run on the component's thread; `parameter_updated` (default no-op) would run on the command caller's thread." |
| arch-undocumented-departure:sdd.md §Behavior/queued-drain-every-sync-entry | fixed | SDD §Behavior queued-dispatch paragraph: departure stated; "Give a queued Rust component exactly one sync/guarded input (its `run`) …; declare other inputs `async`"; cookiecutter `queued` template comment named as DEVELOPMENT |
| jpl:DR-4.11.1.1.1:sdd.queued-drain-every-sync | fixed | same paragraph (reviewer's text verbatim: "Departure from F Prime: on a Rust queued component every sync/guarded input drains the queue, not only the scheduler port; queued handlers therefore run on whichever thread calls any sync/guarded port, in call order.") |
| final-state:helper-crc-not-checked | fixed (CRC checked, anchor preference) | helper verifies `zlib.crc32(data[4:]) & 0xFFFFFFFF == struct.unpack(">I", data[:4])[0]` before parsing records; FAIL names stored/computed values |
| traceability:sdd-concat-submodule-path | fixed | plan decision log 10 precondition: `lib/fprime-rust` checked out at the fprime-rust `campaign/design` DESIGN head (committed submodule pin still JPL-Devin until decision 14) |

## Gate record (round 3; no `.fpp` changed, fpp-check not re-run — last clean run on the full closure at b188d185 in round 2)

- `fth verify-plan plan.json`: plan ok — 11 tests, 3 helpers, 7 planted faults, 30 waived requirements, 3 warnings (single covering test on REQ-RustMonitor-001/-002/-004, each with a `waiver`).
- Decision-log-10 command: `requirements ok: 52 plan requirement ids all in the SDD table (52 rows) of /tmp/sdd-concat.md`.
- `fth render-plan` / `fth planted-faults-menu`: byte-identical to the committed `plan.md` / `faults-menu.json`.
- `fth render-sdd-tests --check`: Tests table agrees with the plan (11 tests) for all four SDDs.

New elicitation findings: none.
