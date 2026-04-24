# CHORE-LOG: agents-md-architectural-boundaries

## 2026-04-02T18:25:33-05:00
- Status: PASS
- Chore: agents-md-architectural-boundaries
- Title: Add Architectural Boundaries to AGENTS.md
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `grep -c 'Do not' AGENTS.md` => rc=0 (0.00s) -- output contains '8'
  - [PASS] `uv run gz lint` => rc=0 (0.39s) -- exit 0 == 0

```text
[grep -c 'Do not' AGENTS.md] stdout:
8
[uv run gz lint] stdout:
Running linters...
All checks passed!

ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.
```
## 2026-04-19T19:45:02-05:00
- Status: PASS
- Chore: agents-md-architectural-boundaries
- Title: Add Architectural Boundaries to AGENTS.md
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `grep -c 'Do not' AGENTS.md` => rc=0 (0.01s) -- output contains '8'
  - [PASS] `uv run gz lint` => rc=0 (0.74s) -- exit 0 == 0

```text
[grep -c 'Do not' AGENTS.md] stdout:
8
[uv run gz lint] stdout:
Running linters...
All checks passed!

ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.
```
## 2026-04-19T20:56:35-05:00
- Status: PASS
- Chore: agents-md-architectural-boundaries
- Title: Add Architectural Boundaries to AGENTS.md
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `grep -c 'Do not' AGENTS.md` => rc=0 (0.01s) -- output contains '8'
  - [PASS] `uv run gz lint` => rc=0 (0.71s) -- exit 0 == 0

```text
[grep -c 'Do not' AGENTS.md] stdout:
8
[uv run gz lint] stdout:
Running linters...
All checks passed!

ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.
```
## 2026-04-24T01:57:30-05:00
- Status: PASS
- Chore: agents-md-architectural-boundaries
- Title: Add Architectural Boundaries to AGENTS.md
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `grep -F 'Do not promote post-1.0 pool ADRs into active work' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not promote post-1.0'
  - [PASS] `grep -F 'Do not add more pool ADRs to the runtime track' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not add more pool ADRs'
  - [PASS] `grep -F 'Do not build the graph engine without locking state doctrine' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not build the graph engine'
  - [PASS] `grep -F 'Do not let reconciliation remain a maintenance chore' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not let reconciliation'
  - [PASS] `grep -F 'Do not let AirlineOps parity become perpetual catch-up' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not let AirlineOps parity'
  - [PASS] `grep -F 'Do not let derived views silently become source-of-truth' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not let derived views'
  - [PASS] `uv run gz lint` => rc=0 (0.40s) -- exit 0 == 0

```text
[grep -F 'Do not promote post-1.0 pool ADRs into active work' AGENTS.md] stdout:
1. **Do not promote post-1.0 pool ADRs into active work.** `ai-runtime-foundations`, `controlled-agency-recovery`, and `evaluation-infrastructure` (the pool version) are post-1.0 concerns. The graph spine, proof architecture, and pipeline lifecycle are not stable enough to support AI runtime controls on top.
[grep -F 'Do not add more pool ADRs to the runtime track' AGENTS.md] stdout:
2. **Do not add more pool ADRs to the runtime track.** The pool has sufficient architectural intent for 2-3 years of work. The problem is insufficient foundation locking, not insufficient vision.
[grep -F 'Do not build the graph engine without locking state doctrine' AGENTS.md] stdout:
3. **Do not build the graph engine without locking state doctrine first.** A graph engine built on implicit state assumptions becomes the single biggest source of reconciliation bugs.
[grep -F 'Do not let reconciliation remain a maintenance chore' AGENTS.md] stdout:
4. **Do not let reconciliation remain a maintenance chore.** If the state doctrine says "derived state is rebuildable," then reconciliation is a core architectural operation — tested, gated, and part of the pipeline. **Freshness check applies once reconciliation has run at least once; zero-event history is bootstrap, not drift** (see `gz validate --reconcile-freshness` fail-open at `src/gzkit/governance/trust_audits.py:1024-1028`).
[grep -F 'Do not let AirlineOps parity become perpetual catch-up' AGENTS.md] stdout:
5. **Do not let AirlineOps parity become perpetual catch-up.** Current parity is sufficient baseline. Future parity should flow from gzkit innovations adopted by AirlineOps, not gzkit chasing AirlineOps patches.
[grep -F 'Do not let derived views silently become source-of-truth' AGENTS.md] stdout:
6. **Do not let derived views silently become source-of-truth.** `gz status` output, pipeline markers, and reconciliation caches are Layer 3. Every fact must trace to Layer 1 (canon) or Layer 2 (ledger).
[uv run gz lint] stdout:
Running linters...
All checks passed!

ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.
```
