---
mode: CREATE
adr_id: ADR-0.19.0-closeout-audit-processes
branch: main
timestamp: "2026-03-21T22:00:00Z"
agent: claude-code
obpi_id:
session_id:
continues_from:
---

## Current State Summary

Session focused on quality enforcement infrastructure, not direct OBPI implementation. ADR-0.19.0 remains Pending with 0/9 OBPIs complete. All 9 OBPI briefs are raw template scaffolding (NO GO, 2.15/4.0). GHI #27 filed and fixed for the validation gap that allowed this.

Three major deliverables completed this session:

1. **Version sync in closeout** — `gz closeout` now bumps pyproject.toml, `__init__.py`, and README badge to match the ADR version when it exceeds the current project version. Version bumped from 0.12.0 to 0.18.0 across all three files.

2. **Scaffold detection and fail-closed promotion** — `ObpiValidator` now detects template scaffold markers on Draft/Proposed OBPIs (not just Completed). `gz adr promote` exits 1 when scaffold is detected, `--force` required to override.

3. **Deterministic ADR/OBPI eval engine** — New `gz adr eval` CLI command with 8-dimension ADR scoring, 5-dimension OBPI scoring, GO/CONDITIONAL_GO/NO_GO verdicts, scorecard generation, and ledger events. Wired into `gz adr promote` as a blocking gate (exit 3 on non-GO). Red-team prompt composition and result parsing built for subagent dispatch.

## Important Context

- ADR-0.19.0's lane is **lite** in the ledger despite the ADR file saying heavy and OBPI briefs saying Heavy. Lane contradiction must be resolved.
- The eval scorer uses `section_body()` for heading matching — some heading variants (e.g., `## Quality Gates (Heavy)`) needed explicit handling. Future heading variants may need similar treatment.
- The eval gate in `gz adr promote` runs AFTER files are written to disk (ADR/OBPIs must exist for eval to read them) but BEFORE the command reports success. `--force` overrides scaffold check but does NOT override the eval gate.
- Validated ADRs (like 0.18.0) score CONDITIONAL_GO (2.65) because they were authored before the eval existed. The user does not want to modify completed work — the scorer should be calibrated over time but historical ADRs stay as-is.

## Decisions Made

- **Decision:** Two-layer eval architecture (deterministic code + LLM red-team)
  **Rationale:** Deterministic layer catches ~70% of quality issues without LLM cost. Red-team layer adds judgment for subjective dimensions.
  **Alternatives rejected:** Pure LLM scoring (non-deterministic, expensive), pure regex scoring (too rigid for nuanced dimensions)

- **Decision:** `gz plan` (ADR creation) does NOT call eval — only `gz adr promote` does
  **Rationale:** Newly created ADRs are Draft with expected scaffold. Eval gates the Draft-to-Proposed transition at promote time.

- **Decision:** REQ fulfillment quality is agent judgment, not system-enforced
  **Rationale:** User explicitly stated requirements during OBPI implementation are "implementation judgment calls for the executing LLM"

- **Decision:** `--force` does NOT override eval gate, only scaffold check
  **Rationale:** Eval is a stronger quality gate. Scaffold bypass is for tooling compatibility; eval bypass would undermine the entire quality system.

## Immediate Next Steps

1. Author all 9 OBPI briefs for ADR-0.19.0 with real allowed paths, fail-closed requirements, concrete acceptance criteria, and verification commands. Start with OBPI-0.19.0-01 (closeout pipeline) since version-sync work is already done.
2. Resolve the lane contradiction — align ledger, ADR file, and OBPI briefs to a single source of truth for ADR-0.19.0.
3. Add Alternatives Considered and explicit Non-Goals sections to ADR-0.19.0 to improve the ADR-level dimension scores.
4. Run `gz adr eval ADR-0.19.0` iteratively after each authoring pass to drive the score toward GO (>=3.0).
5. Once eval passes GO, begin OBPI implementation via the pipeline.

## Pending Work / Open Loops

- ADR-0.19.0 OBPI briefs 01-09 all need authoring (template scaffold, NO GO)
- The eval scorer may need calibration over time as more ADRs are evaluated — some heuristics (word count thresholds, keyword lists) are conservative
- Red-team subagent dispatch is built (prompt composition + parsing) but not yet exercised in a real eval run
- ADRs 0.20.0 through 0.23.0 may also have scaffold OBPIs — should be audited
- GHI #27 is filed but could benefit from a follow-up to audit all existing ADR packages

## Verification Checklist

- [x] `uv run -m unittest -q` — 1018 tests pass
- [x] `uv run ruff check .` — only pre-existing UP038
- [x] `gz adr eval ADR-0.19.0` — NO GO (2.15), exit 3
- [x] `gz adr eval ADR-0.18.0` — CONDITIONAL GO (2.65), exit 3
- [x] `git push` — all changes synced to origin/main

## Evidence / Artifacts

- `src/gzkit/adr_eval.py` — Deterministic eval engine (8 ADR + 5 OBPI dimension scorers, verdict computation, scorecard renderer)
- `src/gzkit/adr_eval_redteam.py` — Red-team prompt composition and result parsing
- `src/gzkit/hooks/obpi.py` — Scaffold detection added to ObpiValidator, section_body made public
- `src/gzkit/commands/common.py` — Version sync helpers (check_version_sync, sync_project_version)
- `src/gzkit/cli.py` — adr_eval_cmd, eval gate in adr_promote_cmd, version sync in closeout_cmd
- `src/gzkit/ledger.py` — adr_eval_completed_event factory
- `tests/test_adr_eval.py` — 25 tests for eval engine
- `tests/test_adr_eval_redteam.py` — 11 tests for red-team layer
- `tests/test_version_sync.py` — 16 tests for version sync
- `tests/test_obpi_validator.py` — 4 new scaffold detection tests
- `tests/commands/test_adr_promote.py` — 1 new scaffold-blocks-promotion test
- `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/EVALUATION_SCORECARD.md` — NO GO scorecard

## Environment State

- Python 3.13+, Windows 11, uv package manager
- 1018 tests passing, ~22s runtime
- Project version: 0.18.0 (bumped from 0.12.0 this session)
