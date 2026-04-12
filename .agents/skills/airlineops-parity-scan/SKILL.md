---
name: airlineops-parity-scan
description: Run a repeatable governance parity scan between ../airlineops (canon) and gzkit (extraction).
category: cross-repository
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-12
metadata:
  skill-version: "1.1.0"
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

## Common Rationalizations

These thoughts mean STOP — you are about to ship a passive-tracking parity report:

| Thought | Reality |
|---------|---------|
| "The matrix is filled in — that closes the cycle" | A scan with `Missing` or `Divergent` findings and no execution artifact (or filed defect) is `INCOMPLETE` by definition. Step 13 is mandatory. |
| "I'll execute the Import Now items next cycle" | Action closure is per-cycle. Deferring is exactly the perpetual-catch-up pattern the constraint was written to prevent. Ship at least one tranche or file a defect now. |
| "Textual diff is good enough for parity" | Parity is operational, not textual. You must mine procedural sources across all surfaces (`.github/`, `.claude/`, `.codex/`, `.gzkit/`, `AGENTS.md`) and exercise rituals from the gzkit runtime. |
| "I don't need to read AirlineOps docs — gzkit is the canonical source now" | The scan is `gzkit ← airlineops`. Skipping the canonical mining inventory makes the report a self-portrait, not a parity scan. |
| "Most items are Parity, the report is mostly done" | The report is the easy part. The failing parity items are the work. Don't conflate report completeness with cycle completeness. |
| "I can write the report without running the runnable ritual checks" | Step 9 ritual checks (`gz cli audit`, `gz check-config-paths`, `gz adr audit-check`, `mkdocs --strict`) provide the procedure-parity evidence. Without them you're claiming parity by inspection. |
| "Findings only need passive `defer (tracked)` classification" | The constraint explicitly prohibits closing a cycle with only passive tracking. Each finding needs an execution path or a tracked defect — there is no third option. |

## Red Flags

- Report contains `Missing` or `Divergent` findings but no commits, diffs, or filed GHIs in the same cycle
- Mining inventory cites only one or two surface roots instead of the full set
- Procedure parity claimed without runtime ritual evidence
- The matrix lists items as `Partial` without specifying what's missing
- Parity classified `Defer (Tracked)` for more than half the findings (perpetual-catch-up signal)
- Report omits canonical-root resolution evidence (Step 2)
- Cycle closed without producing both the parity report AND the mining inventory report

## Related Skills

- gz-adr-create
- gz-adr-audit
