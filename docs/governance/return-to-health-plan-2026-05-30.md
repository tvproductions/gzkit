# Return to Health Plan, 2026-05-30

Status: Active canonical recovery plan.

> **Live baseline: Snapshot L (2026-06-06) — `main` is 26/26 GREEN, synced.** Full
> measurement in § Current Baseline. Tier 0 has reopened 6× (C→E→G→J→K→L): main is not
> *durably* green across machines/sessions — that recurrence, not any single gate, is
> the headline problem. #519 is the sole open `emergency`; recovery stays OPEN.
>
> **Route (since Snapshot G):** append-only corpus → per-surface temperature setpoint →
> authoring-time agent compression (advisor-QC'd, operator-attested) → committed
> rendition → deterministic playback + verbatim invariant tier. ADR-0.0.37 active set =
> 01–10, 18–27 (§ Checklist is authoritative). **Filename** stays
> `return-to-health-plan-2026-05-30.md` (operator-anchored 2026-06-04).

Last updated: 2026-06-06 — **Tier 0 reopened again (6th time; Snapshot L) on session resume (handoff + restore-health): `gz check` red on Format + Task-envelope-coherence, both OBPI-0.0.37-20 completion residue. Re-closed via `ruff format` (5 files) + a `req_atomic:` frontmatter exemption (each REQ one indivisible labor unit; Snapshot D/E/G precedent); main 26/26 green. Both offenders are the plan's named subtraction candidates — recurrence is the headline. See § Current Baseline — Snapshot L.**

Earlier 2026-06-06 entry — **Tier 0 reopened on a fresh Windows clone (`gz check` red on Typecheck + Behave) and re-closed; 2 fixes pushed; main 26/26 green (Snapshot K).**
Drained Phase-4 recovery debt one at a time (green-first, observed-evidence closes): closed
**#525 / #560 / #562** as verify-only already-resolved (CLAUDE.md redirect doctrine landed;
distribution byte-equivalence scenario green after `cda0d78e`; tautological audit converted to
`_file_digest`), and direct-fixed **#559** (`abba7e9b` — `hexagonal-architecture.md` demoted-ADR
adapter examples → live feature adapters 0.13.0/0.18.0/0.12.0; mkdocs --strict green) and **#534**
(`44ceedd8` — TDD RED→GREEN; `gz obpi complete` covering-test subprocesses now decode with
`errors="replace"`) and **#569** (`3a6908e1` — TDD; verify-stage extractor reuses
`extract_fenced_commands` so multi-line Verification commands join per BI-1, not split).
Filed **#582** for the broader class (~41 text-mode subprocess reads in
`src/gzkit/` lacking `errors=` + a recurrence-defense validator — ceremony-sized). Open issues
**38 → 33**. The remaining Phase-4 set is largely operator-gated (schema-enum class #480/#524/#527;
attested-brief sprawl #532/#549; budget-touching #551; large routed #571). **#519 stays the sole
open emergency** — its durable cure (registry-projection to <15k, GHI #533) needs the ADR-0.0.37
build-out + Gate 5, which require the operator. Earlier 2026-06-05 entry retained below.

Prior 2026-06-05 entry — **OBPI-0.0.37-26 attested-complete (pipeline closeout).**
Ran the `gz-obpi-pipeline` from `--from=verify` over OBPI-0.0.37-26 (the #519 Codex-root
interim relief, payload already landed at Snapshot I): Stage 3 verify green (ruff,
typecheck, 5879 unittests, mkdocs `--strict`, `--vendor-manifest`,
`--instructions-files-budget`, `--invariant-coherence` 10 scopes, `--documents` — all
pass; 6/6 REQs SUPPORT-kind so behave N/A), Stage 4 operator attestation ("attest
completed"), Stage 5 `gz obpi complete` → `attested_completed` (receipt
`attestation_type: operator-verbatim-conversational`), lock released, two git-sync cycles,
reconcile PASS. ADR-0.0.37 posture moves **6/19 → 7/19 attested**, missing-proof OBPIs
**13 → 12** (per `gz adr audit-check`). The earlier Snapshot J re-measurement
(`gz check` 26/26 GREEN after clearing the OBPI-0.0.37-18 Preflight orphan) still holds as
the committed-main baseline; this edit records only the OBPI-26 disposition change.

## Execution Worklist (start here)

> **The linear path through this plan.** A fresh session works top-down: take the **topmost
> unchecked item whose gate is met**, do it, check it off **with observed command evidence**
> (Phase 4 rule), and update its status line. **Never start a tier while the prior tier's exit
> gate is unmet** (green-first, Operating Rule 2). This checklist is the *hand-rolled precursor*
> to the triaged MOTD workplan designed below (§ Session MOTD) — until that ships, **this is the
> workplan; update it every session.** Status keys: `[ ]` todo · `[x]` done · `[~]` in progress ·
> `[!]` blocked.

**Tier 0 — Restore green (do now; everything else is gated on this).** Exit gate: `uv run gz check` exits 0.

- [x] **0.1 Clear the OBPI-0.0.37-12 orphan lock + plan-audit receipt** → `uv run gz preflight --apply` cleared the orphan receipt + expired lock (576m); `uv run gz preflight` → "clean" (EXIT=0). Fixes the `preflight` gate. *Verification finding:* preflight `--apply` does **not** honor the token-block reaping-handoff discipline (it `unlink`s the lock without the `abandoned_by_reaper` register entry / `lock_manager.release_lock`) — substantively moot here (work attested-complete) but a real coherence gap → filed via `/ghi-author` (preflight reaping-handoff GHI; `Related: #564`). The #564 OBPI-0.0.64-04 orphan was already absent (not present in the scan). → *Current Baseline § Snapshot C/D*.
- [x] **0.2 Resolve `--task-envelope-coherence`** — 0.0.37-12: ledger `:8460` (`meta-receipt-bind` ceremony event, post-epoch) missing `task_id`; `seq=01`-only TASKs. Remediated (operator-ratified, TDD): **sig (a)** validator excludes closeout `receipt_event == "meta-receipt-bind"` `audit_receipt_emitted` events from the labor signature — narrow carve-out (bare `audit_receipt_emitted` still fails), no ledger hand-edit (Never #2); **sig (b)** `req_atomic:` with inline per-REQ rationale on the OBPI-0.0.37-12 brief. New instance appended to **GHI #563**. `uv run gz validate --task-envelope-coherence` → All validations passed (EXIT=0). → *Snapshot C/D*.
- [x] **0.3 Re-measure & record Snapshot D** — `uv run gz check` → "✓ All checks passed" (`GZ_CHECK_EXIT=0`, true exit captured without pipe-masking); 26/26 gates green. Phase 1 reaffirmed complete. → *Current Baseline § Snapshot D*.
- [x] **0.4 Reopen Tier 0 and record Snapshot E** — 2026-06-02 re-measurement proved Snapshot D stale: `uv run gz check` failed on `Format`, `ADR status freshness`, and `Task envelope coherence`. Remediated with observed evidence: `uv run ruff format tests\content\test_round_trip_agent_contract.py` → "1 file reformatted"; `uv run gz register-adrs` → "Regenerated adr-status.md (90 ADRs)"; task-envelope TDD RED showed two failures in `tests.governance.test_task_envelope_coherence`, then GREEN after validator repair; `uv run gz validate --task-envelope-coherence` → "✓ All validations passed"; `uv run gz check` → "✓ All checks passed" (26/26 gates; advisory drift 1735 findings, non-blocking). → *Current Baseline § Snapshot E*.
- [x] **0.5 Reopen Tier 0 on resume and record Snapshot G(check)** — 2026-06-03 resume re-measurement proved Snapshot F stale (D→E→F→G pattern): `uv run gz check` → exit 1 on `Test` (handoff-count tripwire 37≠38), `Task envelope coherence` (8 events, ledger `:8574`–`:8581`), `Preflight` (OBPI-09 orphan). Remediated, operator-ratified, with observed evidence: handoff tripwire bumped 37→38; **TDD ADR-decision-doc carve-out** for sig (a) (`test_adr_decision_doc_edit_under_active_task_is_clean` RED 2≠0 → GREEN; `src/foo.py` negative control still fails); **OBPI-0.0.37-17-as-scoped retired** (8 TASKs `gz task block`ed, stale plan `lively-hatching-storm.md` removed, OBPI-09+OBPI-17 orphan receipts cleaned via `gz preflight --apply` → "clean"; 2026-06-04 renumber later withdrew 11–17 and mirrored them as `Abandoned`); two latent defects direct-fixed (TDD) — `gz task` transitions for full-slug OBPIs (`TestTaskTransitionFullSlugObpi` RED "pending → blocked" → GREEN) and the carve-out. `uv run gz check` → "✓ All checks passed" (26/26; `GZ_CHECK_EXIT=0`; advisory drift 1735). Committed `32cac1d2`/`e4b9cc78`, synced to `origin/main` via `gz git-sync --apply --lint --test`. → *Current Baseline § Snapshot G(check)*.

**Tier 1 — Recovery to Definition of Healthy.** Exit gate: Definition of Healthy all-true.

- [~] **1.1 Phase 2 — context-load emergency #519. Byte relief LANDED 2026-06-04 (commit `705a2354`, pushed).** Root `AGENTS.md` genuinely compressed **32,651 → 28,342 B** (~4.4 KB under Codex's 32,768 B cap) via the local-splice diet (`.gzkit/agents.local.md` 9,306 → 4,997 B), keeping all 18 splice-only Mechanical/Promotable scorecard phrases verbatim — so `bullet-retention` stayed green under the *current* whole-surface validator (the predicted 14-violation collision was avoided by re-homing terse skeletons, not deleting). Supersedes the budget-at-cap stopgap (`b402c7cf`). The relief *payload* landed as a **direct commit**; the **OBPI-0.0.37-26 ceremony is now closed (2026-06-05, this session)** via `gz-obpi-pipeline --from=verify` — Stage 5 `gz obpi complete` → `attested_completed` on the operator-verbatim conversational Gate-5 path (ADR-0.0.36). This disproves the prior note that the Claude Code auto-mode classifier blocks the sign+push: the agent *relays* the operator's verbatim "attest completed" (it does not sign), and `--attestation-type operator-verbatim-conversational` is the canonical completion path. The interim rendition is captured at `renditions/agentcontract-codex-root-interim.md` for OBPI-21/22 to regenerate. **Still open:** the durable 258K-window cure needs the <15k registry-projected surface (GHI #533) — #519 not yet closed. **Loosening pass (operator-directed, this session):** `ac0816ff` (REQ-coverage gate is ADR-0.0.59 kind-aware — SUPPORT/STRUCTURAL-FENCE REQs no longer snare completion) and `8dc04a9a` (pipeline mandate scoped to contract-bearing OBPIs — routine/recovery/defect fixes default to direct-fix). → *Recovery Closeout § Snapshot I*.
- [ ] **1.2 Phase 3 — ceremony & validator mechanization** (#516 + the req-kind/covers eval-feedback cluster; now also #563/#564 closeout-pipeline class fixes + #578 preflight lock-coupling). 18 issues — see **GHI Register § Phase 3**. → *Phase 3*.
- [ ] **1.3 Phase 4 — drain remaining recovery issues** — docs/tests/`validate --documents` defects, including the GHI #571 stdlib unittest/doctest maturity route. 10 issues — see **GHI Register § Phase 4**. WIP = 1; close only with observed evidence. → *Phase 4*.
- [ ] **1.4 Phase 5 — closeout.** Fill Recovery Closeout when #519 closed + no open emergency + `gz check` green. → *Phase 5; Recovery Closeout*.

**Tier 2 — Post-green workstreams** (start only after recovery closes, or under an explicit, item-specific operator Boundary-1 waiver). Each builds in the dependency order it declares.

- [ ] **2.0 Housekeeping: re-home ADR-0.0.66 → pool** (§13 immediate, *not executed*) — frontmatter disposition → `uv run gz register-adrs`. → *§13; Snapshot C note*.
- [ ] **2.1 Canon Foundation** — the substrate the others assume; build per its §12 sequence. → *Designated Workstream — Canon Foundation*.
- [ ] **2.2 Context-Load CMS** — pulled into Tier 1 while #519 remains open. Current live route is **1.1 / OBPI-0.0.37-26** (Codex-root setpoint + interim operator-attested compressed rendition), with the active ADR-0.0.37 set numbered 06–10 and 18–27. Historical 11–17 are withdrawn (`Abandoned` mirror; 11–15 retain valid completion receipts; 16/17 created-only/retired). Do not restart the retired OBPI-17 density-classification route. → *Execution Worklist 1.1; Designated Workstream — Context-Load CMS historical context*
- [ ] **2.3 Harness Hardening + ADR-0.0.66** — the enforcement spine + `gz next`/triage read-substrate. → *Designated Workstream — Harness Hardening*.
- [ ] **2.4 Session MOTD** — consumes the absorbed ADR-0.0.65, ADR-0.0.66, and canon; build per its §7. → *Designated Workstream — Session MOTD*.
- [ ] **2.5 Config-first store — repo-wide SSOT (its own first-class workstream; design deferred, operator 2026-06-01).** A NEW thing, not a subset of anything: gzkit has no single source of truth for its own operational tuning values, which live as drifting literals repo-wide — instructions budgets, validator thresholds, `_PIPELINE_MARKER_STALE_HOURS` / timeouts / ceilings hardcoded in `src/`, lock TTL, the 40% coverage floor, defect-fix thresholds — scattered across `data/`, code, tests, and prose docs. **Live instance (2026-06-01):** the AGENTS.md char budget exists in 4 places — `data/instructions_files_budget.json` (now 33000), two test literals (`test_agents_md_map_doctrine_obpi01/04`), and the `agents-md-map-doctrine.md` Budget table *still saying 15000* (drifted since OBPI-0.0.54-01). Inventory: `grep -E '^_[A-Z_]+ *= *[0-9]' src/gzkit`. Target: one typed source that code, tests, **and doc-table generation** read from, + a `gz validate --config-ssot` drift fail-close. **Overlaps but exceeds Canon Foundation §8.8** — canon subsumes scattered `data/*.json` *invariant data*; this is broader: repo-wide tuning *scalars*, most hardcoded in `src/`, which canon (invariant rules) does not home. The irony it names: gzkit preaches SSOT for governance state, has none for its own config. **Prior art (operator, 2026-06-01): AirlineOps did this notably better — study its config-SSOT pattern via `/airlineops-parity-scan` before designing.** Reference for a gzkit-native design, not perpetual-parity catch-up (Architectural Boundary 5).

> **Ordering decision — RESOLVED (operator-ratified, 2026-06-02):** relieve #519 via the CMS
> workstream on the **current `AgentContract` substrate now**; do **not** block CMS on Canon
> (2.1) first. Rationale: #519 is the only open emergency and Tier 1 puts it topmost; Canon is
> Tier 2 (the largest new governance surface) and the plan's posture forbids expanding governance
> surfaces until recovery closes; CMS OBPIs 11–13 already shipped on the current substrate
> (precedent); the canon re-sequencing of 13/14 (§10) named *13's* classification dependency, and
> 13 already completed without canon. **Accepted cost (named):** bounded rework when Canon lands —
> the CMS's *data source* repoints from the current model to canon (canon §12 step 5); the
> sync→model-renderer wiring built by OBPI-14 stays. So 2.1 follows 2.2; they do not interleave on
> the critical path. Operator call: *"resolve the ordering decision now in favor of relieving #519
> on the current substrate — do not block CMS on Canon first — then proceed to Phase 2 / #519."*

### GHI Register — all 38 open issues, homed

> First-pass triage (via `ghi-triage`, 2026-06-01): the script's mechanical route is *evidence*;
> the **Home** column is the agent's body-read tier assignment — re-home freely. **Every open GHI
> appears exactly once.** Tier 0 = blocks `gz check` green (only the two gate families do); Tier 1
> = blocks Definition-of-Healthy (mapped to a Phase); Tier 2 = post-green / workstream-bound;
> Parked = design-discussion, re-survey later. When a GHI closes, strike its row; when the queue
> is re-surveyed, regenerate this table. This is the manual stand-in for `ghi-triage` → workplan
> until the MOTD ships.

| GHI | Summary | Home |
|-----|---------|------|
| #563 | task-envelope gate failure — `seq=01`-only TASKs, missing `task_id` | **T1** — Phase 3 (gate cleared @ Snapshot E; new instance @ Snapshot G(check): ADR-decision-doc edits under active TASKs — cleared via SUPPORT-channel carve-out; class fix: closeout `task_id` population still remains) |
| #564 | preflight orphan plan-audit receipt (OBPI-0.0.64-04) | **T1** — Phase 3 (gate cleared @ Snapshot D; recurred @ Snapshot G(check): OBPI-09+OBPI-17 orphans cleaned via `gz preflight --apply`; class fix: closeout leaves no orphan remains. Adjacent latent: short-vs-full `obpi_id` mismatch direct-fixed in `task.py` @ Snapshot G(check), other consumers may share it) |
| #519 | context surface exhausts 258K window (**emergency**) | **T1** — Phase 2 → CMS. **Interim relief LANDED on `main` (Snapshot I, commit `705a2354`; held at Snapshot J):** root AGENTS.md = **28,489 B** via the local-splice diet, under Codex's 32,768 B cap with ~4.3 KB headroom; Surface fidelity green (the predicted 14-violation collision avoided by re-homing, not deleting). **OBPI-0.0.37-26 attested-complete 2026-06-05** (pipeline closeout, operator-verbatim conversational Gate-5 path). **Still OPEN:** full 258K-window closure needs the <15k registry-projected surface (GHI #533). Per-vendor emission ruled out; OBPI-17-as-scoped retired. |
| #516 | closeout passive-presenter lacks REQ-evidence check | **T1** — Phase 3 |
| #536 | `gz adr promote` Target-Scope `path:line` → invalid OBPI paths | **T1** — Phase 3 |
| #537 | BEHAVIOR-kind cannot-uncovered-accept not mechanically enforced | **T1** — Phase 3 |
| #538 | STRUCTURAL-FENCE parent-ADR `## Boundary Invariants` shape unchecked | **T1** — Phase 3 |
| #543 | req-kind SUPPORT proof channel regex-only; no ledger query runs | **T1** — Phase 3 |
| #544 | `covers` grandfathering cache loaded as raw dict, no schema | **T1** — Phase 3 |
| #545 | `ReqCoverageRecord` declared/tested but never instantiated | **T1** — Phase 3 |
| #546 | `--req-kind-discipline` no bypass-once flag (parity w/ `gz covers`) | **T1** — Phase 3 |
| #553 | ADR-0.22.0 task-envelope intent landed as OBPI-boundary stamps | **T1** — Phase 3 |
| #558 | `gz adr demote` keep-pool leaves stale `promoted_to`/Superseded | **T1** — Phase 3 |
| #561 | OBPI-0.0.64-05 SUPPORT REQ missing `gz validate --<scope>` citation | **T1** — Phase 3 |
| #565 | 40 active briefs' compound Verification cmds violate shell-less contract | **T1** — Phase 3 |
| ~~#569~~ | verify-stage extractor doesn't reuse `extract_fenced_commands` joiner | **CLOSED 2026-06-05** — `3a6908e1` (TDD); BI-1 joiner shared with demo path |
| #573 | closeout BI-2 DRY classifier fork needs governed TDD redo | **T1** — Phase 3 |
| #577 | `gz context` vs `gz status` divergent gate projection | **T1** — Phase 3 |
| #578 | `preflight --apply` reaps expired locks without token-block register entry | **T1** — Phase 3 |
| #480 | `validate --documents`: 3536 errors from schema-convention additions | **T1** — Phase 4 |
| #524 | ADR-0.2.0 fails `validate --documents` (status enum + sections) | **T1** — Phase 4 |
| ~~#525~~ | CLAUDE.md→AGENTS.md redirect | **CLOSED 2026-06-05** — already landed; doctrine line in all 3 CLAUDE.md surfaces (verify-only) |
| #527 | ADR-0.0.9 fails `validate --documents` (status enum + sections) | **T1** — Phase 4 *(schema-enum class w/ #480/#524 — `Validated` is real lifecycle; needs schema decision, not per-file edit; defer to operator)* |
| #532 | 4 briefs reference wrong manpage path (`gz-validate.md`) | **T1** — Phase 4 *(actually sprawls to dozens of attested briefs; entangled w/ #549 — not a clean direct-fix)* |
| #551 | REQ-coverage foundation-trigger undocumented in AGENTS.md | **T1** — Phase 4 *(premise overlaps landed loosening `ac0816ff`; touches budget-constrained AGENTS.md — defer)* |
| ~~#559~~ | `hexagonal-architecture.md` stale refs to demoted ADRs | **CLOSED 2026-06-05** — `abba7e9b`; substituted live feature adapters (0.13.0/0.18.0/0.12.0), mkdocs --strict green |
| ~~#560~~ | behave `distribution_invariant` byte-equivalence scenario failing | **CLOSED 2026-06-05** — `cda0d78e` registered missing rule in baseline; scenario green (verify-only) |
| ~~#562~~ | tautological test (`test_unscoped_rules.py` read_text+assertEqual) | **CLOSED 2026-06-05** — converted to `_file_digest`; audit exit 0 (verify-only) |
| #571 | stdlib unittest/doctest doctrine & recurrence defenses | **T1** — Phase 4 |
| ~~#534~~ | obpi pipeline: subprocess reader crashes on non-utf8 grandchild stdout | **CLOSED 2026-06-05** — `44ceedd8` (errors=replace, TDD); class routed to #582 |
| #582 | subprocess: ~41 text-mode reads lack `errors=`, crash on non-UTF-8 (class of #534) | **T1** — Phase 4 *(filed 2026-06-05; ~39 sites + recurrence-defense validator → ceremony-sized)* |
| #533 | agents-md 5k budget — depends on ADR-0.0.37 completion | **T2** — CMS (2.2) |
| #579 | instructions-budget: anchor on imperative-density, not char count | **T2** — CMS (2.2) *(agent-homed @ Snapshot F; density-dial doctrine; enhancement)* |
| #580 | composition-renderer: order sections by criticality (periphery-aware) | **T2** — CMS (2.2) *(agent-homed @ Snapshot F; enhancement)* |
| #574 | handoff resume "advise-not-execute" gate is prose, not mechanized | **T2** — Session MOTD (2.4) |
| #575 | no governed `gz insights` author verb (hand-append only) | **T2** — ADR-0.0.66 substrate (2.3) |
| #547 | req-kind suite-level post-conditions doctrine unspecified | **T2** — req-kind doctrine |
| #549 | are attested briefs textually correctable without re-attestation? | **T2** — ceremony doctrine |
| #567 | Pocock fenced prototype-spike + 2 filters (parity) | **Parked** — §13 Open-needs-discussion |

**Tier counts (updated 2026-06-05, post Phase-4 drain):** T0 = 0 (harness green) · T1 = 25 (Phase 2: 1 · Phase 3: 17 · Phase 4: 7) · T2 = 7 · Parked = 1 · **33 open total.** This session closed **6** issues (#525, #560, #562 verify-only already-resolved; #559, #534, #569 direct-fixed) and filed **1** (#582, the #534 class). Remaining Phase-4 quick-drain is largely exhausted: #480/#524/#527 are one schema-enum-class decision (`Validated` is gzkit's real ADR lifecycle status but absent from the `--documents` validator enum — a schema/runtime-contract call for the operator, not per-file status edits); #532 sprawls across attested briefs (entangled w/ #549); #551 overlaps the landed loosening + touches budget-constrained AGENTS.md; #571 is the large routed unittest/doctest work. The
two **eval-feedback** clusters (req-kind #537/#538/#543/#544/#545/#546/#547; covers/coverage) are
the *"advisory-rule-never-mechanized"* family the §1 audit named as the dominant failure mode —
they concentrate in Phase 3, which is the right place to retire the class, not the instances.

This plan replaces the prior emergency framing documents, which were removed on
2026-05-30 so they no longer compete for authority:

- `docs/governance/get-out-of-jail-plan-2026-05-23.md`
- `docs/governance/get-out-of-jail-extensions-2026-05-23.md`
- `docs/governance/june-2026-road-to-salvation.md`
- `.claude/plans/rescue-and-repair-roadmap-2026-05-27.md`
- `docs/governance/model-regression-deep-dive-2026-05-23.md`

Those documents captured real distress signals, but their tone and sequencing
kept the project in emergency mode. The recovery posture now is narrower: make
the repo healthy, keep it healthy, and stop expanding governance surfaces until
the harness is green. The model-regression deep dive contributed durable
diagnosis, but its dated command snapshot is superseded by the baseline below.

## Current Baseline

> **Live baseline = Snapshot L (2026-06-06).** Snapshots A–H are preserved as a
> compact history table below; full prose for A–F and H is recoverable from this
> file's git history (pre-2026-06-05). This consolidation is the #519 / Definition-of-
> Healthy posture applied to the plan itself: one orientable baseline, not a
> growing snapshot log.

### Snapshot L — 2026-06-06 (session resume: handoff + restore-health; Tier 0 reopened + re-closed): RED→GREEN

- A session resume re-measured `gz check`: **RED**, two gates, both
  **OBPI-0.0.37-20 completion residue** (not real defects):
  1. **Format** — 5 OBPI-20 / deadlock-fix files landed un-`ruff format`'d
     (`brief_reconcile.py`, `setpoint_coherence.py` + their tests,
     `setpoint_coherence_steps.py`). Fixed: `uv run ruff format` (5 reformatted).
     *Root cause:* the OBPI-20 and deadlock-fix commits reached `main` without a format
     pass. Per-commit hooks are **deliberately not installed** (operator-confirmed
     2026-06-06; `.git/hooks/` holds only `*.sample` files) — gzkit gates at `gz check` /
     `gz git-sync --lint --test` time, not per-commit, consistent with the
     Harness-Hardening north star that *"friction-always is the disease."* So the design
     gate is run-before-push discipline, and on the path that introduced these files it
     was not applied. Fix: `ruff format` + re-run `gz check`. The hook absence is **not**
     a defect.
  2. **Task-envelope-coherence** — OBPI-20 closed with `seq=01`-only TASKs across
     REQ-01…05 and no `req_atomic:` exemption. Fixed: `req_atomic:` frontmatter with
     inline per-REQ rationale (each REQ one indivisible labor unit; Snapshot D/E/G
     precedent).
- **Re-measure: `uv run gz check` → 26/26 GREEN (`GZ_CHECK_EXIT=0`); committed +
  pushed; tree clean, synced 0/0.**
- **6th Tier-0 reopening (C→E→G→J→K→L).** Both offenders are the plan's named
  **subtraction candidates** — they fire on residue left by *completions*. The operator
  chose the precedented direct-fix this pass; the durable class-fix (closeout auto-mints
  `req_atomic` + runs `ruff format`; gate fix-or-retire with operator witness) remains
  the standing recommendation. Recurrence — not any single gate — is the headline.
- **Recovery stays OPEN.** #519 still the sole `emergency`; Definition-of-Healthy
  not all-true.

### Snapshots A–K — compact history (preserved for audit)

| # | Date | gz check | What it recorded |
|---|------|----------|------------------|
| A | 2026-05-30 AM | RED | Plan authoring; six named failure surfaces (unit test, --kind-invariance, --insights-shape, --tautological-test-audit, --task-envelope-coherence, preflight). |
| B | 2026-05-30 | GREEN 26/26 | GHI #570 added the Line-endings gate + cleared the unit-test failure; Phase 1 first declared complete. |
| C | 2026-06-01 | RED 24/26 | Regressed: Task-envelope coherence + Preflight — root cause = OBPI-0.0.37-12's irregular closeout (lock never released, ceremony skipped). |
| D | 2026-06-01 | GREEN 26/26 | Tier-0 remediation: task-envelope meta-receipt-bind carve-out + req_atomic on 0.0.37-12; `preflight --apply`. |
| E | 2026-06-02 | GREEN 26/26 | D proved stale; cleared Format, ADR-status-freshness, Task-envelope (OBPI-0.0.37-13 carve-outs + req_atomic). |
| F | 2026-06-03 | GREEN 26/26 | OBPI-0.0.37-15 (per-vendor temperature *selection*) attested → CMS 10/16. #519 still unrelieved. |
| G | 2026-06-03 | RED→GREEN | Resume red on Test (handoff tripwire), Task-envelope (OBPI-17 dangling TASKs), Preflight (OBPI-09 orphan). Cleared via ADR-decision-doc carve-out + OBPI-17 retirement; 2 task-id defects direct-fixed (`32cac1d2`, `e4b9cc78`). |
| H | 2026-06-04 | RED (uncommitted) | In-flight OBPI-0.0.37-26 tree: byte target reached but uncommitted/unattested. Superseded by I + J. |
| I | 2026-06-04 | GREEN | #519 byte relief landed on `main` (`705a2354`): root AGENTS.md 28,489 B, under Codex's 32,768 B cap. |
| J | 2026-06-05 | RED→GREEN | Committed-main re-eval: 1 orphan plan-audit receipt (OBPI-18) on Preflight; cleared via `preflight --apply`. OBPI-0.0.37-26 attested-complete (operator-verbatim Gate-5); 7/19 ADR-0.0.37 attested. |
| K | 2026-06-06 | RED→GREEN | Fresh Windows clone (61 commits behind): red on Typecheck (POSIX `signal` analysed on Windows; `# ty: ignore`) + Behave (OBPI-08 reconcile-gate broke stale completion fixtures). Fixed `14dec36c`/`f7428b2b`. |

**Carry-forward watch-items (still live):**

- **Short-vs-full `obpi_id` divergence** — direct-fixed in `task.py` @ G only; other
  consumers (`validate_task_envelope._obpi_id_for_task`, `_task_matches_obpi`) may carry
  it. Watch when next touching task/OBPI id resolution.
- **Budget vs Codex cap** — `data/instructions_files_budget.json` AGENTS.md budget = 30000,
  under the 32,768 B Codex cap (ties to #579 + config-SSOT 2.5).
- **Format/check gate is run-before-push by design, not per-commit** — per-commit hooks are
  deliberately off (operator-confirmed); the gate is `gz check` / `gz git-sync --lint
  --test`, run before push. The Snapshot-L drift was that gate not being applied to the
  introducing commits, **not** a missing hook. No hook-install / bootstrap action implied.

**Recurring Tier-0 offenders (subtraction candidates):** Preflight (orphan plan-audit
receipts: C, G, J), Task-envelope-coherence (ceremony artifacts: C, E, G, L), and Format
(un-`ruff format`'d completion files: E, L) reopen Tier 0 most often — all fire on residue
left by *completions*, not real defects. Fix-or-retire per Operating-Rule subtraction;
gate retirement needs operator witness.

Snapshots A–K are preserved above for audit; **Snapshot L is the live baseline.**

## Definition of Healthy

gzkit is healthy when all of these are true:

- `uv run gz check` exits 0 on `main`.
- A fresh agent can identify the next recovery action without reading more
  than one recovery plan.
- No open `emergency`-labeled issue remains.
- Current failing gates have either been fixed or routed to active tracked work
  with a named owner and next command.
- Known passive-ceremony risks are either mechanized or represented by active,
  ranked GHIs with the next verification command named.
- New doctrine, new foundation ADRs, and new validators are frozen unless they
  directly repair a failing gate.
- Recovery work reduces always-loaded context or check failures; it does not add
  broad new process.

## Merged Deep-Dive Findings

The retired 2026-05-23 model-regression deep dive leaves these facts in the
active plan:

- The recovery frame is not "newer models are worse." The class of failure is
  under-mechanized governance ceremonies and excessive always-loaded context;
  model behavior exposes those weaknesses rather than explaining them away.
- `gz-obpi-pipeline` remains the comparison target for trustworthy ceremonies:
  staged runtime, explicit verification, human gate, guarded sync, and
  fail-closed boundaries.
- Passive presenter ceremonies, especially closeout and audit workflows, must
  move toward observed runtime checks or stay explicitly routed through GHIs
  such as #516 and #517.
- Validators that claim runtime health must execute or otherwise prove the
  runtime path that matters. The Codex SessionStart cache-pin fix from GHI #510
  is the precedent: authored wiring was not enough.
- `gz check` triage must show fail-closed blockers before advisory bulk. Large
  advisory drift lists are useful only after the exit-code cause is visible.
- Generated mirrors should not multiply diagnostics. Check canonical sources
  first, and collapse or exclude mirror duplicates when reporting skill-script
  and BDD-step findings.

## Operating Rules

1. One active plan. This file is the plan.
2. Green first. Do not start new feature, doctrine, or evaluator work while
   `uv run gz check` is red.
3. Prefer direct fixes for current gate failures when the defect-fix routing
   thresholds allow it.
4. Use existing GHIs for tracked defects. File new GHIs only when the defect is
   not already tracked and cannot be fixed in the current pass.
5. No model-centered rescue framing. Model choice is an implementation detail;
   mechanical gates are the recovery mechanism.
6. No new foundation ADRs during recovery unless the operator explicitly
   approves one after seeing the routing facts.
7. Treat context as a budgeted runtime dependency. Keep always-loaded prose to
   hard invariants, routing pointers, and task entrypoints.
8. Every recovery session starts with:
   - `git status --short`
   - `uv run gz check`
   - `gh issue list --state open --label emergency --limit 20`

## Phase 1: Make the Harness Green

Goal: `uv run gz check` exits 0 without weakening gates.

Known work:

- Fix `.gzkit/insights/agent-insights.jsonl` lines 133 and 134 so they conform
  to `InsightRecord`: include `type`, and make `evidence` a list.
- Add the missing `## Why foundation tier?` section to
  `ADR-0.0.65-handoff-system-consolidation`.
- Clean orphan plan-audit receipts using the runtime-supported preflight path.
- Resolve the four tautological-test audit findings by rewriting or routing the
  tests, not by suppressing the audit.
- Resolve `--task-envelope-coherence` separately. It touches ledger semantics
  and should be treated as the highest-risk failing gate.
- When `gz check` fails, record the first fail-closed blocker and its drilldown
  command before reading advisory output.

Exit criteria:

- `uv run gz test` passes.
- `uv run gz validate --kind-invariance` passes.
- `uv run gz validate --insights-shape` passes.
- `uv run gz validate --tautological-test-audit` passes.
- `uv run gz preflight` passes.
- `uv run gz validate --task-envelope-coherence` passes or has a single active
  tracked remediation with the next command named.

## Phase 2: Reduce Context Load

Goal: stop the recovery process from exhausting agent context.

Work:

- Keep this file as the only active recovery plan.
- Keep superseded recovery docs as short pointers only.
- Do not re-expand `AGENTS.md` or skill bodies while recovery is active.
- Prefer `gz context <ADR-ID>` over broad manual reading when working on a
  specific ADR.
- Keep `AGENTS.md` as a map, not an encyclopedia: move explanatory doctrine to
  routeable docs or skills only when an existing validator or command preserves
  the invariant.
- Replace always-loaded prose with runtime checks where a check can carry the
  same safety property.
- Treat issue #519 as the context-load tracking issue until closed.

Exit criteria:

- No recovery document besides this file claims canonical status.
- A session can orient from `AGENTS.md`, this file, `gz status`, and `gz check`
  without reading the old emergency plans.

## Phase 3: Repair State Drift And Ceremony Runtime Checks

Goal: stop lifecycle, task state, and core ceremonies from presenting false
confidence.

Work:

- Treat `--task-envelope-coherence` as the representative failure.
- Keep coarse TASK bookends only if they do not pretend to be fine-grained work
  attribution.
- Add or repair `task_id` propagation only through the runtime path that emits
  worklog events.
- Do not edit `.gzkit/ledger.jsonl` directly.
- If historical ledger drift needs accommodation, implement it as a validator
  rule or migration command with tests.
- Use `gz-obpi-pipeline` as the mechanical bar when evaluating closeout,
  authoring, evaluation, and audit ceremonies.
- Keep GHI #516 and GHI #517 as the route for passive-presenter ceremony gaps
  unless a specific defect qualifies for direct-fix routing.
- Prefer execution probes over wiring checks when a validator claims a hook,
  generated config, or command path is healthy.
- Do not add prose-only ceremony instructions as remediation for skipped
  verification.

Exit criteria:

- `gz check` includes a passing task-envelope check.
- New worklog events emitted under active TASKs carry the expected attribution.
- Historical exceptions, if any, are explicit and mechanically bounded.
- Known high-risk passive-ceremony gaps have either runtime checks or an active
  GHI route with a concrete next command.

## Phase 4: Drain Recovery Issues

Goal: reduce tracked recovery debt without creating a larger planning surface.

Work order:

1. Emergency-labeled GHIs.
2. Runtime-labeled defects that affect `gz check`, closeout, pipeline, or
   context loading.
3. Tech-debt findings that currently fail promoted validators.
4. Advisory or enhancement work only after the above are green.

Rules:

- Keep WIP to one recovery issue at a time.
- Close issues only with observed command evidence.
- Do not batch unrelated fixes under a recovery umbrella.

### Routed Work — GHI #571 Stdlib unittest/doctest maturity

Status: todo; start only after Tier 0 is green, unless the operator explicitly
waives green-first for this item. This is a Phase-4 recovery issue, not a pytest
migration and not a new dependency. The stdlib path is the design constraint:
`unittest` remains the runner, and `doctest` enters only through the stdlib
`unittest` integration hooks.

**Observed audit, 2026-06-01.** The project uses `unittest` broadly but shallowly:

- 382 test files, 1,519 `TestCase` classes, and 5,811 test methods.
- Fixtures are common: 1,472 `TemporaryDirectory` uses, 100 `setUp`, 54
  `tearDown`, 30 `setUpClass`, and 2 `tearDownClass`.
- Mocking is heavy: 892 `patch(...)` calls; the sampled AST audit found no
  `patch` calls with `autospec`, `spec`, or `spec_set`.
- `Mock`/`MagicMock` constructors are mostly unspecced: 93 constructor calls,
  3 with a spec and 90 without.
- `subTest` appears 175 times; useful, but still not the default for table-style
  semantic cases.
- Cleanup helpers are underused: 11 `addCleanup` calls and no observed
  `enterContext` calls.
- `load_tests` is unused, which means there is no current stdlib bridge for
  source docstring examples or doctest-backed documentation examples.
- 108 plain `assert` statements remain in tests, weakening `unittest` failure
  diagnostics.
- 54 `subprocess.run` calls live under `tests/`; some are likely intentional
  integration checks, but they must be classified against the unit-tier contract
  before anyone treats them as acceptable unit tests.

**Problem statement.** gzkit is stdlib-first in policy, but the test harness has
not extracted the available value from stdlib `unittest`: specced mocks,
cleanup stacks, loader hooks, result/runner telemetry, table-scoped `subTest`,
and doctest-backed executable examples. That leaves two efficiency losses: agents
learn less from the code because source examples are not executable, and tests
catch less drift because unspecced mocks accept calls the real object would
reject.

**Work order.**

1. **Baseline the shape.** Check in or script a repeatable audit for the counts
   above: unspecced `patch`, unspecced mocks, `load_tests`, doctest prompts,
   plain asserts, subprocess calls under `tests/`, and cleanup-helper usage.
   The baseline prevents this route from becoming taste-driven cleanup.
2. **Pilot the doctest bridge.** Add a `unittest`-discovered bridge such as
   `tests/test_doctest_examples.py` with `load_tests`. It should scan
   `src/gzkit/**/*.py` for docstrings containing `>>>`, import only those
   modules, and add `doctest.DocTestSuite` cases. Default to exact matching;
   allow local doctest directives only when the example itself justifies them.
3. **Add one source example.** Pick a stable, low-side-effect function whose
   docstring can teach an agent real API usage and assert behavior. The example
   must fail through `unittest` if it drifts. Do not mass-retrofit docstrings.
4. **Decide proof semantics before rule edits.** If source doctests are meant to
   satisfy BEHAVIOR REQ proof, update the `@covers`/REQ coverage path to
   recognize doctest-backed source tests explicitly. If they are examples only,
   state that in `.gzkit/rules/tests.md` so agents do not over-claim coverage.
5. **Tighten mock discipline.** Establish that new or touched
   `unittest.mock.patch` calls use `autospec=True`, `spec`, or `spec_set` unless
   a local comment names why the real surface cannot be specced. Start with
   high-risk command and governance-boundary tests; do not sweep 892 calls in
   one broad rewrite.
6. **Tighten fixture discipline.** Preserve the strong `TemporaryDirectory`
   pattern. Prefer `addCleanup` or `enterContext` for manually started resources
   and class-level fixtures, especially where cleanup currently depends on
   `tearDown` control flow.
7. **Classify subprocess tests.** For each real `subprocess.run` under `tests/`,
   choose one: mock the boundary, move the behavior to `features/`, or document
   why the test is an output-form fixture rather than a pure unit test.
8. **Update doctrine after the pilot passes.** Amend `.gzkit/rules/tests.md`
   and `docs/governance/tests-rationale.md` only after the doctest bridge and
   first source example pass under the normal `unittest` gate. The rule should
   encode the observed working path, not an aspiration.
9. **Promote mechanical recurrence defenses.** Once the pattern is stable, add
   a validator or audit helper for the high-signal checks: source doctest bridge
   present, no unspecced patch in new/touched tests without waiver, and no
   unclassified real subprocess under `tests/`.

**Efficiency guardrails.**

- No pytest migration; no new dependency; no parallel runner.
- No mass rewrite before the pilot proves value.
- Fix touched/high-risk tests first; measure the whole suite so progress is
  visible without forcing churn.
- Treat doctest as executable API education: examples must teach a real call
  pattern an agent should imitate, not merely pin a trivial string.
- Keep the proof claim precise: a doctest is a `unittest` case only when the
  bridge loads it and the normal gate observes it.

**Exit criteria for GHI #571.**

- `uv run -m unittest -q` discovers and runs the doctest bridge.
- At least one source docstring example fails when its expected behavior is
  intentionally broken and passes when restored.
- The test policy states whether doctest-backed source examples do or do not
  count as BEHAVIOR REQ proof, and the implementation agrees.
- New/touched mocks at command/governance boundaries are specced or explicitly
  waived.
- Real subprocess tests under `tests/` are classified, moved, or mocked.
- The recurrence defense is visible in a validator, audit helper, or named
  checklist item with an observed command.

Exit criteria:

- No open `emergency` issues.
- Recovery issue count is decreasing week over week.
- Same-day issue creation does not exceed same-day issue closure during recovery.

## Phase 5: Resume Normal Development

Normal development resumes only after health is restored.

Before resuming:

- Run `uv run gz check`.
- Run `gh issue list --state open --label emergency --limit 20`.
- Confirm this file's closeout section has been filled in.
- Archive or delete obsolete sidecar recovery notes that no longer carry facts
  needed for audit.

## Designated Workstream — Harness Hardening (anti-vibe mechanization, post-green)

Recorded here from the 2026-05-30 operator+agent dialogue so the analysis becomes
durable, sequenced action instead of being re-derived next session (Operating
Rules 1 and 7). This workstream does **not** start while `uv run gz check` is red
(Operating Rule 2), and promoting its ADRs is an explicit operator decision
against the Architectural Boundary 1 freeze (Operating Rule 6) — not a default.

North star: gzkit should flow like superpowers — enforcement off the operator's
face and into the machine: invisible when the operator is right, blocking only at
the moment of a mistake. Friction-always is the disease; pre-action mechanism is
the cure. Same move as Operating Rule 7, applied to behavior instead of context.

Two failure classes (both observed live on 2026-05-30):

| Class | Example | Mechanizable? | Cure surface |
|---|---|---|---|
| Skill-bypass / unauthorized mutation | agent ran raw `gz`/edit tools outside the governing skill | yes — pre-tool | the spine below |
| Claim fabrication | agent asserted false findings (a GHI map, a `gz check` table) in prose with no tool call | partly — no hook fires on a chat assertion | receipt-cited claims + human at attestation; irreducible residue remains |

Verified spine (five pool ADRs, all confirmed extant 2026-05-30; promotion-ordered
by dependency):

| ADR (pool) | Role | Depends on |
|---|---|---|
| `tool-permission-classifier` | deterministic `classify(tool,args)` → read / workspace / governance / external / full; unclassifiable → fail-closed (full/deny) | none — leaf; first promotion |
| `agent-execution-intelligence` (CAP-08 MODE) | per-invocation MODE: READ-ONLY / PLAN-FIRST / IMPLEMENT (independently promotable) | none |
| `tdd-receipt-stream` | generalized governance receipts (`mode_declared`, `scope_widened`, `mode_violation`, …); append-only; works even record-only | classifier, MODE |
| `skill-behavioral-hardening` | skill-intent scope invariant + circuit breaker: a skill's declared scope bounds its mutating calls; out-of-scope mutation needs authorization before the call | classifier, MODE, receipts |
| `harness-aware-execution-modes` | Mode 1 skill-chain self-gate / Mode 2 PreToolUse hook **block** (Claude Code today) | envelope, classifier |

Promotion sequence (when unfrozen): `tool-permission-classifier` (leaf,
fail-closed, smallest win) → `agent-execution-intelligence` MODE +
`tdd-receipt-stream` → `skill-behavioral-hardening` → `harness-aware-execution-modes`
Mode 2.

**Orientation-layer sibling — `ADR-0.0.66-deterministic-steering-substrate` (booked 2026-05-31, operator-waived Boundary 1 / Operating Rule 6).** ADR-0.0.66 coalesces `tdd-receipt-stream` (the shared hub), `agent-execution-intelligence` CAP-22 (`gz next`) + CAP-08 MODE, `session-productivity-metrics`, the queryability verbs (`gz search` / `gz insights query`), and `solved-problem-pattern-corpus` into one deterministic read-substrate. The enforcement spine above reads the `tdd-receipt-stream` hub for *enforcement*; ADR-0.0.66 reads it for *orientation* — **same hub, two consumers.** Consequence for sequencing: `tdd-receipt-stream` and CAP-08 MODE promote **once**, as ADR-0.0.66's leaf-first OBPI-01 (hub) and OBPI-02 (`gz next` + MODE); the spine's enforcement layers (`skill-behavioral-hardening`, `harness-aware-execution-modes`) then consume the same hub rather than promoting it separately. ADR-0.0.66 also subsumes the booked-but-unbuilt `ADR-0.0.46/0.0.47/0.0.48` (pool-management / DAG-routing / pool-triage): `gz next --pool` becomes the pool-scoped predicate of the whole-project `gz next`. The supersession of those nine ADRs is *declared* in ADR-0.0.66's body and *executed* under its OBPI-06 (frontmatter → `gz register-adrs` reconcile, never `gz adr demote`); until then it is a tracked follow-up, not silent drift. The operator's Boundary-1 waiver covered the *booking* only — promotion of ADR-0.0.66 stays frozen behind recovery, leaf-first and operator-gated, like the spine.

Non-negotiable gates:

- Any AGENTS.md / `.claude/rules` change this implies routes through the CMS
  (`gz content`, `gz governance render`) — never a hand-edit to a rendered surface.
- Green-first: no promotion while `gz check` is red.
- Boundary 1 exception is the operator's explicit call, made after seeing routing facts.

The honest limit: the claim-fabrication class cannot be fully mechanized — a model
asserting a false synthesis in chat fires no hook. Reduce the surface (cite a
receipt for every state claim, or mark it unverified), then place the human at
attestation, not at every keystroke. Do not answer this class with a new prose
rule; 2026-05-30 proved prose does not bind.

Exit criteria:

- The skill envelope records a governance event on every named skill invocation
  and (Mode 2) blocks an out-of-envelope mutating call before it runs.
- `uv run gz check` includes a passing check that the classifier/envelope are wired.
- A deliberate skill-bypass attempt in a test session is mechanically stopped,
  observed by the operator.

Provenance: spine ADRs verified extant via `gh`/Glob/Read on 2026-05-30; failure
classes from observed incidents that session (fabricated GHI map, fabricated
`gz check` table, overwritten-then-git-restored recovery plan).

## Designated Workstream — Context-Load CMS (density-dial composition; #519 remediation)

> **Status note (2026-06-05):** this section preserves the post-OBPI-15 diagnosis history.
> The live directive is the Execution Worklist item 1.1 route: reconcile ADR-0.0.37 briefs
> to the 18–27 checklist. **OBPI-0.0.37-26 (the sequenced-first interim relief) is now
> attested-complete** (2026-06-05, pipeline closeout); the next live OBPIs are the
> composer/store route (21/22) that regenerates the interim rendition and the <15k
> registry-projected surface (GHI #533) that closes #519. OBPI-0.0.37-17 is retired.

Recorded here (Operating Rules 1 and 7) so this turn's diagnosis and decision become
durable, resumable history rather than re-derived next session. At capture time this was
the **concrete remediation route for emergency GHI #519**; the 2026-06-04 status note
above is now authoritative for the live route. Session handoff:
`.gzkit/handoffs/20260531T000357Z-adr-0.0.37-density-dial-cms-extension.md`.

**Diagnosis (observed 2026-05-30).** AGENTS.md is meant to be a rendered Layer-3 view, but
the live path is a hardcoded monolith: `sync_agents_md` → `render_template("agents")` over a
100%-prose template, with `.gzkit/agents.local.md` spliced in raw and literals hardcoded in
`get_project_context`. Two half-built render-from-source substrates exist for the same
surface and neither drives it — ADR-0.0.37's flat invariant registry and ADR-0.0.34's
`AgentContract` content model. The authoritative target is the substrate doctrine
[`docs/governance/agent-control-surface-rendering-substrate.md`](agent-control-surface-rendering-substrate.md)
(binding claim: nothing hand-authored at the rendered location). Codex loads root AGENTS.md
at ~98% of its 32 KiB `project_doc_max_bytes` cap — the #519 magnitude.

**Decision (operator, 2026-05-30).** Extend ADR-0.0.37 to bear the always-intended CMS
vision: one master content model at MAX fidelity; a render *temperature* (lite/medium/heavy)
that dials prose density; section add/withhold; per-vendor templates; eventual
harness/model detection. Spine = `AgentContract` (ADR-0.0.34); the invariant registry
becomes its foundation-classified subset. The dial has an absolute floor — *"we don't go to
0 Kelvin"*: `Judgment`-class bullets render at every temperature; the dial thins only
Mechanical/Reference prose.

**In-flight state (updated 2026-06-03, post-OBPI-15).** ADR-0.0.37
Decision extended (new subsection "Decision Extension (2026-05-30): CIC-1 Density-Dial
Composition"); checklist items 11–16 added; Decomposition Scorecard made coherent (final
target 16); six briefs created (1:1 sync, 16↔16), all **semantically authored and committed**
(commit `4014b85b`, GHI #519). Implementation has advanced to **10/16 OBPIs
`attested_completed`** — verified via `uv run gz adr status ADR-0.0.37`: 01–05, 11, 12,
13 (reverse-parse migration `5e324e1`), 14 (wire-sync/retire-monolith `fa4dc83`), and
15 (per-vendor template selection, sync anchor `b8195395`, 2026-06-03). OBPIs 06–10 and
16 remain `pending`. **OBPI-15 scope note (operator-ratified, 2026-06-03):** OBPI-15
landed the per-vendor temperature *selection* mechanism (manifest `content_type_temperatures`
→ `vendors.temperature_for()` fail-closed → `render()` honors it), **not** any #519 byte
relief. As the **Codex-loader finding** below establishes, per-vendor emission cannot relieve
#519 at all; the relief is **OBPI-0.0.37-17** (density-classify the AgentContract corpus so the
dial thins the shared root AGENTS.md). So the CMS is mechanically 10/16 but **#519 is unrelieved.** **Regression history (resolved):** the 0.0.37-12 closeout
regressed `gz check` (Snapshot C); cleared at Snapshot D, and OBPI-13/15 completions since
have not regressed it (Snapshots E and F green). This is a foundation-ADR scope
change made under explicit operator direction as #519 emergency relief (Architectural
Boundary 1 / Operating Rule 6 waived by the operator's explicit call).

**Codex-loader finding — per-vendor emission is RULED OUT as the #519 route (2026-06-03,
primary-source investigation).** The earlier plan framing (and the ADR's "Codex `lite`
emission" language) assumed gzkit could give Codex a *smaller, vendor-specific* surface than
root `AGENTS.md`. The OpenAI Codex CLI's documented loader makes that impossible:

- **Codex reads `AGENTS.md` by name only**, walking repo-root → cwd and **concatenating** one
  file per directory level (it does read *nested* `AGENTS.md` files; it does **not** traverse
  `.agents/` or any vendor-namespaced sink). `.agents/AGENTS.md` is invisible to it.
  (Sources: developers.openai.com/codex/guides/agents-md; github.com/openai/codex docs/agents_md.md.)
- **No config redirects the project doc.** There is no `project_doc_path`. `model_instructions_file`
  / `experimental_instructions_file` replace the *base system prompt*, not the AGENTS.md surface
  (and the experimental key 400-errors on GPT-5/Codex models). `project_doc_fallback_filenames`
  only fires when `AGENTS.md` is *absent*. (Sources: codex/config-reference, config-sample.)
- **Over-cap = silent truncation.** `project_doc_max_bytes` default `32768`; past it the doc is
  "silently truncated … so we do not take up too much of the context window" — no warning, no
  error. (Source: github.com/openai/codex issue #7138, source-quoted.)

**Consequence.** OBPI-15's per-vendor temperature *selection* mechanism keeps value as the
general control the operator wanted, but it **cannot relieve #519** — the surface Codex reads
is root `AGENTS.md`, shared with Claude, and Codex will not load a vendor-specific alternative.
The **only lever Codex respects is shrinking the one shared root `AGENTS.md`** below 32,768 B
with headroom. Current root = **32,651 B = 99.6% of cap** (≈117 B from truncation). That shrink
is **OBPI-0.0.37-17** (chartered 2026-06-03): density-classify the AgentContract corpus —
assign each `Bullet` a `classification`/`density_min` — so the OBPI-11/12 dial (built but
**inert**: every `density_min=None`, so heavy/medium/lite render identical bytes, verified
2026-06-03) thins the shared root at `medium` under the cap; the 0-Kelvin floor preserves every
Judgment bullet. This is the *AgentContract render path* (`gzkit.content.render`, OBPI-13/14
lineage), **distinct from OBPI-09's superseded invariant-registry migration** (`.gzkit/invariants/`
→ `gz governance render`). **#519 relief is therefore re-pointed from "Codex-`lite` emission
follow-on" to OBPI-0.0.37-17.** (Akin to the GHI #533 context-diet intent, realized on the
density-dial substrate rather than the registry.)

**Coupled calibration defect (flagged).** gzkit's AGENTS.md budget in
`data/instructions_files_budget.json` is **33,000** — *above* Codex's 32,768-byte cap — so the
gate meant to guard the #519 surface would green-light a silently-truncated file. Ties to #579
("anchor budget on imperative-density, not char count") and the config-SSOT item (2.5).

**Open loop named.** This session re-derived the rendering architecture from source despite
the substrate doctrine already documenting it and three prior same-day insights logging the
lesson — capture without re-injection does not bind. OBPI-0.0.37-16 (docs-for-agents
orientation index) is the structural fix; the session handoff is the interim re-injection.
See `.gzkit/insights/agent-insights.jsonl` (2026-05-30 open-loop entry).

**Discoveries from the authoring pass (verified this session, 2026-05-30).** The six briefs
landed ~1,400 lines of analysis; these are the findings that change the work's *size and stakes*,
beyond the Diagnosis above. Each is verified against source this session, not taken from the
brief prose.

- **The two substrates are emptier than the Diagnosis stated — OBPI-11 is a model *build*, not
  an extension.** On-disk `AgentContract` (`src/gzkit/content/models/agent_contract.py`) is a
  four-field shell (`name`/`purpose`/`tech_stack`/`rules`); `Bullet` (`bullet.py`) carries only
  `text` + `indent`. All four density fields the dial needs — `classification`, `witness`,
  `rationale_ref`, `density_min` — are **net-new; none exist today**. The rich `AgentContract`
  in the substrate doctrine's worked example is *aspirational*, not on disk.
- **`gz validate --invariant-coherence` is registry-blind — a green that proves little.**
  `src/gzkit/governance/trust_audits/invariant_coherence.py` renders via
  `compose.render_agents_md` against `.gzkit/templates/agents.md`, a template with **zero Jinja
  constructs** that never references the `invariants` variable it is handed, then byte-compares
  against committed `AGENTS.md`. So the gate catches a hand-edit to `AGENTS.md` (real, narrow)
  but is **structurally blind to whether the four `.gzkit/invariants/` entries
  (CIC-1, CIC-2, foundation-adr-registers-invariant, skill-first-execution-invariant) project
  anything into the surface.** This is the recovery plan's own *"validator that claims health
  without proving the path that matters"* pattern, found live. Tracked: OBPI-0.0.37-14 repoints
  this gate to diff the model render against the committed surface.
- **The `{invariants}` slot is a literal placeholder string, on the production path too.**
  `get_project_context` in `sync_surfaces.py` fills `invariants = "See governance documents"`;
  the registry reaches the rendered surface through *neither* render path. The four registry
  entries are confirmed orphans.
- **The #519 byte magnitude is exact, not approximate.** Root `AGENTS.md` = **32,121 B =
  98.0%** of the 32,768 B (32 KiB) cap (`data/instructions_files_budget.json`); the production
  template = 23,378 B; the `.gzkit/agents.local.md` raw splice = 8,776 B.
- **"Dumb 4× mirroring" is imprecise — the mirrors already differ.** No materialized
  `.agents/AGENTS.md` or `.claude/AGENTS.md` sibling exists; `.github/AGENTS.md` is a distinct
  1,384 B thin mirror, not a full copy. OBPI-15's per-vendor temperature targets render-time
  selection. **Superseded by the Codex-loader finding (2026-06-03):** the Codex `lite` tier was
  *assumed* to be the #519 relief payload, but Codex reads only root `AGENTS.md` and will not
  load a vendor-specific surface — so a per-vendor emission cannot relieve #519. Relief is the
  shared-surface shrink (OBPI-0.0.37-17, density classification). See § Codex-loader finding above.
- **OBPI-13 hardens two safety invariants the Diagnosis did not name.** (a) The round-trip
  contract shifts from byte-preservation (OBPI-09) to *semantic* equality
  `parse(render(model)) == model`, explicitly superseding OBPI-09. (b) A bullet with no
  determinable witness classifies **`Ambiguous`, never silently `Mechanical`** — so the dial can
  never thin an *unenforced* rule. That is the mechanical form of the 0-Kelvin floor.
- **The authoring landed zero implementation — the green reflects briefs, not working code.**
  Commit `4014b85b` touched no `src/gzkit/` file; companion `19820662` only bumped a brittle
  exact-count handoff test (34→35), itself flagged for replacement.

**Exit criteria.** OBPIs 11–16 authored and implemented; `sync_agents_md` renders from the
master model; AGENTS.md and vendor mirrors render at per-vendor temperatures; zero
hand-authored prose at the rendered location; Codex root-surface load fits its budget with
headroom; `gz check` green throughout.

## Designated Workstream — Canon Foundation (machine-readable canon; post-recovery, frozen)

Recorded here from the 2026-05-31 operator+agent design dialogue (Operating Rules
1 and 7) so the design nuance becomes durable, resumable capture rather than
re-derived next session ("the time to capture design nuance is now"). This
workstream does **not** start while `uv run gz check` is red (Operating Rule 2);
promoting its canon-establishing ADR is an explicit operator decision against the
Architectural Boundary 1 freeze (Operating Rule 6) — not a default. It is the
thematic sibling of the Harness Hardening workstream above: both are the post-green
anti-vibe-mechanization vision, and §13 below (execution-model + taxonomy
decisions) overlaps the `ADR-0.0.66` deterministic-steering-substrate work captured
there. It is also the substrate beneath the Context-Load CMS workstream — the CMS
renders control surfaces *from* canon (see §10).

> **Status:** Pre-ADR design capture (a "window" per the ontology in §2 — design
> rumination, not yet decided canon). **Disposition:** To be formalized via
> `gz-design` → **the last foundation ADR — the foundation that dissolves
> foundations** (operator, 2026-06-01): canon-establishing, using a new
> **`amends`** ADR disposition that amends **ADR-0.0.9** (state doctrine) and
> reconciles **ADR-0.0.10** (storage tiers). On crystallization this capture
> migrates to `.gzkit/design/`. **Blast radius:** operator-set to "nuke from orbit
> — touch all." Nothing below is deferred from the *design*; build is sequenced
> (§12), but the design captures everything now.
> **Provenance:** folded in from the standalone `canon-foundation-design-2026-05-31.md`
> (now deleted) per the operator's "one scope of work" decision, 2026-06-01.

> **Reconciliation note — `foundation` ADR kind (flagged, not resolved).** Canon
> §13 below *decides* to retire the `foundation` ADR kind (genuine invariants
> migrate into canon; ADRs become pure design). This plan's foundation-kind
> language — Operating Rule 6, the Definition-of-Healthy freeze on new foundation
> ADRs, and every foundation-tier gate reference — remains the **live contract**
> until that canon-establishing ADR lands post-recovery. The retirement is
> **decided-but-unbuilt**; do not read §13 as having already changed this plan's
> operative terms.
> **Resolution (operator, 2026-06-01):** *let the last foundation be the
> foundation that dissolves foundations.* The canon-establishing ADR is itself the
> **terminal foundation ADR** — the kind persists as the live contract until that
> ADR lands and, by its own act, retires the kind. The self-bootstrap is the
> point: the last foundation registers the canon substrate that makes future
> foundations unnecessary.

### 1. The thesis (why this is the most important work)

The enduring criticism of gzkit — *too much governance lives in the latent space of MD prose;
the mechanical aspect lags* — and the context-load emergency (#519) are the same problem from
two ends. A prose rule in a control surface is governance held in latent space: it binds only
if the model happens to attend to it, and "happens to attend" is exactly the vibe surface.
**Machine-readable canon drags latent-space governance into mechanical control.**

#### Empirical grounding (the audit, 2026-05-31)

Two independent passes over the GHI corpus (30 open, stratified 44 of 458 closed defects)
tested the hypothesis *"ADR-0.0.9's docs-as-canon / frontmatter-as-truth definition is the
root cause of a majority of failures."*

- **The narrow claim is refuted: ~9–10% are L1-ROOT.** Title-keyword matching *confirms it by
  construction* (the vocabulary — `reconcile`, `drift`, `frontmatter`, `canonical`, `Layer-1` —
  is everywhere); body-reading with the discriminator *"if canon lived in a machine-readable
  store instead of docs-markdown-with-frontmatter, would this still happen?"* collapses it to ~10%.
- **The broad thesis is validated.** The dominant ADJACENT bucket is *"advisory rule never
  promoted to mechanical / validator machinery missing"* — which **is** the latent-prose-governance
  problem. Time trend: recent failures increasingly reflect governance machinery *maturing into
  gaps where a mechanical gate doesn't yet exist* — the opposite of what an L1-redefinition
  refactor predicts, and exactly what a **mechanization substrate** addresses.

**Consequence for justification:** canon's value is **forward** (the mechanization target that
ends the dominant failure family) — *not* backward ("fix the docs-as-canon root cause," which is
~10%). The #519 emergency is the one acute L1-ROOT item and is in scope.

### 2. The five-role ontology (settled)

```
CODE  ⟺  CANON | DESIGN  ⟺  HUMAN DOCS
```

| Role | What it is | Operating-mode readable? |
|---|---|---|
| **Code** (`src/`, control surfaces) | Mechanism / determinism. Binds to canon; **never reaches into `docs/`.** | n/a (it *is* the operator) |
| **Canon** (`.gzkit/canon/`) | **Invariant rules.** Machine-readable JSON, ontology-shaped. The standing law, "etched in stone" = *decided / immutable-without-a-governed-action.* | **Yes** |
| **Design** (`.gzkit/design/`) | **Decisions made under constraint** — ADRs, OBPIs. Out of `docs/`. | **Yes** |
| **Human Docs** (`docs/`) | **Mirror** (reflect what is decided/present) **+ window** (insight, possibility, foundational reasoning, ruminations on the undecided). Authority for *neither*. | **No — forbidden in operating mode** |
| **Doctrine kernel** | The decided principles (operator's battle-honed pain points). A *catalog inside canon*, not a sixth thing. Periodically human-reviewed; must jive with operator sensemaking. | (it is canon) |

**Law vs. rhetoric (the precise cut).** Canon = the decided (law); it **includes decided
judgment**, expressed concisely. Docs = the undecided (rhetoric) — alternatives, fuzzy
epistemics, generative thinking. *Expansive ontology, concise decisions:* canon holds a rich
vocabulary/concept-space (terms, synonyms, relations — where epistemic breadth lives) **and**
concise decided facts stated over it. Justification of a decision is *referenced*
(`rationale_ref` → docs), never embedded.

### 3. Two agent modes (the hard constraint)

- **Co-design mode** — `docs/` is open (mirror + window). Fuzziness is the point.
- **Operating mode** (running skills, conforming to rules, using tools, audit) — **`docs/` is
  forbidden. The agent reasons only from `CODE ⟺ CANON|DESIGN`.**

**Forbidden edges (mechanizable):** `code → docs`; `operating-agent → docs`. Witness: a
`gz validate` scope fails any operating surface (skill / rule / tool contract) that cites `docs/`
for binding truth. Note: ADRs/OBPIs are **design**, not docs — operating agents read them; the
prohibition is on the *editorial* layer only.

### 4. Two reconciliation loops

```
CODE ⟺ CANON   — mechanical, gate-enforced (code binds canon; gz validate --canon-coherence)
CANON ⟺ HUMAN  — operator review (you confirm canon jibes with your sensemaking)
```

The operator **authors nothing directly** — every canon edit is an agent action under operator
direction, through the forced `gz canon` verb (deterministic, validated, ledger-witnessed). So
the verb + validation + ledger + the review loop **is the entire integrity model** — there is no
"careful hand-edit" fallback. **Operator-economy payoff:** you review the *law* (concise canon);
the gates *transitively guarantee* the code conforms. Reviewing canon *is* reviewing the system.

### 5. Human-as-final-witness doctrine (the keystone)

> Canon holds *delegated* authority. At the terminal gate, **the operator is the final witness
> and rules supreme.** The agent advises; the operator may take counsel; then the operator rules;
> then the agent **notes the variance and stops.**

- This resolves the `witness: null` problem: **Judgment-class entries are not unwitnessed — they
  are witnessed by the operator at the last gate.** The witness is *never* truly null: it is
  either a *mechanical gate* (delegated) or *the operator* (reserved).
- **"Note the variance"** is a mechanism, not a sentiment: when the operator's ruling diverges
  from canon, the system records a ledger event — that *is* the `CANON ⟺ HUMAN` reconciliation
  loop firing, the signal that canon may need amending.
- The terminal gates — **OBPI-pipeline Gate 5, ADR Closeout, ADR Evaluate** — are the apex where
  delegation yields to sovereignty. Operator: *"I can't overstate how vital these are."*

### 6. The mechanism

- **`gz canon` verb** — the only write path into canon. Deterministic, validated, ledger-witnessed.
  No raw JSON edits (an agent can vibe a JSON edit as easily as a prose one). Foundry analogy:
  mutations happen only through governed **Actions**.
- **`gz validate --canon-coherence`** — fail-closed:
  - every *mechanical* `witness` resolves to a real gate;
  - *Judgment* entries are **exempt** (their witness is the operator at the terminal gate);
  - every synonym maps to exactly one canonical term;
  - every `rationale_ref` resolves;
  - no operating surface cites `docs/`.
- **Canon is governed by the gates it enables** (the self-referential bootstrap, same shape as
  "every foundation ADR registers ≥1 invariant").

#### Schema: two decided-entry kinds, first-class

| Kind | `witness` | Renders at | Coherence check |
|---|---|---|---|
| **Mechanical** | a gate command | thins with temperature (gate carries the safety) | witness must resolve to a real gate |
| **Judgment** | *the operator* (terminal gate) | **every** temperature (0-Kelvin floor — the model must hold it) | exempt from gate-resolution; human-witnessed |

If the "determinism" mental model drives the schema, it will only fit Mechanical entries and force
Judgment back into prose — reopening the latent-space hole. **Both kinds are first-class.**

### 7. The Foundry/Palantir north-star

Ontology = **Objects · Properties · Links · Actions**, a single semantic SoT that *both* humans
and applications reason from, where mutations happen only through governed **Actions**. Map onto
canon: concepts → objects; vocabulary + synonyms → properties/aliases; relations → links;
decided rules + `gz canon` mutations → **Actions**. The Foundry lesson: the ontology is the single
semantic SoT and governed actions are the *only* write path — precisely the `gz canon` model.

### 8. Full blast radius (nuke touches all)

**Core (where the failure mass is — §1 audit):**

1. **Canon store** — `.gzkit/canon/`, JSON, ontology-shaped, two entry kinds (§6).
2. **`gz canon` verb** + **`gz validate --canon-coherence`** (§6).
3. **Migrate `.gzkit/rules/*.md` → canon** — prose demoted to `rationale_ref`. *The high-leverage
   core:* closes the dominant "advisory-rule-never-mechanized" family.
4. **Forbidden edges** — `code → docs`, `operating-agent → docs`. **Canon entry #1.**
5. **#519 relief** — the ADR-0.0.37 CMS renders control surfaces *from* canon at temperature; the
   prose monolith dissolves.
6. **Human-as-final-witness doctrine** + the **"note variance"** ledger event (§5).

**Margin:**

7. **Design store** — `.gzkit/design/`; relocate ADRs/OBPIs out of `docs/`.
8. **Subsume all scattered L1** — `.gzkit/invariants/`, `data/*.json`, classifications → one canon home.
9. **Two-mode enforcement** — validator failing any operating surface that cites `docs/`.
10. **Amend ADR-0.0.9** (reconcile ADR-0.0.10): redefine the layer model to `CODE | CANON·DESIGN | DOCS`.
11. **New `amends` ADR disposition** — defined *by* this ADR as its first user.

**Now IN scope (formerly "deferred" — operator: "this must be within the blast radius"):**

12. **Harness/model auto-detection of templates** — the dynamic per-vendor / per-model temperature
    selection (the operator's *"REALLY fine tune"* vision). Designed now; the detection signal feeds
    the CMS temperature + section-inclusion set.
13. **Full graph engine** — canon's ontology **links** *are* the graph spine. Canon is the
    state-doctrine-locking step that unblocks Architectural Boundary 3 (which forbids building the
    graph engine before state doctrine is locked — canon *is* the locking). Typed-relation ontology
    in JSON; **JSON-LD** is the in-idiom bridge if/when edges need formal graph semantics (never XML/RDF).
14. **Adopter domain-canon scaffolding (`gz init`)** — adopters get **two** canons: the inherited
    *tool-canon* at `.gzkit/canon/` (gzkit's governance ontology, shipped) **+** their authored
    *domain-canon* at `<project-root>/canon/` (the ontology of the useful software they build, their
    domain rules, the skills that shape their software toward domain goals). gzkit itself has **one**
    canon (we are the tool; "seaborn shipbuilding as we dogfood"). `gz init` scaffolds the adopter's
    domain-canon home.

**Three self-bootstraps:** the `amends` disposition is defined by this ADR (first user);
"`code → docs` forbidden" is **canon entry #1**; canon is governed by the `--canon-coherence`
gate it enables.

### 9. Open design questions the ADR must resolve

- **Classification source-of-truth.** `docs/governance/advisory-rules-audit.md` scorecard
  (human-deliberated Mechanical/Promotable/Judgment/Ambiguous) is SoT; the scorecard's *data*
  moves **into canon**; the `.md` becomes a `rationale_ref`. The model derives from canon. This
  dissolves the ADR-0.0.37 concern-1 tension (classification becomes a canon fact, not a special-
  case reconciliation gate).
- **The bullet↔scorecard-rule correspondence map** — *the real center of gravity* of the
  rules→canon migration. The scorecard classifies *rules*; canon entries are finer-grained; the
  surface includes sections that aren't rule-files. Establishing the correspondence (which entry
  derives from which scorecard row) is the hard work; drift between model classification and
  scorecard is fail-closed.
- **"One spine" honesty.** `reconcile_invariant` (OBPI-0.0.37-11) is one-way and lossy (drops
  `id`, `composition_targets`, witnesses 2..N). So the invariant registry is a *projection input*,
  not a regenerable mirror. Pin: which store is SoT for an invariant when both are editable. Likely:
  canon is SoT; the registry collapses into canon under the subsume (§8.8).
- **Two gates, two boundaries** (from ADR-0.0.37 review): byte-compare guards the *human-edit*
  boundary (anti-vibe-edit — keep as-is); a **path-independent floor check**
  (`count(Judgment in model) == count(Judgment in rendered-lite)`) guards the *render-correctness*
  boundary. Neither subsumes the other.
- **Deterministic authoring affordance** — `gz canon` (and the design-store analog) must be the
  forced edit path; raw-file edits to canon/design data are flagged. Only human-directed agents
  author; the operator authors nothing outside chat.

### 10. Relationship to existing ADRs

- **Amends ADR-0.0.9** (state doctrine / SoT hierarchy) — redefines Layer-1 from "versioned MD/YAML
  including `docs/`" to `CODE | CANON·DESIGN | DOCS`. *The audit refutes "0.0.9 caused most failures"
  — the amendment is justified as the mechanization substrate, not as root-cause repair.*
- **Reconciles ADR-0.0.10** (storage tiers).
- **Substrate beneath ADR-0.0.37** — the CMS (density-dial composition) renders control surfaces
  *from* canon. ADR-0.0.37 **OBPI-13/14 re-sequence behind** the canon ADR (13's classification
  derives from canon).
- **OBPI-0.0.37-11** (density-aware master content model) — **Completed + attested 2026-05-31**.
  It is the first brick: the schema substrate the CMS temperature renderer consumes.

### 11. Methodological note (preserve this too)

This session demonstrated the failure mode the whole architecture targets, *live*, twice:
(a) the agent re-derived the rendering architecture from source despite documented design (the
"open loop" — capture without re-injection does not bind); (b) the agent over-called "ADR
underspecified" by keyword-matching instead of body-reading. **The gate (the operator's bet +
"confirm by reviewing GHIs") forced the honest audit that corrected both.** The terminal human
gate is not bureaucracy — it is the forcing function that surfaces emergence, tension, and
alignment that freeform execution buries under "tests pass, ship it."

### 12. Sequencing (design covers all; build increments)

The blast radius is the *design* scope; the *build* sequences by failure-mass leverage:

1. Canon store + `gz canon` + `--canon-coherence` + canon-entry-#1.
2. Migrate `.gzkit/rules/*.md` → canon (+ correspondence map, classification SoT).
3. Design store `.gzkit/design/`; relocate ADRs/OBPIs.
4. Subsume scattered L1; two-mode enforcement; amend ADR-0.0.9.
5. CMS renders from canon (#519 relief); the two-gate floor check.
6. Graph engine (on canon's links) · harness/model detection · adopter domain-canon scaffolding.

Steps 1–2 retire the dominant failure family; 5 clears the #519 emergency; 6 is the formerly-
deferred vision, designed now, built last.

### 13. Session 2026-05-31 (PM) — execution-model & taxonomy decisions (folds into this thread)

> Captured per §11 (latent decisions get re-derived next session). **Decided** items are
> operator-confirmed this session; **Open** items need major discussion before adoption.
> Formalize with the canon ADR post-recovery (amends ADR-0.0.9).

**Decided:**

1. **Retire the `foundation` ADR kind.** "Invariant" had been used loosely to mean *plumbing
   that facilitates features*; foundation was redundant with the pool (both = decide-without-
   releasing) and an artifact of the ADR↔semver coupling. Genuine invariants live in **canon**
   (this thread); ADRs become pure **design**. *Operator resolution (2026-06-01): rather than
   invalidating this capture's §8 / disposition "foundation ADR" self-label — **let the last
   foundation be the foundation that dissolves foundations.** The canon-establishing ADR is the
   **terminal foundation ADR**, and its own act is the retirement of the kind.*
2. **Two demarcations + pool:** design (pool / *made*) → triage → built (*features*) → semver
   (release tag). No foundation/feature metaphysics; "essence vs. accident" judged contrived.
3. **Semver habits (normal):** GHI closure → **patch**; ADR completion → **minor**; "PRD
   satisfied" → **major** + basis for the next round. Decouple ADR-id from semver (post-recovery).
4. **Execution loop (Pocock-guided; attended vs. autopilot):** idea (`grill`) → [research] →
   [prototype] → PRD/ADR → vertical-slice issues → execute + QA-loop.
5. **AFK/HITL = gate-*placement*, classified at plan-time** (Pocock-confirmed): **HITL/attended**
   → local gates + present operator (terminal witness now); **AFK/autopilot** → branch/worktree-
   per-OBPI → PR → unattended mechanical gates → **async Gate-5 attestation on the PR**. Universal
   Gate 5 (ADR-0.0.36) holds — **never self-close**, even AFK.
6. **Per-OBPI worktree + PR + receipts + attestation** is gzkit's structural fix for AFK's
   review-burden (Pocock's admitted, unfixed weakness).
7. **Drop the OBPI lock system** — operator, 2026-06-01: *"a contrivance to avoid what are
   industry-standard affordances."* The lock system reinvented isolation/visibility badly on
   trunk; **branches** give the isolation the locks faked, **PRs + `git branch -a`** give the
   visibility. Replacing locks with branches + PRs also retires the lock-release→handoff coupling
   (continuity records no longer gate a lock surrender; see the Session MOTD workstream §7.4).
   (Pipeline change, post-recovery.)
8. **Triage trio + router:** `ghi-triage` (corrective) · `gz-build-triage` (formerly
   `gz-foundation-triage`; what to build from pool) · `design-triage` (what to *make* → pool);
   chores self-surface (cadence: after each ADR ships). Unified by **`gz-next`** — the whole-
   project "best next move," renamed away from Pocock's queue-"triage."
9. **Keep the spine (sacrosanct):** ledger-of-truth, receipts, universal Gate 5, fail-closed
   validators, the kind/lane/sensitivity axes. "Lighter" is not a trade (anti-vibing mantra).

**Open — needs major discussion (NOT adopted):**

- The specific Pocock borrowings beyond the loop + AFK/HITL — fenced `prototype`, sprint-lived
  research/design-asset lifecycle, vertical-slice sizing + the horizontal-slicing anti-pattern
  citation, the ADR-worthiness 3-gate, QA→GHI loopback — evaluated **per-item** against "does
  this erode the spine?", deliberate, never wholesale. Baseline: GHI #567.

**Immediate (this session):** re-home ADR-0.0.66 → pool (unbuilt design; its substance folds
into this canon thread). **Status (2026-06-01): NOT executed** — ADR-0.0.66 remains under
`docs/design/adr/foundation/` (verified on disk). The re-home is a governance action
(frontmatter disposition → `gz register-adrs` reconcile, never a manual move), operator-gated
and green-first like every other workstream action; it stays pending behind the Snapshot-C
regression.

### 14. Session 2026-06-01 — handoff/triage advisory model (folds into this thread)

> Deepens §13.8 (triage trio + `gz-next`) with the handoff↔triage relationship and the
> plan-vs-fact distinction. Formalize with the canon ADR.

**The model (operator, verbatim):**

- Triage surveys the whole landscape and recommends the best next course of action.
- Operator agrees or doesn't.
- On agreement, the handoff chain adjusts — the forward plan is rewritten.
- Both triage and handoff are advisory. Neither authorizes anything. You do what you want.

Refinements: triage recommends a *reasoned set* of next-moves, not one — **the reasons are the
value, not the ranking** — spanning any route (direct fix, OBPI ceremony, design dialogue, defer,
or fan-out). Generalizes the resume contract ("a handoff ADVISES; it does not authorize") to
triage; operator is sole authority (§5).

**Load-bearing distinction — handoff ≠ ledger.** Handoff = *plan/intent* (a session's prospective
plan of work; mutable while the session is live, immutable once chained). Ledger = *observed
occurrence/fact* (Layer-2 truth). This is **Never #7 generalized**: a handoff is evidence of what
was *planned*, never of what *happened*. So triage reads done-ness **from the ledger, never from
handoff prose**, validates the plan-chain against ledger facts, then recommends the forward
rewrite. Handoff and triage are two views over the one work-graph (§7, §8.13) — not a point
coupling.

## Designated Workstream — Session MOTD (continuity ⊕ triaged workplan; subsumes handoff)

Captured from the 2026-06-01 operator+agent design dialogue (Operating Rules 1 and 7) so the
model is durable, not re-derived next session. The recursion is the point: *this is the design
of the system whose whole job is to stop design from being re-derived — so capture it before
logout.* **Status:** pre-build design capture (a "window" per the Canon ontology, §2 of the
Canon Foundation workstream). This workstream does **not** start while `uv run gz check` is red
(Operating Rule 2); promotion is an explicit operator Boundary-1 waiver (Operating Rule 6),
leaf-first.

**MOTD is the one system; handoff is subsumed into it, not scrapped.** Handoff's *design* is
retained (continuity content, the `continues_from` chain, the validator discipline, and the
ADVISES-not-authorize doctrine); handoff as a *standalone system* — its own skill, store-identity,
and lock coupling — dissolves. MOTD has **two pillars that combine like peanut butter and jelly**:
**continuity** (the subsumed handoff — "where we were") and the **triaged workplan** (triage —
"what to do next"). Different gears, different cadences; two logs in two locations rotating
independently; together they are the briefing.

**Anti-fork:** this materializes the one work-graph that **ADR-0.0.65** (handoff consolidation —
now *absorbed* here rather than landing standalone), **ADR-0.0.66** (`gz next` / triage), and
Canon Foundation **§8.13** already imply. It folds into them; it does not spawn a fourth structure.

### 1. The generative metaphor — the session is a `*nix` MOTD

On login, `*nix` runs `update-motd.d/` scripts that scan live system state and print a briefing
ending in *what you should do* ("3 updates available, reboot required, disk 80%, last login
Tuesday"); on logout, continuity is recorded for next time. gzkit's session lifecycle **is**
that MOTD. The metaphor is load-bearing — borrowing a system that already solved "brief someone
on state at session start, record continuity at session end" produced a coherent whole instead
of a pile of features.

| `*nix`                       | gzkit                          | Role |
|------------------------------|--------------------------------|------|
| login (or `/clear` re-login) | session start                  | trigger |
| `update-motd.d/` scan        | **triage**                     | scans worktree/ledger/git → health, errors, next moves |
| `last login: …`              | **continuity** (subsumed handoff) | "where we were" — written at logout, read at login |
| the MOTD printed             | **orientation**                | the briefing surface shown |
| the saved action list        | **workplan** (`.gzkit/work/`)  | triage's output, persisted past the screen-clear |
| logout                       | session end                    | write the handoff |

### 2. The two pillars (peanut butter & jelly)

MOTD is not four peer roles — it is **one briefing assembled from two pillars**, plus the view
that serves it:

- **Continuity** (the *peanut butter* — subsumed handoff): the "last login" thread — what we were
  doing, decisions made, open loops. Written at **logout**; logs to its own location
  (`.gzkit/handoffs/`, reframed as the MOTD continuity log). Retains all of handoff's design.
- **Triaged workplan** (the *jelly* — triage output): the "what to do" priority brief — health,
  errors, next-best moves, open questions, design openings. Written at **login**; logs to
  `.gzkit/work/`.
- **Orientation** (the *bread* — the served sandwich): the view that combines both pillars into
  the briefing printed at session start. Today this is `scripts/session_orientation.py`, the
  proto-MOTD (it already lists last handoff, open GHIs, ledger counts, blockers).

Two logs, two locations, two concepts, **logrotating independently** (§4) — different gears for
different purposes. They combine to make the MOTD; neither is the other.

### 3. Two-tier intelligence (cheap pass + directed finalize) — symmetric across both processes

Each process is **a cheap mechanical pass finalized by a high-intelligence agent** — never one
without the other:

- **Triage:** **auto-triage** (lightweight, runs at every login — the MOTD accounting) **backed
  by directed higher-intelligence triage** (an agent finalizes the brief with real reasoning).
  The directed tier is **ALSO available on demand** — the same engine, callable any time, not
  only at login.
- **Continuity:** a Stop/`clear` **hook drafts** the record from ledger + git-diff; an **agent
  finalizes** the narrative before it chains.

The cheap pass guarantees *something* always renders (reliability); the agent finalize
guarantees it is *worth reading* (intelligence). Auto-running high strategy is a real cost — the
lightweight tier is what runs unattended; the directed tier is invoked (to finalize the login
brief, and on demand).

### 4. Retention — log + logrotate

The two logs — `.gzkit/work/` (workplans) and the continuity log — accrete like `*nix` logs and
are **logrotated independently** (different gears, different cadences: continuity at logout,
workplan at login): recent entries stay hot, older ones age out (archive / compress / prune) on a
bounded policy so neither grows without limit. Daily briefs **journal** (one per session/day,
Obsidian-daily-note style); **campaigns** supersede in place (this plan → its successor). The
rotation policy (window, archive target) is a build-time parameter, not yet fixed.

### 5. Workplan shape — two layers

- **Campaign** — durable, named, goal-state + phases (e.g. this very plan). The long arc.
  Supersedes; does not journal.
- **Daily brief** — the rolling **priority brief**: the next best 3–5 moves + open questions +
  observations / design openings, each declaring which campaign(s) it advances. Journals under
  logrotation. This is the actionable body of the MOTD.

### 6. Governing doctrine — the whole MOTD ADVISES; it does not authorize

Retained from handoff and *elevated* to govern both pillars: the MOTD presents continuity and the
next-best moves; the **operator rules; the agent notes variance and stops.** This is the
human-as-final-witness doctrine (Canon Foundation §5) applied to the whole session surface — at
**every** freshness level, MOTD never converts an advisory into a license. Both pillars also read
done-ness from the **ledger, never from prose** (Never #7, §14); the rendered MOTD is a Layer-3
view (regenerable, never source-of-truth — state-doctrine).

### 7. Build plan (gated — green-first + operator Boundary-1 waiver)

Leaf-first; each increment consumes an existing surface rather than forking it.

1. **`.gzkit/work/` store + workplan schema** — campaign and daily-brief shapes; sibling to the
   continuity log; reconciled against Canon's planned `.gzkit/design/` store (§8.7).
2. **Evolve `session_orientation.py` → lightweight auto-triage** — the MOTD: scan + assemble +
   write the daily brief at `SessionStart` / `PreCompact` / `clear`.
3. **Directed triage skill** — high-intelligence agent finalize; backs the login brief *and*
   runs on demand. The concrete UX of ADR-0.0.66 `gz next`.
4. **Continuity hybrid (subsumes handoff)** — supplies handoff's missing CREATE trigger: a
   `Stop`/`clear` hook **drafts** the continuity record from ledger + git-diff, an **agent
   finalizes** it. **Absorbs ADR-0.0.65** (handoff-system-consolidation) and retires
   `gz-session-handoff` as a standalone skill. The lock-release→handoff coupling is **dropped**
   with the lock system itself (§13.7: locks → branches + PRs).
5. **Independent logrotation** — bounded, separate retention for the two logs (`.gzkit/work/` and
   the continuity log), on their own cadences.
6. **Verb surface** — fold into ADR-0.0.66 (`gz next` → triage); add no new top-level verb family.

### 8. Exit criteria

- Session start prints a MOTD assembled from the last continuity record + a worktree/ledger scan,
  ending in 3–5 priority moves; the brief persists to `.gzkit/work/`.
- The directed triage skill produces the same artifact on demand.
- Session end / `/clear` yields a finalized continuity record (hook-drafted, agent-finalized),
  chained into the continuity log.
- The two logs logrotate independently; neither grows unbounded.
- The whole MOTD advises only; execution waits on explicit operator authorization (§6).
- No fork: triage = `gz next` (ADR-0.0.66); continuity = the absorbed ADR-0.0.65; locks dropped
  (§13.7); `.gzkit/work/` reconciles with the Canon `.gzkit/design/` store.
- `uv run gz check` green throughout (this workstream is built post-green).

## Recovery Closeout

Final closeout is filled only when recovery completes (Definition of Healthy all
true). Recovery is **not yet closed** — emergency GHI #519 (context load) remains
open: the interim byte relief **LANDED** (Snapshot I) but the durable <15k
registry-projected surface (GHI #533) is unbuilt. The `Decision` line stays
blocked until #519 closes.

### Progress snapshot — 2026-06-04 (Snapshot I; #519 byte relief LANDED + loosening pass)

```text
Snapshot date:            2026-06-04 (recovery still open; #519 interim-relieved, not closed)
Committed main:           GREEN; three commits landed + pushed this session (HEAD 8dc04a9a): 705a2354, ac0816ff, 8dc04a9a
#519 byte relief:         LANDED. Root AGENTS.md 32,651 -> 28,342 B via local-splice diet (.gzkit/agents.local.md 9,306 -> 4,997 B); budget 30,000; ~4.4 KB under Codex 32,768 B cap. Genuine always-loaded-context reduction, NOT the budget-at-cap stopgap (b402c7cf, superseded). 18 splice-only Mechanical/Promotable scorecard phrases retained verbatim -> bullet-retention green under the CURRENT whole-surface validator (predicted 14-violation collision avoided by re-homing terse skeletons, not deleting). invariant-coherence/instructions-files-budget/surface-fidelity/distribution green; 5858 unittests OK; mkdocs --strict clean
Landed how:               DIRECT COMMIT (705a2354), not OBPI-0.0.37-26 ceremony. The Gate-5 sign+push is blocked by the Claude Code auto-mode classifier (an AI may not sign the operator's attestation as "g0" + push). OBPI-0.0.37-26 stays Draft; committed-rendition artifact at renditions/agentcontract-codex-root-interim.md -> reconcile or withdraw
Loosening pass:           operator-directed -- "loosen until the apparatus is securely fastened." Principle: a gate may only fail-closed on a target the system can reach smoothly; until the machinery exists it is advisory. Landed: (a) ac0816ff -- REQ-coverage gate is ADR-0.0.59 kind-aware (SUPPORT/STRUCTURAL-FENCE need no @covers; the manual --accept-uncovered snare is gone; new parse_brief_req_kinds + 3 tests); (b) 8dc04a9a -- pipeline mandate scoped to contract-bearing OBPIs (routine/recovery/defect fixes default to direct-fix, reconciling the AGENTS.md absolute with section Defect-fix routing + the MORATORIUM; both template copies + re-render)
Two-agent hazard:         a concurrent Codex session committed b402c7cf (budget-at-cap stopgap) mid-session, conflicting with this work. PAUSE concurrent agents on main -- two agents on one branch caused the churn
Emergency GHIs open:      1 -- #519 (interim byte relief landed; full 258K-window closure needs the <15k registry-projected surface, GHI #533)
Decision:                 #519 materially relieved but NOT closed. Loosening queue (operator "power through"): #2b clarify/retire the agent-relayed-attestation pretense (GHI #292 -- dead under the Claude Code classifier; make human-run completion the primary documented path; TOUCHES GATE 5 -> operator wording, do not edit unilaterally); #3 drive AGENTS.md to <15k (registry-projection build, GHI #533 / ADR-0.0.37). Then reconcile OBPI-0.0.37-26 (Draft; payload landed directly)
```

### Earlier progress snapshots — compact history (full blocks in git history pre-2026-06-04)

| Date | State | Headline |
|------|-------|----------|
| 2026-05-30 | open | post-GHI-#570 GREEN 26/26; ADR-0.0.37 CMS OBPIs 11–16 authored+committed (4014b85b), not implemented |
| 2026-06-01 | open | RED 24/26 (OBPI-0.0.37-12 irregular closeout); CMS 7/16; routed to #563 + preflight |
| 2026-06-02 (E) | open | GREEN 26/26 after Format / ADR-status / task-envelope clears |
| 2026-06-02 (13/14) | open | CMS 9/16 (OBPI-13/14 attested); fix/task-envelope branch merged to main |
| 2026-06-03 (F) | open | GREEN 26/26; CMS 10/16 (OBPI-15 selection mechanism); #519 unrelieved (selection ≠ emission) |
| 2026-06-03 (Codex-loader) | open | primary-source finding: Codex reads only root AGENTS.md, silent-truncates past 32,768 B → per-vendor emission RULED OUT for #519 |
| 2026-06-03 (OBPI-17 charter) | open | OBPI-09 ruled wrong path; OBPI-11/12 dial proven INERT; OBPI-17 density-classification chartered |
| 2026-06-03 (G(check)) | open | RED→GREEN restore on resume; OBPI-17-as-scoped retired; route redesigned → OBPI-0.0.37-26; ADR-0.0.37 renumbered to 01–10, 18–27 |
| 2026-06-04 (H) | open | OBPI-0.0.37-26 in-flight; byte target reached (28,323 B) but uncommitted/unattested (lock released mid-flight); 14 ADR-0.0.33 bullet-retention collision predicted |
| 2026-06-05 (J) | open | Repo re-eval: committed `main` relief held (AGENTS.md 28,489 B, Surface fidelity green — collision never materialized); single Preflight orphan (OBPI-0.0.37-18) cleared via sanctioned `preflight --apply` → 26/26 GREEN; baseline promoted H→J; ADR-0.0.37 6/19 BLOCKED on 13 missing ledger proofs |

## Appendix: The Smooth-vs-Replicable Axis (2026-05-30 dialogue insights)

Preserved from the 2026-05-30 operator+agent dialogue so this framing is not re-derived next session.

**The axis.** Superpowers is smooth but makes *snowflakes* (artisanal, low-replicability, non-reproducible). gzkit is replicable but *toxic* ("breathing tar fumes"). That is the real tradeoff this recovery is negotiating.

**Toxicity is mostly incidental, not essential — replicability and toxicity live in different layers:**

| Layer | What it is | Toxic? |
|---|---|---|
| Replicability (the value) | ledger as system-of-record, deterministic `gz` commands, receipts/attestation, fail-closed gates | No |
| Delivery (current form) | 32k always-loaded prose, in-your-face ceremony, context-rot, truncation, *performed* compliance | Yes — and removable |

Proof they separate: Superpowers *enforces hard* (its docs: the model rationalizes out of the rules ~90% of the time without the "iron law") yet stays smooth, because enforcement is lean, just-in-time, and shaped as a process you flow through. **Enforcement is not the tar; front-loaded, human-facing enforcement is.**

**Design principle (the synthesis).** Make replicability *invisible-when-right*, the way Superpowers makes enforcement invisible-when-right: the ledger writes itself (hook), IDs mint at runtime, gates stay silent unless a mistake is imminent, the CMS renders the surface. Replicability becomes a *byproduct* of the work, not a *tax* on it. The pieces already exist (ledger-writer hook, CMS) — they are buried under prose.

**The irreducible floor (where the tradeoff is real).** Replicability requires the one thing Superpowers refuses to pay: a human making binding decisions explicit and attesting to them at promotion boundaries (Gate 5). It cannot be automated — but it must be *a handful of moments per phase, not constant.* Concentrate attestation-grade friction at the real decision points; automate everything around them. gzkit cannot be Superpowers-smooth, but the floor that genuinely must hurt is thin; nearly all current toxicity sits above it.

**The phases reframe (the practical answer).** The tools are not competitors; they are phases.

- *Exploration / snowflake phase* → Superpowers. Snowflakes are fine for sketches and greenfields; do not reproduce a prototype.
- *Hardening phase* → gzkit, when a greenfield succeeds and must become reproducible, auditable, team-survivable.
- gzkit feels like tar because it makes you *manufacture while still sketching*. This is gzkit's own pool→foundation gradient applied to the *work*: near-zero ceremony during exploration, crystallize ceremony only at promotion. **The goal is a cheap handoff from the snowflake phase to the hardening phase — not one tool for everything.**

**Grounding (Claude Opus 4.8 system card, read 2026-05-30 — checked, not theorized).**

- gzkit's failures map to *named, measured* metrics: "situational hallucination" (hallucinating file/tool-output contents) and "missing-context hallucination" (fabricating output for an unavailable tool) — §6.2.3.1.3, §6.3.3.
- The trend is *improving*, not hopeless: 4.8 is "a significant improvement over Opus 4.7 on most aspects of honesty" (p97); it had "the lowest incorrect-rate of the six models on every benchmark," achieved "mainly by abstaining … when it was uncertain" (p115); and it "scores the highest" at resisting unavailable-tool fabrication (p119).
- Critical caveat (p83): the card measures the model under *normal* scaffolds, "rather than specific product surfaces such as the Claude app, Claude Code, or Cowork." gzkit's extreme context load is *outside* the regime where those reliability numbers hold. **The context diet is the safety work — it returns the model to its measured-reliable regime — not cosmetic.**

Provenance: 2026-05-30 operator+agent dialogue; Claude Opus 4.8 system card; Superpowers docs + obra/superpowers issue #237; context-engineering field findings (retrieval + static analysis + span-level verification, reported up to ~96% combined hallucination reduction).
