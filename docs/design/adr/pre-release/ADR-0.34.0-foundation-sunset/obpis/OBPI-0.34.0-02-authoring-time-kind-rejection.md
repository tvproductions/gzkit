---
id: OBPI-0.34.0-02-authoring-time-kind-rejection
parent: ADR-0.34.0-foundation-sunset
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.34.0-02-authoring-time-kind-rejection: Authoring Time Kind Rejection

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`
- **Checklist Item:** #2 - "authoring-time-kind-rejection: Reject 'gz plan create --kind foundation' and 'gz adr promote --kind foundation' at the command layer with three-part guardrail-feedback prose (what failed / why forbidden: foundation kind closed ADR-0.34.0 / next step: --kind feature or pool). Close the authoring doors while leaving the schema enum intact for grandfathered validation. (heavy lane: CLI authoring-behavior change)."

**Status:** Completed

## Objective

Close the two foundation-authoring doors — `gz plan create --kind foundation` and `gz adr promote --kind foundation` — by rejecting each at the command handler with three-part guardrail-feedback prose (what failed / why forbidden: the foundation kind is closed by ADR-0.34.0 / governed next step: `--kind feature` or `--kind pool`), while leaving the `foundation` value in the schema `kind` enum and in argparse `choices` intact so the ~51 grandfathered `kind: foundation` ADRs still validate.

## Lane

**Heavy** - This OBPI changes CLI authoring behavior: two operator-facing command verbs (`gz plan create`, `gz adr promote`) that previously accepted `--kind foundation` now reject it. That is a runtime-contract change to a human-used surface, so Gate 3 (docs) and Gate 4 (BDD) fire alongside the universal Gate 5 brief-level attestation (ADR-0.0.36).

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/commands/plan.py` — command handler for `gz plan create`; the `_validate_kind_and_semver` guard (~line 151, before the existing `kind == "foundation"` semver check at ~line 166) is where the closed-kind rejection is seated.
- `src/gzkit/commands/adr_promote.py` — command handler for `gz adr promote`; the `_validate_promotion_kind_semver` guard (~line 54, alongside the existing pool/foundation/feature kind checks) is where the closed-kind rejection is seated.
- `tests/` — new/updated tests covering the three REQs (rejection prose for both verbs; grandfathered-foundation still-validates), plus reconciliation of pre-existing tests that assert the now-closed authoring path.
- `docs/user/manpages/plan-create.md`, `docs/user/manpages/adr-promote.md`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — Gate 3 (Heavy) doc coherence. **Amendment (operator-approved, 2026-07-19):** the brief's Gate 3 section mandated these updates while Allowed Paths omitted them — an authoring contradiction surfaced by the Stage-2 spec review. These four files carry worked examples and operator guidance that the closure makes factually false (e.g. `plan-create.md:90-95` documents an error string the guard now makes unreachable). Fixing the consumer surface in the same commit is AGENTS.md § DO IT RIGHT 1a. Scope is bounded to the false examples and stale guidance; argparse help text, the AGENTS.md/CLAUDE.md Kinds table, `foundation-feature-invariance-test.md`, and the ADR-0.0.35 review remain OBPI-0.34.0-03's sweep per parent-ADR item #3.
- `src/gzkit/commands/interview_cmd.py` — the **third** authoring door. **Amendment (operator-approved, 2026-07-20):** Step-4b adversarial validation (Codex, tier 1) REFUTED the completion claim by reproducing `gz interview adr` authoring a new `kind: foundation` ADR at exit 0. `interview_cmd.py:159-166` carries its *own* kind-routing — it derives `foundation` from a `0.0.x` semver embedded in the ADR id and never calls `plan.py`'s `_render_adr_by_kind`, so there is no shared choke point to guard. Closing only `plan create` and `adr promote` does not discharge this brief's stated objective; per operator doctrine a gap in declared intent is a **correction**, not new scope.
- `features/` — Gate 4 (Heavy) scenarios that assert the now-closed authoring path (`plan_create_nominal.feature`, `adr_promote.feature`). Same amendment; the scenarios carry no `@REQ-0.34.0-02` tag but exercise the surface this OBPI changes, so scoped-tag discipline does not exempt them.
- `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/obpis/OBPI-0.0.57-02-gz-adr-create-nominal-allocator.md` — **supersession annotation only** (operator-approved, 2026-07-20). Deleting `_next_free_nominal_foundation_id` retired the subject of REQ-0.0.57-02-01…-04 and -02-06, so no honest test can cover them. The annotation records the supersession without retracting the attested record; manufacturing coverage instead would be the filesystem-grep anti-pattern (`.gzkit/rules/tests.md` § REQ Scope Discipline).
- `src/gzkit/commands/common.py` — **read-only reference, not modified** (`git status` clean). The REQ-05 test imports `GzCliError` from here to assert the promotion-plan guard's exception type; `gz brief reconcile` surfaces that import as an undeclared surface, so it is declared rather than left as drift.
- `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md` — parent ADR (read-only, for intent and scope).
- This brief itself — evidence sections and the operator-ratified amendments recorded above.


## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/schemas/adr.json` — the `kind` enum MUST retain `foundation` (REQ-0.34.0-02-03 depends on it validating the grandfathered set). Do not remove the value.
- `src/gzkit/cli/parser_governance.py`, `src/gzkit/cli/parser_artifacts.py`, `src/gzkit/cli/parser_maintenance.py` — the argparse `choices=[..., "foundation", ...]` MUST stay so the handler receives `foundation` and emits the guardrail prose (argparse's bare "invalid choice" cannot carry three-part prose). Parser help-text / choices coherence for the closed kind is OBPI-0.34.0-03's coupled-surface sweep, not this OBPI.
- `data/foundation_grandfather.json`, `gz validate --taxonomy` scope — OBPI-0.34.0-01 and -03/-04 own the manifest, closed-kind assertion, and terminal-partition gate.
- All other paths not listed in Allowed Paths; new dependencies; CI files; lockfiles.

> **Governed append-only surfaces are deliberately NOT declared as Allowed Paths.**
> The ledger, the agent-insights log, and the pipeline markers / plan-audit
> receipt under the plans directory are all modified during this OBPI, but only
> ever by governed commands (`gz obpi complete`, `gz task start|complete`,
> `gz insights remember`, the pipeline runtime) — never hand-authored. Allowed
> Paths declares *authoring* scope, and it feeds `is_receipt_fresh()`, which
> compares the reconcile receipt against the mtime of every declared path.
> Declaring the ledger there deadlocks completion permanently: `gz brief
> reconcile` appends its own `brief_reconciled` event, so the ledger is always
> newer than the receipt reconcile just wrote, and no number of re-runs can
> clear it. A first pass added those entries in response to a Step-4b scope
> audit and hit exactly that deadlock — the audit finding was real, but the
> remedy was a category error. Recorded here (deliberately without literal
> backticked paths, which the allowlist extractor would re-capture) so the next
> agent does not re-add them.

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS: Reject at the COMMAND HANDLER (`plan.py` / `adr_promote.py`), never by deleting `foundation` from the schema enum or argparse `choices` — the enum must still validate the ~51 grandfathered `kind: foundation` ADRs.
2. ALWAYS: Each rejection MUST emit three-part guardrail-feedback prose per `.claude/rules/guardrail-feedback-prose.md`: (a) what failed — `--kind foundation` was requested; (b) why forbidden — the foundation kind is closed to new authoring by ADR-0.34.0; (c) governed next step — re-run with `--kind feature` (release-carrying work) or `--kind pool` (backlog).
3. ALWAYS: Both rejected verbs exit non-zero and write no ADR file / perform no promotion I/O (fail before mutation, matching the existing pre-I/O validation ordering in both handlers).
4. NEVER: Widen the rejection to `--kind feature` or `--kind pool` — only `foundation` authoring is closed.
5. NEVER: Break validation of an existing on-disk `kind: foundation` ADR — `gz validate --documents` / `--taxonomy` on the grandfathered set MUST stay green.
6. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.
7. REQUIREMENT: Verification commands MUST be concrete, single-program, and runnable before acceptance.
8. NEVER: Mark the OBPI accepted without explicit human attestation (universal Gate 5, ADR-0.0.36).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary: "reject 'gz plan create --kind foundation' and 'gz adr promote --kind foundation' at the command layer with three-part guardrail-feedback prose (what failed / why forbidden: kind closed ADR-0.34.0 / next step: --kind feature or pool)". The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the sunset closes the foundation kind to new authoring while keeping it a valid schema value for the grandfathered historical set (the kind is SEALED, not deleted).
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.claude/rules/guardrail-feedback-prose.md` — the three-part recovery-prose bar every fail-closed surface must meet (what failed / why forbidden / governed next step).
- [ ] `AGENTS.md` § Gate Covenant / Lane Rules — heavy-lane gate set and universal Gate 5.

**Context:**

- [ ] `src/gzkit/commands/plan.py` `_validate_kind_and_semver` (~line 151) and its existing `console.print(...)` rejection prose for the foundation-semver mismatch — match its console/exit style.
- [ ] `src/gzkit/commands/adr_promote.py` `_validate_promotion_kind_semver` (~line 54) and its existing `--kind pool` rejection prose — match its console/exit style.
- [ ] Sibling OBPIs: OBPI-0.34.0-01 (manifest + closed-kind assertion), OBPI-0.34.0-03 (parser/help coherence sweep) — this OBPI must not overlap their surfaces.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/plan.py` exists and exposes `_validate_kind_and_semver`.
- [ ] `src/gzkit/commands/adr_promote.py` exists and exposes `_validate_promotion_kind_semver`.
- [ ] At least one on-disk `kind: foundation` ADR exists under `docs/design/adr/foundation/` to exercise REQ-0.34.0-02-03.

**Existing Code (understand current state):**

- [ ] Existing tests for `plan create` and `adr promote` kind/semver validation reviewed before implementation (search `tests/` for `_validate_kind_and_semver` / `_validate_promotion_kind_semver` coverage).
- [ ] Both handlers' pre-I/O validation ordering confirmed so the new rejection fires before any file write / promotion move.

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
- [ ] `gz plan create` / `gz adr promote` command docs reflect the closed foundation kind (coordinate with OBPI-0.34.0-03's coupled-surface sweep so the two do not conflict)

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# 1. gz plan create --kind foundation is rejected with three-part guardrail prose
#    (exits non-zero; names ADR-0.34.0 and the --kind feature / --kind pool alternatives; writes no ADR file).
uv run gz plan create sunset-demo --semver 0.0.99 --lane lite --kind foundation

# 2. gz adr promote --kind foundation is rejected with the same three-part guardrail prose.
uv run gz adr promote ADR-pool.some-backlog-item --semver 0.0.99 --kind foundation

# 3. The escape hatch the prose points at still works — feature authoring is unaffected.
uv run gz plan create sunset-demo --semver 0.35.0 --lane lite --kind feature --dry-run

# 4. gz interview adr is the THIRD authoring door: a 0.0.x semver embedded in the
#    canonical id routes to kind: foundation, so it is refused with the same prose.
#    (Found by Step-4b adversarial validation after the first two doors were closed.)
uv run gz interview adr --from answers.json

# 5. An existing grandfathered kind: foundation ADR still validates (closure did not delete the enum value).
uv run gz validate --documents
uv run gz validate --taxonomy
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.34.0-02-01 [BEHAVIOR]: Given `gz plan create --kind foundation`, when the command runs, then it exits non-zero, writes no ADR file, and prints three-part guardrail-feedback prose that (a) states `--kind foundation` was requested, (b) cites the foundation kind as closed to new authoring by ADR-0.34.0, and (c) directs the operator to re-run with `--kind feature` or `--kind pool`.
- [ ] REQ-0.34.0-02-02 [BEHAVIOR]: Given `gz adr promote --kind foundation`, when the command runs, then it exits non-zero, performs no promotion I/O, and prints the same three-part guardrail-feedback prose naming ADR-0.34.0 and the `--kind feature` / `--kind pool` alternatives.
- [ ] REQ-0.34.0-02-03 [BEHAVIOR]: Given an existing grandfathered on-disk `kind: foundation` ADR, when `gz validate --documents` runs over it, then validation exits zero, and the schema `kind` enum and argparse `choices` both still contain `foundation` — closing the authoring doors does not invalidate the frozen grandfathered set. **`gz validate --taxonomy` is deliberately excluded from this REQ** (corrected 2026-07-20): it exits 3 with 74 `foundation_kind_closed` findings, which is OBPI-0.34.0-01's documented interim red pending manifest roster population in OBPI-0.34.0-04. This OBPI must add and remove zero taxonomy findings, and does; requiring exit zero here would make the REQ unsatisfiable by design and invite papering over a deliberate interim state.
- [ ] REQ-0.34.0-02-05 [BEHAVIOR]: Given the programmatic write paths `_render_adr_by_kind` (plan) and `_build_adr_promotion_plan` (promote), when either is called with `kind="foundation"`, then it raises before any file, OBPI, or ledger write — the closure re-validates at the write layer instead of trusting its callers, and `kind="feature"` still renders. **Added 2026-07-20 after Step-4b re-validation** found `_build_adr_promotion_plan` → `_apply_adr_promotion` would still construct a foundation package (6 file writes, 5 ledger appends), and found the first render-layer guard shipped with no covering test (removing it left the whole module green).
- [ ] REQ-0.34.0-02-04 [BEHAVIOR]: Given `gz interview adr` with an answers `id` embedding a `0.0.x` semver (which `_resolve_adr_doc` routes to `kind: foundation`), when the command runs, then it exits non-zero, writes no ADR file, emits no `adr_created` ledger event, and prints the same three-part guardrail prose naming ADR-0.34.0 and the `--kind feature` / `--kind pool` alternatives. **Added 2026-07-20 after Step-4b adversarial validation reproduced this as an open third authoring door** — `interview_cmd.py` derives kind from the embedded semver with its own routing and never calls `plan.py`'s `_render_adr_by_kind`, so guarding the two named verbs left the objective undischarged.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Docs build clean; command docs reflect closed kind
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below; human attestation recorded (Gate 5)

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

### Step 4b — Independent Adversarial Validation

**Adversary:** Codex (`codex-cli 0.144.6`, GPT-5-class) — **tier 1**.
`codex_availability_checked: true`, `codex:setup` reported `ready: true`, so
tiers 2/3 were forbidden (GHI #678). Three rounds, ~50 minutes total, jobs
`task-mrsjk5j1-vbw29i`, `task-mrszks8q-uwwsq6`, `task-mrt0wibe-u5m6ba`.

**Final verdict: REFUTED — resolved.** All three rounds refuted the completion
claim. Each refutation was repaired and re-validated; the sole finding not fixed
here is routed to GHI #706 by operator ruling (see § Tracked Defects).

| Round | Verdict | Claim it broke | Resolution |
|---|---|---|---|
| 1 | REFUTED | `gz interview adr` still authored `kind: foundation` ADRs at exit 0 — `interview_cmd.py` has its own kind-routing and never calls `plan.py`'s render helper, so there was no shared choke point | Guard at `_resolve_adr_doc`; **REQ-0.34.0-02-04 added**. Also fixed 4 red BDD scenarios and 2 attested REQs orphaned by test deletion, both surfaced in the same round |
| 2 | REFUTED | (a) `_build_adr_promotion_plan` → `_apply_adr_promotion` still built a foundation package (6 writes, 5 ledger appends); (b) **the round-1 render-layer guard was hollow** — removing it left all 11 tests green; (c) the strikethrough supersession annotation was **cosmetic** — `gz covers` skipped struck REQs as malformed while `gz adr covers-check` still counted them | Guard added to the promotion-plan builder; **REQ-0.34.0-02-05 added** with three covering tests; strikethrough reverted so both consumers agree on the same 32 REQs |
| 3 | REFUTED | Registration membrane: `gz register-adrs` / first-run `gz init` append `adr_created` for a hand-placed foundation package without a kind check | **Not fixed here** — a correct guard must be manifest-aware and sequences behind OBPI-0.34.0-04. Filed as GHI #706, routed to OBPI-0.34.0-05 (operator ruling 2026-07-20) |

**Round 3 confirmed the round-2 repairs held.** All five guards fire on direct
probe (`_validate_kind_and_semver`, `_render_adr_by_kind`,
`_validate_promotion_kind_semver`, `_build_adr_promotion_plan`,
`_resolve_adr_doc`), and per-guard mutation controls showed **no guard removal
leaves its covering test green** — the round-2 hollow-guard defect is repaired:

```text
test_render_adr_by_kind_refuses_foundation:      guard_removed -> AssertionError: ValueError not raised
test_build_adr_promotion_plan_refuses_foundation: guard_removed -> AssertionError: GzCliError not raised
interview_resolver:                               guard_removed -> AssertionError: 0 == 0
plan_handler / promote_handler:                   guard_removed -> prose assertion fails
```

Round 3 also replayed the ADR-0.0.57 coverage baseline from HEAD objects and
confirmed the delta claim: the only coverage loss is REQ-0.0.57-02-01…-04, with
no unacknowledged regression. It corrected one prose omission (REQ-0.0.57-05-03
was a *third* pre-existing `covers-check` failure), now fixed in that brief.

**Known evidence limitation (disclosed, not worked around).** `gz arb red`
returns weak `failure_class=error` witnesses for all five REQs. Cause, verified
independently by the adversary: `red_witness.py` copies *test* files into the
reconstructed base tree but not the *brief*, so newly-added REQ-04/-05 make
`@covers` fail-close at import against base and collapse the whole module. Logged
as a defect insight against `gz arb red`. Real falsifiability evidence for this
OBPI is the per-guard mutation controls above, not the ARB red receipts.

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

Before: `gz plan create --kind foundation`, `gz adr promote --kind foundation`, and `gz interview adr` (with a `0.0.x` semver embedded in the canonical id) all accepted the foundation kind and scaffolded/promoted a new foundation ADR, so the operator's "no more foundation ADRs" directive was policy-only and could drift. Now: all three authoring doors are closed with actionable three-part guardrail prose that names ADR-0.34.0 and points at the `--kind feature` / `--kind pool` alternatives, and the shared render path (`_render_adr_by_kind`) refuses the kind at the write layer so a future caller cannot reopen it — while the schema enum and argparse choices still carry `foundation` so the grandfathered ADRs keep validating.

The third door was not in the original brief. Step-4b adversarial validation (Codex, tier 1) reproduced `gz interview adr` authoring a foundation ADR at exit 0 after the first two doors were closed, and REFUTED the completion claim; `interview_cmd.py` carries its own kind-routing and never calls `plan.py`'s render helper, so there was no shared choke point to guard. REQ-0.34.0-02-04 and the render-layer guard exist because of that refutation.

### Key Proof


All three authoring doors refuse the kind and write nothing:

```console
$ uv run gz plan create sunset-demo --semver 0.0.99 --lane lite --kind foundation
ERROR: --kind foundation was requested, but the foundation kind is closed to new
authoring by ADR-0.34.0 (Foundation Sunset). It remains a valid schema value
only for the existing grandfathered kind: foundation ADRs already on disk.
Re-run with --kind feature (release-carrying work) or --kind pool (backlog).
$ echo $?
1
```

`gz adr promote --kind foundation` exits 1 with the same prose and leaves the pool ADR and ledger byte-identical. `gz interview adr` with a 0.0.x-embedded id exits 1 and writes no ADR. The escape hatch works: `--kind feature --semver 0.35.0 --dry-run` exits 0.

The grandfathered set is untouched — `uv run gz validate --documents` exits 0 over all 74 on-disk foundation ADRs, and the schema kind enum still reads `['foundation', 'feature']`.

Falsifiability: per-guard mutation controls (Step 4b round 3) show no guard removal leaves its covering test green — `ValueError not raised`, `GzCliError not raised`, `AssertionError: 0 == 0`. This is the real RED evidence; `gz arb red` returns weak error-class witnesses because it copies test files into the reconstructed base tree but not the brief, so newly-added REQs fail-close `@covers` at import (defect insight logged).

### Implementation Summary


- Closed-kind guards seated at five points: `_validate_kind_and_semver` (plan.py), `_validate_promotion_kind_semver` and `_build_adr_promotion_plan` (adr_promote.py), `_resolve_adr_doc` (interview_cmd.py), and `_render_adr_by_kind` (plan.py). Each emits three-part guardrail-feedback prose (what failed / closed by ADR-0.34.0 / re-run with --kind feature or --kind pool) and fails before any file or ledger write.
- Seal-not-delete preserved: `foundation` retained in the adr.json kind enum and in argparse choices, so the 74 grandfathered foundation ADRs still validate.
- Guard ordering is load-bearing: the closure fires before the foundation/semver binding check, so `--kind foundation --semver 0.34.0` reports the closure rather than sending the operator to fix a semver for a kind they may not author.
- Files created: `tests/commands/test_foundation_kind_closed.py` (14 tests); `features/foundation_kind_closed.feature` (3 scenarios), replacing the retired `features/plan_create_nominal.feature`.
- Files modified: `src/gzkit/commands/plan.py`, `src/gzkit/commands/adr_promote.py`, `src/gzkit/commands/interview_cmd.py`; `tests/commands/test_plan.py`, `tests/commands/test_adr_promote.py`, `tests/commands/test_interview_cmd.py`, `tests/test_plan_command.py`, `tests/test_foundation_triage_e2e.py`; `features/adr_promote.feature`, `features/foundation_triage.feature`; `docs/user/manpages/plan-create.md`, `docs/user/manpages/adr-promote.md`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md`.
- Deleted: `_next_free_nominal_foundation_id` (severed from its only production call site by the closure), its tests, 8 orphaned fixture files, and `features/steps/plan_create_nominal_steps.py`.
- 15 pre-existing tests reconciled against the closed door: 4 re-pointed to `--kind feature` (kind was incidental), 2 re-pointed to preserve the last covering proof of attested REQs (REQ-0.0.35-03-06, REQ-0.0.57-05-05), the rest retired with pointers to the closure tests.
- REQ-0.34.0-02-04 and -02-05 were added mid-flight in response to Step-4b adversarial refutations, not authored up front.
- Scope: four operator-ratified Allowed Paths amendments; a supersession annotation on the OBPI-0.0.57-02 brief (REQ-0.0.57-02-01..-04, whose subject the deleted allocator was); GHI #706 filed for the residual registration membrane.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- **GHI #706** — `register-adrs: ledger-books a hand-placed kind: foundation ADR without a kind check`. Found by Step-4b adversarial validation (Codex, tier 1, round 3). `gz register-adrs --all` and first-run `gz init` append `adr_created` for any on-disk versioned ADR without inspecting `kind`, so a hand-authored foundation package can be booked into Layer-2 truth without passing any closure guard. **Deliberately not fixed here** (operator ruling 2026-07-20): a correct guard must be manifest-aware — refusing a foundation package absent from the committed grandfather manifest — and that manifest is still empty pending OBPI-0.34.0-04's roster population, so a naive guard would today refuse all 74 grandfathered ADRs and break REQ-0.34.0-02-03. Routed to **OBPI-0.34.0-05**, which already owns wiring `--taxonomy` into `gz check` and shares the same OBPI-04 dependency. Partial backstop verified in the interim: `foundation_kind_closed` already emits one finding per on-disk foundation absent from the manifest (74 on-disk, 74 findings), so a hand-placed ADR becomes finding #75 — detection, not prevention.

**Distinction this OBPI holds:** *authoring* a foundation ADR is closed at every door (five guards, all verified firing, all mutation-tested). *Registering* an already-on-disk foundation ADR must stay open — that is how the grandfathered set remains in the ledger.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.34.0-02 closes the foundation kind to new authoring at all three CLI doors (gz plan create, gz adr promote, gz interview adr) plus both shared write paths (_render_adr_by_kind, _build_adr_promotion_plan), while the schema kind enum and argparse choices retain `foundation` so all 74 grandfathered on-disk foundation ADRs keep validating (gz validate --documents exit 0). Five BEHAVIOR REQs, 5/5 covered, every guard mutation-tested: no guard removal leaves its covering test green. Evidence: 7178 unittests OK (arb-step-unittest-e68c29af091b4d6a97c40da69a10e1f0), 401 behave scenarios 0 failed (arb-step-behave-b3e8eadb35084f4aad8774fe8859dce2), ruff clean (arb-ruff-efa114e4ff4847f19321f01f4956fa9d), typecheck clean (arb-step-typecheck-6ed5a7a8e429465687edbf9d3586acab), mkdocs --strict clean (arb-step-mkdocs-ca50c772466144e2b10ef244d803fd5c), gz obpi precomplete READY 9/9. gz validate --taxonomy remains at exactly 74 findings, unchanged: this OBPI added and removed none, and roster population is OBPI-0.34.0-04.
- Date: 2026-07-20

---

**Date Completed:** 2026-07-20

**Evidence Hash:** -
</content>
</invoke>
