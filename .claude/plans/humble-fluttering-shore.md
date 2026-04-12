# Plan: OBPI-0.25.0-26 — Drift Detection Pattern

## Context

OBPI-0.25.0-26 is part of ADR-0.25.0 (Core Infrastructure Pattern Absorption), Phase 2. It evaluates `airlineops/src/opsdev/lib/drift_detection.py` (384 lines) against gzkit's existing drift surface (`src/gzkit/commands/drift.py` 186 lines + `src/gzkit/triangle.py` 372 lines = ~558 lines) and records an `Absorb` / `Confirm` / `Exclude` decision in the OBPI brief, following the pattern established by the prior Phase 2 OBPIs (-19 through -25).

The two implementations share only the word *drift* — they address orthogonal concerns:

- **airlineops `drift_detection.py`** = **temporal drift**. Reads validation receipts that anchor an ADR validation to a git commit, then asks "has the codebase moved since validation?" by classifying anchor-vs-HEAD as `none`, `commits_ahead` (linear progression), or `diverged` (rebase/force-push, or commit not found). Provides ADR-level (`detect_drift`) and per-OBPI (`detect_obpi_drift`) detectors built on a pure `classify_drift()` function plus thin git subprocess wrappers.
- **gzkit `triangle.py` + `commands/drift.py`** = **structural triangle drift**. Parses REQ entities from OBPI brief acceptance criteria, scans tests for `@covers REQ-…` linkages, and inspects the active git change set. Reports `unlinked_specs` (REQs with no `@covers`), `orphan_tests` (`@covers` referencing non-existent REQs), and `unjustified_code_changes` (changed `src/` files with no `JUSTIFIES` edge). Pure `detect_drift()` function over Pydantic models.

Critically, gzkit **already captures** `anchor.commit` in validation receipts via `capture_validation_anchor_with_warnings()` in `src/gzkit/utils.py:64-89` (used by `audit_cmd.py`, `obpi_stages.py`, `status_obpi.py`, `ledger_semantics.py`). The data is being written, but no detector reads it back to surface temporal staleness. This is exactly the gap airlineops's module fills.

The expected decision is **Absorb** because:

1. The subtraction test passes: temporal drift detection is not airline-specific; it operates on git plus a generic validation-receipt schema that gzkit already maintains.
2. There is a real capability gap: gzkit writes anchor commits but never asks "is this validation stale?".
3. The airlineops module is well-architected (pure classifier separated from I/O; frozen Pydantic models; thin subprocess wrappers; UTF-8 by default) and already aligns with gzkit conventions.
4. The two `drift` concepts are orthogonal — adding temporal drift does not collide with the existing `gz drift` (triangle) command surface.

The plan is structured so that the comparison work happens first; if the evidence overturns Absorb during the analysis, the same brief sections (Comparison, Decision, Closing Argument) still apply for Confirm/Exclude — only Tasks 4 and 5 (code + tests) become N/A.

## Source Material

- **airlineops:** `../airlineops/src/opsdev/lib/drift_detection.py` (384 lines)
- **gzkit equivalents:**
  - `src/gzkit/commands/drift.py` (186 lines) — triangle drift CLI
  - `src/gzkit/triangle.py` (372 lines) — REQ extraction + triangle drift engine
  - `src/gzkit/utils.py:64-89` — `capture_validation_anchor_with_warnings()` (existing anchor capture, no detector)
- **Pattern reference:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-25-docs-validation-pattern.md` (Confirm decision, full structure)

## Brief Requirements (FAIL-CLOSED)

From `OBPI-0.25.0-26-drift-detection-pattern.md`:

1. Read both implementations completely
2. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
3. Record decision with rationale: Absorb / Confirm / Exclude
4. If Absorb: adapt to gzkit conventions and write tests
5. If Confirm: document why gzkit's implementation is sufficient
6. If Exclude: document why the module is domain-specific

## Allowed Paths (from brief)

- `src/gzkit/` — target for absorbed module
- `tests/` — tests for absorbed module
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and brief

No other paths will be touched. No new directories outside `src/gzkit/` or `tests/`.

## Plan

### Task 1 — Document the side-by-side comparison in the brief

Add a `## Comparison` section to `OBPI-0.25.0-26-drift-detection-pattern.md` containing three tables, mirroring the OBPI-0.25.0-25 pattern:

1. **airlineops `drift_detection.py` table** — function-by-function inventory: `_get_head_commit`, `_is_ancestor`, `_count_commits_between`, `classify_drift`, `detect_drift`, `_read_anchored_obpi_entries`, `detect_obpi_drift`; `DriftResult` and `ObpiDriftResult` Pydantic models; `DriftStatus` literal type.
2. **gzkit drift surface table** — `triangle.py` (REQ entity, vertex/edge model, brief scanner, triangle `detect_drift()`); `commands/drift.py` (`scan_covers_references`, `get_changed_files`, `_format_human`/`_format_plain`, `drift_cmd`); `utils.py:capture_validation_anchor_with_warnings()` (anchor capture without detector).
3. **Capability comparison table** with these dimensions: problem scope, anchor source, drift classification model, output schema, error handling, cross-platform robustness, conventions (Pydantic/pathlib/UTF-8), testability (pure vs orchestrator separation), CLI integration, current gap.

The narrative will name the orthogonality explicitly: gzkit drift = structural triangle; airlineops drift = git-temporal. The capability table will identify the temporal-anchor-detector gap.

**File modified:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-26-drift-detection-pattern.md` (Comparison section added before existing Requirements section)

### Task 2 — Record the decision and rationale

Add `## Decision: Absorb` (or `Confirm` / `Exclude` if Task 1's evidence overturns the recommendation) to the brief, with a numbered rationale of at least 5 points covering:

1. Subtraction test result (temporal drift is not airline-specific)
2. Concrete capability gap (gzkit writes `anchor.commit` but never reads it back)
3. Architectural fit (pure classifier + thin I/O matches gzkit's preferred shape)
4. Convention alignment (frozen Pydantic models, UTF-8, pathlib, subprocess list-form)
5. Why temporal drift does not collide with existing triangle drift (orthogonal concerns, separate module surface)

**File modified:** same OBPI brief (Decision section).

### Task 3 — Add the absorbed module (only if decision = Absorb)

Add `src/gzkit/temporal_drift.py` (target: ~250 lines) adapted from airlineops with these gzkit-specific changes:

- **Imports:** drop `opsdev.lib.adr_recon` and `opsdev.lib.validation_receipt` in favor of gzkit equivalents. Use `gzkit.commands.common.get_project_root()` and read receipts via existing gzkit helpers (will identify the right module by inspecting `audit_cmd.py` and `ledger_semantics.py` while reading the source).
- **Models:** keep `DriftStatus = Literal["none", "commits_ahead", "diverged"]`; keep `DriftResult` and `ObpiDriftResult` as `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` (gzkit default). Field documentation kept verbatim where it remains accurate.
- **Pure classifier:** keep `classify_drift()` byte-for-byte (it is already pure and convention-compliant).
- **Git helpers:** keep `_get_head_commit`, `_is_ancestor`, `_count_commits_between` as private module-level functions. Replace direct `subprocess.run` with the existing `git_cmd()` helper from `src/gzkit/utils.py` to share caching, error capture, and encoding handling. This is the only structural deviation from airlineops and it removes a duplication.
- **Orchestrators:** rewrite `detect_drift(adr_id)` and `detect_obpi_drift(adr_id, *, obpi_id=None)` to read from gzkit's actual ledger/receipt locations (TBD during implementation by tracing how `audit_cmd.py` and `obpi_stages.py` already locate receipts).
- **Module docstring:** explain the temporal-vs-structural distinction so future readers do not confuse this module with `triangle.py`.
- **Public API:** `__all__ = ["DriftStatus", "DriftResult", "ObpiDriftResult", "classify_drift", "detect_drift", "detect_obpi_drift"]`.

No new CLI subcommand is added in this OBPI — surface integration is a follow-on concern. The module is importable and tested standalone. (If a brief reviewer wants CLI surfacing inside this OBPI, the plan can be revised in Task 1's review.)

**File created:** `src/gzkit/temporal_drift.py`

### Task 4 — Add tests for the absorbed module (only if decision = Absorb)

Add `tests/test_temporal_drift.py` covering:

1. **`classify_drift` (pure, no I/O):**
   - Same commit → `none`, `commits_ahead=0`
   - Anchor is ancestor of HEAD, count=N → `commits_ahead`, `commits_ahead=N`
   - Anchor is ancestor of HEAD, count is None → `commits_ahead`, `commits_ahead=0` (None coerced)
   - Anchor not ancestor → `diverged`, `commits_ahead=None`
   - Anchor not in repo (`is_ancestor_result is None`) → `diverged`, `commits_ahead=None`
   - Message field formatting for each branch
2. **`_get_head_commit`, `_is_ancestor`, `_count_commits_between` via `tempfile.TemporaryDirectory` + git init:** create a real temp git repo, make 2-3 commits, exercise each helper for success and failure paths. No mocking.
3. **`detect_drift` orchestrator:** temp repo + temp ledger fixture; assert it returns `None` when no receipt exists, returns a `DriftResult` when one does, and that the classification matches the underlying classify_drift path.
4. **`detect_obpi_drift` orchestrator:** temp repo + temp `obpi-audit.jsonl`; assert filtering by `obpi_id`, sorted output, empty list when no anchored entries.
5. **Cross-platform tests:** all temp paths via `pathlib.Path` + `tempfile.TemporaryDirectory()` context managers (no `shutil.rmtree`); UTF-8 reads explicit; subprocess calls use `git_cmd()` from `utils.py` (no `shell=True`).

Target: ≥15 unittest cases, all derived from REQ-0.25.0-26-01 through -05 acceptance criteria.

**File created:** `tests/test_temporal_drift.py`

### Task 5 — Update the brief gates, acceptance criteria, and Closing Argument

Mark in the brief:

- Gate 1 (ADR): checked
- Gate 2 (TDD): checked (tests pass)
- Gate 3 (Docs): checked (decision recorded)
- Gate 4 (BDD): `[x]` with rationale — if Absorb without CLI changes, it is `N/A` (no operator-visible behavior change yet); document this explicitly.
- Gate 5 (Human): unchecked (Stage 4 ceremony)
- Acceptance Criteria REQ-01 through REQ-05: checked

Write the **Closing Argument** synthesizing:

- Decision and one-paragraph defense
- Implementation Summary (what was added, why)
- Key Proof (one command + expected output)

**File modified:** same OBPI brief (Gates, Acceptance Criteria, Closing Argument sections).

### Task 6 — Present OBPI Acceptance Ceremony (Stage 4 Heavy lane)

Heavy lane → human gate. Present the evidence template required by `gz-obpi-pipeline` Stage 4 (Value Narrative, Key Proof, Evidence table, Files created/modified, REQ coverage table) and wait for attestation.

## Verification

```bash
# Source files exist
test -f ../airlineops/src/opsdev/lib/drift_detection.py
test -f src/gzkit/commands/drift.py
test -f src/gzkit/triangle.py

# Brief records one final decision
rg -n 'Absorb|Confirm|Exclude' \
  docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-26-drift-detection-pattern.md

# If Absorb, the new module and tests exist
test -f src/gzkit/temporal_drift.py        # only if Absorb
test -f tests/test_temporal_drift.py       # only if Absorb

# Quality gates (Heavy lane)
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run mkdocs build --strict

# Per-module test execution (only if Absorb)
uv run -m unittest tests.test_temporal_drift -v

# Behave (only if operator-visible change — N/A here)
# uv run -m behave features/core_infrastructure.feature
```

## Notes

- **No CLI surface change in this OBPI.** The absorbed module is standalone. Wiring it into a `gz drift --temporal` flag or a separate `gz validate --drift` mode is a follow-on OBPI to keep this brief small and focused.
- **No changes to the existing `gz drift` (triangle) command** — the new module lives at `src/gzkit/temporal_drift.py`, not inside `commands/drift.py`, precisely to keep the orthogonal concerns separate.
- **Receipt-reader sourcing.** Task 3 will inspect `audit_cmd.py`, `obpi_stages.py`, `ledger_semantics.py`, and `status_obpi.py` (the four files that import `capture_validation_anchor_with_warnings`) to find the canonical receipt-reading helper before duplicating one. If no helper exists, a small `_read_validation_receipts(adr_id)` will be added to `temporal_drift.py` itself rather than to a separate module.
- **Fallback to Confirm.** If Task 1's deeper read reveals that gzkit's anchor data is structured differently enough that adaptation is non-trivial, the decision flips to Confirm with a rationale explaining the structural mismatch. Tasks 3-4 become N/A and Task 5 marks Gate 2 TDD as "N/A — Confirm decision, no code changes". The plan stops at Task 2 in that case.
- **Plan-audit hook coordination.** The plan-audit hook scans `gzkit/.claude/plans/`. This plan currently lives at `~/.claude/plans/humble-fluttering-shore.md` (where Claude Code's plan mode places it). After ExitPlanMode, the plan must be copied or symlinked into `gzkit/.claude/plans/` and `/gz-plan-audit OBPI-0.25.0-26` re-run so the receipt verdict flips from FAIL → PASS before `/gz-obpi-pipeline OBPI-0.25.0-26` resumes.
