---
id: OBPI-0.33.0-02-airlock-in-pipeline-tracer
parent: ADR-0.33.0-airlock-membrane
item: 2
lane: Heavy
status: Draft
# Each REQ is ONE indivisible Red-Green-Refactor increment inside the single new
# airlock-IN primitive — no labor subdivides below any REQ (ADR-0.0.64 task-envelope
# exemption): 01 the three-beat + gate, 02 the two-layer seam-compute, 03 the §5 live
# NC (un-accounted -> GO unreachable), 04 the diagnostic refusal, 05 the logged
# revocable override, 06 the pipeline Stage-1 wiring, 07 the §5 @enforces claim
# registration (SUPPORT). Default-bucket seq=01 per REQ is the atomic unit here.
req_atomic:
  - REQ-0.33.0-02-01
  - REQ-0.33.0-02-02
  - REQ-0.33.0-02-03
  - REQ-0.33.0-02-04
  - REQ-0.33.0-02-05
  - REQ-0.33.0-02-06
  - REQ-0.33.0-02-07
---

# OBPI-0.33.0-02-airlock-in-pipeline-tracer: Airlock In Pipeline Tracer

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`
- **Checklist Item:** #2 - "Airlock-IN primitive: declare(intent+expectation) -> ping(gz ontology sense/reach) -> reconcile(L1<->L3 vs plan assumptions -> refresh L3 + re-plan) -> acknowledge-and-decide gate; two-layer seam-map (bodies = declared Allowed Paths, push from reach, pull from brief + parent-ADR invariants); section-5 @enforces claim + live NC (un-accounted seam -> GO structurally unreachable, un-forced production); diagnostic refusal (names seam + provenance + one-command re-sense) + logged/revocable captain override; wired into pipeline Stage 1. [BEHAVIOR; MVP spine; landing keystone -- gates all deferred breadth]"

**Status:** Draft

## Objective

Extract the airlock-IN primitive FROM the pipeline's proven Stage-1 pre-flight geometry and wire it into pipeline Stage 1 as the first, in-going half of the symmetric airlock membrane. Airlock-IN is a THREE-BEAT — (1) DECLARE intent + expectation; (2) PING the target's shape via the HULL sonar (`gz ontology reach`), where the L3 projection INFORMS and never DECIDES (state-doctrine Rule 5); (3) RECONCILE the ping against the assumptions the plan permitted, refreshing L3 and re-planning — followed by the ACKNOWLEDGE-AND-DECIDE gate returning exactly one of `proceed | pause | hold | revert`. The gate is fed by a TWO-LAYER seam-map: bodies = the OBPI brief's DECLARED Allowed Paths (seam-as-BODY, operator intent, never an inferred guess); push_edges = `gz ontology reach` (the computed blast radius); pull_edges = the brief + parent-ADR invariants. An UN-ACCOUNTED seam — a real push/pull edge present but absent from the declared set — makes GO STRUCTURALLY UNREACHABLE; the airlock blocks until the declarer accounts for it. "Done" = the primitive computes the seam-map, refuses GO on an un-accounted seam, emits a diagnostic NO-GO that names the exact seam + its provenance + a one-command re-sense, records a logged/revocable captain override, emits the `airlock_in` L2 event (schema from OBPI-01), is called at the pipeline Stage-1 site, and registers a §5 `@enforces` claim whose LIVE negative control runs un-forced through the enforcement-claim meta-validator and asserts GO cannot be reached — the landing keystone that gates all deferred breadth (mx / permitted-entry / doctrine-lawful).

## Lane

**Heavy** - This OBPI ships new runtime-contract surfaces: the `gzkit.airlock.enter` primitive, the additive `airlock in` CLI verb, an additive pipeline Stage-1 call site, and a §5 `@enforces` enforcement-claim registration. Command/API/runtime-contract change ⇒ all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- First backtick token on each bullet is the path; **CREATE** marks net-new
     files (existence-gate exempt, GHI #419). Paths are disjoint from siblings
     OBPI-01/03/04/05/06 in this ADR. -->

- `src/gzkit/airlock/enter.py` — **CREATE**: the airlock-IN primitive — `airlock_enter(...)` (declare/ping/reconcile/gate), the two-layer seam-map compute (bodies = declared Allowed Paths, push from `gz ontology reach`, pull from brief + parent-ADR invariants), the un-accounted → block rule, the diagnostic NO-GO builder, the logged/revocable captain override, and the `_ensure_airlock_claims_registered()` idempotent §5 `@enforces` registration (mirrors `gzkit.mx.proxy_reality._ensure_grader_gaming_registered`)
- `src/gzkit/airlock/__init__.py` — **CREATE**: `gzkit.airlock` package marker (docstring only) — created here iff OBPI-01 has not already seated it; otherwise UNTOUCHED NEIGHBOR
- `src/gzkit/commands/airlock.py` — **CREATE**: the `airlock in` command handler (`airlock_in_cmd`), mirroring `src/gzkit/commands/ontology.py` shape
- `src/gzkit/cli/parser_governance.py` — register the `airlock` group + the `in` subparser ONLY (mirrors the `p_ontology` block); additive
- `src/gzkit/cli/parser_handler_manifest.py` — map `airlock_in_cmd` → `gzkit.commands.airlock` ONLY; additive
- `src/gzkit/pipeline_runtime.py` — **Stage 1 call site ONLY**: invoke `airlock_enter(...)` at the Stage-1 pre-flight seam (adjacent to `check_reconcile_receipt_gate`); additive, no change to existing Stage-1 gate behavior
- `src/gzkit/enforcement.py` — **§5 registration site ONLY**: wire `_ensure_airlock_claims_registered()` into `_ensure_production_claims_registered()` so the airlock claim is discovered by `run_meta_validator` (register THIS claim only; the `mx` sources' wiring is UNTOUCHED)
- `tests/test_airlock_enter.py` — **CREATE**: `@covers`-decorated REQ tests incl. the §5 LIVE negative control (REQ-03)
- `features/airlock.feature` — **CREATE**: the Gate-4 BDD scenario for `airlock in`
- `docs/user/manpages/airlock.md` — **CREATE**: the `airlock in` verb doc (Gate 3 docs coherence)
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md` — parent ADR § Decision / § Boundary Invariants #2, #4, #6 (read-only reference, no edit)
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/obpis/OBPI-0.33.0-02-airlock-in-pipeline-tracer.md` — this brief (evidence recording)

(Security overlap check: no Allowed Path matches a glob in `data/security_surfaces.json` — `src/gzkit/airlock/enter.py`, `src/gzkit/commands/airlock.py`, `src/gzkit/enforcement.py`, and `src/gzkit/pipeline_runtime.py` are none of the registered `*credential*`/`*token*`/`*hash*`/`*secret*`/`*key*` modules, none of the named subprocess/ledger/arb/auth surfaces (`pipeline_markers.py` and `pipeline_dispatch.py` are registered; `pipeline_runtime.py` is NOT). `sensitivity: security` is not declared.)

## Creates These Files

- `src/gzkit/airlock/enter.py`
- `src/gzkit/commands/airlock.py`
- `tests/test_airlock_enter.py`
- `features/airlock.feature`
- `docs/user/manpages/airlock.md`
- `src/gzkit/airlock/__init__.py` (iff not already seated by OBPI-01)

## Denied Paths

<!-- OBPI-01 (model + events), OBPI-03 (airlock-OUT + Stage 5), OBPI-04 (mx door),
     OBPI-05 (permitted-entry), OBPI-06 (doctrine-lawful) are sibling OBPIs. -->

- `src/gzkit/airlock/model.py`, any airlock Pydantic model, and the `airlock_in`/`airlock_out` L2 event schemas — authored by OBPI-01; this OBPI CONSUMES them (imports `SeamEdge`/`SeamMap`/`Preflight` and emits the `airlock_in` event), never defines them
- `src/gzkit/airlock/exit.py`, the airlock-OUT drift-diff, and the pipeline **Stage 5** call site — OBPI-03; not touched here
- `gz mx enter`/`gz mx exit` wiring and `src/gzkit/mx/**` — the mx door is OBPI-04; the ONLY `enforcement.py` change here is adding the airlock claim source to `_ensure_production_claims_registered()`
- The permitted-entry door (new surface) — OBPI-05
- `docs/governance/work-phases-and-airlock.md`, `docs/governance/four-phases-of-work.md`, and any doctrine promotion — OBPI-06 (the one-way door, sequenced last)
- `src/gzkit/commands/validate_cmd.py` / a new `gz validate --airlock-nc` scope — the §5 live NC is discovered and run by the EXISTING enforcement-claim meta-validator (`gz validate --qc-binding` / the `gz check` enforcement floor); no new validate scope is forked here (§ Boundary Invariants #6 — one enforcement-claim surface, not two)
- A second negative-control framework — the airlock claim registers through the single `@enforces` primitive; forking is forbidden
- New runtime dependencies (`graspologic`, `networkx` as a NEW dep), CI files, lockfiles — the tracer stands on the already-attested `gz ontology reach` HULL floor + declared Allowed Paths + brief/ADR invariants
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. NEVER/ALWAYS language. Grounding for agents. -->

1. REQUIREMENT: Deliver ONLY the airlock-IN primitive + its Stage-1 wiring + the §5 `@enforces` claim: the three-beat (declare/ping/reconcile) + acknowledge-and-decide gate, the two-layer seam-map compute, the un-accounted → GO-unreachable block with a diagnostic refusal and a logged/revocable override, the `airlock in` verb, the additive pipeline Stage-1 call site, and the registered §5 live NC.
2. NEVER: let the L3 ontology projection DECIDE. The `gz ontology reach` ping INFORMS the gate; it is advisory input only and MUST NOT be consumed as fail-closing enforcement evidence (state-doctrine Rule 5; parent ADR § Boundary Invariants #6). The gate reaches its verdict from the accounted-vs-declared seam reconciliation, never from the raw sonar reading.
3. ALWAYS: block GO on an un-accounted seam. When a real push edge (`gz ontology reach`) or pull edge (brief + parent-ADR invariant) is present but ABSENT from the declared seam-set, the gate MUST NOT reach `proceed` — GO is structurally unreachable until the declarer accounts for the seam. This is fail-closed: absence of accounting is a NO-GO, never a default-proceed.
4. ALWAYS: make a NO-GO diagnostic. A refusal MUST name (a) the exact un-accounted seam, (b) its provenance (push-from-reach vs pull-from-invariant; `LAW` vs `OBSERVED`), and (c) a one-command re-sense (`gz ontology resense <target>`) to rule out a stale L3 baseline. A bare "NO-GO" with no seam named is a defect (parent ADR § Negative #5 — never a 2am hard wall).
5. ALWAYS: bodies = the DECLARED Allowed Paths (seam-as-BODY), read from the target brief's `## Allowed Paths`, NEVER a statistical inference. Undeclared-body auto-detection is explicitly OUT of the gating path (parent ADR § Negative #2 — the laundered-blind-spot mitigation).
6. ALWAYS: the acknowledge-and-decide gate is a DIFFERENT sort from completion attestation. The gate MUST NOT be emitted, recorded, or worded as a Gate-5 completion attestation; it never spends the sacrosanct word (parent ADR § Boundary Invariants #3).
7. NEVER: write L1 canon. Every airlock encounter is logged to the L2 ledger (`airlock_in` event); the primitive proposes governed amendments only and MUST NOT mutate an ADR, invariant, or canon surface (parent ADR § Boundary Invariants #1).
8. ALWAYS: the captain override is LOGGED to L2 and revocable (ADR-0.29.0 witnessed-override precedent); `blast_radius` is the DELEGATION dial (small + fully-accounted may auto-proceed, logged), never a responsibility dial — the captain owns every outcome.
9. ALWAYS: register the §5 claim through the single `@enforces` primitive and wire it into `_ensure_production_claims_registered()`; its LIVE negative control runs un-forced in production config through the meta-validator (`run_meta_validator`) — no forcing kwarg pre-bound, no mocked entrypoint. A claim registered but un-wired (an ORPHAN) is a §5 facade.
10. ALWAYS: Reconcile the brief with the parent ADR before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- Read the structured input (parent ADR § Decision) before the unstructured. -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision — quote the airlock-IN three-beat + the un-accounted-seam line** verbatim into `### Implementation Summary`. The two lines are this OBPI's contract: (1) "AIRLOCK-IN is a three-beat, not a single compute: (1) DECLARE intent + expectation; (2) PING the shape via the HULL sonar (gz ontology sense/reach) -- state-doctrine Rule 5: the L3 projection INFORMS, it never DECIDES; (3) RECONCILE the ping against the assumptions the plan permitted -> refresh the L3 map + re-plan; then the gate." (2) "An un-accounted seam makes GO STRUCTURALLY UNREACHABLE -- the airlock blocks until the declarer accounts for it, then the captain/delegate decides (the section-5 live negative control: omit a real reach push edge from a real entry, un-forced production, assert GO cannot be reached)."
- [ ] Parent ADR § Intent — the "prosthetic memory / the seam-map IS the externalized working set" why-frame.
- [ ] Parent ADR § Boundary Invariants #1 (never writes L1), #2 (gate fires on every entry), #3 (acknowledge-and-decide ≠ completion attestation), #4 (un-accounted seam → GO unreachable), #6 (L3 informs, never gates).
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`

> **STOP:** If you cannot quote the parent ADR § Decision line that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `docs/governance/state-doctrine.md` § Rule 5 — the L3-informs-never-decides boundary REQ-01/REQ-02 obey
- [ ] `AGENTS.md` § "Every REQ … [kind]" (ADR-0.0.59) — the REQ-kind discipline the Acceptance Criteria below obey
- [ ] `.claude/rules/hexagonal-architecture.md` — `gz ontology reach` is consumed behind its existing port (`OntologyGraph.reachable_from` returns `set[str]`); the primitive stays stdlib + Pydantic core

**Context:**

- [ ] Sibling OBPI-0.33.0-01 (data model + events) — the `SeamEdge`/`SeamMap`/`Preflight` models and the `airlock_in` L2 event schema this OBPI CONSUMES (must be landed first; see Prerequisites)
- [ ] Sibling OBPI-0.33.0-03 (airlock-OUT + Stage 5) — the co-equal exit half; same primitive shape, opposite direction; out of scope here
- [ ] `src/gzkit/enforcement.py` — the `@enforces` decorator + `_ensure_production_claims_registered()` seam (the §5 registration site)
- [ ] `src/gzkit/mx/proxy_reality.py` (`_ensure_grader_gaming_registered`) + `src/gzkit/mx/invariants.py` (`_ensure_gate5_claims_registered`) — the EXACT precedent for extending known-claims (`set_known_claims(_KNOWN_QC_CLAIM_IDS | _AIRLOCK_CLAIM_IDS)`) and idempotent re-registration this OBPI mirrors
- [ ] `src/gzkit/commands/ontology.py` (`ontology_reach_cmd`, `compute_reach`) — the `gz ontology reach` surface the ping calls; the command-module + parser shape `airlock in` mirrors

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.33.0-01 landed: `src/gzkit/airlock/model.py` with `SeamEdge`/`SeamMap`/`Preflight` and the `airlock_in` L2 event schema present and importable — this tracer CONSUMES them; if absent, STOP (this is the landing keystone; the model is its floor)
- [ ] `src/gzkit/enforcement.py` present with `@enforces`, `_ensure_production_claims_registered()`, and `run_meta_validator`
- [ ] `gz ontology reach <id>` present and green (parent ADR Fidelity Assertion row 1: `uv run gz ontology reach ADR-0.32.0-gzkit-ontology` exit 0)
- [ ] `src/gzkit/pipeline_runtime.py` present with the Stage-1 pre-flight seam (`check_reconcile_receipt_gate`)
- [ ] Parent ADR present, registered in `gz state`, carrying `## Boundary Invariants` (STRUCTURAL-FENCE anchors for BI #4)

**Existing Code (read; establish the conventions this primitive mirrors):**

- [ ] `src/gzkit/commands/ontology.py` — read-only sonar command shape; parser wiring pattern
- [ ] `src/gzkit/cli/parser_governance.py` (`p_ontology` block) + `src/gzkit/cli/parser_handler_manifest.py` — how a new noun-group verb registers end-to-end
- [ ] `tests/governance/test_enforces_registry.py` — the `@enforces` registration/fail-close test convention `tests/test_airlock_enter.py` mirrors for the §5 claim

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/airlock.md` documents `airlock in` with a real invocation + observed output

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`
- [ ] `features/airlock.feature` exercises the un-accounted-seam NO-GO through `airlock in`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- CONSTRUCTION HOUSEKEEPING proving the codebase is healthy. AUTHORING
     CONTRACT: single-program, shell-less invocations only — no &&, ||, |, ;,
     $(...), or redirects (GHI #415). One command per line. -->

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_airlock_enter -v
uv run gz validate --qc-binding
uv run -m behave features/airlock.feature
```

## Demo

<!-- THE YIELDED PRODUCT: the airlock-IN gate + the live §5 NC. Concrete,
     runnable invocations (not --help). Harvested by the closeout walkthrough.
     The net-new `airlock in` verb this OBPI introduces cannot yet resolve
     against the registered parser (GHI #432); its block carries the
     speculative command-shape skip marker. The registered surfaces the airlock
     stands on stay validated in the second block. -->

<!-- gz-validate-skip: command-shape -->
```bash
# Airlock-IN reaches a GO on a fully-accounted pipeline entry (three-beat + gate)
uv run gz airlock in --target OBPI-0.33.0-01 --phase build --dry-run
```

The registered surfaces the airlock stands on (validated):

```bash
# The HULL sonar the ping consumes (L3 informs, never decides — state-doctrine Rule 5)
uv run gz ontology reach ADR-0.32.0-gzkit-ontology

# The §5 LIVE negative control: the airlock claim's un-forced NC runs through the
# enforcement-claim meta-validator and asserts GO is unreachable on an un-accounted
# seam (omit a real reach push edge from a real entry). PASS = the airlock bites.
uv run gz validate --qc-binding

# Diagnostic refusal: a NO-GO names the exact seam + provenance + one-command re-sense
uv run gz ontology resense OBPI-0.33.0-01
```

## Acceptance Criteria

<!-- Each REQ carries exactly one [kind] tag (ADR-0.0.59): BEHAVIOR proves via a
     @covers test; SUPPORT via ledger event + structural validator; STRUCTURAL-FENCE
     via a parent-ADR ## Boundary Invariants entry. -->

- [ ] REQ-0.33.0-02-01 [BEHAVIOR]: `gzkit.airlock.enter.airlock_enter(...)` executes the three-beat and returns an acknowledge-and-decide `Preflight` whose `decision` is exactly one of `proceed | pause | hold | revert` — DECLARE (intent + expectation) → PING (`gz ontology reach` on the target, whose result is stored as advisory L3 input, NOT consumed as the verdict) → RECONCILE (ping vs the assumptions the plan permitted → refreshed L3 + re-plan) → gate. A `@covers(REQ-0.33.0-02-01)` test in `tests/test_airlock_enter.py` asserts the beat order runs and the gate returns a value in the closed decision set, and asserts the decision is NOT recorded as a completion attestation (parent ADR § Boundary Invariants #3).
- [ ] REQ-0.33.0-02-02 [BEHAVIOR]: `airlock_enter` computes a TWO-LAYER `SeamMap` where `bodies` equals the target brief's DECLARED `## Allowed Paths` (seam-as-BODY, read from L1, never inferred), `push_edges` are derived from `gz ontology reach` (the computed blast radius), and `pull_edges` are derived from the brief + parent-ADR invariants — proven by a `@covers(REQ-0.33.0-02-02)` test that runs a real entry and asserts `bodies` == the declared allowed-path set and that a known reach dependent appears as a push edge (and asserts NO statistical body inference is performed — the laundered-blind-spot fence, parent ADR § Negative #2).
- [ ] REQ-0.33.0-02-03 [BEHAVIOR]: an UN-ACCOUNTED seam makes GO STRUCTURALLY UNREACHABLE — this is the §5 LIVE negative control (parent ADR § Boundary Invariants #4). A `@covers(REQ-0.33.0-02-03)` test omits a real `gz ontology reach` push edge from the declared seam-set of a REAL pipeline entry and asserts `airlock_enter` cannot return `proceed` (the decision is `hold`/`pause`, never GO); the same violation-builder + production entrypoint are registered as the `airlock-in-unaccounted-seam` `@enforces` claim so the un-forced NC runs in production config through `run_meta_validator` (`gz validate --qc-binding`) and PASSES only because the airlock genuinely refuses GO — a mocked or forced NC is rejected.
- [ ] REQ-0.33.0-02-04 [BEHAVIOR]: a NO-GO is a diagnostic refusal, not a bare denial — the refusal message names (a) the exact un-accounted seam id, (b) its provenance (push-from-reach vs pull-from-invariant; `LAW` vs `OBSERVED`), and (c) a one-command re-sense (`gz ontology resense <target>`) to rule out a stale L3 baseline. A `@covers(REQ-0.33.0-02-04)` test asserts all three components are present in the refusal for a known un-accounted seam (parent ADR § Negative #5 — never a 2am hard wall).
- [ ] REQ-0.33.0-02-05 [BEHAVIOR]: a captain override of a NO-GO is LOGGED to the L2 ledger and is REVOCABLE (ADR-0.29.0 witnessed-override precedent), and `blast_radius` acts only as the DELEGATION dial (a small, fully-accounted entry may auto-proceed, logged) — never as a responsibility dial. A `@covers(REQ-0.33.0-02-05)` test asserts an override records an L2 event carrying the overridden seam + attestor and that the override can be revoked, and asserts a non-accounted seam is NOT auto-proceeded by blast_radius alone.
- [ ] REQ-0.33.0-02-06 [BEHAVIOR]: `airlock_enter` is invoked at the pipeline Stage-1 pre-flight call site in `src/gzkit/pipeline_runtime.py` (additive, adjacent to `check_reconcile_receipt_gate`, no change to existing gate behavior) and emits the `airlock_in` L2 event (schema from OBPI-01) on transit. A `@covers(REQ-0.33.0-02-06)` test asserts the Stage-1 seam calls the primitive and that a transit books an `airlock_in` event to L2 (never a write to L1 canon — parent ADR § Boundary Invariants #1).
- [ ] REQ-0.33.0-02-07 [SUPPORT]: the §5 `airlock-in-unaccounted-seam` `@enforces` claim is registered into the single enforcement-claim registry via `_ensure_airlock_claims_registered()` and wired into `_ensure_production_claims_registered()` in `src/gzkit/enforcement.py` so `run_meta_validator` discovers it (no ORPHAN) — proven by an `enforcement_claim_verified` ledger event emitted for the airlock claim at meta-validator run AND `uv run gz validate --qc-binding` exiting 0 with the airlock claim among the verified set.

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

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
</content>
</invoke>
