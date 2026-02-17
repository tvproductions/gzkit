# gz-obpi-reconcile

Full OBPI reconciliation workflow — **Sync → Audit → Sync**.

## Workflow Diagram

```text
╔══════════════════════════════════════════════════════════════════════╗
║  PHASE 1: PRE-SYNC                                                   ║
║  └── /gz-obpi-sync ADR-X.Y.Z                                         ║
║      Align ADR table with brief statuses (trust briefs as baseline)  ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 2: AUDIT                                                      ║
║  └── For each OBPI-X.Y.Z-NN brief:                                   ║
║      ├── Parse acceptance criteria                                   ║
║      ├── Search for evidence (tests, @covers, coverage)              ║
║      ├── Run tests: uv run -m unittest -v {test}                     ║
║      ├── Check coverage: ≥40% threshold                              ║
║      ├── Write ledger entry (proof) → logs/obpi-audit.jsonl          ║
║      └── Fix brief if work done but status stale                     ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 3: POST-SYNC                                                  ║
║  └── /gz-obpi-sync ADR-X.Y.Z                                         ║
║      Propagate audit fixes to ADR table                              ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 4: REPORT                                                     ║
║  └── Summary: progress %, briefs fixed, ledger location              ║
╚══════════════════════════════════════════════════════════════════════╝
```

## Quick Reference

| Phase | Action | Output |
|-------|--------|--------|
| 1 | Sync ADR ← briefs | Baseline established |
| 2 | Audit each brief | Ledger entries written |
| 3 | Sync ADR ← briefs | Fixes propagated |
| 4 | Report | Human-readable summary |

## Ledger Location

```text
docs/design/adr/adr-{series}/ADR-{id}-{slug}/logs/obpi-audit.jsonl
```

## Related

- **Skill procedure:** `SKILL.md` (this folder)
- **Prompt invocation:** `/gz-obpi-reconcile` (`.github/prompts/`)
- **Atomic skills:** `gz-obpi-sync`, `gz-obpi-audit`
