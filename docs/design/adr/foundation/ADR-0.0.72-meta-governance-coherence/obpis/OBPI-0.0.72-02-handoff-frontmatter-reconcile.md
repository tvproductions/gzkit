---
id: OBPI-0.0.72-02-handoff-frontmatter-reconcile
parent: ADR-0.0.72-meta-governance-coherence
item: 2
lane: Heavy
status: Completed
# req_atomic: each REQ is a single indivisible labor unit (ADR-0.0.64 exemption).
# 01 regex-widen; 02/03 model-field declarations; 04 typo-defense (inherent in the
# superset, no separate edit); 06 gate-wiring. 05 bundles the shape-aware validator
# and the reaping adr_id fix, but they are coupled FACETS of one outcome ("real
# register-entry documents round-trip clean") — neither is independently shippable
# (the round-trip needs both), so 05 is one labor unit, not subdivisible seq=02+.
req_atomic:
  - REQ-0.0.72-02-01
  - REQ-0.0.72-02-02
  - REQ-0.0.72-02-03
  - REQ-0.0.72-02-04
  - REQ-0.0.72-02-05
  - REQ-0.0.72-02-06
---

# OBPI-0.0.72-02-handoff-frontmatter-reconcile: Handoff Frontmatter Reconcile

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- **Checklist Item:** #2 - "ADAPTER (C1/C2/C3): reconcile `HandoffFrontmatter` — widen `obpi_id` to the canonical `obpi.json` slug-optional pattern; replace bare `extra=forbid` with an explicit SUPERSET model declaring the min-info fields (last_lock_event_timestamp, last_commit_sha, branch_state) and degenerate/reaping fields (abandoned, category, abandoned_by, abandoned_at, previous_agent, reason); wire `validate_handoff_document` into a gate; verify the model round-trips clean against write_degenerate_handoff, _write_reaping_handoff, a normal-release handoff, and that a slug-bearing obpi_id both validates and exact-matches find_handoff_for_release."

**Status:** Completed

## Objective

Done means `HandoffFrontmatter` accepts the canonical slug-bearing `obpi_id` and every field its own writers emit and its consumers require (the min-info fields `last_lock_event_timestamp`/`last_commit_sha`/`branch` and the degenerate/reaping fields `abandoned`/`category`/`abandoned_by`/`abandoned_at`/`previous_agent`/`reason`), with typo-defense preserved by replacing bare `extra="forbid"` with an explicit SUPERSET model so unknown keys still raise, and `validate_handoff_document` wired into the `gz check` gate so the model can no longer drift un-noticed. This closes C1 (consumer-required fields rejected), C2 (own writers' output rejected), and C3 (slug `obpi_id` rejected and unmatched by `find_handoff_for_release`).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/handoff_validation.py` — the `HandoffFrontmatter` model, the `_OBPI_ID_RE` pattern, the `_validate_obpi_id` validator, and shape-aware `validate_handoff_document`
- `src/gzkit/quality.py` — new `run_handoff_document_audit` gate function that runs `validate_handoff_document` over the `.gzkit/handoffs/` store
- `src/gzkit/commands/quality.py` — register the new audit in the `gz check` bundle (`_build_check_steps`)
- `src/gzkit/lock_manager.py` — EDIT (operator-approved coupled-surface amendment 2026-06-14, full-coherence-fix decision): fix `_write_reaping_handoff`'s `adr_id` derivation so a full-slug lock yields a valid `ADR-X.Y.Z` (the rsplit derivation produced an invalid id; the OBPI's own gate would then fail-close on the reaping writer's output)
- `tests/test_handoff_frontmatter_coherence.py` — **CREATE** round-trip (against REAL writer output) + typo-defense + slug-`obpi_id` + shape-awareness coverage tests
- `data/behave_coverage_waivers.json` — EDIT: OBPI-level behave-coverage waiver (REQ-01..05 unit-proven BEHAVIOR; REQ-06 SUPPORT; no Gherkin-observable verb)
- `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md` — parent ADR for intent and scope (read-only)
- `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/obpis/OBPI-0.0.72-02-handoff-frontmatter-reconcile.md` — active brief and evidence record

**Read-only coherence targets (consult, do NOT edit — these define the shapes the model must accept):**

- `src/gzkit/governance/trust_audits/lock_handoff_coupling.py` — `_MIN_INFO_FRONTMATTER_FIELDS` and `validate_lock_handoff_coupling` (the consumer that REQUIRES the min-info fields, `:170-171`)
- `src/gzkit/schemas/obpi.json` — canonical slug-bearing `id` pattern the `obpi_id` regex must match (`:16`)
- `src/gzkit/traceability.py` — consumed `@covers` decorator source for the REQ tests (NOT edited). Listed here because `gz brief reconcile`'s `_compute_missing_in_brief` neighborhood heuristic flags it as a false positive for top-level-`src/gzkit/` OBPIs: its docstring claims cross-cutting test-infra like `gzkit.traceability` is excluded, but the only mechanism is the parent-dir neighborhood, which coincides with `src/gzkit/` here. Tracked Defects notes the heuristic gap for a separate fix.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT [BEHAVIOR]: A slug-bearing `obpi_id` (canonical `obpi.json` pattern `^OBPI-[0-9]+\.[0-9]+\.[0-9]+-[0-9]{2}(-[a-z0-9-]+)?$`) MUST validate via `HandoffFrontmatter` AND exact-match in `find_handoff_for_release`; the short-form `OBPI-X.Y.Z-NN` MUST still validate (additive, no regression) — closes C3.
2. REQUIREMENT [BEHAVIOR]: The min-info fields `last_lock_event_timestamp` and `last_commit_sha` (the coupling consumer's `_MIN_INFO_FRONTMATTER_FIELDS`, alongside the already-declared `branch`) MUST be accepted by `HandoffFrontmatter` — closes C1.
3. REQUIREMENT [BEHAVIOR]: The degenerate/reaping fields `abandoned`, `category`, `abandoned_by`, `abandoned_at`, `previous_agent`, `reason` MUST be accepted by `HandoffFrontmatter` — closes C2.
4. REQUIREMENT [BEHAVIOR]: Typo-defense MUST be preserved via an EXPLICIT SUPERSET model — an unknown or misspelled key MUST still raise `ValidationError`; `extra="forbid"` is NOT dropped, every real field is declared.
5. REQUIREMENT [BEHAVIOR]: Each REAL document emitted by `write_degenerate_handoff` and `_write_reaping_handoff` MUST round-trip through the shape-aware `validate_handoff_document` with zero violations. Degenerate/reaping register entries (`abandoned: true`) are validated as a DISTINCT document class — frontmatter + abandon fields only; the seven-section and referenced-file contracts apply ONLY to CREATE/RESUME session handoffs. Session handoffs MUST still require all seven sections (shape-awareness does not weaken them). `_write_reaping_handoff` MUST derive a valid `ADR-X.Y.Z` id from the OBPI semver triplet for full-slug locks (the rsplit derivation was broken). The test MUST validate the REAL emitted documents, not synthetic substitutes.
6. REQUIREMENT [SUPPORT]: `validate_handoff_document` MUST be wired into the `gz check` gate (`run_handoff_document_audit` registered in `_build_check_steps`) — closing the enforcement asymmetry without fail-closing on the project's own register-entry writers.
7. NEVER: add a runtime dependency (stdlib + Pydantic only, per `.gzkit/rules/models.md`); edit the read-only coherence targets (`lock_handoff_coupling.py`, `obpi.json`); widen `obpi_id` non-additively; weaken the seven-section contract for CREATE/RESUME session handoffs.
8. ALWAYS: follow TDD (failing test first — today the writer output and slug `obpi_id` are REJECTED); reconcile the brief with the parent ADR before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- [ ] Required path exists: `src/gzkit/handoff_validation.py` (the `HandoffFrontmatter` model + `_OBPI_ID_RE` to reconcile)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

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
- [ ] Relevant docs updated

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

# Specific verification for this OBPI
uv run gz validate --lock-handoff-coupling
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# 1. A real degenerate-handoff frontmatter (slug obpi_id + min-info + abandon fields)
#    now round-trips clean through the reconciled model (today this raises).
uv run python -c "from gzkit.handoff_validation import HandoffFrontmatter; HandoffFrontmatter(mode='CREATE', adr_id='ADR-0.0.72', obpi_id='OBPI-0.0.72-02-handoff-frontmatter-reconcile', branch='main', timestamp='2026-06-13T00:00:00Z', agent='main-session', abandoned=True, category='reaping', reason='ttl', last_lock_event_timestamp='2026-06-13T00:00:00Z', last_commit_sha='abc123'); print('valid')"

# 2. A misspelled key is STILL rejected (typo-defense preserved by the superset).
uv run python -c "from gzkit.handoff_validation import HandoffFrontmatter; from pydantic import ValidationError; \
exec(\"try:\n HandoffFrontmatter(mode='CREATE', adr_id='ADR-0.0.72', branch='main', timestamp='2026-06-13T00:00:00Z', agent='a', last_commmit_sha='x')\n print('LEAKED')\nexcept ValidationError:\n print('rejected as expected')\")"

# 3. The gated coupling validator (consumer side) now passes against a real release handoff.
uv run gz validate --lock-handoff-coupling
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.72-02-01 [behavior]: Given a slug-bearing `obpi_id` matching the canonical `obpi.json` pattern (e.g. `OBPI-0.0.72-02-handoff-frontmatter-reconcile`), when it is passed to `HandoffFrontmatter` and then to `find_handoff_for_release`, then the model validates it AND the lookup exact-matches a handoff carrying that same id (closes C3). (@covers test)
- [ ] REQ-0.0.72-02-02 [behavior]: Given the min-info fields `last_lock_event_timestamp` and `last_commit_sha` that `validate_lock_handoff_coupling`'s `_MIN_INFO_FRONTMATTER_FIELDS` requires (alongside the already-declared `branch`), when they appear in handoff frontmatter, then `HandoffFrontmatter` accepts them rather than raising on extras (closes C1). (@covers test)
- [ ] REQ-0.0.72-02-03 [behavior]: Given the degenerate/reaping fields `abandoned`, `category`, `abandoned_by`, `abandoned_at`, `previous_agent`, and `reason`, when they appear in handoff frontmatter, then `HandoffFrontmatter` accepts them (closes C2). (@covers test)
- [ ] REQ-0.0.72-02-04 [behavior]: Given a handoff frontmatter containing an unknown or misspelled key (e.g. `last_commmit_sha`), when it is passed to `HandoffFrontmatter`, then the model STILL raises `ValidationError` — typo-defense is preserved by the explicit superset, not dropped. (@covers test)
- [ ] REQ-0.0.72-02-05 [behavior]: Given the REAL document emitted by `write_degenerate_handoff` and by `_write_reaping_handoff` (driven live, not hand-copied), when each is run through the shape-aware `validate_handoff_document`, then it round-trips with zero violations — register entries (`abandoned: true`) validated as a distinct class (no 7-section/referenced-file check), `_write_reaping_handoff` deriving a valid `ADR-X.Y.Z` for a full-slug lock — AND a CREATE/RESUME session handoff missing sections is STILL flagged (shape-awareness scoped, not a blanket bypass). (@covers test)
- [ ] REQ-0.0.72-02-06 [support]: Given that `validate_handoff_document` was wired to no gate, when the reconciliation lands, then a `run_handoff_document_audit` step is registered in `gz check`'s `_build_check_steps` and the gated path is exercised by `gz validate --lock-handoff-coupling` (structural validator), with an `artifact_edited` ledger event recording the wiring — closing the enforcement asymmetry so the model can no longer drift un-noticed.

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


- `uv run gz validate --lock-handoff-coupling` -> exit 0 (was RED with 5 violations before this OBPI + the 5 handoff repairs).
- `uv run -m unittest tests.test_handoff_frontmatter_coherence -v` -> 8/8 pass, driving the REAL write_degenerate_handoff and _write_reaping_handoff (not synthetic substitutes); test_shape_awareness_does_not_weaken_session_handoffs proves the 7-section contract still fires for CREATE/RESUME handoffs.
- Full sweep 6157 pass (arb-step-unittest-e7bc1c9b05d74eb8abe0f2d101cb8acc); ruff/typecheck/mkdocs receipts green; real gz validate --invariant-coherence green.

### Implementation Summary


- Files created: tests/test_handoff_frontmatter_coherence.py (8 @covers tests: coherence + shape-awareness + gate)
- Files modified: src/gzkit/handoff_validation.py (explicit-superset HandoffFrontmatter + widened _OBPI_ID_RE + shape-aware validate_handoff_document), src/gzkit/quality.py (run_handoff_document_audit gate), src/gzkit/commands/quality.py (gate registration), src/gzkit/lock_manager.py (adr_id semver derivation fix), 3 handoff repairs (--lock-handoff-coupling RED->GREEN), data/behave_coverage_waivers.json (OBPI waiver)
- Tests added: 8; full unittest sweep 6157 pass / 1 skipped
- Date completed: 2026-06-14
- Attestation status: operator-attested "attest completed" (Heavy/foundation Gate 5; --accept-security-floor for additive run_*_audit runner in security-registered quality.py)
- Defects noted: spec-review caught masked REQ-05 (synthetic-doc validation) -> full coherence fix; tracked follow-ups: list_locks adr_filter sibling bug (same class), reconcile traceability neighborhood heuristic gap, pre-existing behave constitutional_invariants failures + Windows behave cp1252 encoding (both campaign-orthogonal)

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

**Brief internal contradiction surfaced + resolved (full-coherence fix, operator-approved 2026-06-14).** Spec-review caught that the original REQ-05 ("each emitted document round-trips clean") was unsatisfiable as written: the read-only writers emit terse register entries that fail the full-document validator (reaping: invalid `adr_id` from a broken full-slug derivation + 5 missing sections; degenerate: a self-referential pointer to the deleted lock → "Referenced file not found"). Gate-wiring `validate_handoff_document` (REQ-06) would then fail-close `gz check` on every post-cutover reaping/abandon op. The implementer's first-pass test masked this by validating synthetic clean documents instead of the real emitted output (the vibing surface the two-stage review exists to catch). **Resolution (operator-approved):** (1) `validate_handoff_document` made shape-aware — `abandoned: true` register entries are a distinct document class (frontmatter + abandon fields; no 7-section/referenced-file contract); session handoffs keep the full contract. (2) `_write_reaping_handoff`'s `adr_id` derivation fixed to use the OBPI semver triplet (allowlist amended to add `lock_manager.py` as a coupled-surface edit). (3) the REQ-05 test rewritten to drive the REAL writers. DO IT RIGHT full-coherence fix; closes the latent self-breakage rather than re-interpreting the REQ.

**Reconcile heuristic gap (recurs across the ADR-0.0.65/0.0.72 campaign).** `gz brief reconcile`'s `_compute_missing_in_brief` (`src/gzkit/governance/brief_reconcile.py:287`) docstring claims cross-cutting test-infrastructure imports like `gzkit.traceability` (the `@covers` decorator) are excluded, but the only implemented mechanism is the parent-dir neighborhood filter. For any OBPI whose allowlist edits top-level `src/gzkit/*.py` modules, the neighborhood IS `src/gzkit/` so `traceability.py` (a sibling) is flagged as scope leakage — a systematic false positive. Worked around here by listing `traceability.py` in the read-only coherence targets (consumed, not edited). Proper fix: add an explicit `_CROSS_CUTTING_TEST_INFRA = {"gzkit.traceability"}` exclusion in `_compute_missing_in_brief` (deferred — the pipeline-gate hook blocks editing `brief_reconcile.py` while this OBPI's pipeline is active; route as a direct-fix between OBPIs or fold into OBPI-0.0.72-01).

**GHI #612 linkage (audit-trail backfill, 2026-07-01).** The reconciliation this OBPI performed (explicit-superset `HandoffFrontmatter`, widened `_OBPI_ID_RE`, shape-aware `validate_handoff_document`) is also the direct-fix resolution for external GHI #612 ("handoff-model: HandoffFrontmatter rejects fields its own writers emit") — its C1/C2/C3 canonical-contradiction items map 1:1 onto REQ-0.0.72-02-01/02/03. The landing commit (`81ae707b`, a `gz git-sync` chore sweep) carried no `(GHI #612)` trailer, so `ghi-close`'s Phase 3 commit-trailer check found no citation; this note plus its own commit trailer close that audit-trail gap without rewriting the original commit.

_No further defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.72-02: HandoffFrontmatter reconciled (explicit-superset model accepts all writer/consumer fields — slug obpi_id, min-info, degenerate/reaping; typo-defense intact); validate_handoff_document made shape-aware (register entries a distinct doc class); _write_reaping_handoff adr_id derivation fixed for full-slug locks; gate-wired into gz check. Spec-review round-2 PASS after a masked-REQ-05 critical (synthetic-doc validation) was fully fixed to drive the real writers; --lock-handoff-coupling RED->GREEN (5 handoff repairs); full sweep 6157 pass (arb-step-unittest-e7bc1c9b05d74eb8abe0f2d101cb8acc), ruff (arb-ruff-babc4572511448aca4c0df5d49df22d9) / typecheck (arb-step-typecheck-c84c2851c6c44cd3bcb667156c298ddf) / mkdocs (arb-step-mkdocs-57a565e168964c858a216346ce6f02dd) green.
- Date: 2026-06-14

---

**Date Completed:** 2026-06-14

**Evidence Hash:** -
