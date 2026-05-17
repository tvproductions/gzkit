# Plan: OBPI-0.0.35-01-concept-page

**OBPI:** `OBPI-0.0.35-01-concept-page`
**Parent ADR:** `ADR-0.0.35-foundation-feature-invariance-test`
**Lane:** Lite
**Authored:** 2026-05-17

## Context

OBPI-0.0.35-01 authors the canonical operator-facing reference for the Foundation/Feature Invariance Test. The concept page lands the verbatim invariance test, the hexagonal-ports lens with port/plug definitions, both worked examples (ledger discipline vs. backend; ADR-0.0.33/0.0.34 paired foundations), the anti-pattern ("classifying as foundation because it feels foundational"), and integrates bidirectionally into the existing concept surface.

No source code changes. No test files. Pure documentation. The semantic equivalent of TDD red-green is: mkdocs --strict fails before the page exists (broken nav link), passes after authoring.

## Files

**Create:**
- `docs/user/concepts/foundation-feature-invariance-test.md` — the canonical concept page

**Modify:**
- `docs/user/concepts/adr-taxonomy.md` — one forward cross-link to the new page in the Related section
- `docs/user/index.md` — add concept page entry in a Concepts section
- `mkdocs.yml` — nav entry after "ADR Taxonomy" under `Concepts:` block
- `docs/user/runbook.md` — cross-reference at `## PRD → ADR Derivation` section where kind classification is discussed

## Steps

### Step 1: Verify prerequisites (STOP-on-BLOCKERS)

```bash
test -f docs/user/concepts/adr-taxonomy.md && echo "adr-taxonomy.md exists" || echo "BLOCKER: adr-taxonomy.md missing"
grep -n "Concepts:" mkdocs.yml && echo "mkdocs.yml Concepts block found" || echo "BLOCKER: Concepts block missing"
```

### Step 2: Capture failing-state evidence (Gate 2 RGR)

Add nav entry to mkdocs.yml first (creates broken link), then run:
```bash
uv run mkdocs build --strict 2>&1 | tail -20
```
This produces the "red" evidence — build fails because the linked page doesn't exist yet.

### Step 3: Author `docs/user/concepts/foundation-feature-invariance-test.md`

The page mirrors `adr-taxonomy.md` structure:
- No frontmatter (prose-first)
- H1: "Foundation/Feature Invariance Test"
- H2 sections: "The invariance test", "The hexagonal-ports lens", "Worked examples", "The anti-pattern", "Related"
- Content requirements (all FAIL-CLOSED):
  - Verbatim test: *"Foundation = without it, we wouldn't be doing the project."*
  - Hexagonal-ports lens with explicit port-vs-plug definitions
  - Ledger discipline (foundation) vs. storage backend (feature) worked example — both sides classified
  - ADR-0.0.33 + ADR-0.0.34 paired-foundations example — invariance answer named for each
  - Anti-pattern: *"classifying as foundation because it feels foundational"* + corrective

### Step 4: Update `docs/user/concepts/adr-taxonomy.md`

Add one forward cross-link sentence/entry in the `## Related` section:
```
- [Foundation/Feature Invariance Test](foundation-feature-invariance-test.md) — one-line test that resolves the substrate-vs-port and doctrine-vs-tooling edge cases.
```

Verify the new page links back to `adr-taxonomy.md` (already included in Step 3 page's Related section).

### Step 5: Update `docs/user/index.md`

Add a Concepts section (currently absent) with links to the concept pages. Minimum: an entry for the new page. Preferred: a short Concepts section listing the canonical concept pages including the new one, consistent with the mkdocs nav listing.

### Step 6: Update `mkdocs.yml`

Insert nav entry after `ADR Taxonomy: user/concepts/adr-taxonomy.md`:
```yaml
- Foundation/Feature Invariance Test: user/concepts/foundation-feature-invariance-test.md
```

(Step 2 above already does this to capture the failing state; Step 3 then satisfies it.)

### Step 7: Update `docs/user/runbook.md`

At `## PRD → ADR Derivation`, in the paragraph referencing `adr-taxonomy.md` (around line 758), add a cross-reference to the new concept page for the invariance test. Natural insertion point: after "See `docs/user/concepts/adr-taxonomy.md` for the canonical definitions..." add: "For edge cases where the heuristic leaves classification ambiguous — substrate-vs-port or doctrine-vs-tooling — apply the one-line invariance test in [`concepts/foundation-feature-invariance-test.md`](concepts/foundation-feature-invariance-test.md)."

Also add a cross-reference at the "### Anti-pattern: foundation-first, features-on-top" section which discusses foundation kind decisions directly.

### Step 8: Verify all cross-links

```bash
# Page exists and contains verbatim test
test -f docs/user/concepts/foundation-feature-invariance-test.md
grep -F "Foundation = without it, we wouldn't be doing the project" docs/user/concepts/foundation-feature-invariance-test.md

# Bidirectional cross-link
grep -F "foundation-feature-invariance-test" docs/user/concepts/adr-taxonomy.md
grep -F "adr-taxonomy" docs/user/concepts/foundation-feature-invariance-test.md

# Index and nav integration
grep -F "foundation-feature-invariance-test" docs/user/index.md
grep -F "foundation-feature-invariance-test" mkdocs.yml

# Runbook cross-reference
grep -F "foundation-feature-invariance-test" docs/user/runbook.md
```

### Step 9: mkdocs --strict clean build (Gate 3)

```bash
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb ruff
```

### Step 10: Present OBPI Acceptance Ceremony

Present Stage 4 evidence to operator for foundation-kind brief-level Gate 5 attestation.

## Verification

```bash
uv run mkdocs build --strict
grep -F "Foundation = without it, we wouldn't be doing the project" docs/user/concepts/foundation-feature-invariance-test.md
grep -F "foundation-feature-invariance-test" docs/user/concepts/adr-taxonomy.md
grep -F "adr-taxonomy" docs/user/concepts/foundation-feature-invariance-test.md
grep -F "foundation-feature-invariance-test" docs/user/index.md
grep -F "foundation-feature-invariance-test" mkdocs.yml
grep -F "foundation-feature-invariance-test" docs/user/runbook.md
```

## Notes

- Lane: Lite — no ARB receipts beyond mkdocs and ruff (no src/ changes)
- Foundation-kind parent → brief-level Gate 5 human attestation required
- Scope collisions (54 sibling-ADR overlaps on runbook.md/index.md) are advisory-only — all contested OBPIs are Completed
- No tests/ changes allowed; no src/ changes allowed
- The "red" mkdocs --strict evidence must be captured BEFORE Step 3 authoring
