---
id: OBPI-0.19.0-06-audit-templates-and-evidence-aggregation-from-ledger
parent: ADR-0.19.0-closeout-audit-processes
item: 6
lane: Lite
status: Draft
---

# OBPI-0.19.0-06: Audit Templates and Evidence Aggregation from Ledger

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- **Checklist Item:** #6 - "OBPI-0.19.0-06: Audit templates and evidence aggregation from ledger"

**Status:** Draft

## Objective

Replace the inline string assembly in `audit_cmd()` with a template-based audit report system that aggregates governance evidence from the ledger — OBPI completion receipts (`obpi_receipt_emitted` events), gate check events (`gate_checked`), attestation events (`attested`), and closeout events (`closeout_initiated`) — into a structured, reproducible AUDIT.md and AUDIT_PLAN.md, following the existing template pattern established in `src/gzkit/templates/` (e.g., `closeout.md`).

## Lane

**Lite** - Inherited from parent ADR-0.19.0-closeout-audit-processes (lite per ledger `adr_created` event).

> This OBPI refactors internal report generation from inline strings to templates and adds ledger evidence aggregation logic. It does not change CLI flags, exit codes, subcommand surface, or machine-readable JSON output schema. Templates are internal implementation artifacts, not external contracts.

## Allowed Paths

- `src/gzkit/cli.py` - `audit_cmd()` function (line ~2634): replace inline AUDIT.md/AUDIT_PLAN.md string assembly with template rendering calls; extract evidence aggregation into a helper function
- `src/gzkit/commands/common.py` - Add `aggregate_audit_evidence()` helper that queries ledger for OBPI receipts, gate checks, attestation, and closeout events for a given ADR ID and returns a structured dict for template rendering
- `src/gzkit/templates/` - Add `audit.md` and `audit_plan.md` template files following the pattern of `closeout.md` (string `.format()` with named placeholders)
- `tests/test_audit_pipeline.py` - Tests for template rendering, evidence aggregation from ledger, and end-to-end audit report content

## Denied Paths

- `src/gzkit/ledger.py` - No new event types or model changes (this OBPI reads existing events, does not create new ones)
- `src/gzkit/templates/__init__.py` - Template loader unchanged unless new templates need registration
- `docs/user/commands/audit.md` - No CLI contract change
- New dependencies (no Jinja2 or external template engines; use Python string `.format()` like `closeout.md`)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `src/gzkit/templates/audit.md` MUST exist as a template file using Python `.format()` placeholders (not Jinja2), consistent with `closeout.md`.
2. REQUIREMENT: `src/gzkit/templates/audit_plan.md` MUST exist as a template file using Python `.format()` placeholders.
3. REQUIREMENT: The evidence aggregation helper MUST query the ledger for these event types scoped to the target ADR: `obpi_receipt_emitted` (child OBPIs), `gate_checked`, `attested`, and `closeout_initiated`.
4. REQUIREMENT: The aggregated evidence dict MUST include: `obpi_completions` (list of OBPI IDs with their latest receipt event and completion status), `gate_results` (list of gate number/status/command tuples), `attestation` (attestor/status/ts or null), and `closeout` (by/mode/ts or null).
5. REQUIREMENT: The rendered AUDIT.md MUST contain sections for: header (ADR ID, date), attestation record, gate results from ledger, OBPI completion summary, verification command results, and evidence file links.
6. NEVER: The template system MUST NOT introduce Jinja2 or any external template dependency; use stdlib string formatting only.
7. NEVER: Template rendering MUST NOT change the exit code or `--json` output structure of `audit_cmd()`.
8. ALWAYS: The `aggregate_audit_evidence()` function MUST be deterministic given the same ledger state — no random ordering, timestamps are preserved from events.

> STOP-on-BLOCKERS: if `src/gzkit/templates/closeout.md` does not exist (template pattern not established) or `Ledger.query()` is unavailable, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- [ ] Related OBPIs: OBPI-0.19.0-04 (attestation/gate/evidence in audit), OBPI-0.19.0-05 (audit_generated event)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/templates/closeout.md` exists (template pattern exemplar)
- [ ] `src/gzkit/templates/__init__.py` exists (template module)
- [ ] `src/gzkit/ledger.py` contains `Ledger.query(event_type=..., artifact_id=...)` (line ~1014)
- [ ] `src/gzkit/ledger.py` contains `Ledger.get_artifact_graph()` (line ~1277) for OBPI child enumeration

**Existing Code (understand current state):**

- [ ] `src/gzkit/templates/closeout.md`: string template with `{adr_id}`, `{adr_path}`, `{heavy_gates}`, `{heavy_evidence}` placeholders
- [ ] `src/gzkit/cli.py` lines 2719-2754: inline AUDIT_PLAN.md and AUDIT.md assembly using list-of-strings join
- [ ] `src/gzkit/commands/common.py` lines 1-60: existing common utilities and imports
- [ ] `src/gzkit/ledger.py` lines 1120-1148: `_artifact_creation_entry()` shows graph fields for OBPIs (children, receipt state)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification: templates exist
uv run python -c "
from pathlib import Path
assert Path('src/gzkit/templates/audit.md').exists(), 'audit.md template missing'
assert Path('src/gzkit/templates/audit_plan.md').exists(), 'audit_plan.md template missing'
print('PASS: audit templates exist')
"

# Specific verification: evidence aggregation function exists
uv run python -c "
from gzkit.commands.common import aggregate_audit_evidence
import inspect
sig = inspect.signature(aggregate_audit_evidence)
print(f'aggregate_audit_evidence signature: {sig}')
print('PASS: evidence aggregation function importable')
"

# Run specific tests
uv run -m unittest tests.test_audit_pipeline -v
```

## Acceptance Criteria

- [ ] REQ-0.19.0-06-01: Given `src/gzkit/templates/`, when the templates directory is listed, then `audit.md` and `audit_plan.md` exist as `.format()`-style templates with named placeholders for `adr_id`, `adr_path`, `attestation_section`, `gate_results_section`, `obpi_summary_section`, `verification_results_section`, and `evidence_links_section`.
- [ ] REQ-0.19.0-06-02: Given a ledger containing `obpi_receipt_emitted`, `gate_checked`, `attested`, and `closeout_initiated` events for ADR-X.Y.Z, when `aggregate_audit_evidence(ledger, adr_id, graph)` is called, then it returns a dict with `obpi_completions`, `gate_results`, `attestation`, and `closeout` keys populated from the ledger events.
- [ ] REQ-0.19.0-06-03: Given `audit_cmd()` after refactoring, when `gz audit ADR-X.Y.Z` runs successfully, then AUDIT.md is rendered from the `audit.md` template with evidence aggregated from the ledger, not from inline string assembly.
- [ ] REQ-0.19.0-06-04: Given an ADR with three completed OBPIs in the ledger, when the audit report is generated, then the OBPI completion summary section lists all three OBPIs with their completion status and receipt event type.
- [ ] REQ-0.19.0-06-05: Given the same ledger state, when `aggregate_audit_evidence()` is called twice, then both calls return identical dicts (deterministic ordering).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

## Value Narrative

Before this OBPI, audit reports were assembled from inline string concatenation in `audit_cmd()`, producing minimal content that listed only verification command pass/fail results. The reports contained no governance evidence from the ledger — no OBPI completion status, no historical gate results, no attestation context. Operators who needed a comprehensive audit trail had to manually query the ledger and correlate events. After this OBPI, audit reports are rendered from maintainable templates that aggregate all governance evidence from the ledger into structured sections, making AUDIT.md a complete, reproducible audit artifact that captures the full lifecycle history of the ADR.

## Key Proof

```text
# Expected audit.md template structure (after implementation):
$ cat src/gzkit/templates/audit.md
# Audit: {adr_id}

- ADR: `{adr_path}`
- Generated: {generated_ts}

## Attestation Record
{attestation_section}

## Gate Results (from ledger)
{gate_results_section}

## OBPI Completion Summary
{obpi_summary_section}

## Verification Results
{verification_results_section}

## Evidence Links
{evidence_links_section}

# Expected aggregate_audit_evidence output:
{
  "obpi_completions": [
    {"obpi_id": "OBPI-0.19.0-01-...", "receipt_event": "completed", "ledger_completed": true}
  ],
  "gate_results": [
    {"gate": 2, "status": "pass", "command": "uv run gz test", "returncode": 0}
  ],
  "attestation": {"by": "human:Jeff", "status": "completed", "ts": "2026-03-21T..."},
  "closeout": {"by": "agent", "mode": "standard", "ts": "2026-03-21T..."}
}
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a` (Lite lane; parent ADR lane is lite per ledger)
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
