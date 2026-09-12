# CHORE-LOG: control-surface-validator-reachability

## 2026-09-12T12:15:29-05:00
- Status: FAIL
- Chore: control-surface-validator-reachability
- Title: Control Surface Audit — Validator Reachability & Ungated Ratchet (Pass D)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [FAIL] `uv run python scripts/check_proof_freshness.py control-surface-validator-reachability` => rc=3 (0.13s) -- exit 3 != 0

```text
[uv run python scripts/check_proof_freshness.py control-surface-validator-reachability] stdout:
proof-freshness gate — control-surface-validator-reachability
  audited surfaces:  src/gzkit/cli, src/gzkit/commands/quality.py, .pre-commit-config.yaml, .github/workflows, .claude/hooks
  surface last moved: 2026-09-11
  conformance-sweep.md         2026-08-15  STALE
  reachability-matrix.md       2026-08-15  STALE
[uv run python scripts/check_proof_freshness.py control-surface-validator-reachability] stderr:
POLICY BREACH:
  .gzkit/chores/control-surface-validator-reachability/proofs/conformance-sweep.md was last committed 2026-08-15, before its audited surface last moved (2026-09-11).
    Why: this chore's acceptance previously gated on `test -f`, which passes forever once a report exists and cannot see that the evidence now describes a surface that has changed.
    Fix: re-run the control-surface-validator-reachability audit and commit refreshed proofs. Touching the file without redoing the analysis restores the green-by-construction gate this replaced.
  .gzkit/chores/control-surface-validator-reachability/proofs/reachability-matrix.md was last committed 2026-08-15, before its audited surface last moved (2026-09-11).
    Why: this chore's acceptance previously gated on `test -f`, which passes forever once a report exists and cannot see that the evidence now describes a surface that has changed.
    Fix: re-run the control-surface-validator-reachability audit and commit refreshed proofs. Touching the file without redoing the analysis restores the green-by-construction gate this replaced.
```
