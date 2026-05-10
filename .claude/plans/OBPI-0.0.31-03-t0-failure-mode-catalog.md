# Plan: OBPI-0.0.31-03-t0-failure-mode-catalog

## OBPI Reference

**ID:** OBPI-0.0.31-03-t0-failure-mode-catalog
**Parent:** ADR-0.0.31-distribution-invariant-doctrine
**Lane:** Lite | **Kind:** Foundation
**Brief:** `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/obpis/OBPI-0.0.31-03-t0-failure-mode-catalog.md`

## Context

This OBPI authors `docs/governance/distribution_invariant_catalog.md` — the
operator-facing companion to the T0 doctrine paragraph in trust-doctrine.md.
The catalog turns T0 from "a paragraph anyone can cite" into "a checklist
anyone can apply."

**Source material:**
- T0 doctrine paragraph: `docs/governance/trust-doctrine.md` § T0 — Distribution
  Invariant (OBPI-0.0.31-01, Completed)
- Failure class analysis: GHI #318 body — classes A (rules unscaffolded),
  B (skills as stubs), C (wheel chores-only), D (re-run adds missing only)
- Chores precedent: ADR-0.0.21 § Intent — chores promoted to first-class surface
  with project-first + package-fallback resolution, by accident-of-timing not doctrine
- Mechanical enforcement: ADR-0.0.32 OBPIs 01-08

**Failure class → closing OBPI mapping (sourced from ADR-0.0.32 checklist):**
- A (rules unscaffolded): OBPI-0.0.32-03 (physical migration) + OBPI-0.0.32-04 (scaffolder)
- B (skills as stubs): OBPI-0.0.32-01 (physical migration) + OBPI-0.0.32-02 (scaffolder)
- C (wheel chores-only): OBPI-0.0.32-06 (smoke test + pyproject.toml) + OBPI-0.0.32-07 (validate --distribution)
- D (re-run adds missing only): OBPI-0.0.32-05 (gz init --update)

**Plan-before-exploration disclosure (GHI #288 Step 6a):**
- Destination-in-mind: Author a catalog doc in docs/governance/ following the same
  structure as defect-fix-routing.md and arb-middleware.md — narrative pedagogy sections
  with a concrete decision tree at the end.
- Rejected alternatives: (a) embed all examples directly in trust-doctrine.md — rejected
  because trust-doctrine.md is the doctrine layer; worked examples belong in a companion
  "application surface" document. (b) defer the catalog to ADR-0.0.32 — rejected because
  T0 is already doctrine-stable (OBPI-0.0.31-01 completed); the catalog applies the
  doctrine and should land with ADR-0.0.31, not wait for ADR-0.0.32 mechanics.

**Scope-edge flags (pre-authoring disclosure per brief STOP-on-BLOCKERS):**
1. REQ-5 requires a "see also" back-link in trust-doctrine.md. That file is listed in
   Denied Paths (for re-authoring the T0 doctrine paragraph). OBPI-0.0.31-01 did not
   add this link (confirmed by grep). Resolution: Allowed Paths amended below to include
   trust-doctrine.md for a single "see also" line addition only — not touching the
   doctrine paragraph.
2. REQ-8 requires runbook discoverability. Neither runbook has a canonical-surface
   promotion entry. Resolution: Allowed Paths amended to include governance_runbook.md
   for a one-line entry.

## Files

**Primary (new):**
- `docs/governance/distribution_invariant_catalog.md`

**Amended allowed paths (minimal scope expansions with rationale):**
- `docs/governance/trust-doctrine.md` — "see also" addition only (REQ-5; not denied
  for this purpose; OBPI-0.0.31-01 left this link unwritten)
- `docs/governance/governance_runbook.md` — one-line discoverability entry (REQ-8)

**Denied (unchanged from brief):**
- `src/**`, `tests/**`, `features/**`, `pyproject.toml` — no code surface
- `.gzkit/rules/**` — catalog is docs/governance/, not a rule promotion
- `docs/design/adr/foundation/ADR-0.0.32-*` — no backward cross-references

## Steps

### Step 1: Author `docs/governance/distribution_invariant_catalog.md`

Structure (all sections required):

**Opening paragraph** — cross-link to `trust-doctrine.md` § T0 as the doctrine this
catalog applies. One paragraph. No T0 redefinition.

**## Worked Example #1: GHI #318 — Self-Hosting Blindness**
How the dogfood loop concealed missing canonical shipment for the entire pre-1.0 cycle.
Sub-sections for each failure class with forward-link to the closing OBPI:
- **A — Rules entirely unscaffolded** → closed by OBPI-0.0.32-03 + OBPI-0.0.32-04
- **B — Skills scaffold as one-line stubs** → closed by OBPI-0.0.32-01 + OBPI-0.0.32-02
- **C — Wheel package-data is chores-only** → closed by OBPI-0.0.32-06 + OBPI-0.0.32-07
- **D — Re-run upgrade only adds missing** → closed by OBPI-0.0.32-05

**## Worked Example #2: The Chores Promotion Gap (ADR-0.0.21)**
How chores got the right packaging treatment by accident-of-timing rather than by
doctrine, and why that pattern is the implicit T0 enforcement that has been working
invisibly. Framed as "T0 was operationally true before it was named."

**## Is This a T0 Breach? (Decision Tree)**
Concrete yes/no branches, each terminating at a recovery action:
1. Does the surface ship in the wheel? (check `pyproject.toml` include list)
   → No → Recovery: extend `[tool.hatch.build.targets.wheel] include:`
2. Does `pip install py-gzkit && gz init` reproduce it? (check scaffolder)
   → No → Recovery: add `scaffold_core_<surface>()` call in `init_cmd`
3. Does the baseline manifest list it? (check `data/distribution_baseline_manifest.json`)
   → No → Recovery: extend the baseline manifest and re-run `gz validate --distribution`
4. Does `gz validate --distribution` cover it? (check validator scope)
   → No → Recovery: extend T0 validator scope (OBPI-0.0.32-07 pattern); file follow-up GHI if ADR-0.0.32 not yet closed

**Forward-link to ADR-0.0.32** — mechanical enforcement surface section.

### Step 2: Add "see also" to trust-doctrine.md § T0

Add one line below the existing T0 section's "Doctrine source" reference line:

```
**See also:** [T0 Failure-Mode Catalog](distribution_invariant_catalog.md) — worked examples and a "Is this a T0 breach?" decision tree for applying T0 to new canonical surfaces.
```

Do NOT modify the T0 doctrine paragraph itself.

### Step 3: Add runbook discoverability entry

In `docs/governance/governance_runbook.md`, locate the appropriate governance-maintainer
section and add:

```
When promoting a new canonical surface, read `docs/governance/distribution_invariant_catalog.md` first to check it against the T0 breach decision tree.
```

### Step 4: Verify

```bash
uv run gz lint
uv run gz validate --documents
uv run mkdocs build --strict

test -f docs/governance/distribution_invariant_catalog.md
grep -q "GHI #318" docs/governance/distribution_invariant_catalog.md
grep -q "ADR-0.0.21" docs/governance/distribution_invariant_catalog.md
grep -q "ADR-0.0.32" docs/governance/distribution_invariant_catalog.md
grep -q "trust-doctrine" docs/governance/distribution_invariant_catalog.md
grep -ic "decision tree\|is this a t0 breach" docs/governance/distribution_invariant_catalog.md
```

## Verification

Per OBPI brief § Verification:

```bash
uv run gz lint
uv run gz validate --documents
uv run mkdocs build --strict
test -f docs/governance/distribution_invariant_catalog.md
grep -q "GHI #318" docs/governance/distribution_invariant_catalog.md
grep -q "ADR-0.0.21" docs/governance/distribution_invariant_catalog.md
grep -q "ADR-0.0.32" docs/governance/distribution_invariant_catalog.md
grep -q "trust-doctrine" docs/governance/distribution_invariant_catalog.md
grep -ic "decision tree\|is this a t0 breach" docs/governance/distribution_invariant_catalog.md
```

## Notes

- Documentation-only OBPI. No unit tests required. Gate 2 = validation gates only.
- Foundation-lite lane; Gate 5 brief-level human attestation required.
- Prerequisites confirmed: OBPI-0.0.31-01 Completed (T0 doctrine stable);
  OBPI-0.0.31-02 Draft; ADR-0.0.32 booked.
- Scope-edge flags recorded above as pre-authoring disclosure.
- No third worked example planned: GHI #318 + ADR-0.0.21 are the two canonical real
  examples. No current in-flight hook-promotion or persona-promotion meets the bar
  for a concrete third example without becoming contrived. Brief REQ-4 confirms two
  real examples beat three with a contrived third.
