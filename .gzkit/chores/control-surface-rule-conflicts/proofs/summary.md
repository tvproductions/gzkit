# Conflict Matrix Summary — Pass A

> Chore: `control-surface-rule-conflicts` (Lite lane, audit-only)
> Date: 2026-05-11
> Inputs: `rule-inventory.md`, `conflict-matrix.md`

## Counts

| Severity | Definition | Rows |
|----------|-----------|------|
| `blocking` | Agent hits this monthly or more often; live mid-work surface | 1 |
| `episodic` | Hit during a specific ADR or change-shape class | 5 |
| `theoretical` | Pair could disagree on a misread, but the canonical reading reconciles | 5 |

**Total disagreement rows:** 11
**Pairs surveyed:** 231 (22 files × 21 / 2)
**Conflict density:** 4.8% of pairs produced a substantive disagreement row

## Top 5 (priority-ordered for follow-up)

Ordered by `severity` first, then by surface-blast-radius (how many agent moments the misread surfaces in).

1. **Row 2 — PD 4 "Scope expansion" vs Defect-fix routing "Crosses brief boundaries"** (`blocking`)
   The only blocking row. Surfaces every time an agent finds adjacent rot mid-OBPI. Fix is a one-line qualifier on PD 4; sized for a direct-fix GHI per AGENTS.md § Defect-fix routing.

2. **Row 7 — gate5-runbook-code-covenant "docs+runbook in same patch" vs Lane Rules "lite: Gates 1, 2 required"** (`episodic`)
   Fires whenever a Lite-lane fix touches a documented surface. Fix is a one-line amendment to AGENTS.md § Lane Rules; bounded direct-fix.

3. **Row 11 — pythonic.md "50/600/300 absolutes" vs complexity-thresholds.md "one canonical threshold table"** (`episodic`)
   Drifted authority. The 50/600/300 numbers were authored before the threshold table existed. Resolution touches a foundation-doctrine file (`pythonic.md`) — sized at the edge of direct-fix; route per `gz log --grep='^fix(pythonic'`.

4. **Row 10 — Behavior Rule Never #1 "Bypass Gate 5" vs Lane × Kind × Sensitivity matrix** (`episodic`)
   Surfaces on every Lite-lane feature OBPI close. Behavior Rule is over-broad relative to the matrix; one-line scope clause fixes it.

5. **Row 8 — complexity-thresholds.md "amendments require ADR ceremony" vs skill-surface-sync.md "bump version on every edit"** (`episodic`)
   Surfaces on any editorial edit to `complexity-thresholds.md`. One-sentence scope clarification distinguishing the JSON data file from this narrative file.

## Prioritized follow-up list (ready for ghi-author / direct-fix)

Each entry sized for either a direct-fix GHI (≤10 lines, single named surface, ≥3 precedent `fix(` commits) or a mechanical-promotion GHI per AGENTS.md § Defect-fix routing.

| Order | Route | Target file | Edit summary | Pairs resolved | Acceptance check |
|-------|-------|-------------|--------------|----------------|------------------|
| 1 | direct-fix | `AGENTS.md` § PRIME DIRECTIVE 4 | Append qualifier: *"within the active brief's `Allowed Paths`"* | Row 2 | new prose; no validator change |
| 2 | direct-fix | `AGENTS.md` § Lane Rules | Append Gate 3 trigger for `manpages/**` or `runbook*.md` touches | Row 7 | new prose; downstream `gz validate --documents` already enforces |
| 3 | direct-fix | `AGENTS.md` § Behavior Rules § Never #1 | Reword to "when the Lane × Kind × Sensitivity matrix requires it" | Row 10 | existing `_requires_human_obpi_attestation` predicate is unchanged |
| 4 | direct-fix | `complexity-thresholds.md` § Operator-amendable mapping protocol | Add scope sentence distinguishing data file from narrative | Row 8 | no validator change; `gz validate --complexity-thresholds` already scopes the JSON |
| 5 | direct-fix | `pythonic.md` § Size Limits & Refactoring | Demote 50/600/300 to authoring-guidance; cite `complexity-thresholds.md` | Row 11 | no validator change; threshold-table validator already canonical |
| 6 | mech-promotion | Skill JSON Schema | Restrict `Output Contract` enum to human-readable forms | Row 6 | schema enforcement; new fail-closed validator path |
| 7 | direct-fix | `tool-skill-runbook-alignment.md` § When to apply | Mirror the Output-form fixture carve-out pointer | Row 1 | no validator change; pointer-only |
| 8 | direct-fix | `.claude/rules/governance-core.md` | Verify scope clause mirrored from canonical (sync drift check) | Row 3 | regenerate via `gz agent sync control-surfaces` |
| 9 | direct-fix | `models.md` | Cite AGENTS.md § STDLIB-First named-departure clause explicitly | Row 4 | no validator change; cross-reference only |
| 10 | direct-fix | `tests.md` § Two runners | Add chore-lane vs `gz check` scope sentence | Row 5 | no validator change |
| 11 | direct-fix | `CLAUDE.md` § Opus 4.7 tuning | Add cross-reference to `model-selection.md` § Routing matrix | Row 9 | no validator change |

## What this audit does not produce

Per CHORE.md § Overview, Pass A is **audit-only**. No rule body, skill, or source file is modified by this run. The follow-up table above is operator-fueled work routed individually through `ghi-author` or direct-fix; this chore does not author those edits.

## Stability commitments

- The matrix has 11 rows. A future agent re-running this audit should expect the row count to fluctuate by <=±2 absent a doctrinal shift; any larger swing is itself a finding worth surfacing.
- Rows classified `theoretical` are the most likely to be re-misread by future agents; the proposed cross-reference edits exist precisely to lower the false-positive surface.

## Audit posture

- **Lane:** Lite — no file outside `.gzkit/chores/control-surface-rule-conflicts/proofs/` was edited.
- **Scope discipline:** the matrix admits only pair-rows with a concrete worked example. "These could maybe conflict" candidates were excluded (see `rule-inventory.md` § Method).
- **Evidence resolution:** each row carries either a GHI number within the plausible-range floor or a SHA verifiable via `git log -1`. The chore acceptance gate (`check_evidence.py --offline`) is the mechanical witness.
- **Coverage:** the 22-file in-scope set was walked pairwise; pairings against the generated subtree readme (`.gzkit/rules/AGENTS.md`) were folded into pairings against the originals it re-exports.
