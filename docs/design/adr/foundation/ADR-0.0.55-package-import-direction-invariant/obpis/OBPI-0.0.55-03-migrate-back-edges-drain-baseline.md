---
id: OBPI-0.0.55-03-migrate-back-edges-drain-baseline
parent: ADR-0.0.55-package-import-direction-invariant
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.55-03-migrate-back-edges-drain-baseline: Migrate the Genuine Back-Edges + Drain the Baseline

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.55-package-import-direction-invariant/ADR-0.0.55-package-import-direction-invariant.md`
- **Checklist Item:** #3 — "OBPI-0.0.55-03: Migrate high-volume back-edges (cli↔commands, governance→cli/commands, doc_coverage→commands, etc.) + drain baseline allowlist of bootstrap entries"

**Status:** Draft

## Objective

Migrate every genuine vertical-to-vertical back-edge off the `data/package_import_direction_baseline.json` allowlist: the `cli ↔ commands` bidirectional flow, `governance → cli`/`governance → commands`, `doc_coverage → commands`, `chores → commands`, `justify → cli`, and the `arb → commands` Provider-to-above-floor leak. Each edge is relocated or inverted in the canonical import direction, removed from the baseline with a per-edge migration commit trailer, and pinned by a regression-invariant test. The baseline's `phase: bootstrap` entries are drained to zero by this OBPI's completion.

## Lane

**Heavy** — Behavior change across the `src/gzkit/` import graph: source-symbol relocations and dependency inversions touching `cli`, `commands`, `governance`, `doc_coverage`, `chores`, `justify`, and `arb`. Per AGENTS.md § Architectural Boundaries this is an architectural-boundary intervention. Foundation-kind parent ADR-0.0.55 triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `src/gzkit/cli/` — receives shared utilities extracted from the `cli ↔ commands` back-edge in the canonical direction
- `src/gzkit/commands/` — the relocation target for the `cli ↔ commands` shared symbols; the source of the `governance → commands`, `doc_coverage → commands`, `chores → commands` back-edges to invert
- `src/gzkit/governance/` — the `governance → cli` / `governance → commands` back-imports are relocated or inverted through a `ports` Provider
- `src/gzkit/doc_coverage/` — the `doc_coverage → commands` back-edges are relocated or inverted
- `src/gzkit/chores/` — the `chores → commands` back-edge is relocated or inverted
- `src/gzkit/justify/` — the `justify → cli` back-edge is relocated or inverted
- `src/gzkit/arb/` — the `arb → commands` Provider-to-above-floor leak is cleaned (NOT exempted)
- `data/` — each migrated edge is removed from `data/package_import_direction_baseline.json` (created by OBPI-01); `phase: bootstrap` entries drain to zero
- `tests/governance/` — OBPI creates `tests/governance/test_package_layer_order.py` (the permanent import-graph fixture + per-edge regression-invariants)
- `docs/design/adr/foundation/ADR-0.0.55-package-import-direction-invariant/**` — parent ADR package scope

## Denied Paths

- `data/package_layer_order.json`, `src/gzkit/governance/import_direction.py`, `.gzkit/rules/package-import-direction.md` — the manifest, helper, and rule are OBPI-01 scope
- `src/gzkit/governance/trust_audits/import_direction.py` — the validator's exit-code policy stays warn-only here; the fail-closed flip is OBPI-04
- The rule-version bump to `1.0.0` — OBPI-04 scope
- New abstraction subpackages (e.g. a new `commands/cli_helpers/` *subpackage*) without a migration receipt naming the relocation — the relocation target is a sibling *within* `commands/`, per ADR § Negative #6
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The `cli ↔ commands` bidirectional flow is resolved — the shared utilities are extracted into a sibling within `commands/` and `cli` imports them in the canonical direction (`cli` at L7 importing `commands` at L6). The reverse `commands → cli` edges are eliminated.
2. REQUIREMENT: The `governance → cli` and `governance → commands` back-edges are relocated — by moving consumed symbols into a lower vertical layer, by inverting through a `ports` Provider, or by promoting the consumed concern to a new Provider declaration with empirical justification recorded in the migration receipt.
3. REQUIREMENT: The `doc_coverage → commands`, `chores → commands`, and `justify → cli` back-edges each receive the same relocate-or-invert treatment.
4. REQUIREMENT: The `arb → commands` edge — a Provider importing a layer above its declared floor of L2 — is CLEANED, never exempted, because it breaks the Provider depend-only-on-lower-layers discipline (ADR § Decision item 3, criterion d).
5. REQUIREMENT: Each migrated edge is removed from `data/package_import_direction_baseline.json` with a commit trailer naming the migration receipt; the allowlist shrinks monotonically and carries zero `phase: bootstrap` entries at this OBPI's completion.
6. REQUIREMENT: Zero new predicate violations are introduced during this OBPI — the `gz validate --import-direction` validator (still warn-only) surfaces any new back-edge as a warning the OBPI completion gate rejects.
7. REQUIREMENT: Every back-edge migration is paired with a regression-invariant test under `tests/governance/test_package_layer_order.py` capturing the relocated symbol's behavior before and after the move; the test fails if post-migration behavior differs. The `# audit-exempt: regression-invariant-overlay <reason>` marker per `.claude/rules/adr-audit.md` is permitted where a test enforces the prior invariant.
8. REQUIREMENT: `tests/governance/test_package_layer_order.py` carries the import-graph empirical audit as a permanent fixture and asserts the violation inventory has shrunk by the migrated-edge count.
9. REQUIREMENT: No source file is relocated except as required by a named back-edge migration; existing module names are preserved (ADR § Scope boundary).
10. REQUIREMENT: NEVER include the operator's personal email in any migrated source, the baseline, or any test.

> STOP-on-BLOCKERS: if OBPI-02 has not landed (`gz validate --import-direction` not a registered scope), print BLOCKERS and halt — this OBPI depends on the validator tooling to verify zero-new-violations.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 3 — quote verbatim** into the brief's Implementation Summary. Decision item 3 is the contract.
- [ ] Parent ADR § Decision — the per-edge migration list (a/b/c/d) and the relocate-or-invert options.
- [ ] Parent ADR § Consequences — Negative #1 (longest-OBPI pre-mortem; regression-invariant pairing), Negative #6 (`cli ↔ commands` third-subpackage pre-mortem).
- [ ] Parent ADR § Q&A Transcript — the pre-authoring audit edge counts (the migration inventory).

**Governance (read once, cache):**

- [ ] `.gzkit/rules/package-import-direction.md` (OBPI-01) — the invariant the migration satisfies
- [ ] `.claude/rules/adr-audit.md` § Legitimate-authoring exemptions — the `# audit-exempt: regression-invariant-overlay` marker shape
- [ ] `.gzkit/rules/tests.md` § Tests assert semantics, not strings

**Context — the migration surface:**

- [ ] `data/package_import_direction_baseline.json` (OBPI-01) — the `phase: bootstrap` entries to drain
- [ ] `src/gzkit/governance/import_direction.py` — `compute_import_edges` for the before/after edge inventory
- [ ] The seven subpackages in scope (`cli`, `commands`, `governance`, `doc_coverage`, `chores`, `justify`, `arb`) — read the back-edge call sites before relocating

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01 landed: manifest, helper, baseline present
- [ ] OBPI-02 landed: `gz validate --import-direction` is a registered (warn-only) scope

**Existing Code (understand current state):**

- [ ] Each back-edge's call sites — the symbols crossing the layer boundary
- [ ] Existing tests adjacent to the relocated symbols — the behavior to pin with regression-invariant tests

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 3 quoted in Implementation Summary

### Gate 2: TDD

- [ ] Per-edge regression-invariant tests written before each relocation (capture prior behavior, then move)
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)
- [ ] Any runbook/manpage reference to a relocated symbol updated in the same patch set

### Gate 4: BDD (Heavy)

- [ ] No new BDD scenario applies — the migration preserves observable behavior (regression-invariant tests are the witness). Any runbook command whose code path moved is re-verified. Waiver noted.

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion
- [ ] Attestation confirms the baseline carries zero `phase: bootstrap` entries

## Verification

```bash
uv run python -c "import json; b = json.load(open('data/package_import_direction_baseline.json')); entries = b if isinstance(b, list) else b.get('entries', []); assert not [e for e in entries if isinstance(e, dict) and e.get('phase') == 'bootstrap'], 'bootstrap entries remain'; print('baseline drained of bootstrap entries')"
uv run gz validate --import-direction
uv run gz arb step --name unittest -- uv run -m unittest -q tests.governance.test_package_layer_order
uv run gz validate --documents --surfaces
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# The back-edge inventory has shrunk to zero genuine vertical-to-vertical violations:
uv run python -c "from pathlib import Path; from gzkit.governance.import_direction import compute_import_edges, violates_predicate; \
edges = compute_import_edges(Path('src/gzkit')); \
viol = [(s, d) for (s, d) in edges if violates_predicate(s, d)]; \
print('remaining predicate violations:', viol)"
# The baseline allowlist is drained of bootstrap entries:
uv run python -c "import json; print(json.load(open('data/package_import_direction_baseline.json')))"
```

## Acceptance Criteria

- [ ] REQ-0.0.55-03-01: Given parent ADR § Decision item 3, when the `cli ↔ commands` flow is inspected, then the bidirectional coupling is resolved — shared utilities sit within `commands/` and `cli` imports them in the canonical direction.
- [ ] REQ-0.0.55-03-02: Given the `governance → cli`/`governance → commands` back-edges, when migrated, then each is relocated, inverted through a `ports` Provider, or promoted to a Provider declaration with recorded empirical justification.
- [ ] REQ-0.0.55-03-03: Given the `doc_coverage → commands`, `chores → commands`, and `justify → cli` back-edges, when migrated, then each receives relocate-or-invert treatment and is removed from the baseline.
- [ ] REQ-0.0.55-03-04: Given the `arb → commands` Provider-to-above-floor leak, when this OBPI completes, then it is cleaned (not exempted) and `arb` imports only layers at or below its L2 floor.
- [ ] REQ-0.0.55-03-05: Given `data/package_import_direction_baseline.json`, when this OBPI completes, then it carries zero `phase: bootstrap` entries (monotonic drain).
- [ ] REQ-0.0.55-03-06: Given each back-edge migration, when `tests/governance/test_package_layer_order.py` runs, then a regression-invariant test pins the relocated symbol's behavior and the violation inventory has shrunk by the migrated-edge count.
- [ ] REQ-0.0.55-03-07: Given the no-new-violations bar, when `gz validate --import-direction` runs at completion, then zero new back-edges were introduced during the migration.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 3 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** Per-edge regression-invariant tests written before relocation; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (12+ accumulating back-edges) vs capability-now (genuine vertical-to-vertical violations migrated; baseline drained)
- [ ] **Key Proof:** The empty-of-bootstrap baseline; the shrunk violation inventory
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste unittest output + arb-step-unittest receipt ID here
```

### Code Quality

```text
# Paste lint + typecheck + mkdocs output here with ARB receipt IDs
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
