---
name: gz-plan-audit
description: Pre-flight alignment audit — verify ADR intent, OBPI brief scope, and plan are aligned before implementation begins. Use when exiting plan mode, before starting implementation, or to catch scope drift between ADR intent and the active OBPI brief.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-12
compatibility: Works with GovZero-compliant repositories; in gzkit the receipt is written under .claude/plans/, consumed by gz-obpi-pipeline, and enforced by the registered plan-exit hooks tracked by ADR-0.12.0.
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
  version-consistency-rule: "Skill major version tracks GovZero major. Minor increments for governance rule changes. Patch increments for tooling/template improvements."
  govzero_layer: "Layer 1 - Evidence Gathering"
---

# gz-plan-audit (v6.0.0)

## Purpose

Pre-flight alignment audit that catches misalignment before implementation
begins. The operator runs this after plan mode produces a plan, verifying three
artifacts agree:

```text
ADR (intent) <-> OBPI brief (scope) <-> Plan (execution steps)
```

Misalignment between these artifacts is the root cause of wasted implementation
work: building the wrong thing, missing requirements, or solving problems the
ADR did not ask for. This audit catches that drift before a single line of code
is written.

Typical workflow:

1. Operator runs `/gz-plan-audit OBPI-X.Y.Z-NN` and audits ADR <-> OBPI
   alignment. If no plan exists yet, the plan audit is skipped.
2. If gaps are found, update the ADR or OBPI brief before planning.
3. If aligned, plan mode produces a plan in `.claude/plans/`.
4. Operator runs `/gz-plan-audit OBPI-X.Y.Z-NN` again after planning.
5. If the plan aligns, proceed into `gz-obpi-pipeline`.

Current gzkit compatibility rule:

- The `gz-plan-audit` skill is ported and may write
  `.claude/plans/.plan-audit-receipt.json`.
- `gz-obpi-pipeline` already consumes that receipt when it exists.
- The registered Claude hook chain now consumes that receipt mechanically:
  `plan-audit-gate.py` blocks `ExitPlanMode` without a valid receipt and
  `pipeline-router.py` routes PASS receipts into `gz-obpi-pipeline`.

## Invocation

```text
/gz-plan-audit OBPI-X.Y.Z-NN
```

Run before planning for ADR <-> OBPI alignment and again after planning for
Plan <-> OBPI alignment.

## Trust Model

Layer 1 - Evidence Gathering. See
`docs/governance/GovZero/layered-trust.md`.

- Reads: ADR files, OBPI briefs, plan files in `.claude/plans/`, and relevant
  codebase files
- Produces: alignment report with gaps, mismatches, recommendations, and a
  receipt file

## Inputs

| Parameter | Required | Description |
|-----------|----------|-------------|
| `obpi_id` | Yes | OBPI identifier, for example `OBPI-0.12.0-07` |
| `adr_id` | No | Parent ADR identifier; derive from OBPI ID if omitted |
| `plan_path` | No | Path to a plan file in `.claude/plans/`; auto-discover if omitted |

## Outputs

- Alignment report presented to the operator with:
  - ADR <-> OBPI alignment status
  - Plan <-> OBPI alignment status
  - Specific gaps and mismatches with citations
  - Recommendations to update the brief, update the plan, or flag an ADR defect
- Receipt file written to `.claude/plans/.plan-audit-receipt.json`

## Procedure

### Step 1: Read the parent ADR

Locate and read the parent ADR under `docs/design/adr/`. Extract:

- Intent: the problem being solved and the decision made
- Feature Checklist: the full WBS with numbered checklist items
- The specific checklist item this OBPI maps to
- Goals and anti-patterns from the agent context frame
- Lane: Lite or Heavy
- Integration points: other OBPIs, shared modules, config entries

### Step 2: Read the OBPI brief

Locate and read the brief from either of these layouts:

- `docs/design/adr/**/obpis/OBPI-{id}-*.md`
- `docs/design/adr/**/briefs/OBPI-{id}-*.md`

Extract:

- Objective
- Requirements
- Allowed and denied paths
- Acceptance criteria
- Verification commands

### Step 3: Audit ADR <-> OBPI alignment

Compare the brief against its parent ADR checklist item:

| Check | Question |
|-------|----------|
| Objective match | Does the brief objective match the ADR checklist item's intent? |
| Scope match | Are the brief allowed paths consistent with the ADR integration points? |
| Requirements coverage | Do the brief requirements cover what the ADR checklist item implies? |
| Lane consistency | Does the brief lane match the parent ADR lane? |
| Attestation rule | Does the brief inherit the parent ADR attestation requirement correctly? |
| No scope creep | Does the brief avoid adding requirements not present in the ADR? |
| No scope gap | Does the brief avoid omitting requirements present in the ADR? |

Record each check as Aligned, Drifted, or Missing.

### Step 4: Find and read the plan file

Auto-discover the plan file from `.claude/plans/`:

1. Search `.claude/plans/*.md` for files referencing this OBPI ID.
2. If multiple matches exist, use the newest by modification time.
3. If `plan_path` was provided explicitly, use that instead.
4. If no plan exists, report `No plan found` and skip Step 5.

Extract:

- Context
- Files
- Steps
- Verification
- Notes

### Step 5: Audit Plan <-> OBPI alignment

Compare the plan against the brief:

| Check | Question |
|-------|----------|
| OBPI reference | Does the plan reference the correct OBPI brief? |
| Requirements coverage | Does every brief requirement appear as a plan step? |
| Allowed paths | Does the plan only touch files in the brief allowlist? |
| Denied paths | Does the plan avoid files in the brief denylist? |
| Verification | Does the plan include the brief verification commands? |
| No gold-plating | Does the plan avoid extra work not required by the brief? |
| Feasibility | Based on current codebase state, are the plan steps achievable? |

### Step 6: Present the alignment report

Use this structure:

```text
## ADR <-> OBPI Alignment

| Check | Status | Detail |
|-------|--------|--------|
| Objective match | Aligned / Drifted / Missing | [specifics] |
| Scope match | ... | ... |

## Plan <-> OBPI Alignment

| Check | Status | Detail |
|-------|--------|--------|
| Requirements coverage | Aligned / Drifted / Missing | [specifics] |
| Allowed paths | ... | ... |

## Gaps Found

1. [specific gap with file:line citation]

## Recommendations

1. [specific action]

## Verdict

PASS - All checks aligned, safe to proceed with implementation.
FAIL - N gaps found. Fix alignment before implementing.
```

Write the receipt file on completion:

```json
{
  "obpi_id": "OBPI-X.Y.Z-NN",
  "timestamp": "2026-03-12T12:00:00Z",
  "verdict": "PASS",
  "plan_file": "shimmering-beaming-sonnet.md",
  "gaps_found": 0
}
```

Receipt contract:

- `verdict` must be `PASS` or `FAIL`
- `plan_file` should name the plan that was audited
- receipt freshness is fail-closed: the receipt must be newer than the plan file

Stop cleanly. The audit produces a report and receipt. Fixing alignment is a
separate action.

## Enforcement

Active enforcement contract for gzkit:

- Registered hook: `.claude/hooks/plan-audit-gate.py`
- Registered router consumer: `.claude/hooks/pipeline-router.py`
- Active registration surface: `.claude/settings.json`
- Current consumer already present: `.gzkit/skills/gz-obpi-pipeline/SKILL.md`

Current state:

- The operator still invokes `/gz-plan-audit` manually.
- `gz-obpi-pipeline` consumes `.claude/plans/.plan-audit-receipt.json` when it
  exists.
- Missing or stale receipts are now a mechanical `ExitPlanMode` block through
  `plan-audit-gate.py`.
- PASS receipts now trigger the registered `pipeline-router.py` surface after
  plan exit, directing operators into `gz-obpi-pipeline`.

Future gate logic to preserve:

1. Find the most recently modified plan in `.claude/plans/`
2. Extract OBPI IDs from the plan content
3. If no OBPI reference exists, allow
4. Check `.claude/plans/.plan-audit-receipt.json`:
   - receipt must exist
   - receipt OBPI must match plan OBPI
   - receipt must be newer than the plan file
   - receipt must contain a `PASS` or `FAIL` verdict
5. Invalid or missing receipt blocks plan exit in the registered hook chain

## Failure Modes

| Failure | Cause | Resolution |
|---------|-------|------------|
| ADR not found | ADR ID incorrect or structure mismatch | Verify ADR ID; search `docs/design/adr/` |
| Brief not found | OBPI ID typo or brief missing | Check `obpis/` and `briefs/` layouts |
| Brief lacks required sections | Incomplete or non-standard brief | Report as an alignment gap |
| No plan file found | Plan mode not run yet or no matching plan exists | Audit ADR <-> OBPI only and skip plan checks |
| Multiple plan files match | Several plans reference the same OBPI | Use the newest plan and note ambiguity |
| ADR checklist item ambiguous | Checklist item text is vague | Flag an ADR defect and recommend clarification |

## Acceptance Rules

- Audit report covers both ADR <-> OBPI and Plan <-> OBPI alignment when a plan
  exists
- Each check is recorded as Aligned, Drifted, or Missing with specifics
- Gaps include citations where applicable
- Report ends with a clear PASS or FAIL verdict
- Recommendations are actionable
- The agent stops cleanly after presenting the report

## Related

- `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
- `.gzkit/skills/gz-obpi-audit/SKILL.md`
- `.gzkit/skills/gz-session-handoff/SKILL.md`
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`
