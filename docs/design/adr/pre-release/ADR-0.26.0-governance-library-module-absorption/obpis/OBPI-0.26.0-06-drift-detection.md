---
id: OBPI-0.26.0-06-drift-detection
parent: ADR-0.26.0-governance-library-module-absorption
item: 6
status: Completed
lane: heavy
date: 2026-03-21
decision: Absorb
paired_with: OBPI-0.25.0-26-drift-detection-pattern
---

# OBPI-0.26.0-06: Drift Detection

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-06 — "Evaluate and absorb lib/drift_detection.py (384 lines) — governance drift detection and alerting"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/drift_detection.py` (384 lines) and
determine: Absorb (opsdev is better) or Exclude (domain-specific). gzkit has
no equivalent module for governance drift detection. The opsdev module
provides dedicated drift detection for comparing declared governance state
against actual filesystem and artifact state, making this a strong absorption
candidate unless the logic is ops-specific.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/drift_detection.py` (384 lines)
- **gzkit equivalent:** None (per parent-ADR Tidy First Plan table). Body-level
  observation in `## Comparison`: gzkit ships
  `src/gzkit/temporal_drift.py` (348 L) absorbed under
  OBPI-0.25.0-26-drift-detection-pattern (attested 2026-04-09). Parent-ADR
  header is intentionally not amended (mirror of OBPI-0.26.0-04 / -05
  pattern).

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane, and any absorption outcome
binds future governance-library absorption work. The brief frontmatter
records a doctrine choice (Absorb-by-reference to OBPI-0.25.0-26) that
future agents will treat as canonical, so Heavy scrutiny applies even
though no code changes under this brief.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Drift detection is fundamental to governance integrity — if governance documents say X exists but it doesn't, that's a governance failure
- The actual gzkit comparison surface for opsdev `lib/drift_detection.py` is
  `src/gzkit/temporal_drift.py` (348 L) plus `tests/test_temporal_drift.py`,
  already absorbed under OBPI-0.25.0-26 — recorded in `## Comparison` body
  section (parent-ADR-authored Source Material header not amended)

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building real-time drift monitoring or alerting infrastructure beyond detection
- Re-running the comparison work already attested under
  OBPI-0.25.0-26-drift-detection-pattern (2026-04-09) on identical source
  material — divergent rationale on identical material is itself a
  doctrine-drift signal

## Requirements (FAIL-CLOSED)

1. Read both implementations completely.
2. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage.
3. Record decision with rationale: Absorb / Exclude.
4. If Absorb: adapt to gzkit conventions and write tests.
5. If Exclude: document why the module is domain-specific.

## Allowed Paths

- `src/gzkit/` — target for absorbed modules (Absorb path only)
- `tests/` — tests for absorbed modules (Absorb path only)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- Any path outside `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/`
  for an Absorb-by-reference outcome (the absorption already shipped under
  OBPI-0.25.0-26; this brief introduces no new code or tests)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies added as a side-effect of a
  governance-library comparison brief
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — understand the 12-module absorption program and the subtraction test
- [x] Sibling OBPI-0.26.0-05-ledger-schema brief (Completed 2026-05-01) — confirm Exclude/Absorb-by-reference structural pattern, source-material observation pattern, `[doc]` REQ tag convention, and GHI #376 third-instance precedent
- [x] OBPI-0.25.0-26-drift-detection-pattern brief (attested 2026-04-09) — canonical precedent for the same source-module evaluation; recorded **Decision: Absorb** with full dimension comparison and the gzkit-side adaptation that ships at `src/gzkit/temporal_drift.py`
- [x] `src/gzkit/schemas/obpi.json` — required headers contract (validator caught ALL-CAPS heading drift; corrected to title case)
- [x] GHI #376 (open) — duplicate-OBPI tracking surface; this brief is the third structural instance of the same defect for `lib/drift_detection.py`

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/drift_detection.py` (384 lines) — opsdev source under review
- [x] Required path exists: `src/gzkit/temporal_drift.py` (348 lines) — gzkit absorbed module shipped under OBPI-0.25.0-26
- [x] Required path exists: `tests/test_temporal_drift.py` — test coverage for the absorbed surface
- [x] Required path exists: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md` — parent ADR
- [x] Parent ADR Cross-Reference Matrix row for `drift_detection.py` reviewed: anticipates "Strong absorption candidate unless drift semantics are ops-specific"

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/drift_detection.py` structure confirmed at lines 32 (`DriftStatus`), 35-54 (`DriftResult`), 57-78 (`ObpiDriftResult`), 86-105 (`_get_head_commit`), 108-129 (`_is_ancestor`), 132-154 (`_count_commits_between`), 162-225 (`classify_drift` pure), 233-262 (`detect_drift` orchestrator), 269 (`OBPI_AUDIT_FILENAME`), 272-325 (`_read_anchored_obpi_entries`), 328-374 (`detect_obpi_drift`), 377-384 (`__all__`)
- [x] `src/gzkit/temporal_drift.py` structure confirmed at lines 41 (`DriftStatus`), 44-54 (`DriftResult`), 57-68 (`ObpiDriftResult`), 76-88 (`_get_head_commit` using `git_cmd`), 91-100 (`_resolve_full_commit` SHA-7 normalization — gzkit-specific addition), 103-116 (`_is_ancestor`), 119-130 (`_count_commits_between`), 138+ (`classify_drift` pure), plus orchestrators reading `gzkit.ledger.Ledger` instead of per-ADR `validation_receipt.read_receipts`
- [x] `tests/test_temporal_drift.py` confirmed: covers `classify_drift` five-branch pure semantics (lines 73-118), plus orchestrator coverage
- [x] Duplicate-OBPI surface check: same source module `lib/drift_detection.py` evaluated under both ADR-0.25.0/OBPI-26 (Absorb, attested) and ADR-0.26.0/OBPI-06 (this brief) — defect tracked under **GHI #376** (will be extended via third-instance comment in Stage 5)

## Quality Gates

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test --obpi OBPI-0.26.0-06-drift-detection` (vacuous parity-gate pass on `[doc]` REQ pattern via `_synthesize_doc_proof_linkage`; covered by `gz covers` parity gate)
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — **already-shipped** under OBPI-0.25.0-26 at `src/gzkit/temporal_drift.py` + `tests/test_temporal_drift.py`

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Exclude` decision (frontmatter `decision: Absorb` + `## Decision` body)
- [x] Comparison rationale names concrete capability differences and the chosen outcome (six-point rationale anchored on OBPI-0.25.0-26 precedent)

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior, the brief names `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [x] Otherwise the brief records `N/A` rationale for no external-surface change — see `### Gate 4 (BDD): N/A` in `## Decision`

### Gate 5: Human

- [ ] Human attestation required (Heavy lane) — recorded during Stage 4 ceremony of `gz-obpi-pipeline`

## Acceptance Criteria

- [x] REQ-0.26.0-06-01: [doc] Given the completed comparison, then the brief
  records one final decision: `Absorb` or `Exclude`.
  **Decision: Absorb** — see frontmatter `decision: Absorb` and `## Decision`
  below.
- [x] REQ-0.26.0-06-02: [doc] Given the decision rationale, then it cites
  concrete capability, robustness, or ergonomics differences between opsdev
  and gzkit. See `## Comparison` (per-dimension table re-anchored from
  OBPI-0.25.0-26 with refreshed line ranges) and `## Decision` (six-point
  rationale anchored on OBPI-0.25.0-26-drift-detection-pattern).
- [x] REQ-0.26.0-06-03: [doc] Given an `Absorb` outcome, then gzkit contains
  the adapted module/tests needed to carry the pattern safely.
  **Already-shipped** under OBPI-0.25.0-26 at `src/gzkit/temporal_drift.py`
  (348 L) + `tests/test_temporal_drift.py`. No new code under this brief —
  re-shipping the absorbed module would invalidate the prior 2026-04-09
  attestation.
- [x] REQ-0.26.0-06-04: [doc] Given an `Exclude` outcome, then the brief
  explains why the pattern is ops-specific or otherwise not fit for gzkit.
  **N/A — Absorb outcome.** This REQ is vacuously satisfied.
- [x] REQ-0.26.0-06-05: [doc] Given any operator-visible behavior change,
  then Gate 4 behavioral proof is present; otherwise the brief records
  `N/A` with rationale. **N/A.** Absorb-by-reference outcome with zero
  code changes under `src/gzkit/`, zero new CLI verbs, zero generated-surface
  change — nothing operator-visible changes under this brief, so Gate 4
  behavioral proof is not required. The original Gate 4 evidence for the
  absorbed module was attested under OBPI-0.25.0-26 on 2026-04-09.

## Verification

```bash
test -f ../airlineops/src/opsdev/lib/drift_detection.py
# Expected: opsdev source under review exists

test -f src/gzkit/temporal_drift.py
# Expected: gzkit absorbed module exists (shipped under OBPI-0.25.0-26)

rg -n '^decision: Absorb|^\*\*Absorb\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Expected: brief frontmatter and Decision body record the Absorb verdict
# (OBPI-0.26.0-06-specific verification command)

rg -n 'OBPI-0.25.0-26' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Expected: brief cites the canonical precedent in body and Closing Argument
# (OBPI-0.26.0-06-specific verification command)

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-06-drift-detection
# Expected: OBPI-scoped tests remain green (vacuous pass when no @covers
# tests target this OBPI — the [doc] REQ pattern routes to brief-content
# proof via _synthesize_doc_proof_linkage; covered by gz covers parity gate)

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Expected: completed brief captures operator-visible proof requirement or N/A rationale
```

## Comparison

### Source-material observation

The brief Source Material header at line 31 of the parent-ADR-authored
scaffold names "gzkit equivalent: None" — mirroring the parent ADR's Tidy
First Plan table at `ADR-0.26.0-...md:31`. That assertion is stale at
authoring time: gzkit ships `src/gzkit/temporal_drift.py` (348 L), absorbed
from this very source file under
**OBPI-0.25.0-26-drift-detection-pattern** (attested 2026-04-09). The
absorbed module's docstring explicitly cites the lineage:

> Lineage: adapted from `opsdev.lib.drift_detection` in airlineops, with
> gzkit-specific changes documented in
> `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-26-drift-detection-pattern.md`.

This observation is body-level (Comparison section); the parent-ADR-authored
Source Material header is intentionally not amended (mirror of the
OBPI-0.26.0-04 / OBPI-0.26.0-05 pattern).

| Surface | Lines | Role |
|---------|-------|------|
| `../airlineops/src/opsdev/lib/drift_detection.py` | 384 | Original opsdev module (reads per-ADR `validation_receipt` ledger + per-OBPI `obpi-audit.jsonl`) |
| `src/gzkit/temporal_drift.py` | 348 | Adapted gzkit module (reads central `.gzkit/ledger.jsonl` via `gzkit.ledger.Ledger`; adds SHA-7 short-anchor normalization via `git_cmd`) |
| `tests/test_temporal_drift.py` | (multi-class) | Pure-classifier and orchestrator coverage for the absorbed surface |

### Per-dimension comparison (re-anchored from OBPI-0.25.0-26 precedent)

The dimension table established by OBPI-0.25.0-26-drift-detection-pattern
(2026-04-09, attested) holds for the gzkit/opsdev capability shape because
the source artifact is identical (`lib/drift_detection.py`, 384 lines) and
the gzkit absorbed surface in `temporal_drift.py` preserves the
two-layer-pure-plus-orchestrator architecture. Line anchors are refreshed
to the current files; gzkit-specific deltas are noted inline.

| Dimension | opsdev `lib/drift_detection.py` (384 L) | gzkit `temporal_drift.py` (348 L) |
| --- | --- | --- |
| Drift state vocabulary | `DriftStatus = Literal["none", "commits_ahead", "diverged"]` (`drift_detection.py:32`) | `DriftStatus = Literal["none", "commits_ahead", "diverged"]` (`temporal_drift.py:41`) — **identical** |
| ADR-level result model | `DriftResult` (Pydantic, `frozen=True`, `extra="forbid"`) — `adr_id`, `status`, `anchor_commit`, `head_commit`, `commits_ahead`, `message` (`drift_detection.py:35-54`) | `DriftResult` with **identical** fields (`temporal_drift.py:44-54`) — same `ConfigDict(frozen=True, extra="forbid")` |
| OBPI-level result model | `ObpiDriftResult` adds `obpi_id`, `adr_id` (`drift_detection.py:57-78`) | `ObpiDriftResult` with **identical** fields (`temporal_drift.py:57-68`) |
| HEAD-commit helper | `_get_head_commit()` raw `subprocess.run` (`drift_detection.py:86-105`) | `_get_head_commit(project_root)` via `gzkit.utils.git_cmd` (`temporal_drift.py:76-88`) — **gzkit-specific delta**: shares the project-wide `git_cmd` cache rather than spawning a fresh subprocess each call |
| Short-SHA normalization | (none — opsdev assumes full SHAs) | `_resolve_full_commit(project_root, short_sha)` via `git_cmd("rev-parse", short_sha)` (`temporal_drift.py:91-100`) — **gzkit-specific addition**: anchors persisted to `.gzkit/ledger.jsonl` are typically SHA-7; this helper round-trips them to full SHA before classification |
| Ancestor check | `_is_ancestor(ancestor, descendant)` returns `True/False/None` (`drift_detection.py:108-129`) | `_is_ancestor(project_root, ancestor, descendant)` with the **same three-state contract** (`temporal_drift.py:103-116`) |
| Commit-count helper | `_count_commits_between(ancestor, descendant)` (`drift_detection.py:132-154`) | `_count_commits_between(project_root, ancestor, descendant)` (`temporal_drift.py:119-130`) — **same contract** |
| Pure classifier | `classify_drift(adr_id, anchor_commit, head_commit, is_ancestor_result, commits_ahead_count)` — five-branch (same / not-found / ancestor-of-HEAD / not-ancestor / message synthesis) (`drift_detection.py:162-225`) | `classify_drift` with **identical signature and five-branch semantics** (`temporal_drift.py:138+`) — testable without mocks |
| ADR-level orchestrator | `detect_drift(adr_id)` reads `adr_folder/logs/{VALIDATION_LEDGER_FILENAME}` via `read_receipts()` (`drift_detection.py:233-262`) | `detect_drift(...)` reads central `.gzkit/ledger.jsonl` via `gzkit.ledger.Ledger` (`temporal_drift.py` orchestrator section) — **gzkit-specific delta**: storage layout re-architected from per-ADR `obpi-audit.jsonl` (CLAUDE.md § Architectural Boundaries item 6 violation) to central Layer-2 ledger reads |
| OBPI-level orchestrator | `detect_obpi_drift(adr_id, obpi_id=None)` parses per-ADR `obpi-audit.jsonl` (`drift_detection.py:328-374`) | `detect_obpi_drift(...)` parses central ledger events emitting OBPI completion anchors — **same gzkit-specific storage delta** |
| Public surface | `__all__ = ["DriftStatus", "DriftResult", "ObpiDriftResult", "classify_drift", "detect_drift", "detect_obpi_drift"]` (`drift_detection.py:377-384`) | **Identical** public surface (`temporal_drift.py` `__all__` block) — gzkit honors the opsdev contract verbatim |
| Test coverage | (opsdev test file external to this evaluation) | `tests/test_temporal_drift.py` exercises `classify_drift` five branches (lines 73-118) plus orchestrator paths — meets `unittest` policy and `TempDBMixin` patterns where DB state is required |

### Cross-platform / convention-compliance observations

opsdev `lib/drift_detection.py` is stdlib + Pydantic + raw `subprocess`
calls. The gzkit absorption substitutes `gzkit.utils.git_cmd` for raw
`subprocess.run`, which:

1. Routes through the project-wide HEAD/git cache (avoids redundant
   subprocess spawns when `_get_head_commit` and `_is_ancestor` fire on
   the same OBPI run).
2. Honors gzkit's UTF-8 encoding contract (`.claude/rules/cross-platform.md`)
   on Windows where opsdev's bare `subprocess.run` would default to
   `cp1252`.
3. Returns `(rc, stdout, stderr)` triples, letting orchestrators distinguish
   "git absent on PATH" (rc 127) from "commit not in repo" (rc 128) without
   conflating both into `RuntimeError`.

The pure classifier is byte-for-byte equivalent in semantics across both
modules — the gzkit-specific deltas are confined to the I/O orchestrators
and the SHA-7 normalization helper. This is exactly the
two-layer-pure-plus-orchestrator architecture OBPI-0.25.0-26 attested as
"the right way to absorb a git-anchored drift primitive."

## Decision

**Absorb** (by reference to OBPI-0.25.0-26-drift-detection-pattern, attested
2026-04-09). The pattern is already adapted into `src/gzkit/temporal_drift.py`
(348 L) with `tests/test_temporal_drift.py` as proof. Re-running the
comparison from scratch on identical source material would either reproduce
the OBPI-0.25.0-26 rationale (waste) or diverge from it (doctrine drift).
This brief records the Absorb verdict by reference and extends GHI #376
with a third instance of the duplicate-OBPI defect.

### Rationale

1. **Canonical precedent.** OBPI-0.25.0-26-drift-detection-pattern evaluated
   the same opsdev source file (`lib/drift_detection.py`, 384 lines) against
   gzkit's drift surface three weeks earlier (attested 2026-04-09) and
   recorded **Decision: Absorb**, with the absorbed module shipping at
   `src/gzkit/temporal_drift.py` (348 L). The source artifact is
   byte-for-byte identical at this brief's authoring time. The OBPI-0.26.0-05
   sibling NON-GOAL section names this pattern explicitly: "Re-running the
   comparison work already attested... on identical source material —
   divergent rationale on identical material is itself a doctrine-drift
   signal." Absorb-by-reference is the structurally correct landing.

2. **Module already shipped.** `src/gzkit/temporal_drift.py` exists at this
   brief's authoring time with the full opsdev public surface (`DriftStatus`,
   `DriftResult`, `ObpiDriftResult`, `classify_drift`, `detect_drift`,
   `detect_obpi_drift`) preserved verbatim, the two-layer-pure-plus-
   orchestrator architecture preserved, and the lineage docstring citing
   OBPI-0.25.0-26 explicitly. Re-shipping under this brief's name would
   invalidate the prior 2026-04-09 attestation and trigger spurious
   `gz validate --reconcile-freshness` drift on a stable surface.

3. **Subtraction test passed.** Drift detection — comparing a recorded git
   anchor commit against current HEAD — is a governance-integrity primitive,
   not airline-specific. The opsdev module's only ops-specific lean was its
   storage assumption (per-ADR `validation_receipt.py` and `obpi-audit.jsonl`
   reads), which OBPI-0.25.0-26 re-architected against gzkit's central
   `.gzkit/ledger.jsonl` per CLAUDE.md § Architectural Boundaries item 6.
   The pure-classifier core is general-purpose; the orchestrators were
   adapted; the contract was preserved.

4. **Pure-classifier-plus-orchestrator architecture preserved.** The
   `classify_drift` function in `temporal_drift.py:138+` is byte-for-byte
   semantically equivalent to opsdev's at `drift_detection.py:162-225` —
   five-branch pure logic, no I/O, fully testable without mocks (verified
   in `tests/test_temporal_drift.py:73-118`). The architecture
   discrimination — git helpers (private subprocess) → pure classifier →
   orchestrators — is the exact shape OBPI-0.25.0-26 attested as the
   absorption justification.

5. **gzkit-specific improvements integrated, not novelties.** The
   gzkit-specific deltas (HEAD cache via `git_cmd`, SHA-7 normalization
   via `_resolve_full_commit`, central-ledger orchestrator reads, UTF-8
   subprocess encoding contract) are integration adjustments, not new
   capabilities. They preserve the opsdev contract while honoring gzkit's
   cross-platform and storage-doctrine rules. No narrow standalone idiom
   warrants a separate absorption beyond what shipped.

6. **Tooling layer vs consumer layer (resolved by re-architecture).**
   gzkit is governance *tooling* that downstream projects adopt; its drift
   detection must read the canonical Layer-2 ledger (`.gzkit/ledger.jsonl`)
   to remain general-purpose. opsdev's original module sat in the consumer
   layer (airlineops-specific per-ADR `obpi-audit.jsonl` files). The
   re-architecture in `temporal_drift.py` lifts the pure logic up into the
   tooling layer while leaving the consumer-layer storage assumption
   behind — exactly the move the subtraction test calls for.

### Tracking the duplicate-evaluation signal

This brief is the third OBPI evaluating an opsdev `lib/` module across two
parent ADRs after the canonical OBPI-0.25.0-* sweep already covered the
same source artifact:

| OBPI | Parent ADR | Source | Decision | Status |
|------|------------|--------|----------|--------|
| OBPI-0.25.0-20-adr-governance-pattern | ADR-0.25.0 | `lib/adr_governance.py` | Confirm | attested 2026-04-11 |
| OBPI-0.26.0-04-adr-governance | ADR-0.26.0 | (same) | Confirm-by-reference | attested |
| OBPI-0.25.0-29-ledger-schema-pattern | ADR-0.25.0 | `lib/ledger_schema.py` | Exclude | attested 2026-04-13 |
| OBPI-0.26.0-05-ledger-schema | ADR-0.26.0 | (same) | Exclude-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-26-drift-detection-pattern | ADR-0.25.0 | `lib/drift_detection.py` | Absorb | attested 2026-04-09 |
| **OBPI-0.26.0-06-drift-detection** | **ADR-0.26.0** | **(same)** | **Absorb-by-reference** (this brief) | **in-flight** |

The duplicate-OBPI surface is structurally identical to GHI #376's canonical
defect ("OBPI absorption sweep authored two parallel OBPIs for the same
source artifact across two ADRs"). Same root cause: the ADR-0.26.0 authoring
did not check whether ADR-0.25.0's earlier absorption sweep had already
covered each module in scope. Same proposed mitigation: the mechanical
guard `gz validate --absorption-duplicates` enumerated in GHI #376's
"Tracking impact" section would catch this third instance alongside the
prior two.

Resolution: extend GHI #376 with this `lib/drift_detection.py` third
instance via `gh issue comment` rather than file a parallel GHI — root
cause and mitigation are identical; tracking unification keeps the
ADR-0.26.0 closeout-audit footprint single. The Absorb-by-reference verdict
here closes the in-flight duplicate; GHI #376 carries the long-term
tracking surface.

### Gate 4 (BDD): N/A

No operator-visible behavior change introduced by this brief. The
absorption already shipped under OBPI-0.25.0-26 on 2026-04-09; its
operator-visible Gate 4 evidence (if any was required) was attested then.
This brief introduces no new commands, flags, output formats, or
behavioral changes — `features/heavy_lane_gate4.feature` is not touched.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.26.0 checklist item #6 captured verbatim above (`OBPI Entry (Level 1 WBS)` line).
- [x] **Gate 2 (TDD):** `uv run gz test --obpi OBPI-0.26.0-06-drift-detection` remains green; vacuous pass on `[doc]` REQ pattern via `_synthesize_doc_proof_linkage`. Absorbed-module test coverage at `tests/test_temporal_drift.py` exists from OBPI-0.25.0-26. Evidence captured in Stage 3 of the pipeline run.
- [x] **Gate 3 (Docs):** Decision rationale completed above (`## Decision`, six points + duplicate-evaluation tracking + Gate 4 N/A) with concrete capability deltas, architectural preservation observations, and the storage re-architecture between opsdev and gzkit.
- [x] **Gate 4 (BDD):** N/A — the Absorb-by-reference outcome introduces no operator-visible behavior change. `features/heavy_lane_gate4.feature` is not touched. Rationale: no CLI surface, no user-facing command, no ledger entry type, and no doc output is added, removed, or modified by this decision.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony of `gz-obpi-pipeline`.

### Implementation Summary


- Decision: Absorb — by reference to OBPI-0.25.0-26-drift-detection-pattern (attested 2026-04-09). gzkit's `src/gzkit/temporal_drift.py` (348 L) + `tests/test_temporal_drift.py` ship the absorbed surface with the full opsdev public contract preserved (`DriftStatus`, `DriftResult`, `ObpiDriftResult`, `classify_drift`, `detect_drift`, `detect_obpi_drift`).
- Modules compared: opsdev `drift_detection.py` (384 L; raw `subprocess`, per-ADR `validation_receipt` + `obpi-audit.jsonl` reads, no SHA-7 normalization) vs gzkit `temporal_drift.py` (348 L; `gzkit.utils.git_cmd` for HEAD cache + UTF-8 encoding, central `.gzkit/ledger.jsonl` orchestrator reads, `_resolve_full_commit` SHA-7 normalization).
- Architectural preservation: pure-classifier-plus-orchestrator shape preserved; `classify_drift` is byte-for-byte semantically equivalent (five-branch pure logic; testable without mocks at `tests/test_temporal_drift.py:73-118`). gzkit-specific deltas confined to I/O orchestrators and the new short-SHA helper.
- Storage re-architecture: opsdev's per-ADR `logs/obpi-audit.jsonl` and `validation_receipt` reads were re-architected against gzkit's central `.gzkit/ledger.jsonl` per CLAUDE.md § Architectural Boundaries item 6 (derived views never silently become source-of-truth). The OBPI-0.25.0-26 absorption performed this re-architecture; this brief inherits it by reference.
- Canonical precedent: OBPI-0.25.0-26-drift-detection-pattern (attested 2026-04-09) recorded **Absorb** with full dimension comparison and the gzkit-side adaptation. This brief reproduces the rationale by reference with refreshed line anchors plus a sixth point on the duplicate-OBPI surface.
- Source-material observation: brief Source Material header (parent-ADR-authored) asserts "gzkit equivalent: None"; actual comparison surface is `temporal_drift.py` + tests, already shipped. Recorded in body, parent-ADR-authored header not amended (mirror of OBPI-0.26.0-04 / -05 pattern).
- Duplicate-OBPI surface tracked under **GHI #376** — third structural instance after `lib/adr_governance.py` (OBPI-0.26.0-04) and `lib/ledger_schema.py` (OBPI-0.26.0-05). Resolution: extend GHI #376 with a third-instance comment, do not file parallel GHI.
- Brief-scaffold drift corrected in flight: ALL-CAPS section headings (`OBJECTIVE`, `SOURCE MATERIAL`, `ASSUMPTIONS`, `NON-GOALS`, `REQUIREMENTS (FAIL-CLOSED)`, `ALLOWED PATHS`, `QUALITY GATES (Heavy)`, `ADR ITEM`) renamed to title case; added missing `Lane`, `Denied Paths`, `Discovery Checklist` sections; corrected `status: Pending` (capital P) to allowed lowercase `pending`; renamed `Verification Commands (Concrete)` → `Verification` and added OBPI-specific `rg -n '^decision: Absorb' ...` and `rg -n 'OBPI-0.25.0-26' ...` commands.
- No code absorbed under this brief; no `src/gzkit/` or `tests/` edits required — the absorption shipped under OBPI-0.25.0-26 and re-shipping would invalidate the prior attestation.

### Key Proof


```bash
rg -n '^decision: Absorb|^\*\*Absorb\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Confirms brief frontmatter and ## Decision body record the Absorb verdict.

rg -n 'OBPI-0.25.0-26' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Confirms brief cites the canonical precedent in body and Closing Argument.

test -f src/gzkit/temporal_drift.py && wc -l src/gzkit/temporal_drift.py
# Expected: 348 src/gzkit/temporal_drift.py (gzkit absorbed module shipped under OBPI-0.25.0-26).

uv run gz covers OBPI-0.26.0-06-drift-detection --json
# Expected: {"summary": {"total_reqs": 5, "uncovered_reqs": 0, ...}} — parity-gate pass for [doc] REQs via _synthesize_doc_proof_linkage.

uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Expected: OBPI Validation Passed.
```

ARB receipts (Stage 3): ruff `arb-ruff-f639783ea13d4d80982a3207da2a7e02`, typecheck `arb-step-typecheck-386e3e7d002344ec9140a92bc7ac251f`, unittest (OBPI-scoped, canonical) `arb-step-unittest-c3231c44dcdb4ca9a7fa2b08b1082428`, mkdocs `arb-step-mkdocs-f68fdcd8d38a49ca971d3b0e78869953`. REQ→@covers parity: `gz covers OBPI-0.26.0-06-drift-detection --json` → `uncovered_reqs: 0` (vacuous parity-gate pass on `[doc]` REQs via `_synthesize_doc_proof_linkage`). Pre-existing failures surfaced during Stage 3, both out of brief boundary and tracked: **GHI #377** (`.gzkit/insights/agent-insights.jsonl:21` violates GHI #358 schema — record uses pre-canonical `kind`/string-evidence/event_id shape, regression of GHI #358 hardening; authored 2026-05-01T01:50:00Z under OBPI-0.26.0-03), **GHI #378** (`release.drift_command` flag past `remove_by=2026-04-30` — calendar boundary tipped today; routes to OBPI ceremony per CLI-surface scope). Mirroring the OBPI-05 sibling precedent: pre-existing failures disclosed, not introduced by this brief.

## Human Attestation

- Attestor: `g0`
- Date: 2026-05-01
- Attestation: attest completed — Absorb-by-reference to OBPI-0.25.0-26-drift-detection-pattern (attested 2026-04-09) on identical opsdev source lib/drift_detection.py (384 lines). gzkit's src/gzkit/temporal_drift.py (348 L) + tests/test_temporal_drift.py ship the absorbed surface with full opsdev public contract preserved (DriftStatus, DriftResult, ObpiDriftResult, classify_drift, detect_drift, detect_obpi_drift); two-layer-pure-plus-orchestrator architecture preserved; classify_drift byte-for-byte semantically equivalent (testable without mocks at tests/test_temporal_drift.py:73-118). gzkit-specific deltas confined to I/O orchestrators (gzkit.utils.git_cmd HEAD cache + UTF-8 contract; central .gzkit/ledger.jsonl reads instead of opsdev's per-ADR validation_receipt + obpi-audit.jsonl per CLAUDE.md Architectural Boundaries item 6) and the new _resolve_full_commit SHA-7 normalization helper. Six-point rationale anchored on canonical precedent (OBPI-0.25.0-26 attested on identical source 3 weeks 1 day earlier), already-shipped module, subtraction-test pass with storage re-architecture, pure-classifier preservation, gzkit-specific improvements as integration not novelty, and tooling-vs-consumer distinction resolved by re-architecture. ARB receipts: ruff arb-ruff-f639783ea13d4d80982a3207da2a7e02, typecheck arb-step-typecheck-386e3e7d002344ec9140a92bc7ac251f, unittest (OBPI-scoped, canonical, mirroring OBPI-05 precedent) arb-step-unittest-c3231c44dcdb4ca9a7fa2b08b1082428, mkdocs arb-step-mkdocs-f68fdcd8d38a49ca971d3b0e78869953. REQ→@covers parity gate green (uncovered_reqs=0; [doc] route via _synthesize_doc_proof_linkage; gz covers parity-gate confirmation). Brief-scaffold drift corrected in flight: ALL-CAPS section headings renamed to title case; added Lane, Denied Paths, Discovery Checklist sections; status Pending corrected to lowercase pending; renamed Verification Commands (Concrete) to Verification with two OBPI-specific commands added. Duplicate-OBPI surface tracked under GHI #376 (third structural instance after OBPI-0.26.0-04 lib/adr_governance.py Confirm-by-reference and OBPI-0.26.0-05 lib/ledger_schema.py Exclude-by-reference); resolution is gh issue comment 376 in Stage 5, not parallel GHI. Pre-existing failures surfaced during Stage 3, both out of brief boundary, both filed today: GHI #377 (.gzkit/insights/agent-insights.jsonl:21 violates GHI #358 schema, regression of #358 hardening, authored 2026-05-01T01:50:00Z under OBPI-0.26.0-03), GHI #378 (release.drift_command flag past remove_by=2026-04-30, calendar boundary tipped today, OBPI ceremony routing). Course-correction insight (Behavior Rule 11): seven-weeks date-arithmetic error caught by operator at Stage 4, corrected in brief body line 287 (three weeks) and recorded in .gzkit/insights/agent-insights.jsonl:22. Heavy-lane Gate 5 attestation; no code under src/gzkit/ or tests/ modified by this brief — Gate 4 N/A documented inline; re-shipping the absorbed module would invalidate the 2026-04-09 OBPI-0.25.0-26 attestation.

### Closing Argument

**Absorb-by-reference.** opsdev's `lib/drift_detection.py` (384 lines) is a
governance-integrity primitive — comparing a recorded git anchor commit
against current HEAD with five-branch pure-classifier semantics — that
gzkit already absorbed under
**OBPI-0.25.0-26-drift-detection-pattern** (attested 2026-04-09). The
absorbed module ships at `src/gzkit/temporal_drift.py` (348 L) with the
full opsdev public surface (`DriftStatus`, `DriftResult`,
`ObpiDriftResult`, `classify_drift`, `detect_drift`, `detect_obpi_drift`)
preserved verbatim, the two-layer-pure-plus-orchestrator architecture
preserved, and the lineage docstring citing OBPI-0.25.0-26 explicitly.
Test coverage at `tests/test_temporal_drift.py` exercises the pure
classifier's five branches (lines 73-118) and the orchestrator paths.

The gzkit-specific deltas — `gzkit.utils.git_cmd` for HEAD cache + UTF-8
encoding, central `.gzkit/ledger.jsonl` orchestrator reads (instead of
opsdev's per-ADR `validation_receipt` + `obpi-audit.jsonl` reads), and
`_resolve_full_commit` SHA-7 normalization — are integration adjustments
that honor gzkit's cross-platform contract and CLAUDE.md § Architectural
Boundaries item 6 (derived views never silently become source-of-truth)
without disturbing the opsdev contract. The pure classifier is byte-for-byte
semantically equivalent.

This brief is the third evaluation of an opsdev `lib/` module across two
parent ADRs that the canonical OBPI-0.25.0-* sweep had already covered.
Re-running the comparison with divergent rationale on identical source
material would itself be a doctrine-drift signal — Absorb-by-reference is
the structurally correct landing, with GHI #376 extended to track this
third occurrence of the duplicate-OBPI defect so the absorption sweep does
not silently recur. No code under `src/gzkit/` or `tests/` is modified by
this brief; re-shipping the already-attested module would invalidate the
2026-04-09 OBPI-0.25.0-26 attestation. Gate 4 N/A: zero operator-visible
behavior change.
