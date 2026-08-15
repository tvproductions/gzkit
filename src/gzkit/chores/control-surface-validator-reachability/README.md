# Control Surface — Validator Reachability & Ungated Ratchet (Pass D)

Tiers every runnable `gz validate --<scope>` by **what invokes it**, sweeps each
scope individually to capture its own exit code, and holds the ungated set to a
shrink-only baseline.

Passes A/B/C of this family ask about content relationships. This one asks
whether a check **runs at all** — a validator can be semantically perfect and
still execute on no commit path, protecting nothing while reading as coverage.

## Commands

```bash
# Tier census (fast)
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py --report

# Conformance sweep — every scope in its own process, own exit code (slow)
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py --sweep

# Ratchet enforcement — exit 3 when the ungated set grew
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py

# Re-baseline after draining (refuses to grow)
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py --report --write
```

## Tiers and dispositions

| Tier | Meaning | Disposition |
|---|---|---|
| A | Gated by `gz check`, a hook, CI, or pre-commit | target state |
| B | Referenced only from `tests/**` / `features/**` | verify the test runs against the live repo, not a fixture |
| C | Named in docs or skills, invoked by nothing | wire into a gate or retire |
| D | No caller anywhere | delete |

## Baseline

`data/validator_reachability_grandfather.json`, registered shrink-only in
`data/waiver_ratchet_registry.json` (ADR-0.0.73 Boundary Invariant #8). Read the
count from the file or `--report`; it is deliberately not restated in prose.

See [`CHORE.md`](CHORE.md) for the full method, guardrails, and the 2026-08-15
findings that produced this chore.
