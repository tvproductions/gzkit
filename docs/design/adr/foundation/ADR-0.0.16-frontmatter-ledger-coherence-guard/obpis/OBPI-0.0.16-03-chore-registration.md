---
id: OBPI-0.0.16-03-chore-registration
parent: ADR-0.0.16
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.16-03-chore-registration: Chore registration and reconciliation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- **Checklist Item:** #3 - "Chore registration: config/chores/frontmatter-ledger-coherence.toml with ledger-wins auto-fix, idempotent reconciliation, receipt emission per run including ledger cursor, --dry-run mode, operator notes on destructive-to-hand-edits behavior"

**Status:** Draft

## Objective

Register a `frontmatter-ledger-coherence` chore at `config/chores/frontmatter-ledger-coherence.toml` that sweeps every ADR/OBPI file, consumes the OBPI-01 validator's drift output, and reconciles drift with ledger-wins semantics (overwrites frontmatter `id`/`parent`/`lane`/`status` to match the ledger, using the OBPI-02 canonical status-vocabulary mapping). Each run emits a JSON reconciliation receipt at `artifacts/receipts/frontmatter-coherence/<ISO8601>.json` containing the ledger cursor sampled, every file rewritten, and per-field before/after values. Supports `--dry-run` that computes the same output without mutating files. Idempotent: running twice with no intervening ledger change produces an empty receipt on the second run. No gate wiring here; no one-time backfill here (that's OBPI-04 consuming this chore).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `config/chores/frontmatter-ledger-coherence.toml` — new chore registration with ledger-wins semantics
- `src/gzkit/chores/frontmatter_coherence.py` — new chore implementation importing the OBPI-01 validator and OBPI-02 status-vocab mapping
- `data/schemas/frontmatter_coherence_receipt.schema.json` — JSON schema for reconciliation receipts
- `tests/chores/test_frontmatter_coherence.py` — unit tests: reconciliation, idempotence, dry-run, receipt schema, ungoverned-key preservation
- `docs/user/commands/chores.md` — document the new chore
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md` — parent ADR for intent and scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: A chore named `frontmatter-ledger-coherence` is registered at `config/chores/frontmatter-ledger-coherence.toml` and appears in `gz chores list`.
2. REQUIREMENT: The chore imports and invokes the OBPI-01 validator — it NEVER reimplements drift detection. If the validator returns exit code 0, the chore emits an empty-receipt and exits 0.
3. REQUIREMENT: When drift is detected, the chore ALWAYS rewrites the frontmatter to match the ledger (ledger-wins). It NEVER rewrites the ledger to match frontmatter.
4. REQUIREMENT: The `status:` field is rewritten using the OBPI-05 canonical status-vocabulary mapping (imported as `STATUS_VOCAB_MAPPING`), not the raw ledger term. (If the mapping does not cover a term, the chore STOPs with a BLOCKER naming the unmapped term — it NEVER silently passes it through.)
5. REQUIREMENT: A reconciliation receipt is written to `artifacts/receipts/frontmatter-coherence/<ISO8601>.json` on every non-dry-run invocation. The receipt contains: `ledger_cursor` (latest ledger event hash/id sampled), `run_started_at`, `run_completed_at`, `files_rewritten` (list), `files_rewritten[].path`, `files_rewritten[].diffs[]` (with `field`, `before`, `after`), `dry_run` (bool).
6. REQUIREMENT: The receipt validates against a JSON schema `data/schemas/frontmatter_coherence_receipt.schema.json` with `$id: gzkit.frontmatter_coherence_receipt.schema.json`.
7. REQUIREMENT: `--dry-run` produces the same receipt content with `dry_run=true` and makes NO filesystem writes to ADR/OBPI files. The dry-run receipt is still emitted to `artifacts/receipts/frontmatter-coherence/`.
8. REQUIREMENT: Idempotence — after a non-dry-run invocation completes, a subsequent invocation with no intervening ledger change produces a receipt with empty `files_rewritten`.
9. REQUIREMENT: The chore NEVER mutates ungoverned frontmatter keys (`tags:`, `related:`, others). It preserves them byte-identically.
10. REQUIREMENT: Operator notes at the top of `config/chores/frontmatter-ledger-coherence.toml` state plainly: "Frontmatter `id`/`parent`/`lane`/`status` are derived state. Hand-edits to these fields will be overwritten on the next chore run. Edit the ledger via `gz` commands instead."
11. REQUIREMENT: The chore does NOT close any GitHub issues. Issue closure is OBPI-04's responsibility.
12. REQUIREMENT: The chore does NOT wire into `gz gates`. Gate integration lives in OBPI-02.
13. REQUIREMENT: Tests cover: chore registration visibility (`gz chores list`), ledger-wins rewrite correctness (one ADR per governed field), idempotence, dry-run non-mutation, receipt schema validation, ungoverned-key preservation, unmapped-status-term BLOCKER behavior.
14. REQUIREMENT (prerequisites): OBPI-0.0.16-01 (validator) AND OBPI-0.0.16-05 (status-vocab mapping) MUST both be completed before this OBPI starts.

### Known Edge Cases (MUST be addressed in implementation)

These edge cases were surfaced during ADR-0.0.16 red-team review (Consumer Challenge). They are not hypothetical — each has a concrete failure mode the chore must handle explicitly.

1. **Mid-gate-transition race.** If a ledger write is in flight (a gate transition event being appended) when the chore reads the ledger cursor, the chore can see the pre-event state and rewrite frontmatter to the pre-transition value — which is then immediately stale. **Resolution:** the chore snapshots the ledger cursor at run-start and samples the artifact graph at that cursor only; it NEVER mixes the starting cursor with any subsequent ledger state during the same run. Tests cover this by seeding a ledger mutation mid-run (via fixtures, not real concurrency) and asserting the chore's receipt reflects the starting cursor's state.
2. **Pool ADRs (unregistered frontmatter).** ADR files under `docs/design/adr/pool/` may exist on disk without a corresponding ledger entry (they are pre-promotion backlog). For a pool ADR, the ledger's artifact-graph lookup returns nothing. **Resolution:** the chore skips pool ADRs entirely (identified by the `ADR-pool.` prefix in `id:` or path location under `pool/`) and emits a per-skip note in the receipt so operators see which files were intentionally untouched. Tests assert that seeding drift into a pool ADR's frontmatter leaves it unchanged after the chore runs.
3. **Partial-failure mid-sweep.** If the chore crashes after rewriting N of M files (disk full, SIGKILL, etc.), the receipt must still reflect the N completed rewrites so the operator can resume or audit the partial state. **Resolution:** the chore writes each per-file rewrite's receipt entry immediately after each file's write, not as a single batch at the end. The receipt file is append-flushed per file. If the chore is interrupted, the receipt shows exactly which files were rewritten. A subsequent full run is idempotent (per REQUIREMENT 8) and completes the remainder. Tests cover this by simulating interruption after file N and asserting the receipt shows N entries, then re-running and asserting idempotent completion.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/**`
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
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.16-03-01: Given `gz chores list`, when the operator runs it after OBPI-03, then `frontmatter-ledger-coherence` appears in the chore registry with its description and default cadence.
- [ ] REQ-0.0.16-03-02: Given a repo with seeded drift in `status:` for one ADR, when `gz chore run frontmatter-ledger-coherence` executes (non-dry-run), then the ADR's frontmatter `status:` is rewritten to the canonical ledger term and a receipt is emitted under `artifacts/receipts/frontmatter-coherence/`.
- [ ] REQ-0.0.16-03-03: Given `--dry-run`, when the chore runs against a drifted repo, then no ADR/OBPI file is mutated, and the receipt contains `dry_run=true` with the same `files_rewritten` list the non-dry-run would have produced.
- [ ] REQ-0.0.16-03-04: Given the chore has completed once against a drifted repo, when it is invoked a second time with no intervening ledger change, then the receipt's `files_rewritten` array is empty.
- [ ] REQ-0.0.16-03-05: Given a frontmatter file with ungoverned keys (`tags:`, `related:`), when the chore rewrites governed fields, then the ungoverned keys are preserved byte-identically.
- [ ] REQ-0.0.16-03-06: Given every emitted receipt, when validated against `data/schemas/frontmatter_coherence_receipt.schema.json`, then validation succeeds.
- [ ] REQ-0.0.16-03-07: Given a ledger term with no mapping in the OBPI-05 status vocab, when the chore encounters it, then the chore exits with a BLOCKER naming the unmapped term and NO files are mutated.
- [ ] REQ-0.0.16-03-08: Given a simulated mid-run ledger mutation (fixture injection), when the chore completes, then the receipt reflects the starting-cursor state only — never a mixed view.
- [ ] REQ-0.0.16-03-09: Given a pool ADR with seeded frontmatter drift (`ADR-pool.*` or path under `docs/design/adr/pool/`), when the chore runs, then the file is skipped and a per-skip note appears in the receipt.
- [ ] REQ-0.0.16-03-10: Given a simulated interruption after rewriting N of M files, when the receipt is inspected, then it shows exactly N entries; a subsequent re-run idempotently completes the remaining M-N rewrites.

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

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
