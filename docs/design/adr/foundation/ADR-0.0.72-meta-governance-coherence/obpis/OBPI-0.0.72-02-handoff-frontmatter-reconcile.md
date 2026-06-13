---
id: OBPI-0.0.72-02-handoff-frontmatter-reconcile
parent: ADR-0.0.72-meta-governance-coherence
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.72-02-handoff-frontmatter-reconcile: Handoff Frontmatter Reconcile

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- **Checklist Item:** #2 - "ADAPTER (C1/C2/C3): reconcile `HandoffFrontmatter` — widen `obpi_id` to the canonical `obpi.json` slug-optional pattern; replace bare `extra=forbid` with an explicit SUPERSET model declaring the min-info fields (last_lock_event_timestamp, last_commit_sha, branch_state) and degenerate/reaping fields (abandoned, category, abandoned_by, abandoned_at, previous_agent, reason); wire `validate_handoff_document` into a gate; verify the model round-trips clean against write_degenerate_handoff, _write_reaping_handoff, a normal-release handoff, and that a slug-bearing obpi_id both validates and exact-matches find_handoff_for_release."

**Status:** Draft

## Objective

Done means `HandoffFrontmatter` accepts the canonical slug-bearing `obpi_id` and every field its own writers emit and its consumers require (the min-info fields `last_lock_event_timestamp`/`last_commit_sha`/`branch` and the degenerate/reaping fields `abandoned`/`category`/`abandoned_by`/`abandoned_at`/`previous_agent`/`reason`), with typo-defense preserved by replacing bare `extra="forbid"` with an explicit SUPERSET model so unknown keys still raise, and `validate_handoff_document` wired into the `gz check` gate so the model can no longer drift un-noticed. This closes C1 (consumer-required fields rejected), C2 (own writers' output rejected), and C3 (slug `obpi_id` rejected and unmatched by `find_handoff_for_release`).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/handoff_validation.py` — the `HandoffFrontmatter` model, the `_OBPI_ID_RE` pattern, the `_validate_obpi_id` validator, and `validate_handoff_document`
- `src/gzkit/quality.py` — new `run_handoff_document_audit` gate function that runs `validate_handoff_document` over `.gzkit/handoffs/*.md`
- `src/gzkit/commands/quality.py` — register the new audit in the `gz check` bundle (`_build_check_steps`)
- `tests/test_handoff_frontmatter_coherence.py` — **CREATE** round-trip + typo-defense + slug-`obpi_id` + writer-output coverage tests
- `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/**` — parent ADR package scope (this brief + evidence)

**Read-only coherence targets (consult, do NOT edit — these define the shapes the model must accept):**

- `src/gzkit/lock_manager.py` — `_write_reaping_handoff` (reaping frontmatter writer, `:231-245`)
- `src/gzkit/governance/trust_audits/lock_handoff_coupling.py` — `_MIN_INFO_FRONTMATTER_FIELDS` and `validate_lock_handoff_coupling` (the consumer that REQUIRES the min-info fields, `:170-171`)
- `src/gzkit/schemas/obpi.json` — canonical slug-bearing `id` pattern the `obpi_id` regex must match (`:16`)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS preserve typo-defense via an EXPLICIT SUPERSET model. NEVER simply drop `extra="forbid"` — an unknown or misspelled frontmatter key MUST still raise `ValidationError`. The reconciliation declares every real field; it does not loosen the guard.
2. ALWAYS widen `obpi_id` to accept the canonical slug-bearing `obpi.json` pattern (`^OBPI-[0-9]+\.[0-9]+\.[0-9]+-[0-9]{2}(-[a-z0-9-]+)?$`). The widening is ADDITIVE — the short-form `OBPI-X.Y.Z-NN` MUST still validate (no regression).
3. ALWAYS declare every field the module's writers emit: the min-info fields `last_lock_event_timestamp`, `last_commit_sha`, `branch` (the coupling consumer's `_MIN_INFO_FRONTMATTER_FIELDS`; `branch` is already declared, the other two are not) and the degenerate/reaping fields `abandoned`, `category`, `abandoned_by`, `abandoned_at`, `previous_agent`, `reason`.
4. ALWAYS wire `validate_handoff_document` into the `gz check` gate. NEVER leave the authoring model un-gated — the enforcement asymmetry (strict consumer, toothless authoring model) is the root cause this OBPI closes.
5. NEVER add a runtime dependency. Stdlib + Pydantic only (Pydantic is the named departure per `.gzkit/rules/models.md`).
6. ALWAYS keep changes inside the Allowed Paths. NEVER edit the read-only coherence targets (`lock_manager.py`, `lock_handoff_coupling.py`, `obpi.json`) — the model reconciles TO them; they are the fixed contract.
7. ALWAYS follow TDD: write the failing test first (today the writer output and the slug `obpi_id` are REJECTED by the model), then the model change turns it green.

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
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/**`
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
- [ ] REQ-0.0.72-02-05 [behavior]: Given the exact frontmatter emitted by `write_degenerate_handoff` and by `_write_reaping_handoff`, when each emitted document is run through `validate_handoff_document`, then it round-trips with zero violations (the writers' own output validates against their own authoring model). (@covers test)
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
