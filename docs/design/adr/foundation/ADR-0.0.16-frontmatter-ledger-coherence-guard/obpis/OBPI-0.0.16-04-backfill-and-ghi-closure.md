---
id: OBPI-0.0.16-04-backfill-and-ghi-closure
parent: ADR-0.0.16
item: 4
lane: Heavy
status: pending
---

# OBPI-0.0.16-04-backfill-and-ghi-closure: One-time backfill and GHI closure

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- **Checklist Item:** #4 - "One-time backfill and GHI closure: execute chore once against current repo, attach reconciliation receipt as evidence, close GHI #162, #167, #168, #169, #170 with receipt reference"

**Status:** Draft

## Objective

Execute the OBPI-03 chore once against the live repo to clear the current 94.7% `status:` drift (and any other governed-field drift), attach the resulting reconciliation receipt to this ADR's evidence, and close five upstream GHIs (#162, #167, #168, #169, #170) with `gh issue close` comments that cite the receipt path, the ADR ID, and the OBPI-03 chore as the ongoing enforcement mechanism. This OBPI is the dogfooding run — it verifies the chore works end-to-end on real data and produces the evidence artifact that the umbrella-GHI reframing claims as resolved. No new code here; this OBPI is execution + evidence + issue closure.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `artifacts/receipts/frontmatter-coherence/` — receipt emission directory (chore writes here)
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md` — update ADR Evidence section with receipt paths and GHI closure timestamps
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-CLOSEOUT-FORM.md` — update OBPI-04 status and evidence citations
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/obpis/OBPI-0.0.16-04-backfill-and-ghi-closure.md` — record receipt evidence in Evidence section of this brief
- `tests/chores/test_frontmatter_coherence_backfill.py` — regression test pinning post-backfill state (repo stays at zero drift when `gz validate --frontmatter` runs)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Prerequisites — OBPI-0.0.16-01 (validator), OBPI-0.0.16-02 (gate wiring), OBPI-0.0.16-03 (chore), and OBPI-0.0.16-05 (status-vocab mapping) MUST all be completed before this OBPI starts. STOP-on-BLOCKERS if any prerequisite is Pending.
2. REQUIREMENT: ALWAYS run `gz chore run frontmatter-ledger-coherence --dry-run` FIRST, paste the dry-run receipt summary into this OBPI's Evidence section, and obtain operator sign-off on the list of files-to-be-rewritten before the non-dry-run invocation.
3. REQUIREMENT: After operator sign-off, run `gz chore run frontmatter-ledger-coherence` once. The receipt path (`artifacts/receipts/frontmatter-coherence/<ISO8601>.json`) is recorded in this OBPI's Evidence section and in the ADR's Evidence section.
4. REQUIREMENT: After the run, `gz validate --frontmatter` on the full repo MUST exit 0 (no residual drift). If it exits 3, STOP and triage — do NOT hand-edit remaining drift; fix the chore.
5. REQUIREMENT: A second `gz chore run frontmatter-ledger-coherence --dry-run` invocation MUST produce an empty-receipt (idempotence check against the live repo).
6. REQUIREMENT: Close each of the following GHIs via `gh issue close <N> --comment "..."`. The comment text MUST include: the ADR ID (`ADR-0.0.16`), the receipt path from step 3, and a one-line statement of how the guard+chore closes the issue:
   - GHI #162 (ADR frontmatter status: systemically stale — 94.7% drift rate) — closed by backfill receipt.
   - GHI #167 (umbrella: no guard gate or chore audit validates derived frontmatter) — closed by guard (OBPI-01) + gate (OBPI-02) + chore (OBPI-03).
   - GHI #168 (registration path unguarded) — closed by guard; consumer paths are now safe cache reads per umbrella reframing.
   - GHI #169 (identity resolution path unguarded) — closed by guard; consumer paths are now safe cache reads per umbrella reframing.
   - GHI #170 (lineage derivation path unguarded) — closed by guard; consumer paths are now safe cache reads per umbrella reframing.
7. REQUIREMENT: This OBPI does NOT write new source code, schemas, or chore logic. All deliverables are chore invocations, receipt evidence, and issue-closure comments.
8. REQUIREMENT: This OBPI does NOT hand-edit any ADR/OBPI frontmatter. Every rewrite goes through the chore.
9. REQUIREMENT: This OBPI does NOT close GHI #166 (orphan false-positive) — that is a follow-up PR outside this ADR's scope, noted in the downstream-decisions section of ADR-0.0.16.
10. REQUIREMENT: The ADR's Evidence section is updated with: receipt paths (dry-run + live run), the five GH issue numbers + closure timestamps, and the `gz validate --frontmatter` post-run exit code. This OBPI is NOT considered complete until that section is written.

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

- [ ] REQ-0.0.16-04-01: Given all three prerequisite OBPIs are Completed, when OBPI-04 begins, then validator/gate/chore are all runnable end-to-end.
- [ ] REQ-0.0.16-04-02: Given `gz chore run frontmatter-ledger-coherence --dry-run` has been executed, when its receipt is reviewed, then the Evidence section of this brief cites the receipt path and a summary of the files it proposes to rewrite.
- [ ] REQ-0.0.16-04-03: Given operator sign-off on the dry-run plan, when `gz chore run frontmatter-ledger-coherence` executes once, then the live receipt appears under `artifacts/receipts/frontmatter-coherence/<ISO8601>.json` and is cited in both this OBPI's and the ADR's Evidence sections.
- [ ] REQ-0.0.16-04-04: Given the live backfill has completed, when `gz validate --frontmatter` runs against the full repo, then exit code is 0 and no drift is reported.
- [ ] REQ-0.0.16-04-05: Given the backfill has completed, when `gz chore run frontmatter-ledger-coherence --dry-run` runs a second time, then the receipt's `files_rewritten` list is empty (idempotence verified).
- [ ] REQ-0.0.16-04-06: Given the five target GHIs (#162, #167, #168, #169, #170), when each is closed via `gh issue close`, then each closure comment cites `ADR-0.0.16` and the live-run receipt path.
- [ ] REQ-0.0.16-04-07: Given the ADR Evidence section, when it is read at closeout, then it contains: dry-run receipt path, live-run receipt path, five GH issue numbers with closure timestamps, and the post-run `gz validate --frontmatter` exit code.

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

### Dry-run #1 (REQ-02)

- **Command:** `uv run gz frontmatter reconcile --dry-run`
  - **Brief defect:** Brief REQ-02 specifies `gz chore run frontmatter-ledger-coherence --dry-run`, but `gz chores run` (plural) does not accept `--dry-run`. The canonical dry-run surface is `gz frontmatter reconcile --dry-run` (same handler, same receipt schema, same registry-mapped chore). Filed for follow-up in Tracked Defects.
- **Receipt:** `artifacts/receipts/frontmatter-coherence/20260418T095852Z.json`
- **Ledger cursor:** `sha256:519f3e4a2baf7…`
- **Run window:** `2026-04-18T09:58:52.444Z → 2026-04-18T09:58:52.786Z`
- **Files rewritten (proposed):** 257
- **Skipped:** 69 (all `pool-adr` — by-design exclusion)
- **Diff field totals:** `status` 256 · `lane` 1 · `id` 1 · `parent` 1
- **Top status transitions:**
  - `Completed → in_progress` × 204 (largest class — exposes false-completion frontmatter claims)
  - `Proposed → Validated` × 15
  - `Proposed → Pending` × 15
  - `Draft → pending` × 6
  - `Draft → Validated` × 4
  - `Accepted → pending` × 4
  - `Completed → Validated` × 3
  - `Pending → Validated` × 2
  - `Draft → Pending` × 2
  - `Pending-Attestation → Validated` × 1
- **Non-status rewrites (3, structural):**
  - `lane: heavy → lite` × 1
  - `id: OBPI-0.27.0-09-arb-telemetry-sync → OBPI-0.27.0-09-arb-supabase-sync` × 1
  - `parent: ADR-0.3.0 → PRD-GZKIT-1.0.0` × 1
- **Operator sign-off:** _Granted 2026-04-18 ("go") after risk review of 204 `Completed → in_progress` rewrites_

### Live run (REQ-03, REQ-08)

- **Command:** `uv run gz frontmatter reconcile`
- **Receipt:** `artifacts/receipts/frontmatter-coherence/20260418T100437Z.json`
- **Ledger cursor:** `sha256:15ca97fff9efe…`
- **Run window:** `2026-04-18T10:04:36.650Z → 2026-04-18T10:04:37.025Z`
- **Files rewritten:** 257 · **Skipped:** 69 (`pool-adr`)
- **Hand-edits:** 0 (REQ-08 honored — every rewrite passed through the chore)

### Post-run validation (REQ-04) — **BLOCKED**

- **Command:** `uv run gz validate --frontmatter`
- **Exit code:** **3** (policy breach)
- **Errors:** 56 — **all 56 in `docs/design/adr/pool/**`; 0 in active ADR surface**
- **Root cause:** `src/gzkit/commands/validate_frontmatter.py` has no pool-skip filter, while the chore library `src/gzkit/governance/frontmatter_coherence.py` (which the live run correctly invoked) DOES skip pool ADRs (lines 123, 214, 277, 282, 292; comment at line 300: *"validator should not emit errors for pool ADRs"*). The validator was authored under OBPI-0.0.16-01 without parity. Active surface is 100% clean post-backfill.
- **Defect filed:** [GHI #192](https://github.com/tvproductions/gzkit/issues/192) — `validate_frontmatter omits pool-ADR skip filter that frontmatter_coherence library applies`
- **STOP-on-fail honored** per REQ-04 ("do NOT hand-edit remaining drift; fix the chore"). REQ-07 prohibits writing new source code in this OBPI, so the validator fix cannot land here.

### Idempotence dry-run #2 (REQ-05) — **PASS**

- **Command:** `uv run gz frontmatter reconcile --dry-run --json`
- **Receipt:** `artifacts/receipts/frontmatter-coherence/20260418T100647Z.json`
- **Files rewritten:** 0 (idempotence verified — chore stable against post-backfill repo)
- **Skipped:** 69 (unchanged — pool ADRs)

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

- **[GHI #192](https://github.com/tvproductions/gzkit/issues/192)** — `validate_frontmatter` omits the pool-ADR skip filter that `frontmatter_coherence` library applies. Discovered by REQ-04 dogfooding (this OBPI). Blocks REQ-04 exit 0. Suggested fix: new sibling OBPI-0.0.16-06-validator-pool-skip-parity (Lite lane, ~5-line validator change + TDD). Until then OBPI-04 cannot mark Stage 4 ceremony.
- **[GHI #191](https://github.com/tvproductions/gzkit/issues/191)** — `plan-audit-gate` ↔ plan-mode deadlock; surfaced during this OBPI's pipeline entry. Not blocking OBPI-04 itself but tracked for follow-up.
- **Brief command defect** — REQ-02/03/05 specify `gz chore run frontmatter-ledger-coherence [--dry-run]`, but the chores subcommand is plural (`gz chores run`) and does not accept `--dry-run`. Canonical surface is `gz frontmatter reconcile [--dry-run]`. Recommend brief amendment when ADR-0.0.16 reopens for OBPI-06.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
