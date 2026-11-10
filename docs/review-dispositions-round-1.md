# Review dispositions — DESIGN lane, round 1

Author: DESIGN-lane author child (lestarch-autobot). Records: requirements (25/23), design (5/11), architecture (3/10),
design-principles (3/14), system-test Mode A (9/7). Dispositions: `fixed` (where), `disagree` (reason; reviewer re-reviews),
`deferred-to-DEVELOPMENT` (only where the record says so). Anchor rulings of round 1 are applied as stated in the fix pass.
SDD = fprime-rust `docs/sdd.md`; plan = fprime-rust-reference `FprimeRustReference/ReferenceDeployment/test/int/plan.json`.

| Finding key | Disposition | Where / reason |
|---|---|---|
| req-no-verification:REQ-FprimeRust-008 | fixed | SDD REQ-008 reworded ("of kind active, queued or passive shall dispatch its handlers to Rust"); `Unit Test; Integration Test: L2-1, L2-4, L2-5`; UT-SHIM-5 (one fixture per kind), UT-SHIM-6 (queued dispatch) |
| req-no-verification:REQ-FprimeRust-009 | fixed | REQ-009 `Unit Test; Integration Test`; UT-SHIM-2 names sync, guarded and async fixtures |
| req-not-verifiable:REQ-FprimeRust-011 | fixed | REQ-011 reworded with the observable ("reach the Rust handler … reach the C++ handler, with arguments unchanged") |
| req-no-verification:REQ-FprimeRust-012 | fixed | REQ-012 `Unit Test; Integration Test`; UT-SHIM-1 names async/sync/guarded commands and the two responses |
| req-no-verification:REQ-FprimeRust-013 | fixed | REQ-013 `Unit Test; Integration Test`; UT-SHIM-7 one event per severity, FATAL under the death-test fixture |
| req-not-verifiable:REQ-FprimeRust-015 | fixed | split: REQ-015 (read with validity) and REQ-030 (parameter-updated handler invoked with the id) |
| req-no-verification:REQ-FprimeRust-015 | fixed | REQ-015 `Unit Test; Integration Test: L2-2, L5-1`; UT-SHIM-8 (VALID/DEFAULT/INVALID), UT-SHIM-4 (parameterUpdated) |
| req-not-verifiable:REQ-FprimeRust-017 | fixed (anchor ruling) | rejected-element table after the requirements list (serial port, state-machine instance, data-product container/port, struct/array/`Fw.Buffer` argument or return); REQ-017 points at it; internal ports (REQ-031), overflow hooks (REQ-032), port return values (REQ-033) supported |
| req-contains-design:REQ-FprimeRust-019 | fixed | row deleted; the workspace stays in §Design "Linkage" |
| req-set-inconsistent:REQ-FprimeRust-029+012..015 | fixed | row deleted; plan tests re-pointed at REQ-012..015 and component rows |
| req-no-rationale:REQ-FprimeRust-005 | fixed | plan `requirements[REQ-FprimeRust-005].rationale` ("E1/R1: … generated C++ class over the autocoded base") |
| req-no-rationale:REQ-FprimeRust-006 | fixed | plan rationale ("R1 / parent REQ-FprimeRust-026 …") |
| req-no-rationale:REQ-FprimeRust-016 | fixed | plan rationale ("E1: type set of the MVP; R1 …") |
| req-no-rationale:REQ-FprimeRust-025 | fixed | plan rationale ("RS-2 lifecycle …") |
| req-no-rationale:REQ-FprimeRust-028 | fixed | plan rationale ("parent REQ-FprimeRust-022 …") |
| req-no-rationale:REQ-RustCounter-001..006 | fixed | plan `requirements[REQ-RustCounter-*].rationale` naming the fprime-rust rows each exercises (anchor E-2) |
| req-no-rationale:REQ-RustMonitor-001..005 | fixed | plan `requirements[REQ-RustMonitor-*].rationale` |
| req-no-rationale:REQ-Relay-001..002 | fixed | plan `requirements[REQ-Relay-*].rationale` |
| req-set-gap:"match fprime-python" | fixed (anchor ruling) | REQ-031/-032/-033 rows + name-table rows (internal port, `hook`); rejected-by-name table; strings REQ-037/-038 |
| req-set-no-fault-coverage:fpp-cache/missing-or-empty | fixed | REQ-034; UT-AC-2 |
| req-set-no-fault-coverage:cargo/missing-or-build-fails | fixed | REQ-035, REQ-036; UT-BUILD-2 |
| req-set-no-fault-coverage:rust-string-out/exceeds-size-or-NUL | fixed | REQ-037 (truncate to carrier capacity; bytes after an interior NUL dropped), REQ-038 (lossy UTF-8 in); carrier capacity paragraph; UT-SHIM-10 |
| req-set-no-fault-coverage:output-port/unconnected | fixed | plan decision log 11 (owned by the autocoded base, FW_ASSERT in X_out) |
| req-contains-design:REQ-RustCounter-006 | fixed | "A THRESHOLD update shall take effect on the next BUMP." |
| req-contains-design:REQ-RustMonitor-005 | fixed | "Each `run` shall process every count and command received since the previous `run`, then increment and publish `RunCount` and publish `Limit`." |
| req-set-no-fault-coverage:annotation/non-component-element | fixed | plan decision log 12; UT-AC-1 asserts an annotated port/module emits nothing |
| req-set-no-fault-coverage:deployment/no-rust-components | fixed | REQ-039; UT-BUILD-2; §Design "Linkage" states no cargo, no archive |
| req-unclear:REQ-FprimeRust-001 | fixed | reworded per rewrite |
| req-unclear:REQ-FprimeRust-002 | fixed | reworded per rewrite ("reading or writing no JSON model") |
| req-unclear:REQ-FprimeRust-010 | fixed | reworded per rewrite |
| req-weak-verification:REQ-FprimeRust-008 / -009 / -010 / -012 / -013 / -014 / -015 | fixed | all seven `Unit Test; Integration Test: …` |
| req-unclear:REQ-FprimeRust-016 | fixed | "per the type-mapping table"; FFI column moved to §Design ("FFI carriers") |
| req-unclear:REQ-FprimeRust-018 | fixed | reworded ("exactly one copy of the Rust runtime … no duplicate Rust symbol definitions"); verification `Inspection` (UT-BUILD-1 names the counts) per the anchor and systest unit-tests:REQ-018-link-once |
| req-unclear:REQ-FprimeRust-020 | fixed | reworded per rewrite |
| req-weak-verification:REQ-FprimeRust-020 | fixed | `Unit Test` (UT-BUILD-1) |
| req-unclear:REQ-FprimeRust-021 | fixed | reworded per rewrite |
| req-weak-verification:REQ-FprimeRust-021 | fixed | `Unit Test` (UT-BUILD-1) |
| req-unclear:REQ-FprimeRust-024 | fixed | "shall report its message and location through the F Prime assertion hook and abort the process" (closes jpl panic-hook too) |
| req-unclear:REQ-FprimeRust-026 | fixed | "shall match the generated-name table" |
| req-unclear:REQ-FprimeRust-028 | fixed | "byte-identical files" |
| req-set-gap:"platform constraint stated" | fixed | REQ-040 `Inspection`; UT-INSP-1 |
| req-unclear:verification-column | disagree | `fth render-sdd-tests` (pinned v0.1.2) rewrites every Verification cell that names a test id to `<plan note>: <tests>`; the plan is the authority for that cell and the contract makes the tool-rendered form binding. The cells keep the skill vocabulary as the first word(s) (`Unit Test; Integration Test: L2-1, …`); dropping the ids would make the cell diverge from the renderer's output on the next render. The anchor's E-2 ruling ("trace … so verify-plan --sdd passes") also relies on the ids. |
| req-unclear:sdd-waiver-tables | fixed | the four "Out-of-scope failure modes" tables removed; owners recorded in plan decision log 11–12 |
| req-unclear:REQ-RustCounter-003 | fixed | "A BUMP whose sum would exceed THRESHOLD shall set the counter to THRESHOLD and emit `Saturated`, never wrapping." |
| req-unclear:REQ-RustCounter-004 | fixed | "Every completed RESET or BUMP shall publish `Counter` and send the counter on `countOut`, whether or not the value changed." |
| req-unclear:REQ-RustMonitor-002 | fixed | names VALIDATION_ERROR |
| req-unclear:REQ-RustMonitor-004 | fixed | "increment and publish `Exceedances`" |
| req-unclear:RustMonitor-constants | fixed | REQ-RustMonitor-006 ("Until SET_LIMIT is accepted, the limit shall be 4294967295"); L2-5 `first(rustMonitor.Limit) == 4294967295`, L6-1 |
| req-weak-verification:REQ-RustCounter-001..006 | fixed | `Unit Test; Integration Test`; RustCounter unit-test list UT-RC-1..5 |
| req-weak-verification:REQ-RustMonitor-001..005 | fixed | `Unit Test; Integration Test`; RustMonitor unit-test list UT-RM-1..4 |
| req-weak-verification:REQ-Relay-001..002 | fixed | `Unit Test; Integration Test` |
| design-fpp-form:topology.fpp/connections RustReference | fixed | block moved inside the topology after `connections FileHandling_DataProducts`; fpp-check clean on the full closure at b188d185 |
| design-fpp-form:Packets.fppi/omit | fixed | Packets.fppi mirrors fprime-python-reference (CDH, CDHErrors incl. the Dropped/CommandErrors counters, SystemRes1/3, DataProducts, Version1, Version_Library1, RustReference) with the remainder in `omit`; fpp-check clean |
| design-under-scoped:fprime-rust sdd/Context.doDispatch | fixed (anchor ruling) | name-table row "queued dispatch": `doDispatch()` / `do_dispatch` / `ctx.do_dispatch() -> MsgDispatchStatus`, `ctx.dispatch_available_messages()`; alias-safety rule in §Behavior; UT-SHIM-6; RustMonitor §Behavior calls it |
| design-fault-handling-gap:RustCounter.BUMP/overflow | fixed | `saturating_add` in the command table and §Behavior; REQ-RustCounter-003 "never wrapping"; clamp-down case stated; UT-RC-3 |
| design-intent-mismatch:REQ-FprimeRust-008/passive | fixed (anchor ruling (b)) | Relay stays C++; REQ-008 verified by UT-SHIM-5 (one fixture per kind) + integration for active/queued only; plan not_covered_ack lists passive Rust as shim-UT-only |
| design-fpp-form:topology.fpp/deployment-keyword | fixed | `deployment topology FprimeRustReference`; the pinned nasa/fprime b188d185 requires fprime-fpp 4.0.0a1, which accepts it (fpp-check v4.0.0a1 clean); the reviewer's pin 5d748fd/3.3.0a2 is the stale submodule, not the ruling's pin |
| design-intent-mismatch:REQ-FprimeRust-009/guarded | fixed | REQ-009 `Unit Test; Integration Test`; UT-SHIM-2 (guarded fixture), UT-SHIM-3; not_covered_ack names guarded as shim-UT-only |
| design-intent-mismatch:REQ-FprimeRust-012/sync-guarded-commands | fixed | REQ-012 `Unit Test; Integration Test`; UT-SHIM-1 names the three kinds; not_covered_ack |
| design-fault-handling-gap:RustMonitor.queue-full | fixed | `async input port countIn: FprimeRustReference.Count drop`; SET_LIMIT keeps the F Prime default; RustMonitor §Configure states the sustainable rate |
| design-under-scoped:fprime-rust sdd/queue-full hook | fixed (anchor ruling: supported) | name-table row `hook` member; REQ-032; UT-SHIM-9; §Behavior: hooks run on the caller's thread under the instance mutex |
| design-code-mismatch:instances.fpp/rateGroup1 rate | fixed | topology.fpp comments 1 Hz / 0.5 Hz / 0.25 Hz |
| design-fprime-anti-pattern:RustMonitor.Limit/initial | fixed | `Limit` published every `run` (REQ-RustMonitor-005); `init` has no port access (fprime-rust §Behavior), so publication is at the first run |
| design-sdd-form:Components/*/docs/sdd.md/block-diagram | fixed | ASCII port boxes (inputs left, outputs right, special ports as a note) in the three component SDDs |
| design-code-mismatch:fprime-rust sdd Configure vs reference CMakeLists | fixed (anchor: now) | reference root CMakeLists: `FPRIME_ENABLE_JSON_MODEL_GENERATION` removed, `include(FprimeRust)`; SDD §Configure comment |
| design-under-scoped:RustCounter.REQ-004/"change" | fixed | REQ-RustCounter-004 reworded |
| design-intent-mismatch:REQ-FprimeRust-016/type-surface | fixed | §Design "Deliberate deviation from fprime-python: struct and array types are rejected in this release (follow-on: serializers from fprime-cpp-codegen)" |
| arch-rate-group-violation:topology.fpp/connections RustReference | fixed | as design-fpp-form:topology.fpp/connections RustReference |
| arch-kind-incoherence:RustMonitor.run+sdd.md §Design/name-table | fixed | as Context.doDispatch; UT-SHIM-6; RustMonitor §Behavior |
| arch-primitive-misuse:sdd.md §Behavior/instance-mutex | fixed (anchor: one rule) | §Behavior "Instance mutex rule, every component kind": every FFI entry receiving `&mut Implementation` (ports of all kinds, internal/command handlers, hooks, parameter_updated, init); dispatched handlers do not re-take; non-recursive re-entry is a documented design error; UT-SHIM-3 (active + guarded racing async), UT-SHIM-4 (parameterUpdated) |
| arch-primitive-misuse:sdd.md §Behavior/Context-Send | fixed (anchor) | `Context<'call>` neither `Send` nor `Sync`; UT-RT-2 `assert_not_impl_any!` |
| arch-undocumented-departure:sdd.md §Behavior/sync-as-guarded | fixed | §Behavior sentence ("sync and guarded inputs are therefore equivalent … not suitable for lock-free cyclic work shared by several callers") |
| arch-undocumented-departure:sdd.md §Design/deployment-discovery | fixed | §Design "Linkage": no topology annotation, executable is the deployment, zero-component case (REQ-039) |
| arch-primitive-misuse:sdd.md §Design/module-target-sources | fixed | §Design "Linkage" first sentences: autocoder returns `Comp.cpp` as build sources, removes `.rs` from the compiled list, records `FPRIME_RUST_COMPONENTS`/`FPRIME_RUST_SOURCES` |
| arch-undocumented-departure:sdd.md §Design/cross-target-link-line | fixed | `FPRIME_RUST_TARGET` constant, `--target`, `native-static-libs` on the link line; "only the host triple is exercised by this campaign" |
| arch-undocumented-departure:sdd.md §Behavior/unsupported-elements | fixed | rejected-element table (serial, state machine, data product, struct/array/Fw.Buffer); hooks and internal ports bound |
| arch-rate-group-violation:topology.fpp/RateGroups-comments | fixed | as design-code-mismatch:instances.fpp/rateGroup1 rate |
| arch-undocumented-departure:sdd.md §Configure/json-model-option | fixed | §Design "Model loading" and §Configure comment; reference CMakeLists edited |
| arch-undocumented-departure:sdd.md §Design/fpp-python-pin | disagree | anchor ruling of round 1: `fprime-fpp-python==4.0.1` stays (the version verified by the spike on the campaign host). A venv holding both libraries is not this project's case; a range pin is a release decision for the fprime-rust package, recorded here as the reviewer's suggestion. |
| arch-primitive-misuse:sdd.md §Requirements/type-table String-out | fixed | type table: `&str` out copied by the shim (no owned `String` across the FFI); §Design "Rust components allocate through std; they are not for allocation-free deployments" |
| jpl:DR-4.11.1.1.1:Context.doDispatch | fixed | as Context.doDispatch (Rust-driven `ctx.dispatch_available_messages()`, alias rule stated) |
| jpl:DR-4.11.4.13:sdd.behavior.mutex | fixed | as instance-mutex |
| jpl:DR-4.11.1.1.1:topology.RustReference | fixed | topology block moved; rate comments corrected |
| jpl:DR-4.4.7.1:counters | fixed | profile `overflow-checks = false` stated; BUMP uses `saturating_add`; TickCount/RunCount/Exceedances/Relayed "wraps at U32::MAX" in the telemetry tables |
| jpl:DR-4.11.3.3:RustCounter.BUMP | fixed | ranges for `amount` and THRESHOLD (0 pins the counter at 0); equality and amount-0 cases are `Bumped`; UT-RC-2 |
| jpl:DR-4.4.6.4:RustCounter.Counter | fixed | `Counter` written every tick (REQ-RustCounter-005) |
| jpl:DR-4.4.6.4:RustMonitor.Limit | fixed | `Limit` published every run (REQ-RustMonitor-005) |
| jpl:DR-4.11.2.1:sdd.lifecycle.init | fixed | `fn init(&mut self, ctx: &InitContext)` with no port/event/telemetry/parameter access; §Behavior |
| jpl:DR-4.11.2.1:RustCounter.initial-state | fixed | RustCounter §Behavior "At construction counter = 0 and tick count = 0; nothing is published until the first handler call" |
| jpl:DR-4.11.1.3:sdd.type-table.string | fixed | §Design "FFI carriers" (lossy UTF-8 in, truncation out, bool 0/1 / `!= 0`); REQ-037/-038 |
| jpl:DR-4.11.4.11:sdd.ffi-ownership | fixed | §Behavior: `Context<'call>` borrows the shim frame (storing it is a compile error); borrowed pointers valid for the call; no allocation changes owner |
| jpl:DR-4.4.6.8:sdd.panic-hook | fixed | REQ-024 reworded; §Behavior panic hook → F Prime assertion hook before abort; UT-RT-3 |
| jpl:DR-4.11.1.4:sdd.target-triple | fixed | `FPRIME_RUST_TARGET` constant; host-only statement |
| jpl:DR-4.11.5.2:sdd.ut-linkage | fixed | §Design "Linkage": `target/fprime_rust.cmake` runs per deployment and per unit-test executable; `libfprime_rust_<Comp>_ut.a` |
| jpl:DR-4.11.5.2:RustComponents.unit-tests | fixed | "Unit-test list" sections UT-RC-1..5 and UT-RM-1..4 added; mechanism = GTest tester base over the shim (fprime-rust §Design) |
| jpl:DR-4.11.1.1.1:sdd.hook | fixed (anchor: bind) | as queue-full hook |
| jpl:DR-4.11.1.5:sdd.lints | fixed | §Design "Linkage": workspace lint set (`unsafe_op_in_unsafe_fn`, `clippy::unwrap_used`, `clippy::expect_used`, `clippy::indexing_slicing`, `clippy::arithmetic_side_effects` = deny) |
| bench:gds-no-app | fixed | `-n` dropped; notes state the GDS owns the process |
| model:topology-connections-outside-block | fixed | as design-fpp-form:topology.fpp/connections RustReference |
| traceability:component-sdd-ids | fixed (anchor E-2) | all 15 component ids in plan `requirements` with rationale; `fth verify-plan --sdd` passes against the union of the four tables (see NEW finding N-2: fth v0.1.2 `--sdd` takes one baseline file, so the four SDDs were concatenated for the check) |
| pass-rule:L0-1-payload | fixed / partly disagree | L0-1 now judges `LibraryVersions count == 1` and a `version_payloads_present` helper (non-empty, not UNKNOWN) on all three events. Disagree on the rewrite's `(version="{manifest.describe}")` form: fth v0.1.2's predicate grammar (`fth/engine.py` P_COUNT…P_TREF_SENT) has no manifest substitution [V]; describe equality is the deliver/audit `dictionary_describe_check` declared by `image_version: required` (plan decision log 15, L0-1 rationale). |
| fault-menu:fails-incomplete | fixed | `bump_wrong_amount` (+Bumped(7), precedes), `skip_reset` (+Counter == 0, LastCount == 0), `negative_wrong_limit` (+delta Limit, last Limit), `bump_zero` (+precedes); menu regenerated |
| fault-menu:uut-state-class | fixed (anchor E-1) | `threshold_not_saved` (uut-state, L7-1) suppresses PRM_SAVE_FILE so the parameter file — the final-state artifact — is not written |
| final-state:dump-is-image-hash | fixed as far as the tool allows (anchor E-1) | L7-1 saves THRESHOLD 42 (`THRESHOLD_PRM_SET/SAVE`, `PRM_SAVE_FILE`) and downlinks `PrmDb.dat`; the auditor parses the downlinked file (record format cited). Bench `dump` stays the executable read-back because fth v0.1.2 `run.flash()` fails the run when the read-back sha256 differs from the image [V run.py]; see NEW finding N-1 |
| traceability:over-claims | fixed | REQ-008/-009/-012/-013/-015 carry `Unit Test; Integration Test`, named UT rows with asserted values; plan not_covered_ack names every kind/severity the reference does not exercise |
| design:json-model-on | fixed (anchor: now) | reference root CMakeLists edited; SDD §Configure comment; REQ-002 "reading or writing no JSON model" |
| constants:rate-group-comment | fixed | comments corrected; L2-4/L4-1 rationale cites `Main.cpp startRateGroups(Fw::TimeInterval(1, 0))` and the divider |
| model:packets-omit-empty | fixed | as design-fpp-form:Packets.fppi/omit |
| bench:paths-and-pins | fixed | `install` relative (`run/FprimeRustReference/FprimeRustReference`); scripts named as DEVELOPMENT design items in `provenance.note` and plan decision log 14; dictionary rewrite reliance stated in `notes` |
| fault-menu:ripples-empty | fixed | insulation stated in the module docstring and every `mechanism` (each test opens with RESET / explicit SET_LIMIT and restores state); `ripples_to` stays empty by that argument |
| design:submodule-pin | fixed | plan decision log 14 names the URL/branch change and the lib/fprime SHA as DEVELOPMENT edits |
| unit-tests:REQ-018-link-once | fixed (anchor) | REQ-018 `Inspection`; UT-BUILD-1 names the counts (one archive on the link line, one `rust_begin_unwind`, no duplicate-symbol diagnostics) |
| unit-tests:assertion-values | fixed | every UT row in the fprime-rust list names its asserted value/diagnostic (UT-AC-2/3/5, UT-RT-3, UT-SHIM-1..10, UT-BUILD-1/2) |
| E-1 (systest elicitation) | applied per anchor, with N-1 | see final-state:dump-is-image-hash |
| E-2 (systest elicitation) | applied per anchor, with N-2 | see traceability:component-sdd-ids |

## New elicitation findings (author, round 1)

- **N-1** fth v0.1.2 `run.flash()` executes the bench `dump` right after `flash` and records "read-back differs from image" when sha256(readback) ≠ sha256(image) [V `fth/run.py`]. The ruling E-1 ("`dump` reads that file back") therefore cannot be met with `dump` = PrmDb.dat without a harness change (tooling pin = plan change). Applied: `dump` reads the installed executable; the final-state artifact leaves the UUT by `FileHandling.fileDownlink.SendFile(PrmDb.dat, PrmDb.dat)` inside the L7-1 window and the auditor parses the downlinked file. Recommended ruling: accept (evidence path is the file-downlink service, not the UUT's telemetry/events), or schedule an fth change adding a post-run dump row.
- **N-2** fth v0.1.2 `verify-plan --sdd` takes one baseline file and requires every cited id to be in that file; with four SDDs each holding its own table no single `--sdd` run passes. Applied: the check ran against the concatenation of the four SDD files (53/53 ids). Recommended ruling: accept the concatenation check as the gate, or extend fth to accept repeated `--sdd`.
- **N-3** fth v0.1.2 predicate grammar has no manifest-substituted form; the L0-1 payload ↔ `manifest.repos[].describe` equality is judged by `fth deliver`/`audit` (`dictionary_describe_check`) under `image_version: required`. Recommended ruling: accept.
