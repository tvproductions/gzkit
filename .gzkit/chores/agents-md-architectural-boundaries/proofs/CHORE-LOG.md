# CHORE-LOG: agents-md-architectural-boundaries

## 2026-05-10T11:19:50-05:00
- Status: PASS
- Chore: agents-md-architectural-boundaries
- Title: Add Architectural Boundaries to AGENTS.md
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `grep -F 'Do not promote post-1.0 pool ADRs into active work' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not promote post-1.0'
  - [PASS] `grep -F 'Do not add more pool ADRs to the runtime track' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not add more pool ADRs'
  - [PASS] `grep -F 'Do not build the graph engine without locking state doctrine' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not build the graph engine'
  - [PASS] `grep -F 'Do not let reconciliation remain a maintenance chore' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not let reconciliation'
  - [PASS] `grep -F 'Do not let AirlineOps parity become perpetual catch-up' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not let AirlineOps parity'
  - [PASS] `grep -F 'Do not let derived views silently become source-of-truth' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not let derived views'
  - [PASS] `uv run gz lint` => rc=0 (1.05s) -- exit 0 == 0

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
## 2026-05-10T14:15:51-05:00
- Status: PASS
- Chore: agents-md-architectural-boundaries
- Title: Add Architectural Boundaries to AGENTS.md
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `grep -F 'Do not promote post-1.0 pool ADRs into active work' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not promote post-1.0'
  - [PASS] `grep -F 'Do not add more pool ADRs to the runtime track' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not add more pool ADRs'
  - [PASS] `grep -F 'Do not build the graph engine without locking state doctrine' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not build the graph engine'
  - [PASS] `grep -F 'Do not let reconciliation remain a maintenance chore' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not let reconciliation'
  - [PASS] `grep -F 'Do not let AirlineOps parity become perpetual catch-up' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not let AirlineOps parity'
  - [PASS] `grep -F 'Do not let derived views silently become source-of-truth' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not let derived views'
  - [PASS] `uv run gz lint` => rc=0 (0.99s) -- exit 0 == 0

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
## 2026-06-29T21:43:26-05:00
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
  - [PASS] `uv run gz lint` => rc=0 (0.58s) -- exit 0 == 0

```text
[grep -F 'Do not promote post-1.0 pool ADRs into active work' AGENTS.md] stdout:
1. Do not promote post-1.0 pool ADRs into active work.
[grep -F 'Do not add more pool ADRs to the runtime track' AGENTS.md] stdout:
2. Do not add more pool ADRs to the runtime track.
[grep -F 'Do not build the graph engine without locking state doctrine' AGENTS.md] stdout:
3. Do not build the graph engine without locking state doctrine first.
[grep -F 'Do not let reconciliation remain a maintenance chore' AGENTS.md] stdout:
4. Do not let reconciliation remain a maintenance chore.
[grep -F 'Do not let AirlineOps parity become perpetual catch-up' AGENTS.md] stdout:
5. Do not let AirlineOps parity become perpetual catch-up.
[grep -F 'Do not let derived views silently become source-of-truth' AGENTS.md] stdout:
6. Do not let derived views silently become source-of-truth — `gz status`, pipeline markers, and reconciliation caches are Layer 3; every fact traces to Layer 1 canon or Layer 2 ledger.
[uv run gz lint] stdout:
Running linters...
All checks passed!

ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.
```
## 2026-07-07T05:44:32-05:00
- Status: PASS
- Chore: agents-md-architectural-boundaries
- Title: Add Architectural Boundaries to AGENTS.md
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `grep -F 'Do not promote post-1.0 pool ADRs into active work' AGENTS.md` => rc=0 (0.01s) -- output contains 'Do not promote post-1.0'
  - [PASS] `grep -F 'Do not add more pool ADRs to the runtime track' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not add more pool ADRs'
  - [PASS] `grep -F 'Do not build the graph engine without locking state doctrine' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not build the graph engine'
  - [PASS] `grep -F 'Do not let reconciliation remain a maintenance chore' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not let reconciliation'
  - [PASS] `grep -F 'Do not let AirlineOps parity become perpetual catch-up' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not let AirlineOps parity'
  - [PASS] `grep -F 'Do not let derived views silently become source-of-truth' AGENTS.md` => rc=0 (0.00s) -- output contains 'Do not let derived views'
  - [PASS] `uv run gz lint` => rc=0 (0.62s) -- exit 0 == 0

```text
[grep -F 'Do not promote post-1.0 pool ADRs into active work' AGENTS.md] stdout:
1. Do not promote post-1.0 pool ADRs into active work.
[grep -F 'Do not add more pool ADRs to the runtime track' AGENTS.md] stdout:
2. Do not add more pool ADRs to the runtime track.
[grep -F 'Do not build the graph engine without locking state doctrine' AGENTS.md] stdout:
3. Do not build the graph engine without locking state doctrine first.
[grep -F 'Do not let reconciliation remain a maintenance chore' AGENTS.md] stdout:
4. Do not let reconciliation remain a maintenance chore.
[grep -F 'Do not let AirlineOps parity become perpetual catch-up' AGENTS.md] stdout:
5. Do not let AirlineOps parity become perpetual catch-up.
[grep -F 'Do not let derived views silently become source-of-truth' AGENTS.md] stdout:
6. Do not let derived views silently become source-of-truth — `gz status`, pipeline markers, and reconciliation caches are Layer 3; every fact traces to Layer 1 canon or Layer 2 ledger.
[uv run gz lint] stdout:
Running linters...
All checks passed!

ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.
```
## 2026-07-07T06:13:27-05:00
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
  - [PASS] `uv run gz lint` => rc=0 (0.62s) -- exit 0 == 0

```text
[grep -F 'Do not promote post-1.0 pool ADRs into active work' AGENTS.md] stdout:
1. Do not promote post-1.0 pool ADRs into active work.
[grep -F 'Do not add more pool ADRs to the runtime track' AGENTS.md] stdout:
2. Do not add more pool ADRs to the runtime track.
[grep -F 'Do not build the graph engine without locking state doctrine' AGENTS.md] stdout:
3. Do not build the graph engine without locking state doctrine first.
[grep -F 'Do not let reconciliation remain a maintenance chore' AGENTS.md] stdout:
4. Do not let reconciliation remain a maintenance chore.
[grep -F 'Do not let AirlineOps parity become perpetual catch-up' AGENTS.md] stdout:
5. Do not let AirlineOps parity become perpetual catch-up.
[grep -F 'Do not let derived views silently become source-of-truth' AGENTS.md] stdout:
6. Do not let derived views silently become source-of-truth — `gz status`, pipeline markers, and reconciliation caches are Layer 3; every fact traces to Layer 1 canon or Layer 2 ledger.
[uv run gz lint] stdout:
Running linters...
All checks passed!

ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.
```
## 2026-07-31T19:06:37-05:00
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
  - [PASS] `uv run gz lint` => rc=0 (0.64s) -- exit 0 == 0

```text
[grep -F 'Do not promote post-1.0 pool ADRs into active work' AGENTS.md] stdout:
1. Do not promote post-1.0 pool ADRs into active work.
[grep -F 'Do not add more pool ADRs to the runtime track' AGENTS.md] stdout:
2. Do not add more pool ADRs to the runtime track.
[grep -F 'Do not build the graph engine without locking state doctrine' AGENTS.md] stdout:
3. Do not build the graph engine without locking state doctrine first.
[grep -F 'Do not let reconciliation remain a maintenance chore' AGENTS.md] stdout:
4. Do not let reconciliation remain a maintenance chore.
[grep -F 'Do not let AirlineOps parity become perpetual catch-up' AGENTS.md] stdout:
5. Do not let AirlineOps parity become perpetual catch-up.
[grep -F 'Do not let derived views silently become source-of-truth' AGENTS.md] stdout:
6. Do not let derived views silently become source-of-truth — `gz status`, pipeline markers, and reconciliation caches are Layer 3; every fact traces to Layer 1 canon or Layer 2 ledger.
[uv run gz lint] stdout:
Running linters...
All checks passed!

ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.
```
