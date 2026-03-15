---
name: airlineops-parity-scan
description: Run a repeatable governance parity scan between ../airlineops (canon) and gzkit (extraction).
category: cross-repository
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# SKILL.md

## AirlineOps Parity Scan

Run a repeatable governance parity scan between `../airlineops` (canon) and gzkit (extraction).

## Trigger

- Weekly parity check cadence.
- Before promoting any pool ADR into active implementation.
- Any time a canonical GovZero skill/doc changes in AirlineOps.

## Behavior

Produce a dated parity report with explicit gaps, severity, and required ADR/OBPI follow-up.
Parity is operational, not textual. The scan MUST evaluate behavior/procedure sources across multiple surfaces.

Operational identity rule:

`GovZero = AirlineOps - (AirlineOps product capabilities)`

Treat every AirlineOps process habit/structure/rule as GovZero parity scope unless it is purely product capability behavior.

GovZero mining rule:

- Treat `AGENTS.md`, governance docs, and control-surface directories (`.github/`, `.claude/`, `.codex/`, `.gzkit/`) as first-class GovZero extraction sources.
- Mine process habits from all of them; do not restrict extraction to one docs subtree.

## Prerequisites

- `../airlineops` exists and is readable.
- gzkit repo is initialized with `docs/` and `docs/design/`.
- Use canonical references in `docs/design/lodestar/govzero-doctrine.md`.

## Steps

1. Confirm both repos are present:
   `test -d ../airlineops && test -d .`
2. Resolve canonical root deterministically:
   - explicit override (if provided)
   - sibling path `../airlineops`
   - absolute fallback `/Users/jeff/Documents/Code/airlineops`
   Fail closed if none resolve.
   Record canonical-root evidence in the parity report.
3. Read canonical source declarations:
   `docs/design/lodestar/govzero-doctrine.md`, `docs/design/lodestar/README.md`, `AGENTS.md`.
4. Build a behavior/procedure source matrix from canonical and extraction surfaces:
   - Canonical behavior sources (AirlineOps):
     - `.github/skills/gz-*`
     - `.github/instructions/*.instructions.md`
     - `.claude/**`
     - `.codex/**`
     - `.gzkit/**`
     - `AGENTS.md`, `CLAUDE.md`
     - `docs/governance/GovZero/**/*.md`
     - operator runbook/proof docs where rituals are declared
   - gzkit extraction surfaces:
     - `.github/skills/*`
     - `.claude/**`
     - `.codex/**` (if present)
     - `.gzkit/**`
     - `AGENTS.md`, `CLAUDE.md`
     - `docs/governance/GovZero/**/*.md`
     - `docs/user/commands/*`, `docs/user/concepts/*`, `docs/user/runbook.md`
     - runtime control surfaces (`src/gzkit/cli.py`, ledger events, validation commands)
5. Produce a GovZero mining inventory:
   - list each mined norm/habit
   - cite source file/path
   - map to extracted gzkit surface (or mark missing/divergent)
   - classify confidence and remediation target
6. Apply parity intake rubric to each candidate import:
   - Use `docs/governance/parity-intake-rubric.md`
   - Classify each item as `Import Now`, `Import with Compatibility`, `Defer (Tracked)`, or `Exclude`
   - Record rationale and runtime/proof backing for the classification
7. Compare both artifact parity and procedure parity:
   - artifact parity: presence/path/content
   - procedure parity: orientation, tool use, post-accounting, validation, verification, presentation, human authority boundaries
8. Classify each matrix item as:
   - `Parity`
   - `Partial`
   - `Missing`
   - `Divergent`
9. Execute and record runnable ritual checks from gzkit surfaces:
   - `uv run gz cli audit`
   - `uv run gz check-config-paths`
   - `uv run gz adr audit-check ADR-<target>`
   - `uv run mkdocs build --strict`
10. Write a dated report:
   `docs/proposals/REPORT-airlineops-parity-YYYY-MM-DD.md`
   Use `docs/proposals/REPORT-TEMPLATE-airlineops-parity.md`.
   Also produce mining inventory report:
   `docs/proposals/REPORT-airlineops-govzero-mining-YYYY-MM-DD.md`
   Use `docs/proposals/REPORT-TEMPLATE-airlineops-govzero-mining.md`.
11. For every `Missing`, `Divergent`, or high-impact `Partial` finding:
   - Propose target SemVer minor
   - Identify parent ADR and OBPI linkage
   - Add an explicit next action
12. Summarize risk:
   - What blocks 1.0 readiness
   - What can wait
   - What must be done next cycle
13. Enforce action closure for this scan cycle:
   - For each `Import Now` finding, execute at least one concrete tranche in the
     same cycle (code/docs/settings change) and record file-level evidence.
   - If execution cannot happen in-cycle, open a trackable defect (`gh issue create --label defect`)
     and link it in the report.
   - A scan with findings but no execution artifact or defect artifact is `INCOMPLETE`.

## Examples

### Example 1

**Input**: "Run the weekly AirlineOps parity scan."

**Output**: `docs/proposals/REPORT-airlineops-parity-2026-02-07.md` with matrix, severity, and action list.

## Constraints

- Do not modify anything in `../airlineops`.
- Do not claim parity without path-level evidence.
- Do not claim procedure parity without executable ritual evidence from gzkit runtime/docs surfaces.
- Do not use patch versions for new feature sequencing.
- Keep findings actionable: each gap must map to ADR/OBPI follow-up.
- Do not close a scan cycle with only passive tracking; require execution or a filed defect.

## Related Skills

- gz-adr-create
- gz-adr-audit
