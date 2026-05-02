# AUDIT — ADR-0.0.24-attestation-receipt-binding

**Date:** 2026-05-02
**Status:** PAUSED — blocked on GHI #385

## Outcome

Audit cannot proceed to `validated` receipt emission. `gz adr audit-check
ADR-0.0.24` returns exit=3 with 21 blocking covers-backfill findings against
OBPI-0.0.24-01 and OBPI-0.0.24-02 test files. The skill's "Audit fails → no
receipt" rule applies; no `gz adr emit-receipt --event validated` issued.

## Diagnosis

Per `.claude/skills/gz-adr-audit/SKILL.md` § Audit Procedure Step 2, each
flagged finding was inspected to distinguish:

- **(a) Genuinely missing coverage** — REQ has no test asserting its semantics
- **(b) Coverage-shape drift** — test exists but assertion drifted from REQ
- **(c) Validator false-positive** — neither (a) nor (b)

Reading the flagged tests at:

- `tests/governance/test_attestation_receipt_validator.py:83–220`
- `tests/commands/test_obpi_complete.py:197–542`
- `tests/commands/test_adr_emit_receipt.py:175,203`

confirms category **(c)** for every flagged decorator:

- Each `@covers(REQ-...)` decorates exactly one REQ
- Each test asserts distinct REQ semantics (different exit codes, different
  `entries[0].status` values: `resolved` / `missing` / `status_mismatch` /
  `claim_mismatch` / `malformed_id`; different lane×kind axes)
- Module docstring explicitly cites `.claude/rules/tests.md` § "Tests assert
  semantics, not strings"

## Root cause

The ADR-0.0.23-05 covers-backfill heuristic measures `(commits, days)` gap
between the introducing commit and the closing receipt. When both are the
same `gz git-sync` ceremony commit (the canonical workflow for OBPI receipt
emission), gap=0 by construction even for properly-disciplined TDD work.

The heuristic was authored with a per-OBPI / per-day commit cadence in mind;
the actual repo workflow squashes per-OBPI work into a single
`chore: ... (gz git-sync)` ceremony commit. Every TDD-disciplined heavy-lane
or foundation-kind ADR completed via `gz git-sync` will trip the heuristic.

## Coverage status (advisory, non-blocking)

```
Coverage: 14/19 REQs covered (73.7%)
  OBPI-0.0.24-01: 6/6 (100.0%)
  OBPI-0.0.24-02: 5/5 (100.0%)
  OBPI-0.0.24-03: 0/5 (0.0%)   # doc-update OBPI; advisory only
  OBPI-0.0.24-04: 3/3 (100.0%)
```

OBPI-0.0.24-03 is the documentation-update OBPI; its REQs legitimately have
no `@covers` test (doc REQs are validated by `mkdocs build --strict` and
`gz validate --documents`, not unit tests). The 5 advisory uncovered REQs do
NOT block the audit.

## Routing decision

Per `AGENTS.md § Defect-fix routing thresholds`, the heuristic fix:

- Crosses ADR boundaries (touches ADR-0.0.23-05 surface)
- Affects core governance / heavy-lane validator runtime
- Requires schema or behavior change to `audit_thresholds.json` /
  `adr_audit_covers_backfill.py`

Direct-fix thresholds exceeded → routed to GHI per
AGENTS.md Behavior Rule 9 (operator-attested route A).

## Tracking

- **GHI #385** — covers-backfill heuristic false-positives on `gz git-sync`
  ceremony commits — https://github.com/tvproductions/gzkit/issues/385

## Resume condition

Re-run this audit when GHI #385 is closed. At that point:

1. `uv run gz adr audit-check ADR-0.0.24` should return exit=0
2. Proceed with skill Step 3 (Demonstrate Value), Steps 4–9

## Proofs

- `proofs/audit-check.txt` — captured `gz adr audit-check ADR-0.0.24` output
  with exit code, showing all 21 blocking findings
