# gz personas drift

Report persona trait adherence from behavioral proxies.

---

## Usage

```bash
gz personas drift [--persona NAME] [--json]
```

---

## Description

Scans local governance artifacts (ledger events, OBPI audit logs) for
evidence of trait-aligned behavior. Reports per-trait pass/fail for each
persona using behavioral proxies only -- no activation-space measurement,
no network access.

Each persona trait is evaluated against a proxy registry that maps trait
keywords to deterministic artifact checks. Traits without a registered
proxy receive `no_evidence` status (honest: unmeasurable traits are not
claimed as passing or failing).

---

## Options

| Flag | Description |
|------|-------------|
| `--persona NAME` | Evaluate only the named persona (default: all) |
| `--json` | Output valid JSON PersonaDriftReport to stdout |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No drift detected |
| 3 | Policy breach -- drift detected in one or more trait checks |

---

## Proxy Categories

| Proxy | Evidence Checked | Traits Served |
|-------|-----------------|---------------|
| governance_activity | gate_checked, attested events | governance-aware, governance-fidelity |
| test_evidence | OBPI audit test_count, tests_passed | test-first, thorough |
| evidence_quality | criteria_evaluated with PASS | evidence-driven, precision |
| completion_quality | brief_status_after = Completed | complete-units, atomic-edits |
| plan_discipline | adr_created before gate_checked | methodical, plan-then-write |

---

## Examples

```bash
# Human-readable drift report for all personas
uv run gz personas drift

# JSON output for machine consumption
uv run gz personas drift --json

# Check a single persona
uv run gz personas drift --persona implementer

# Check exit code
uv run gz personas drift --persona implementer; echo $?
```
