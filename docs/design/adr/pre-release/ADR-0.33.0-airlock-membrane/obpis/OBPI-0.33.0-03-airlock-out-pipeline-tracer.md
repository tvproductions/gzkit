---
id: OBPI-0.33.0-03-airlock-out-pipeline-tracer
parent: ADR-0.33.0-airlock-membrane
item: 3
lane: Heavy
status: Completed
req_atomic:
  # Each REQ is one indivisible unit of labor — a single Red-Green-Refactor
  # cycle each: 01 the drift-diff push-minus-pull engine, 02 the findings +
  # closed decision menu, 03 fresh-transit routing (never smuggle), 04 the
  # ALWAYS-log-to-L2 event + Stage 5 call site, 05 the NEVER-write-L1 fence.
  # No labor subdivided below any REQ; airlock-OUT is co-equal MVP spine.
  - REQ-0.33.0-03-01
  - REQ-0.33.0-03-02
  - REQ-0.33.0-03-03
  - REQ-0.33.0-03-04
  - REQ-0.33.0-03-05
---

# OBPI-0.33.0-03-airlock-out-pipeline-tracer: Airlock Out Pipeline Tracer

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`
- **Checklist Item:** #3 - "Airlock-OUT primitive (co-equal): drift-diff push-minus-pull -> findings + recommendations -> decision menu (leave-it-be | modify | repair | adjust-maps) -> fresh-transit routing for discovered correction -> log to L2; wired into pipeline Stage 5. [BEHAVIOR; MVP spine]"

**Status:** Completed

## Objective

Ship airlock-OUT as the co-equal exit membrane — a `gzkit.airlock.exit` primitive that computes the DRIFT-DIFF (push-minus-pull over the two-graph: a fact-edge with no intent-edge = "you wrecked something", an intent-edge with no fact-edge = "broken contract"), renders FINDINGS + RECOMMENDATIONS behind a closed DECISION MENU (leave_it_be | modify | repair | adjust_maps), ROUTES every discovered correction as a FRESH TRANSIT through the right door (pipeline | mx | permitted-entry) instead of smuggling it into the current sortie, ALWAYS logs the encounter to the L2 ledger via the `airlock_out` event, and NEVER writes L1 canon — surfaced as a new gz airlock out subcommand and invoked from the pipeline Stage 5 exit/sync call site.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because it adds a new importable runtime primitive (`gzkit.airlock.exit`),
a new operator CLI subcommand (gz airlock out) with its parser wiring and
handler manifest entry, and an additive call site in the pipeline Stage 5
exit/sync stage that later doors and the parent ADR's Fidelity Assertions bind
against. All three are external contract surfaces.

## Allowed Paths

<!-- First backtick token on each bullet is the path; **CREATE** marks net-new
     files (existence-gate exempt, GHI #419). -->

- `src/gzkit/airlock/exit.py` — **CREATE**: the airlock-OUT primitive — the drift-diff push-minus-pull engine over the two-graph, the closed `ExitDecision` menu enum, findings/recommendations rendering, fresh-transit routing directive, and `airlock_out` L2 event emission. Never writes L1.
- `src/gzkit/commands/airlock.py` — **CREATE** (net-new within ADR-0.33.0), **COUPLED SURFACE (AGENTS.md § DO IT RIGHT 1a)**: the module is first seated by OBPI-0.33.0-02 (which owns the gz airlock noun + the `in` subcommand); this OBPI adds ONLY the `out` subcommand handler. Sequenced AFTER OBPI-02; the `in`/`out` handlers must not clobber each other — verify OBPI-02's handler surface in the same edit that adds `out`.
- `src/gzkit/cli/parser_governance.py` — **COUPLED SURFACE (§ DO IT RIGHT 1a, shared with OBPI-02)**: add ONLY the `out` subparser under the gz airlock noun (mirrors how `ontology` seats its verbs here). OBPI-02 creates the `airlock` noun + `in` subparser; this OBPI attaches `out` to it.
- `src/gzkit/cli/parser_handler_manifest.py` — **COUPLED SURFACE (§ DO IT RIGHT 1a, shared with OBPI-02)**: map ONLY the `airlock_out_cmd` handler key to `gzkit.commands.airlock`. Additive single entry; OBPI-02 adds `airlock_in_cmd`.
- `src/gzkit/pipeline_runtime.py` — **Stage 5 gate helper ONLY**: author `check_airlock_out_gate(...)` (which invokes `airlock.exit`) adjacent to `check_airlock_in_gate`; additive, no change to existing Stage-5 helper behavior. `pipeline_runtime.py` holds Stage-5 *helpers*, never the executor (mirrors OBPI-02's Stage-1 split).
- `src/gzkit/commands/obpi_stages.py` — **Stage 5 call site ONLY**, **COUPLED SURFACE (AGENTS.md § DO IT RIGHT 1a)**: invoke `check_airlock_out_gate(...)` inside `_run_pipeline_sync_stage` at the exit membrane (the seam that calls `remove_pipeline_artifacts`); additive, no existing Stage-5 step is reshaped. (Declared because `pipeline_runtime.py` holds Stage-5 *helpers*, never the executor — the invocation seam is a real pull edge, and leaving it undeclared is the un-accounted seam this OBPI exists to forbid. Exact mirror of OBPI-02's `obpi_cmd.py` Stage-1 declaration. Allowlist amended under operator approval 2026-07-11, Gate Friction escalation; not a registered security surface.)
- `tests/test_airlock_exit.py` — **CREATE**: `@covers`-decorated REQ tests for the drift-diff, decision menu, fresh-transit routing, L2 log, and never-writes-L1 fence.
- `docs/user/manpages/airlock-out.md` — **CREATE**, coupled doc surface (Gate 3): the per-subcommand manpage for `gz airlock out`, H1 `# gz airlock out`, mirroring `airlock-in.md`. (Brief-reality correction: OBPI-02 established one manpage PER subcommand — `airlock-in.md` — not a single `airlock.md`; `cli audit` resolves `<group>-<subcommand>.md` with H1 = full verb. Allowlist amended under operator approval 2026-07-11.)
- `docs/user/manpages/index.md` — coupled doc surface (Gate 3): add the `gz airlock out` catalog row (mirrors the OBPI-02 `airlock in` row); additive.
- `config/doc-coverage.json` — coupled surface: add the `"airlock out"` verb→manpage coverage entry (mirrors OBPI-02's `"airlock in"` entry); additive. Without it the `doc-coverage` gate fails on an AST-discovered verb with no manifest row.
- `src/gzkit/governance/trust_audits/cli.py` — coupled surface: add the `_NO_SKILL_VERBS["airlock out"]` entry (same rationale as `airlock in` — the production wielder is the pipeline Stage-5 seam, a dedicated wielding skill awaits deferred breadth); additive. Satisfies skill-alignment Invariant 1 without a premature wielding skill.
- `features/airlock.feature` — coupled surface (Gate 4 BDD): add `gz airlock out` smoke scenarios (dry-run exit 0, `--json` payload) mirroring the `airlock in` scenarios; additive.
- `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — coupled doc surfaces: verb-resolution mentions of `gz airlock out` iff the cli-alignment gate requires them (OBPI-02 touched both); additive, surgical.
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md` — parent ADR (read-only reference; § Decision, § Boundary Invariants #1 and #5, § Fidelity Assertions — no edit).
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/obpis/OBPI-0.33.0-03-airlock-out-pipeline-tracer.md` — this brief (evidence).

## Denied Paths

<!-- Sibling OBPIs own these surfaces; airlock-OUT never reaches into them. -->

- `src/gzkit/airlock/model.py`, `src/gzkit/schemas/airlock_*.json`, and the `airlock_in`/`airlock_out` event SCHEMA definitions — the Pydantic model + ledger-event schema layer is OBPI-0.33.0-01. This OBPI CONSUMES those models/events; it never defines or edits them.
- `src/gzkit/airlock/enter.py`, the pipeline Stage 1 pre-flight call site, and the section-5 `@enforces` claim + live negative control — the airlock-IN primitive and its NC are OBPI-0.33.0-02. This OBPI mirrors IN's shape but never edits its code.
- `src/gzkit/mx/**` and `gz mx enter/exit` wiring — the mx door is OBPI-0.33.0-04.
- Any new `permitted-entry` surface (the ad-hoc/spurious door) — OBPI-0.33.0-05.
- `docs/governance/work-phases-and-airlock.md`, `docs/governance/four-phases-of-work.md`, and the doctrine-lawful promotion — OBPI-0.33.0-06.
- New runtime dependencies (networkx beyond the attested floor, tree-sitter, graspologic), CI files, lockfiles — the tracer stands on `gz ontology reach` (attested HULL floor) + declared Allowed Paths + brief/ADR invariants only.
- Any path not listed in Allowed Paths.

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. NEVER/ALWAYS language. -->

1. REQUIREMENT: Deliver ONLY the airlock-OUT primitive + its `out` subcommand + the Stage 5 call site: the drift-diff push-minus-pull engine, the closed decision menu, fresh-transit routing, the `airlock_out` L2 log, and the never-writes-L1 fence. No airlock-IN, mx, permitted-entry, model/schema, or doctrine work. The primitive must never be forked per-door nor duplicate airlock-IN's compute — airlock-OUT is the co-equal exit half of the ONE extracted primitive ("same shape both ways"); the other doors CALL it (parent ADR § Boundary Invariant #3, door-drift).
2. NEVER: write L1 canon from any airlock-OUT path. The primitive reports findings and PROPOSES governed, attested amendments only; it MUST NOT mutate an ADR, invariant, or canon surface directly (parent ADR § Boundary Invariants #1, state-doctrine). A canon write from airlock.exit is a fail-closed defect. Equally, the primitive must never consume the L3 ontology projection (the reach ping / seam-map) as fail-closing gate evidence — the projection INFORMS the drift-diff, it never gates (state-doctrine Rule 5; parent ADR § Boundary Invariant #6).
3. ALWAYS: log the encounter to the L2 ledger — every airlock-OUT transit emits exactly one `airlock_out` event (defined in OBPI-01). An exit that computes a drift-diff but emits no ledger event is a fail-closed defect (L3 recomputes from L1+L2; a silent exit breaks the recompute).
4. ALWAYS: route any discovered correction as a FRESH TRANSIT through the appropriate door (pipeline | mx | permitted-entry). Work discovered mid-sortie is NEVER smuggled into the current transit (parent ADR § Boundary Invariants #5; "better housekeeping/bookkeeping").
5. ALWAYS: keep the `ExitDecision` menu a CLOSED enum of exactly `{leave_it_be, modify, repair, adjust_maps}`. A fifth or renamed member is a fail-closed drift the covering test must catch.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- Read the structured input (parent ADR § Decision) before the unstructured
     one (allowed paths, prerequisites). Order pinned — GHI #321. -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision — quote the airlock-OUT clause** verbatim into `### Implementation Summary`. The clause is this OBPI's contract:

  > AIRLOCK-OUT (co-equal): drift-diff push-minus-pull -> findings + recommendations -> a decision menu (leave-it-be | modify | repair | adjust-maps) -> route any discovered correction as a FRESH transit through the right door (never smuggled inline; 'better housekeeping/bookkeeping') -> log to L2.

- [ ] Parent ADR § Intent — the "prosthetic memory" / "account for what was disturbed and update the maps" why-frame for the exit membrane.
- [ ] Parent ADR § Boundary Invariants #1 (never writes L1 canon) and #5 (discovered correction routes as a fresh transit) — the two doctrine lines airlock-OUT holds.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`

> **STOP:** If you cannot quote the parent ADR § Decision airlock-OUT clause that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § "Every REQ … [kind]" (ADR-0.0.59) — the REQ-kind discipline the Acceptance Criteria below obey (each REQ carries exactly one kind).
- [ ] `AGENTS.md` § DO IT RIGHT 1a (coupled-surface coherence) — the rule the shared commands/airlock.py + CLI parser surfaces are declared under.
- [ ] `docs/governance/state-doctrine.md` § Rule 5 — L3 informs, never gates (the fence for Requirement 7).

**Context:**

- [ ] Sibling OBPI-0.33.0-02 (airlock-in-pipeline-tracer) — the co-equal "same shape both ways" declare->ping->reconcile->gate shape airlock-OUT mirrors, AND the OBPI that creates the shared `src/gzkit/commands/airlock.py` module + gz airlock noun this OBPI attaches `out` to. Sequenced BEFORE this OBPI.
- [ ] Sibling OBPI-0.33.0-01 (airlock-data-model-and-events) — defines `SeamEdge`/`SeamMap`/`DriftDiff` Pydantic models + the `airlock_out` event schema this OBPI consumes.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/airlock.py` present with the gz airlock noun + `in` subcommand (from OBPI-0.33.0-02) — STOP if absent: the `out` subcommand attaches to OBPI-02's noun and cannot be authored before it lands (sequencing gate).
- [ ] `src/gzkit/airlock/model.py` present with `DriftDiff`/`SeamEdge`/`SeamMap`, and the `airlock_out` event defined (from OBPI-0.33.0-01) — STOP if absent: the drift-diff engine and L2 log consume these.
- [ ] `gz ontology reach` present (the attested HULL floor) — the push (fact/OBSERVED) edges of the two-graph come from reach; STOP if the sonar is unavailable.
- [ ] Pipeline Stage 5 exit/sync call site present: `_run_pipeline_sync_stage` / `_build_sync_stage_steps` in `src/gzkit/commands/obpi_stages.py`, re-exported through `src/gzkit/pipeline_runtime.py` — the stage that removes the Stage 1 marker, where `airlock.exit` is invoked.

**Existing Code (read; do NOT modify unless in Allowed Paths — establishes the conventions this module mirrors):**

- [ ] `src/gzkit/commands/obpi_stages.py` (`_build_sync_stage_steps`, `_run_pipeline_sync_stage`, lines ~436-535) — the Stage 5 step list; the `airlock.exit` call site is wired here via the `pipeline_runtime.py` re-export, additive to the existing complete/sync/reconcile steps.
- [ ] `src/gzkit/ontology/work.py` (Provenance vein, lines ~59-66) — INTENT (LAW) edges vs OBSERVED (fact) edges; the drift-diff reads push=OBSERVED fact edges (from reach) minus pull=INTENT law edges (from brief + parent-ADR invariants).
- [ ] `src/gzkit/ledger_events.py` — the append-only ledger event emission pattern the `airlock_out` emit follows (ledger is never edited directly).
- [ ] `src/gzkit/cli/parser_governance.py` (`register_governance_parsers`, the `gz ontology` noun at lines ~845-863) — how a governance noun seats its subverbs; the `out` subparser attaches to OBPI-02's `airlock` noun the same way.

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/airlock.md` `out` section added

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- CONSTRUCTION HOUSEKEEPING (lint, type, test, docs) proving the codebase is
     healthy. AUTHORING CONTRACT: single-program, shell-less invocations only —
     no &&, ||, |, ;, $(...), or redirects (GHI #415). One command per line.
     The yielded product (concrete gz airlock out runs) is in `## Demo`. -->

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f src/gzkit/airlock/exit.py
uv run -m unittest tests.test_airlock_exit -v
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete gz airlock out invocations.
     The gz airlock out verb is introduced by THIS OBPI's scope and cannot yet
     resolve against the registered parser, so the block carries the
     speculative-skip marker (GHI #432) directly above the fence. -->

<!-- gz-validate-skip: command-shape -->
```bash
# Drift-diff at the pipeline exit for a completed transit (dry-run: no L2 write)
uv run gz airlock out --target OBPI-0.33.0-01 --dry-run

# Machine-readable drift-diff: findings, recommendations, decision menu
uv run gz airlock out --target OBPI-0.33.0-01 --json

# A real exit that ALWAYS logs the airlock_out encounter to L2
uv run gz airlock out --target OBPI-0.33.0-01

# A discovered correction is routed as a FRESH transit (never smuggled inline):
# the output names the door (pipeline | mx | permitted-entry), it does not repair here
uv run gz airlock out --target OBPI-0.33.0-01 --json
```

## Acceptance Criteria

<!-- Each REQ carries exactly one [kind] tag (ADR-0.0.59): BEHAVIOR proves via a
     @covers test; SUPPORT via ledger event + structural validator; STRUCTURAL-FENCE
     via a parent-ADR ## Boundary Invariants entry. -->

- [ ] REQ-0.33.0-03-01 [BEHAVIOR]: airlock-OUT (`gzkit.airlock.exit`) computes the DRIFT-DIFF as push-minus-pull over the two-graph — a FACT edge (OBSERVED provenance, from `gz ontology reach`) with no matching INTENT edge yields a "you wrecked something" finding, and an INTENT edge (LAW provenance, from the brief + parent-ADR invariants) with no matching FACT edge yields a "broken contract" finding (parent ADR § Decision / § 2); a `@covers(REQ-0.33.0-03-01)` test in `tests/test_airlock_exit.py` builds a two-graph fixture with exactly one un-matched fact edge and one un-matched intent edge, asserts both findings are emitted with the correct classification, and asserts a fully-matched two-graph yields an empty drift set.
- [ ] REQ-0.33.0-03-02 [BEHAVIOR]: airlock-OUT renders FINDINGS + RECOMMENDATIONS behind a CLOSED `ExitDecision` menu of exactly `{leave_it_be, modify, repair, adjust_maps}`; a `@covers(REQ-0.33.0-03-02)` test asserts the menu enum member-set is exactly those four (a fifth or renamed member fails the test — the partition can fail on a business-logic change, not merely author error) and that every emitted finding carries a non-empty recommendation.
- [ ] REQ-0.33.0-03-03 [BEHAVIOR]: any discovered correction is ROUTED AS A FRESH TRANSIT through the appropriate door (`pipeline` | `mx` | `permitted-entry`) and is NEVER smuggled into the current sortie (parent ADR § Boundary Invariants #5); a `@covers(REQ-0.33.0-03-03)` test drives a drift-diff carrying a discovered correction, asserts airlock-OUT returns a fresh-transit routing directive naming the correct door, and asserts `airlock.exit` performs zero in-sortie mutation of the discovered surface.
- [ ] REQ-0.33.0-03-04 [BEHAVIOR]: airlock-OUT ALWAYS logs the encounter to L2 by emitting exactly one `airlock_out` event (schema from OBPI-01), and the pipeline Stage 5 exit/sync call site invokes `airlock.exit`; a `@covers(REQ-0.33.0-03-04)` test drives the Stage 5 call site (via the `pipeline_runtime.py` re-export) and asserts exactly one `airlock_out` event is appended to the ledger for the transit — a computed drift-diff with no emitted event fails the test (fail-closed: no event = no accounted exit).
- [ ] REQ-0.33.0-03-05 [BEHAVIOR]: airlock-OUT NEVER writes L1 canon — it reports findings and PROPOSES governed, attested amendments only (parent ADR § Boundary Invariants #1); a `@covers(REQ-0.33.0-03-05)` test runs `airlock.exit` against a fixture that surfaces a canon-amendment recommendation and asserts zero mutations to any L1 surface (ADR / invariant / canon file) — the primitive returns a proposal object, never a canon write. This behavior test bites per-OBPI and reinforces the ADR-level structural fence at § Boundary Invariants #1.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded; parent ADR § Decision airlock-OUT clause quoted in the plan and Implementation Summary.

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Verified assertion-level RED against the stub skeleton (production withheld):
#   test_push_minus_pull_classifies_wrecked_and_broken  FAIL  [] != ['FACT-A']
#   test_every_finding_carries_non_empty_recommendation FAIL  () is not true
#   test_discovered_correction_routes_fresh_never_smuggled FAIL () is not true
#   test_airlock_exit_books_exactly_one_airlock_out_event FAIL 0 != 1
#   test_stage5_gate_reaches_primitive_and_books_l2      FAIL  0 != 1
#   test_canon_amendment_is_proposed_never_written       FAIL  () is not true
# GREEN after implementation:
$ uv run -m unittest tests.test_airlock_exit
Ran 9 tests in 0.046s
OK
# RED falsifiability witness (gz arb red), all 5 BEHAVIOR REQs, failure_class=error,
# zero `none` verdicts: arb-red-REQ-0.33.0-03-01..05 receipts emitted.
# Full-sweep ARB receipt: arb-step-unittest-1b0ee20e9a0a404aa5dfc6cccbc3a6e2 (exit_status=0)
```

### Code Quality

```text
$ uv run gz arb ruff        # exit 0 — receipt arb-ruff-7de1c2f4efec4728887912b7849e3e57
$ uv run gz arb typecheck   # exit 0 — receipt arb-step-typecheck-5f5082058be9430aae63587bcc19325e
```

### Gate 3 (Docs)

```text
$ uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# exit 0 — receipt arb-step-mkdocs-f94367b3511042f5bef473ed6bdf99e6
$ uv run gz cli audit       # exit 0 — Cross-coverage: 124/124 commands fully covered
$ uv run gz validate --documents          # exit 0
$ uv run gz validate --cli-alignment      # exit 0
```

### Gate 4 (BDD)

```text
$ uv run gz arb step --name behave -- uv run -m behave --tags=@REQ-0.33.0-03-02 features/airlock.feature
1 feature passed, 0 failed; 2 scenarios passed
# receipt arb-step-behave-96a67d97be014669b49f47bc1b7dfc9d
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Step 4b — Independent Adversarial Validation

- **Adversary:** Independent Claude subagent (fresh context, refute-framed). **Degraded tier, disclosed:** the preferred different-vendor Codex adversary (`codex:codex-rescue`, GHI #643 preferred tier) failed to start (companion runtime unavailable, exit 1); per the Step-4b ladder the fallback independent-Claude adversary ran instead. The different-vendor cross-check did not run.
- **Verdict:** `NOT-REFUTED` — all 5 REQs backed by executable code; drift-diff proven a real symmetric difference by an independent probe; closed menu genuinely closed (set-equality bites a 5th member); Stage-5 call site genuinely reachable; `airlock_exit` structurally cannot write L1 (grep found no write primitive); all 5 `arb-red` receipts `failure_class=error` (never `none`), so tests are non-tautological.
- **Two real gaps named and FIXED before attestation (never handed over as clean):**
  1. **Weakest point — REQ-04 orphan-blessing test.** The original `test_..._not_orphan` asserted only `hasattr(obpi_stages, "check_airlock_out_gate")` — it blessed the import, not the call. Fixed: extracted a named `_run_airlock_out_diagnostic` helper (mirroring airlock-IN's `_run_airlock_in_diagnostic`) and replaced the hasattr test with `test_stage5_executor_exit_membrane_books_airlock_out`, which DRIVES the executor seam and asserts exactly one `airlock_out` event lands via the stage path — fails if the call block is deleted.
  2. **Ledger-hygiene ordering.** The `airlock_out` event was booked AFTER the accounting `git add/commit/push` in `_run_pipeline_sync_stage`, leaving it uncommitted. Fixed: moved the airlock-OUT diagnostic BEFORE the accounting commit so `git add -A` sweeps the event into the commit.
- **Re-validation:** full suite green post-fix (6977 tests OK, receipt `arb-step-unittest-22b84dabf6ac47a99704982062da1d9b`); covers 0 uncovered; REQ-04 RED witness re-emitted.
- **Accepted caveat:** all `arb-red` witnesses are `failure_class=error` (net-new module absent at base), not `assertion`. The assertion-level RED was observed directly against the stub skeleton (6 tests failing on their own assertions before GREEN) — the stronger falsifiability evidence the net-new `arb red` case cannot reproduce.

### Value Narrative

Before this OBPI the airlock had an entry membrane (airlock-IN, OBPI-02) but no
co-equal EXIT membrane: a completed transit tore down its Stage-1 marker and left
the project with no structural accounting of what it disturbed on the way out —
the "prosthetic memory" was half-built. This OBPI ships airlock-OUT as the
co-equal exit half ("same shape both ways"): a `gzkit.airlock.exit` primitive
that computes a drift-diff push-minus-pull over the two-graph (FACT/OBSERVED
reach edges vs INTENT/LAW invariant edges), classifies wrecked-something vs
broken-contract findings behind a CLOSED decision menu, routes any discovered
correction as a FRESH transit (never smuggled), books exactly one `airlock_out`
L2 event, and NEVER writes L1 canon — surfaced as `gz airlock out` and wired into
the pipeline Stage-5 exit membrane.

### Key Proof


```text
$ uv run -m unittest tests.test_airlock_exit
Ran 9 tests in 0.046s
OK

# The drift-diff bites (REQ-01): a fact-with-no-intent edge classifies as
# WRECKED_SOMETHING, an intent-with-no-fact edge as BROKEN_CONTRACT, and a
# fully-matched two-graph yields empty drift + Verdict.CLEAN.
# REQ-04 wiring is non-orphan: _run_pipeline_sync_stage in obpi_stages.py invokes
# check_airlock_out_gate at the exit membrane (asserted by
# test_stage5_gate_is_wired_into_sync_call_site_not_orphan).
$ uv run gz airlock out --target OBPI-0.33.0-01 --dry-run
airlock out (dry-run) — OBPI-0.33.0-01
  verdict: clean
  decision menu: leave_it_be, modify, repair, adjust_maps
```

### Calibration frontier (tracer scope)

Co-equal with airlock-IN's frontier: a real leaf-OBPI exit computes an empty
two-graph (`compute_reach` returns transitive dependents, of which a leaf has
none; `parent_invariants` is not passed at the wired call site), so the drift-diff
is `clean` and no findings surface at a real exit. The MECHANISM is proven by the
fixture tests (synthetic fact/intent edges); the wired Stage-5 seam is
DIAGNOSTIC-ONLY (logs findings as a warning, never `SystemExit`). Real-exit
accounting is the same deferred WWHTBT-(a) condition. Not claimed done here.

### Implementation Summary


- Files created: `src/gzkit/airlock/exit.py` (the airlock-OUT primitive), `tests/test_airlock_exit.py` (9 `@covers` tests), `docs/user/manpages/airlock-out.md`.
- Files modified: `src/gzkit/commands/airlock.py` (`airlock_out_cmd`), `src/gzkit/cli/parser_governance.py` (`out` subparser), `src/gzkit/cli/parser_handler_manifest.py` (`airlock_out_cmd` handler), `src/gzkit/pipeline_runtime.py` (`check_airlock_out_gate`), `src/gzkit/commands/obpi_stages.py` (Stage-5 exit-membrane call site), `docs/user/manpages/index.md`, `config/doc-coverage.json`, `src/gzkit/governance/trust_audits/cli.py` (`_NO_SKILL_VERBS`), `features/airlock.feature`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md`.
- Tests added: 9 (`tests.test_airlock_exit`), covering REQ-01..05; full suite green; 5 `arb-red` witnesses (failure_class=error, zero `none`).
- Date completed: 2026-07-11
- Attestation status: pending operator attestation (Stage 4).
- Defects noted: see Tracked Defects.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- Reconcile allowlist false-positive (same class OBPI-02 documented) — `_compute_missing_in_brief` flags `src/gzkit/airlock/model.py` and `src/gzkit/ledger.py` as `missing_in_brief` because `tests/test_airlock_exit.py` imports them and they share a directory-neighborhood with allowlisted paths. Both are CONSUMED, not modified: `model.py` is in this brief's `## Denied Paths` (OBPI-01 owns it); `ledger.py` is a stdlib-tier consumed dependency. The heuristic reads `## Allowed Paths` but never `## Denied Paths`, so a correct consumed-declaration cannot suppress the flag. Resolution: documented `gz obpi complete --accept-stale-reconciliation --reason` override at Stage 5 (operator-approved). Candidate for the same direct-fix OBPI-02 proposed (exclude Denied-Paths entries from the coupling heuristic).
- Pre-existing `gz validate --sensitivity` exit 3 (NOT introduced by this OBPI) — the repo-wide sensitivity scan fails on pre-cutover briefs overlapping `ledger_integrity` / `deserialization_user_input` surfaces (`src/gzkit/sync.py`, `src/gzkit/sync_surfaces.py`, config surfaces). OBPI-0.33.0-03 is named ZERO times in the violation set and none of its declared Allowed Paths match a security glob, so it does not trip the scoped `gz obpi complete` security walkthrough. Flagged as a pre-existing tracked defect (out of scope: entirely different surfaces).

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.33.0-03 airlock-OUT co-equal exit membrane: gzkit.airlock.exit drift-diff push-minus-pull + gz airlock out verb + Stage-5 exit-membrane wiring (_run_airlock_out_diagnostic). 9/9 @covers tests green, full sweep 6977 tests OK (receipt arb-step-unittest-22b84dabf6ac47a99704982062da1d9b); ruff clean (arb-ruff-7de1c2f4efec4728887912b7849e3e57); typecheck clean (arb-step-typecheck-5f5082058be9430aae63587bcc19325e); mkdocs clean (arb-step-mkdocs-f94367b3511042f5bef473ed6bdf99e6); behave clean (arb-step-behave-96a67d97be014669b49f47bc1b7dfc9d); cli-audit 124/124; 5/5 REQ covers parity. Step-4b adversary NOT-REFUTED (independent-Claude tier, degraded from unavailable Codex; two named gaps — orphan-blessing test + ledger-hygiene ordering — fixed pre-attestation).
- Date: 2026-07-11

---

**Date Completed:** 2026-07-11

**Evidence Hash:** -
</content>
</invoke>
