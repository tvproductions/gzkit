---
id: OBPI-0.25.0-17-console-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 17
status: in_progress
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-17: Console Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-17 — "Evaluate and absorb common/console.py (45 lines) — console I/O abstractions"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/common/console.py` (45 lines) against gzkit's `commands/common.py` (745 lines) and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides console I/O abstractions and TTY-aware output. gzkit's equivalent is 16x larger and covers far more territory, but the comparison must verify whether airlineops defines any clean abstractions that gzkit could benefit from factoring out of its monolithic common module.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/common/console.py` (45 lines)
- **gzkit equivalent:** `src/gzkit/commands/common.py` (745 lines)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's 16x larger module may benefit from airlineops's smaller, focused abstraction as a refactoring guide

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Refactoring gzkit's entire `commands/common.py` in this OBPI

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## DECISION

**Decision: Confirm** — gzkit's console implementation is sufficient. No upstream absorption warranted.

**Rationale:** airlineops's `common/console.py` (45 lines) is a `create_console()` factory that detects terminal encoding on Windows via `sys.stdout.encoding` and configures Rich's `legacy_windows` flag accordingly (UTF-8 terminals get full Unicode, legacy terminals get ASCII fallback). gzkit handles the same concern with a stronger two-layer approach: (1) `_ensure_utf8_console()` in `cli/main.py:93-100` reconfigures both `sys.stdout` and `sys.stderr` to UTF-8 at startup — before any Rich output — which forces UTF-8 at the OS stream level rather than adapting per-Console, and (2) a module-level Console singleton in `commands/common.py:30-33` with `NO_COLOR` and `FORCE_COLOR` environment variable support. The airlineops encoding detection is subsumed by `_ensure_utf8_console()` because once stdout is reconfigured to UTF-8, Rich's `legacy_windows` detection becomes irrelevant. Additionally, gzkit's singleton pattern avoids the per-call factory overhead and ensures consistent Console configuration across all commands.

## COMPARISON ANALYSIS

| Dimension | airlineops (45 lines, 1 file) | gzkit (2 locations, ~30 lines total) | Winner |
|-----------|-------------------------------|--------------------------------------|--------|
| Encoding strategy | Per-Console detection: reads `sys.stdout.encoding`, sets `legacy_windows` | Process-level fix: `_ensure_utf8_console()` reconfigures stdout/stderr to UTF-8 at startup | gzkit |
| Scope of fix | Rich Console only — non-Rich output on legacy terminals still fails | All output — stdout and stderr are UTF-8 regardless of consumer | gzkit |
| Console creation | Factory function: new Console per call, caller manages lifecycle | Module-level singleton: single Console shared across all commands | Tie (different trade-offs) |
| Environment support | `force_terminal` passthrough only | `NO_COLOR` (accessibility) and `FORCE_COLOR` env var support | gzkit |
| Windows compatibility | Detects cp1252 vs UTF-8 at Console level | Forces UTF-8 at stream level, making detection unnecessary | gzkit |
| Error handling | None — assumes `sys.stdout` always has `encoding` attr | Guards with `hasattr(stream, "reconfigure")` | gzkit |
| Cross-platform | Windows-specific detection branch, passthrough for others | Windows-specific reconfigure with safe fallthrough | Tie |
| Test coverage | No visible tests for the factory function | `_ensure_utf8_console()` is implicitly tested via CLI smoke tests | Tie |

### Patterns Worth Noting (But Not Absorbing)

- airlineops's per-Console factory is a clean pattern for applications needing multiple Console instances with different configurations. gzkit's singleton approach is appropriate for a CLI where one Console serves all commands.
- airlineops's `legacy_windows` detection logic is sound but redundant when the stream is already reconfigured to UTF-8 upstream.

## GATE 4 BDD: N/A Rationale

A Confirm decision produces no code changes and no operator-visible behavior changes. No behavioral proof is required. The existing gzkit test suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Confirm decision, no code changes)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (Confirm decision, no operator-visible behavior change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-17-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`. — **Confirm** recorded in Decision section.
- [x] REQ-0.25.0-17-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Eight-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-17-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Confirm decision).
- [x] REQ-0.25.0-17-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted. — Rationale in Decision section: gzkit's two-layer approach subsumes airlineops's per-Console detection.
- [x] REQ-0.25.0-17-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/common/console.py
# Expected: airlineops source under review exists

test -f src/gzkit/commands/common.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-17-console-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (existing suite, no code changes for Confirm)
- [x] **Gate 3 (Docs):** Decision rationale completed
- [x] **Gate 4 (BDD):** N/A recorded with rationale (Confirm, no behavior change)
- [ ] **Gate 5 (Human):** Attestation recorded

## Evidence

### Gate 1 (ADR)

- Intent and scope recorded in brief objective and requirements sections

### Gate 2 (TDD)

- Existing gzkit test suite passes — no new tests needed for a Confirm decision
- Verification: `uv run gz test`

### Code Quality

- No code changes — Confirm decision is documentation-only
- Verification: `uv run gz lint`, `uv run gz typecheck`

### Value Narrative

Before this OBPI, there was no documented comparison between airlineops's `common/console.py` and gzkit's console surface. The airlineops module provides a clean `create_console()` factory with per-Console encoding detection, but gzkit addresses the same concern more robustly with `_ensure_utf8_console()` — a process-level UTF-8 reconfiguration that runs once at startup and covers all output, not just Rich Console instances. The module-level Console singleton in `commands/common.py` additionally supports `NO_COLOR` and `FORCE_COLOR` environment variables that airlineops does not handle. No absorption is warranted.

### Key Proof


- Decision: Confirm
- Comparison: eight-dimension analysis in Comparison Analysis section
- airlineops `common/console.py`: 45 lines, `create_console()` factory with per-Console Windows encoding detection
- gzkit console surface: two-layer approach — `_ensure_utf8_console()` (cli/main.py:93-100) forces UTF-8 at stream level; Console singleton (commands/common.py:30-33) with env var support
- airlineops encoding detection is subsumed by `_ensure_utf8_console()` — once stdout is UTF-8, `legacy_windows` detection is irrelevant
- gzkit's approach is stronger: covers all output, not just Rich Console

### Implementation Summary


- Decision: Confirm
- Files created: none
- Files modified: this brief only
- Tests added: none (no code changes)
- Date: 2026-04-11

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: 2026-04-11

## Closing Argument

airlineops's `common/console.py` (45 lines) is a `create_console()` factory that detects terminal encoding on Windows via `sys.stdout.encoding` and configures Rich's `legacy_windows` flag to toggle between full Unicode and ASCII fallback. gzkit handles the same concern with a stronger two-layer approach: `_ensure_utf8_console()` in `cli/main.py:93-100` reconfigures both stdout and stderr to UTF-8 at startup — before any Rich output — which forces UTF-8 at the OS stream level rather than adapting per-Console instance. The module-level Console singleton in `commands/common.py:30-33` adds `NO_COLOR` and `FORCE_COLOR` environment variable support that airlineops lacks. Once `_ensure_utf8_console()` runs, the encoding detection in airlineops's factory becomes redundant — Rich sees a UTF-8 stream regardless of the original terminal encoding. The airlineops factory pattern (new Console per call) is appropriate for multi-Console applications but unnecessary for gzkit's CLI where a single shared Console serves all commands. **Decision: Confirm.**
