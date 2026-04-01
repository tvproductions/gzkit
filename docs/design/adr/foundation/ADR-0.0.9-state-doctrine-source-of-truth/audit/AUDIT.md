# AUDIT (Gate-5) — ADR-0.0.9

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.9 |
| ADR Title | State Doctrine and Source-of-Truth Hierarchy |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth |
| Audit Date | 2026-03-31 |
| Auditor(s) | jeff |

## Feature Demonstration (Step 3 — MANDATORY)

**What does this ADR deliver?**

- Ledger-first state reads: all `gz` status commands derive state from L2 ledger events, not L3 frontmatter
- Force-reconciliation via `gz state --repair` to fix frontmatter drift from ledger truth
- Three-layer model (L1 canon, L2 events, L3 derived) with explicit authority rules
- Lifecycle auto-fix at closeout/attest/reconcile moments
- Layer 3 gate independence: no derived artifact can block a gate check

### Capability 1: Ledger-first state query

```bash
$ uv run gz state --json
{
  "PRD-GZKIT-1.0.0": {
    "type": "prd",
    "created": "2026-01-22T10:29:54.384608+00:00",
    "parent": null,
    "children": ["ADR-0.1.0-enforced-governance-foundation", ...],
    ...
  },
  "ADR-0.0.9-state-doctrine-source-of-truth": {
    "type": "adr",
    "obpi_completion": "6/6",
    "lifecycle_status": "Validated",
    ...
  }
}
```

**Why it matters:** Every `gz` command that asks "is this done?" gets the answer from ledger events, not from YAML frontmatter that could silently drift. This prevents unproven work from passing gates.

### Capability 2: Force-reconciliation with `gz state --repair`

```bash
$ uv run gz state --repair
                              State Repair Results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ OBPI          ┃ Old Status ┃ New Status ┃ File                               ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ OBPI-0.1.0-01 │ Draft      │ Completed  │ docs/design/adr/ADR-0.1.0/obpis/O… │
└───────────────┴────────────┴────────────┴────────────────────────────────────┘

Repaired 1 frontmatter status field(s).
```

**Why it matters:** Real drift was caught during this audit — OBPI-0.1.0-01 frontmatter said "Draft" but the ledger recorded it as "Completed". The repair command corrected it without manual editing. This is the doctrine in action: frontmatter is a convenience mirror, the ledger is truth.

### Capability 3: CLI discoverability

```bash
$ uv run gz state --help
usage: gz state [-h] [--json] [--blocked] [--ready] [--repair] ...

Query artifact graph, blockers, and readiness from ledger.

options:
  --json         Output as JSON
  --blocked      Show only blocked artifacts
  --ready        Show only ready-to-proceed artifacts
  --repair       Force-reconcile all frontmatter status from ledger-derived state
```

**Why it matters:** The `--repair` flag is discoverable via `--help` with a clear description. Operators can self-serve recovery without reading governance docs.

### Value Summary

Before ADR-0.0.9, there was no locked doctrine for which storage layer was authoritative. Commands could independently decide to read frontmatter or ledger, creating silent divergence. Now every status read goes through the ledger, frontmatter drift is auto-detected and repairable, and no Layer 3 artifact can block gates.

---

## Execution Log

| Check | Command / Method | Result | Notes |
|-------|------------------|--------|-------|
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.9` | ✓ | 6/6 OBPIs completed with evidence |
| Ledger-first state reads | `uv run gz state --json` | ✓ | Full artifact graph derived from ledger |
| State repair command | `uv run gz state --repair` | ✓ | Caught real drift in OBPI-0.1.0-01 |
| CLI discoverability | `uv run gz state --help` | ✓ | `--repair` flag documented |
| Unit tests | `uv run -m unittest -q -k test_state_doctrine` | ✓ | 12 tests pass in 0.01s |
| Docs build | `uv run mkdocs build -q` | ✓ | Clean build, no warnings |
| Gates | `uv run gz gates --adr ADR-0.0.9` | ✓ | Gate 1 PASS, Gate 2 PASS (2258 tests) |

## Evidence Index

- `audit/proofs/audit-check.txt` — Ledger completeness output
- `audit/proofs/state-json.txt` — Full state graph JSON
- `audit/proofs/state-repair.txt` — Repair command output showing drift fix
- `audit/proofs/state-help.txt` — CLI help text
- `audit/proofs/unittest.txt` — State doctrine test results
- `audit/proofs/mkdocs.txt` — Docs build output
- `audit/proofs/status-table.txt` — Status table output

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ All 6 OBPIs delivered |
| Data Integrity | ✓ Ledger-first reads enforced; drift auto-repaired |
| Documentation Alignment | ✓ mkdocs builds clean; `--repair` in help text |
| Risk Items Resolved | ✓ No L3 gate blockers; repair is discoverable |

## Recommendations

- **Advisory:** REQ coverage is 10% (2/20 REQs have `@covers` decorators). Non-blocking but could improve traceability in future pass.
- **OBPI-0.1.0-01 drift:** Frontmatter keeps reverting to "Draft" — the state doctrine catches and fixes it each time, but the root cause of the revert should be investigated separately.

## Attestation

I/we attest that ADR-0.0.9 is implemented as intended, evidence is reproducible, and no blocking discrepancies remain.

Signed: _jeff, 2026-03-31_
