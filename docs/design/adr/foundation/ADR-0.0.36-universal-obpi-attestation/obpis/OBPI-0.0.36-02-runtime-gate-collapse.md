---
id: OBPI-0.0.36-02-runtime-gate-collapse
parent: ADR-0.0.36-universal-obpi-attestation
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.36-02-runtime-gate-collapse: Runtime Gate Collapse

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/ADR-0.0.36-universal-obpi-attestation.md`
- **Checklist Item:** #2 — "`_requires_human_obpi_attestation` collapse + `_is_foundation_adr` orphan audit (runtime gate)"

**Status:** Draft

## Objective

Collapse `_requires_human_obpi_attestation` in `src/gzkit/commands/adr_audit.py` to `return True` while preserving the function signature so call-sites remain unchanged, then audit the orphaned `_is_foundation_adr` helper for remaining call-sites and either remove it or mark it deprecated with a docstring pointing at this ADR.

## Lane

**Heavy** — runtime contract change to a foundation gate that fires on every OBPI completion. Every receipt-emitting code path runs through this function; the collapse must preserve callers' behavior expectations exactly (signature in, return type out) while changing the semantic floor from "depends on parent ADR kind/lane" to "always true."

## Allowed Paths

- `src/gzkit/commands/adr_audit.py` — primary runtime gate file containing `_requires_human_obpi_attestation` and `_is_foundation_adr`
- `tests/commands/test_adr_audit.py` — existing test module for `adr_audit.py` (any test path that asserts the lane/kind branching needs to flip to assert universality)
- `tests/governance/test_attestation_universality.py` — new test module asserting the gate returns True across the full kind × lane cross product

## Denied Paths

- `AGENTS.md` — doctrine surface owned by OBPI-0.0.36-01
- `src/gzkit/governance/trust_audits.py`, `src/gzkit/validate_pkg/` — validator scope is OBPI-0.0.36-03
- `data/historical_self_close_waivers.json` — waiver list is OBPI-0.0.36-04
- `.gzkit/skills/**/SKILL.md`, `.claude/rules/**`, `.gzkit/rules/**` — skill/rule prose sweep is OBPI-0.0.36-05
- New runtime dependencies; CI files; lockfiles
- Receipt schema files (touched by OBPI-03)
- Removal of `_enforce_human_attestation_authenticity` (out of scope; complementary defense per ADR Non-goals)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `_requires_human_obpi_attestation(parent_adr, parent_lane)` MUST return `True` for every input. The signature `(parent_adr: str | None, parent_lane: str) -> bool` MUST be preserved exactly so all 4+ call-sites in `adr_audit.py` (currently around line 494) continue compiling without edit.
2. REQUIREMENT: The function body MUST collapse to a single `return True` (or a one-line equivalent that is unconditionally truthy across all inputs). The foundation/lane branching logic at the current line range (around 257–272) MUST be removed.
3. REQUIREMENT: `_is_foundation_adr` MUST be audited via `Grep` across `src/**/*.py` and `tests/**/*.py`. If zero remaining call-sites exist after the collapse, the helper MUST be removed. If non-zero call-sites exist for unrelated purposes (taxonomy classification, validator scoping), it MUST be retained with a docstring noting that it is no longer load-bearing for attestation routing — citing this OBPI and ADR-0.0.36 inline.
4. REQUIREMENT: Existing tests asserting lane-conditional attestation (e.g. tests that verified a `feature × lite` parent did NOT require human attestation) MUST be updated or removed — they assert the inverse of the new doctrine. Updates flip the assertion to require attestation universally; removals require a new test asserting the universal behavior covers the previously-tested case.
5. REQUIREMENT: A new test module `tests/governance/test_attestation_universality.py` MUST assert the gate returns True across the full kind × lane cross product (`foundation × lite`, `foundation × heavy`, `feature × lite`, `feature × heavy`, plus `parent_adr=None` edge case). Tests assert REQ-derived semantics per `.gzkit/rules/tests.md`.
6. REQUIREMENT: `_enforce_human_attestation_authenticity` (TTY + ATTEST gate) MUST remain unmodified. This OBPI addresses the absence-of-attestation surface; authenticity is a complementary defense that this OBPI does not touch.

> STOP-on-BLOCKERS: if `_requires_human_obpi_attestation` has additional callers in modules outside the discovered set, halt and surface the call-site list before editing.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item #2 — quote verbatim into Implementation Summary** (the runtime gate collapse to `return True`).
- [ ] Parent ADR § Intent — why universal attestation is the doctrine the runtime gate now enforces.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/ADR-0.0.36-universal-obpi-attestation.md`

> **STOP:** If you cannot quote the parent ADR § Decision item #2 that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.claude/rules/tests.md` § Tests assert semantics, not strings — assertion derivation rule
- [ ] `.claude/rules/pythonic.md` — type-ignore suppression syntax (in case ty flags the collapsed body)

**Context:**

- [ ] `src/gzkit/commands/adr_audit.py` — current `_requires_human_obpi_attestation` body (around line 257) and call-sites (search for the function name across the file)
- [ ] `src/gzkit/commands/adr_audit.py` — `_enforce_human_attestation_authenticity` (must remain untouched; read to confirm boundary)
- [ ] OBPI-0.0.36-01 brief — sequencing: this OBPI lands AFTER doctrine collapse so runtime matches canon

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/adr_audit.py` exists
- [ ] `tests/commands/test_adr_audit.py` exists (existing test surface)
- [ ] OBPI-0.0.36-01 has landed (AGENTS.md matrix collapsed) — runtime collapse must not precede doctrine collapse

**Existing Code (understand current state):**

- [ ] `Grep _requires_human_obpi_attestation` across `src/**` and `tests/**` — enumerate every call-site
- [ ] `Grep _is_foundation_adr` across `src/**` and `tests/**` — enumerate every call-site
- [ ] Read existing test patterns in `tests/commands/test_adr_audit.py` to match the table-driven style for the new universality test module

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item #2 quoted in Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: `tests/governance/test_attestation_universality.py::test_gate_returns_true_for_feature_lite` fails before edit (current branch returns False for feature × lite)
- [ ] GREEN: same test passes after collapse
- [ ] Red-Green-Refactor cycle followed for each kind × lane case
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`
- [ ] Unused-import sweep clean (collapsed function may orphan a `re` import or similar)

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] If `docs/governance/governance_runbook.md` or `docs/user/runbook.md` references the lane-conditional gate, update to reflect universal behavior

### Gate 4: BDD (Heavy)

- [ ] Behave scenario tagged `@REQ-0.0.36-02-NN` asserting `gz obpi complete` requires human attestation for a feature × lite parent (the case that previously self-closed); scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Universal under this very ADR)

- [ ] Human attestation recorded with TTY+ATTEST under `gz obpi complete`

## Verification

```bash
# Universality assertions across kind × lane
uv run -m unittest tests.governance.test_attestation_universality -v

# Existing adr_audit tests still pass after assertion flip
uv run -m unittest tests.commands.test_adr_audit -v

# Orphan audit
rg -n "_is_foundation_adr" src/ tests/

# Standard quality gates
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# ARB receipts for Heavy-lane attestation
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name coverage -- uv run coverage run -m unittest discover -s tests -t .
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. The closeout
     ceremony walkthrough harvests this section (parser-validated;
     unregistered verbs are dropped). Prefer real paths and arguments
     over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

- [ ] REQ-0.0.36-02-01: Given `_requires_human_obpi_attestation` after this OBPI, when called with any combination of `parent_adr` (foundation, feature, None) × `parent_lane` (lite, heavy, empty string), then the return value is `True`.
- [ ] REQ-0.0.36-02-02: Given the function source after this OBPI, when read, then the body is a single `return True` (or unconditionally-true equivalent) and the function signature is unchanged from the pre-collapse signature.
- [ ] REQ-0.0.36-02-03: Given `_is_foundation_adr` after this OBPI, when grep searches for its call-sites under `src/**` and `tests/**`, then either (a) zero call-sites remain and the helper is removed, or (b) call-sites for unrelated purposes remain and the helper carries a docstring citing OBPI-0.0.36-02 and ADR-0.0.36 noting it is no longer load-bearing for attestation routing.
- [ ] REQ-0.0.36-02-04: Given `tests/governance/test_attestation_universality.py`, when run, then it asserts `_requires_human_obpi_attestation` returns True across the full kind × lane cross product including the previously-self-closeable `feature × lite` case.
- [ ] REQ-0.0.36-02-05: Given `_enforce_human_attestation_authenticity` after this OBPI, when compared to its pre-OBPI implementation, then the function body is byte-identical (this OBPI does not touch the authenticity gate).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; Decision item #2 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle followed; universality test asserts REQ-derived semantics
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** mkdocs --strict clean; runbook updated if applicable
- [ ] **Gate 4 (BDD):** behave scenarios tagged + passing
- [ ] **Gate 5 (Human):** TTY+ATTEST attestation recorded
- [ ] **Value Narrative:** Documented below
- [ ] **Key Proof:** Concrete test output + grep evidence below

> Universal attestation rule applies under ADR-0.0.36; Gate 5 fires regardless of lane.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste RED + GREEN test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs --strict output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text + TTY+ATTEST receipt here
```

### Value Narrative

Before this OBPI, `_requires_human_obpi_attestation` branched on parent ADR kind and lane, returning False for feature × lite parents — the runtime mechanism through which the GHI #332 self-close receipts were emitted with `attested_*` absent. After this OBPI, the gate returns True unconditionally; no caller can construct an OBPI completion path that omits the human-attestation requirement at runtime. The function signature is preserved so all call-sites compile without edit.

### Key Proof

```bash
# Before (sketch):
$ python -c "from gzkit.commands.adr_audit import _requires_human_obpi_attestation; print(_requires_human_obpi_attestation('ADR-0.16.0', 'lite'))"
False

# After:
$ python -c "from gzkit.commands.adr_audit import _requires_human_obpi_attestation; print(_requires_human_obpi_attestation('ADR-0.16.0', 'lite'))"
True
```

### Implementation Summary

- Files created/modified: `src/gzkit/commands/adr_audit.py` (gate collapse; possibly `_is_foundation_adr` removal), `tests/commands/test_adr_audit.py` (assertion flips for any pre-OBPI lane-conditional tests), `tests/governance/test_attestation_universality.py` (new universality test module)
- Tests added: `test_gate_returns_true_for_foundation_lite`, `test_gate_returns_true_for_foundation_heavy`, `test_gate_returns_true_for_feature_lite`, `test_gate_returns_true_for_feature_heavy`, `test_gate_returns_true_for_parent_adr_none`
- Date completed: TBD
- Attestation status: pending TTY+ATTEST under universal attestation rule
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb` (universal under ADR-0.0.36)
- Attestation: substantive attestation text recorded at completion
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
