# Plan: OBPI-0.0.31-01-author-t0-doctrine

**OBPI:** `OBPI-0.0.31-01-author-t0-doctrine`
**Parent ADR:** `ADR-0.0.31-distribution-invariant-doctrine`
**Lane:** Lite (foundation-kind → Gate 5 required)

## Context

This OBPI lands T0 as authored doctrine in `docs/governance/trust-doctrine.md`.
The trust-doctrine page currently establishes T1/T2/T3 layers; this OBPI extends
it by prepending a T0 layer (Distribution) to the table and adding the T0 paragraph.

The verbatim failure-mode quote (from GHI #318 and ADR-0.0.31 § Decision):
> "a wheel that ships without a canonical surface is a T0 breach, regardless of
> whether downstream `gz init` reports success"

The three-item mechanical enforcement contract (verbatim from ADR-0.0.31 § Decision):
1. A T0 audit MUST detect missing package data without depending on downstream installation evidence.
2. A T0 audit MUST distinguish "canonical surface authored but not shipped" (the GHI #318 class) from "canonical surface authored and shipped" (correct state) and from "no canonical surface authored" (out of scope — T0 governs *delivery* of authored canon, not authorship volume).
3. A T0-passing build MUST produce a wheel that, when installed into a fresh venv and run through `gz init`, yields a project whose canonical surfaces are byte-equivalent (modulo project-name substitution) to a frozen baseline manifest.

## Files

**Allowed (from OBPI brief):**
- `docs/governance/trust-doctrine.md` — extend layer table T1/T2/T3 → T0/T1/T2/T3, add T0 paragraph
- `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md` — cross-link from Evidence section

**Denied (all others, per brief):**
- `docs/governance/advisory-rules-audit.md` (OBPI-0.0.31-02 scope)
- `docs/governance/distribution_invariant_catalog.md` (OBPI-0.0.31-03 scope)
- `src/**`, `tests/**`, `features/**`, `pyproject.toml`, `.gzkit/rules/**`
- `docs/design/adr/foundation/ADR-0.0.32-*`

## Steps

### Step 1: Extend the layer table in trust-doctrine.md

The existing layer section in trust-doctrine.md has T1/T2/T3 as three-column
rows under `### The three invariants`. The *layer table* (from ADR-0.0.31 § Decision):

| Layer | Authority | Question it answers |
|-------|-----------|---------------------|
| **T0** | Distribution | Does the wheel reproducibly deliver every canonical surface to a fresh `gz init`? |
| **T1** | Canon | What is the authored, source-controlled truth? |
| **T2** | Ledger | What event sequence has been witnessed? |
| **T3** | Derived | What does a current view assert? |

Trust-doctrine.md currently does not contain a layer table like this — it names
T1/T2/T3 as invariants. T0 must be integrated as a new layer entry that sits
*upstream* of T1 in the conceptual hierarchy.

Locate the appropriate section in trust-doctrine.md to add a new "## T0 — Distribution Invariant" section above the three invariants section, and add T0 to the layer table if one exists (or create the table).

### Step 2: Author the T0 paragraph

Write a new section `## T0 — Distribution Invariant` that:

1. Names T0's authority as "Distribution" and its question as "Does the wheel
   reproducibly deliver every canonical surface to a fresh `gz init`?"
2. Includes the verbatim failure-mode quote from GHI #318:
   > "a wheel that ships without a canonical surface is a T0 breach, regardless of
   > whether downstream `gz init` reports success"
3. Forward-links to ADR-0.0.32 as the named mechanical enforcement surface.
4. States the three-item mechanical enforcement contract verbatim (from ADR-0.0.31 § Decision).
5. Explains T0 sits upstream of T1: if a canonical surface only exists in the
   repo's `.gzkit/` and never ships, then T1 (canon-as-truth) is silently
   project-specific instead of project-portable.

The paragraph follows the same authority/question framing that T1/T2/T3 use.

### Step 3: Update trust-doctrine.md "Related" section

Add a reference to ADR-0.0.31 in the `## Related` section of trust-doctrine.md
so readers can trace T0 to its backing ADR.

### Step 4: Cross-link from ADR-0.0.31 Evidence section

In `ADR-0.0.31-distribution-invariant-doctrine.md`, update the `## Evidence` section
to confirm the bidirectional link:

```markdown
- [x] Doctrine: `docs/governance/trust-doctrine.md` (T0 paragraph alongside T1/T2/T3 table) — added T0 layer, failure-mode quote, three-item contract, forward-link to ADR-0.0.32
- [x] Cross-link: this ADR references the trust-doctrine layer table (see ## Evidence)
```

### Step 5: Run verification

```bash
uv run gz validate --documents
uv run gz lint
uv run mkdocs build --strict
grep -q "T0" docs/governance/trust-doctrine.md && echo "T0 found"
grep -q "ADR-0.0.32" docs/governance/trust-doctrine.md && echo "ADR-0.0.32 linked"
grep -q "trust-doctrine" docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md && echo "cross-link confirmed"
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run mkdocs build --strict
grep -n "T0" docs/governance/trust-doctrine.md
grep -n "ADR-0.0.32" docs/governance/trust-doctrine.md
```

## Notes

- Documentation-only work — no Python edits, no source changes, no tests needed
- Gate 5 (human attestation) is required because parent ADR is `kind: foundation`
- Scorecard entry in advisory-rules-audit.md is explicitly OUT OF SCOPE (OBPI-0.0.31-02)
- The failure-mode catalog is explicitly OUT OF SCOPE (OBPI-0.0.31-03)

### Destination-in-mind disclosure (Step 6a)

**Approach formed before authoring this plan:** Prepend a T0 row to the trust-doctrine
layer table and add a corresponding `## T0 — Distribution Invariant` section above
the existing T1/T2/T3 invariants. This was formed from reading the OBPI brief objective
and the ADR-0.0.31 § Decision layer table.

**Rejected alternatives:**
1. Adding T0 as a new section at the end with a pointer to the table — rejected
   because REQ-02 requires T0 to be the *first* (upstream) row in the table.
2. Creating a separate `t0-distribution-invariant.md` linked from trust-doctrine.md
   — rejected because the brief requires T0 paragraph to be *in* trust-doctrine.md
   alongside T1/T2/T3.
3. Renaming T1/T2/T3 → T2/T3/T4 to insert T0 at T1 — rejected because T1/T2/T3
   naming is established across the codebase with multiple references.
