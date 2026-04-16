---
id: OBPI-0.25.0-02-progress-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 2
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-02: Progress Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-02 — "Evaluate and absorb core/progress.py (383 lines) — unified Rich progress API facade"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/progress.py` (383 lines) against gzkit's Rich usage in `commands/common.py` and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides a unified Rich progress API facade with context managers and TTY-aware handling. gzkit currently scatters progress display logic across command modules.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/progress.py` (383 lines)
- **gzkit equivalent:** Rich usage in `src/gzkit/commands/common.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- A unified progress facade would reduce duplication across gzkit commands

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Refactoring all existing gzkit commands to use the new facade in this OBPI

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Confirm decision)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Comparison

### airlineops `core/progress.py` (383 lines)

| Pattern | Lines | Assessment |
|---------|-------|-----------|
| `build_progress_columns()` | 45-59 | Hardcoded canonical column list; gzkit inlines equivalent columns per context |
| `ProgressManager` dataclass | 63-155 | Imperative start/stop facade; less Pythonic than gzkit's context managers |
| `progress_scope()` | 161-201 | Context manager with Windows UnicodeEncodeError handling; gzkit handles UTF-8 at runtime entrypoint |
| `make_batch_progress_callback()` | 204-239 | Callback pattern for batch progress; less clean than context manager approach |
| `make_download_progress()` | 242-282 | Domain-specific (download operations); gzkit has no download use case |
| `sqlite_heartbeat()` | 285-305 | No-op placeholder with no implementation |
| `create_warehouse_progress()` | 322-383 | Warehouse-domain-specific; fails subtraction test |

### gzkit progress infrastructure

| Module | Lines | Capabilities |
|--------|-------|-------------|
| `src/gzkit/cli/progress.py` | 135 | `progress_spinner`, `progress_phase`, `progress_bar` — context-manager-based, mode-aware (quiet/json suppression), stderr-targeted |
| `src/gzkit/cli/formatters.py` `ProgressContext` | ~75 | Step-counted progress with TTY-aware Rich rendering, non-TTY fallback (`[step/total]` to stderr), quiet/json suppression via `OutputFormatter` |

### Capability Comparison

| Dimension | airlineops | gzkit | Winner |
|-----------|-----------|-------|--------|
| Output mode integration | None — no quiet/json suppression | Integrated with `OutputFormatter` (quiet/json/human) | gzkit |
| API pattern | Imperative start/stop (`ProgressManager`) | Context managers (`with` blocks) | gzkit |
| TTY fallback | None — Rich-or-nothing | Non-TTY fallback prints `[step/total]` to stderr | gzkit |
| Stderr discipline | Mixed — some progress to stdout | All progress to stderr | gzkit |
| Windows Unicode | Explicit `UnicodeEncodeError` catch in `progress_scope` | Runtime UTF-8 configuration at CLI entrypoint | gzkit (architectural) |
| Spinner support | Via `SpinnerColumn` in progress bar | Dedicated `progress_spinner` context manager | gzkit |
| Step counting | Not supported | `progress_phase` with `[step/total]` labels | gzkit |
| Domain helpers | Warehouse, download, SQLite — domain-specific | None needed — gzkit is a governance toolkit | gzkit (cleaner) |

## Decision: Confirm

gzkit's existing progress infrastructure is more integrated, more Pythonic, and already surpasses what airlineops offers. No absorption is warranted.

**Rationale:**

1. **Mode integration**: gzkit progress respects quiet/json/human output modes via `OutputFormatter` — airlineops has no equivalent, meaning progress output cannot be suppressed in machine-readable modes.
2. **Context managers**: gzkit uses `with` blocks throughout — the idiomatic Python pattern for resource lifecycle. airlineops relies on imperative `start()`/`stop()` which is error-prone.
3. **TTY fallback**: gzkit's `ProgressContext` degrades gracefully to `[step/total]` text on non-TTY stderr. airlineops is Rich-or-nothing with no fallback.
4. **Stderr discipline**: gzkit routes all progress to stderr, keeping stdout clean for data. airlineops mixes output channels.
5. **No domain leakage**: airlineops's warehouse-specific, download-specific, and SQLite helpers are domain-specific patterns that fail the subtraction test. gzkit's progress API is generic and sufficient.
6. **Windows Unicode**: gzkit handles UTF-8 at the CLI entrypoint level (`sys.stdout.reconfigure(encoding="utf-8")`), making per-callsite `UnicodeEncodeError` catches unnecessary.

### Gate 4 (BDD): N/A

No operator-visible behavior change. This is a Confirm decision — no code was added, removed, or modified. The existing progress infrastructure continues to function identically.

## Acceptance Criteria

- [x] REQ-0.25.0-02-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [x] REQ-0.25.0-02-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [x] REQ-0.25.0-02-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [x] REQ-0.25.0-02-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [x] REQ-0.25.0-02-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/progress.py
# Expected: airlineops source under review exists

test -f src/gzkit/commands/common.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-02-progress-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (no code changes — Confirm decision)
- [x] **Gate 3 (Docs):** Decision rationale completed with side-by-side comparison
- [x] **Gate 4 (BDD):** N/A — Confirm decision, no operator-visible behavior change
- [ ] **Gate 5 (Human):** Attestation recorded

## Closing Argument

gzkit's progress infrastructure (`cli/progress.py` and `cli/formatters.py ProgressContext`) already surpasses airlineops's `core/progress.py` on every dimension that matters for a governance CLI toolkit: output-mode integration, context-manager API, TTY fallback, stderr discipline, and architectural UTF-8 handling. The airlineops module's domain-specific helpers (warehouse progress, download progress, SQLite heartbeat) fail the subtraction test — they are airline-specific patterns, not reusable infrastructure. The imperative `ProgressManager` facade is less Pythonic than gzkit's existing context managers. No absorption is warranted; gzkit's implementation is the stronger pattern.

### Implementation Summary


- **Decision:** Confirm — gzkit's existing progress infrastructure is sufficient
- **Patterns evaluated:** 7 airlineops `core/progress.py` patterns (383 lines)
- **gzkit equivalents:** `cli/progress.py` (135 lines) + `cli/formatters.py ProgressContext` (~75 lines)
- **Mode integration:** gzkit integrates with OutputFormatter for quiet/json/human suppression; airlineops has none
- **API pattern:** gzkit uses context managers; airlineops uses imperative start/stop
- **TTY fallback:** gzkit degrades to `[step/total]` text on non-TTY; airlineops is Rich-or-nothing
- **Domain leakage:** airlineops warehouse, download, SQLite helpers fail subtraction test
- **Code changes:** None — Confirm decision, no absorption warranted

### Key Proof


```bash
rg -n 'Decision: Confirm' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-02-progress-pattern.md
# 107:## Decision: Confirm
```

### Human Attestation

- Attestor: `Jeffry`
- Date: 2026-04-09
- Attestation: attest completed
